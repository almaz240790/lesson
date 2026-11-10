#!/usr/bin/env python3
"""Глава 13. Демонстрационный бэктест правила «Откат к EMA 50 на 4H по тренду 1D».

Правило зафиксировано ДО запуска (см. RULE ниже). Скрипт печатает метрики целиком, по годам,
по парам и на отложенном отрезке; сохраняет список сделок в ch13_trades.json.

Запуск:  python3 ch13_backtest.py            # основной прогон
         python3 ch13_backtest.py plateau    # проверка «плато» по длине EMA (40/50/60)
"""
import datetime as dt
import json
import math
import os
import sys

sys.path.insert(0, '/home/user/lesson/10_Учебник/img/src')
from figlib import load, ema, atr  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))

RULE = dict(
    ema_day=200,        # 1D: закрытие последней закрытой дневной свечи выше EMA 200
    ema_4h=50,          # 4H: сигнальная свеча коснулась EMA 50 (low <= EMA) и закрылась выше неё
    lookback=6,         # минимум отката = минимум сигнальной свечи и 5 свечей перед ней (сутки на 4H)
    atr_n=14,           # ATR(14) на 4H
    atr_pad=0.5,        # запас стопа: 0,5 x ATR
    target_r=2.0,       # цель 2R
    fee=0.001,          # комиссия 0,1% за сторону
    min_stop=0.02,      # стоп не ближе 2% от входа (комиссия за круг 0,2% x 10)
    start='2020-01-01', # начало теста (EMA 200 на 1D к этому дню посчитана по 365 свечам)
    split='2025-01-01', # с этой даты — отложенный отрезок
)


def prepare(sym, rule):
    d1 = load(sym, '1d')
    h4 = load(sym, '4h')
    e200 = ema([c['c'] for c in d1], rule['ema_day'])
    day_ok = {}                               # дата дневной свечи -> закрытие выше EMA 200
    for c, e in zip(d1, e200):
        day_ok[c['date']] = (e is not None and c['c'] > e)
    e50 = ema([c['c'] for c in h4], rule['ema_4h'])
    a14 = atr(h4, rule['atr_n'])
    return d1, h4, day_ok, e50, a14


def last_closed_day(c4):
    """Дата последней дневной свечи, закрытой к моменту закрытия 4H-свечи c4."""
    t_close = c4['t'] + 4 * 3600
    d = dt.datetime.fromtimestamp(t_close, dt.timezone.utc)
    return (d.date() - dt.timedelta(days=1)).strftime('%Y-%m-%d')


def signals(sym, rule):
    """Сигналы по одной паре: словарь {t открытия свечи входа: параметры сделки}."""
    d1, h4, day_ok, e50, a14 = prepare(sym, rule)
    out = {}
    skipped_close_stop = 0
    for i in range(rule['lookback'], len(h4) - 1):
        c = h4[i]
        if c['date'] < rule['start'] or e50[i] is None or a14[i] is None:
            continue
        if not day_ok.get(last_closed_day(c), False):
            continue
        if not (c['l'] <= e50[i] < c['c'] and c['c'] > c['o']):
            continue
        entry = h4[i + 1]['o']                               # сигнал по закрытию -> вход на следующей свече
        low = min(x['l'] for x in h4[i - rule['lookback'] + 1:i + 1])
        stop = low - rule['atr_pad'] * a14[i]
        risk = entry - stop
        if risk <= 0:
            continue
        if risk / entry < rule['min_stop']:
            skipped_close_stop += 1
            continue
        out[h4[i + 1]['t']] = dict(sym=sym, i_sig=i, i_entry=i + 1, entry=entry, stop=stop,
                                   target=entry + rule['target_r'] * risk, risk=risk,
                                   ema50=e50[i], atr=a14[i], low=low)
    return h4, out, skipped_close_stop


def resolve(h4, s, rule):
    """Ведёт сделку от свечи входа до стопа или цели. В одной свече и стоп, и цель -> считаем стоп."""
    entry, stop, target, risk = s['entry'], s['stop'], s['target'], s['risk']
    for j in range(s['i_entry'], len(h4)):
        c = h4[j]
        if c['l'] <= stop:
            px = min(stop, c['o'])            # гэп ниже стопа -> исполнение по открытию
            kind = 'stop'
        elif c['h'] >= target:
            px = target
            kind = 'target'
        else:
            continue
        gross = (px - entry) / risk
        cost = rule['fee'] * (entry + px) / risk
        return dict(i_exit=j, exit=px, kind=kind, gross=gross, cost=cost, r=gross - cost,
                    t_exit=c['t'], exit_date=c['date'])
    return None


