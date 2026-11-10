from figlib import *


def vol_set(cs, base, spikes):
    for i, c in enumerate(cs):
        c['v'] = base * (0.85 + 0.3 * ((i * 7) % 5) / 4)
    for i, v in spikes.items():
        cs[i]['v'] = v


# ============================================================ 10.1 откат в тренде
cs = synth([100, 107, 104, 120, 111, 113, 112.5, 121], bars_per_leg=[6, 3, 9, 7, 1, 2, 9], noise=0.15, seed=11)
# свеча 24 — конец отката (минимум 111), свеча 25 — зелёная с нижней тенью
cs[24].update(c=112.0, l=111.0)
cs[24]['o'] = max(cs[24]['o'], 112.6)
cs[24]['h'] = max(cs[24]['h'], cs[24]['o'] + 0.2)
cs[25].update(o=112.0, l=110.9, c=113.0, h=113.3)
n = len(cs)
ch = Chart(cs, schematic=True, extra_bars=3, main_h=330,
           title='Откат в тренде: покупаем коррекцию у опоры, а не импульс',
           subtitle='Схема, цены условные')
ch.zone(110.5, 112.5, 0, n + 2, kind='support', label='Зона поддержки 1D')
ch.line([(0, 101.5), (n - 1, 116.0)], color=ORANGE, width=2)
ch.text(1, 102.6, 'EMA 50', size=12, color=ORANGE, weight=600)
ch.hline(120, 0, 24.5, color=RED, dash=True, label='Сопротивление: прежний максимум', label_at='left', tag=False)
ch.mark(13, 113, 'Импульс', where='left')
ch.mark(21, 116, 'Откат', where='right')
ch.mark(24, 111, 'Минимум отката', where='left')
ch.mark(25, 113.3, 'Свеча-триггер', where='above', color=BLUE)
ch.trade(25, 113, 110, 119.5, i_end=n + 1,
         labels=('Вход: закрытие триггера', 'Стоп: минимум отката − 0,5 ATR', 'Цель: перед сопротивлением, R:R 1:2,2'), show_rr=False)
ch.save('10-model-pullback.svg')

# ============================================================ 10.2 пробой и ретест
cs = synth([100, 109.5, 104, 110, 105.5, 113.5, 110.3, 112, 111.6, 119.5],
           bars_per_leg=[6, 4, 5, 4, 5, 3, 1, 2, 8], noise=0.15, seed=5)
vol_set(cs, 100, {22: 250, 23: 330, 24: 70, 25: 55, 26: 45, 27: 85})
n = len(cs)
ch = Chart(cs, schematic=True, extra_bars=2, main_h=330,
           title='Пробой и ретест: пробитое сопротивление проверяют как поддержку',
           subtitle='Схема, цены условные')
ch.zone(109, 110.5, 0, 22, kind='resistance')
ch.text(0.3, 111.3, 'Сопротивление 1D', size=12, color=RED, weight=600)
ch.zone(109, 110.5, 22, n + 1, kind='support', label='…стало поддержкой', label_at='right')
ch.zone(118.5, 120, 29, n + 1, kind='resistance', label='Следующее сопротивление 1D', label_at='right')
ch.mark(5, cs[5]['h'], 'Касание 1', where='above')
ch.mark(14, cs[14]['h'], 'Касание 2', where='above')
ch.mark(23, cs[23]['h'], 'Пробой: закрытие выше зоны,\nобъём выше среднего', where='left')
ch.mark(26, cs[26]['l'], 'Ретест', where='left')
ch.mark(27, cs[27]['h'], 'Свеча-триггер', where='above', color=BLUE)
ch.trade(27, 112, 109.3, 118, i_end=n - 1,
         labels=('Вход: закрытие триггера', 'Стоп: минимум ретеста − 0,5 ATR', ''), show_rr=False)
ch.text(33, 117.3, 'Цель: перед сопротивлением, R:R 1:2,2', anchor='end', size=12, color=GREEN, weight=600)
ch.volume()
ch.save('10-model-breakout-retest.svg')

# ============================================================ 10.3 BTC, пробой и ретест, убыток
f = load('btc', '4h')
cl = [c['c'] for c in f]
e50 = ema(cl, 50)
a, b = find(f, '2024-09-19 00:00'), find(f, '2024-10-02 20:00')
cs = f[a:b + 1]
ix = lambda d: find(f, d) - a
ib, ir, it, ip, istop = (ix('2024-09-26 12:00'), ix('2024-09-26 20:00'), ix('2024-09-27 00:00'),
                         ix('2024-09-27 12:00'), ix('2024-09-30 00:00'))
ch = Chart(cs, title='Пробой и ретест по всем правилам закончились стопом',
           subtitle='BTC/USDT, 4H, 19 сентября — 2 октября 2024', main_h=340, extra_bars=2)
ch.zone(64500, 65000, kind='resistance', label='Сопротивление 1D 64 500–65 000')
ch.mark(ib, cs[ib]['h'], 'Пробой: закрытие 65 229, объём ×3,3', where='left')
ch.mark(ir, cs[ir]['l'], 'Ретест 64 634', where='below')
ch.mark(it, cs[it]['h'], 'Триггер', where='above', color=BLUE)
ch.mark(ip, cs[ip]['h'], '+1R: 66 498', where='above')
ch.mark(istop, cs[istop]['l'], 'Стоп, −1R', where='below', color=RED)
ch.trade(it, 65366, 64233, 68100, i_end=istop, labels=('', '', ''), show_rr=False, prices=False)
ch.text(istop - 1, 65000, 'Вход 65 366', anchor='end', size=12, color=BLUE, weight=600)
ch.text(istop - 4, 63950, 'Стоп 64 233', anchor='end', size=12, color=RED, weight=600)
ch.text(istop, 67550, 'Цель 68 100, R:R 1:2,4', anchor='end', size=12, color=GREEN, weight=600)
ch.volume()
ch.save('10-breakout-retest-btc-loss.svg')

# ============================================================ 10.4 ложный пробой
c1 = synth([116, 101, 112, 100.5, 110, 100.6], bars_per_leg=[8, 6, 6, 5, 5], noise=0.15, seed=4)
trig = {'o': 100.6, 'h': 102.3, 'l': 98.6, 'c': 102.0, 'v': 0}
c2 = synth([102, 101.8, 115.5], bars_per_leg=[2, 10], noise=0.15, seed=9)
cs = c1 + [trig] + c2
it = len(c1)
n = len(cs)
ch = Chart(cs, schematic=True, extra_bars=2, main_h=380,
           title='Ложный пробой: вход после возврата цены в зону',
           subtitle='Схема, цены условные')
ch.zone(100, 101.5, 0, n + 1, kind='support', label='Поддержка 1D: нижняя граница диапазона')
ch.zone(115, 116.5, 0, n + 1, kind='resistance', label='Верхняя граница диапазона', label_at='right')
ch.text(1, 98.4, 'Стопы покупателей и стоп-ордера продавцов пробоя', size=12, color=MUTED)
ch.mark(7, 101, 'Касание 1', where='below')
ch.mark(19, 100.5, 'Касание 2', where='below')
ch.mark(it, 98.6, 'Прокол', where='left')
ch.mark(it, 102.3, 'Свеча-триггер: закрытие выше зоны', where='above', color=BLUE)
ch.trade(it, 102, 97.9, 114.5, i_end=n - 1,
         labels=('Вход: закрытие триггера', 'Стоп: минимум прокола − 0,5 ATR', ''), show_rr=False)
ch.text(33, 113.7, 'Цель: у границы диапазона, R:R 1:3', anchor='end', size=12, color=GREEN, weight=600)
ch.save('10-model-false-breakout.svg')

# ============================================================ 10.5 BTC, ложный пробой, прибыль
a, b = find(f, '2024-12-29 00:00'), find(f, '2025-01-17 20:00')
cs = f[a:b + 1]
ix = lambda d: find(f, d) - a
i1, i2, ip, it_ = ix('2024-12-30 12:00'), ix('2025-01-09 20:00'), ix('2025-01-13 12:00'), ix('2025-01-15 12:00')
ch = Chart(cs, title='Прокол поддержки и возврат в зону дали вход с R:R 1:2',
           subtitle='BTC/USDT, 4H, 29 декабря 2024 — 17 января 2025', main_h=340, extra_bars=2,
           ymin=87500, ymax=106500)
ch.zone(90500, 91530, kind='support', label='Поддержка 1D 90 500–91 530')
ch.mark(i1, cs[i1]['l'], '', where='below')
ch.text(i1 - 2, 89400, 'Касание 30 декабря', anchor='start', size=12, weight=600)
ch.mark(i2, cs[i2]['l'], 'Касание 9 января', where='below')
ch.mark(ip, cs[ip]['l'], 'Прокол: минимум 89 257, закрытие 92 124, объём ×5,2', where='left', color=BLUE)
ch.mark(it_, cs[it_]['h'], 'Цель, +2,01R', where='above', color=GREEN)
ch.trade(ip, 92124, 88503, 99400, i_end=it_,
         labels=('Вход', 'Стоп', 'Цель'), show_rr=False)
ch.volume()
ch.save('10-false-breakout-btc.svg')