def run(rule=RULE, syms=('btc', 'eth'), verbose=False):
    """Общий счёт: одновременно открыта одна сделка (BTC и ETH в одну сторону = одна позиция).
    Сигналы в одну и ту же свечу: берём BTC."""
    data, sigs, skipped = {}, {}, {}
    for s in syms:
        data[s], sigs[s], skipped[s] = signals(s, rule)
    times = sorted({t for s in syms for t in sigs[s]})
    trades, busy_until, missed = [], -1, 0
    for t in times:
        if t <= busy_until:                    # позиция ещё открыта (или закрылась в этой же свече)
            missed += sum(1 for s in syms if t in sigs[s])
            continue
        cands = [s for s in syms if t in sigs[s]]
        s = cands[0]
        missed += len(cands) - 1
        sig = sigs[s][t]
        res = resolve(data[s], sig, rule)
        if res is None:                        # не закрылась до конца данных
            break
        h4 = data[s]
        tr = dict(sig)
        tr.update(res)
        tr['entry_date'] = h4[sig['i_entry']]['date']
        tr['signal_date'] = h4[sig['i_sig']]['date']
        tr['bars'] = res['i_exit'] - sig['i_entry'] + 1
        trades.append(tr)
        busy_until = res['t_exit']
    return trades, dict(skipped_close_stop=skipped, missed_busy=missed)


def metrics(rs):
    n = len(rs)
    if n == 0:
        return None
    wins = [r for r in rs if r > 0]
    losses = [-r for r in rs if r <= 0]
    p = len(wins) / n
    W = sum(wins) / len(wins) if wins else 0.0
    L = sum(losses) / len(losses) if losses else 0.0
    E = sum(rs) / n
    pf = sum(wins) / sum(losses) if losses and sum(losses) > 0 else float('inf')
    sd = math.sqrt(sum((r - E) ** 2 for r in rs) / (n - 1)) if n > 1 else 0.0
    eq = peak = 0.0
    dd = 0.0
    i_peak = 0
    dd_span = (0, 0)
    for k, r in enumerate(rs, 1):
        eq += r
        if eq > peak:
            peak, i_peak = eq, k
        if peak - eq > dd:
            dd, dd_span = peak - eq, (i_peak, k)
    streak = best = 0
    for r in rs:
        streak = streak + 1 if r <= 0 else 0
        best = max(best, streak)
    return dict(n=n, wins=len(wins), p=p, W=W, L=L, E=E, total=sum(rs), pf=pf, sd=sd,
                maxdd=dd, dd_span=dd_span, streak=best)


def fmt(m):
    if m is None:
        return 'нет сделок'
    return (f"N={m['n']:3d}  приб={m['wins']:3d}  винрейт={m['p'] * 100:5.1f}%  W={m['W']:.2f}R  L={m['L']:.2f}R  "
            f"E={m['E']:+.3f}R  итог={m['total']:+6.1f}R  PF={m['pf']:.2f}  σ={m['sd']:.2f}  "
            f"maxDD={m['maxdd']:.1f}R {m['dd_span']}  серия={m['streak']}")


def report(trades, info, rule=RULE):
    rs = [t['r'] for t in trades]
    print('Сделок:', len(trades), '| пропущено из-за близкого стопа:', info['skipped_close_stop'],
          '| пропущено, пока позиция открыта:', info['missed_busy'])
    print('ВСЕ          ', fmt(metrics(rs)))
    print('без комиссии ', fmt(metrics([t['gross'] for t in trades])))
    print('средняя комиссия в R:', round(sum(t['cost'] for t in trades) / len(trades), 3),
          '| средний стоп, %:', round(100 * sum(t['risk'] / t['entry'] for t in trades) / len(trades), 2),
          '| средняя длительность, свечей 4H:', round(sum(t['bars'] for t in trades) / len(trades), 1))
    dev = [t['r'] for t in trades if t['entry_date'] < rule['split']]
    oos = [t['r'] for t in trades if t['entry_date'] >= rule['split']]
    print('РАЗРАБОТКА   ', fmt(metrics(dev)))
    print('ОТЛОЖЕННЫЙ   ', fmt(metrics(oos)))
    for y in sorted({t['entry_date'][:4] for t in trades}):
        print(y, '        ', fmt(metrics([t['r'] for t in trades if t['entry_date'][:4] == y])))
    for s in ('btc', 'eth'):
        print(s.upper(), '         ', fmt(metrics([t['r'] for t in trades if t['sym'] == s])))
    m = metrics(rs)
    if m['E'] > 0:
        print('N = (2σ/E)² =', round((2 * m['sd'] / m['E']) ** 2))


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'plateau':
        for n in (40, 50, 60):
            r = dict(RULE, ema_4h=n)
            tr, info = run(r)
            dev = [t['r'] for t in tr if t['entry_date'] < r['split']]
            print(f'EMA {n} (разработка 2020–2024):', fmt(metrics(dev)))
        sys.exit(0)
    trades, info = run()
    report(trades, info)
    keep = ('sym', 'signal_date', 'entry_date', 'exit_date', 'entry', 'stop', 'target', 'exit', 'kind',
            'gross', 'cost', 'r', 'bars', 'ema50', 'atr', 'low')
    out = [{k: (round(t[k], 4) if isinstance(t[k], float) else t[k]) for k in keep} for t in trades]
    with open(os.path.join(HERE, 'ch13_trades.json'), 'w', encoding='utf-8') as f:
        json.dump(dict(rule=RULE, trades=out), f, ensure_ascii=False, indent=1)
    print('saved ch13_trades.json')
