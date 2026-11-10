import json
import sys

from figlib import *

import ch13_backtest as bt  # правило бэктеста из главы 13.7, прогоняется на реальных свечах

trades, _info = bt.run()


def rfmt(x, d=1, sign=True):
    s = f'{x:+.{d}f}' if sign else f'{x:.{d}f}'
    return s.replace('-', '−').replace('.', ',')


# ------------------------------------------------------------ 13.1 цикл проверки
cv = Canvas(760, 330, title='Правило становится системой после трёх проверок и может вернуться в начало с любой',
            subtitle='Каждый этап заканчивается разбором по журналу; дальше проходит только то, что выдержало проверку')
names = [
    ('Гипотеза', ['правила «да/нет»', 'записаны в план'], MUTED),
    ('Бэктест', ['100 сделок,', 'отложенный отрезок', 'смотрят один раз'], BLUE),
    ('Демосчёт', ['100 сделок по плану,', 'правила в 95%', 'сделок'], GREEN),
    ('Реальный счёт', ['малый, риск 0,5–1%', 'на сделку, без плеча'], AMBER),
    ('Система', ['работает, пока', 'метрики в норме'], PURPLE),
]
bw_, gap, x0 = 134, 15.5, 14
by, bh = cv.y0 + 6, 104
xs = [x0 + k * (bw_ + gap) for k in range(5)]
for k, (nm, lines, col) in enumerate(names):
    cv.rect(xs[k], by, bw_, bh, fill=col, stroke=col, opacity=0.10)
    cv.rect(xs[k], by, bw_, bh, stroke=col, sw=1.5)
    cv.text(xs[k] + bw_ / 2, by + 24, nm, size=13.5, anchor='middle', color=INK, weight=700)
    for j, s in enumerate(lines):
        cv.text(xs[k] + bw_ / 2, by + 46 + j * 17, s, size=11.5, anchor='middle', color=MUTED)
    if k < 4:
        cv.arrow(xs[k] + bw_ + 2, by + bh / 2, xs[k + 1] - 2, by + bh / 2, color=INK, width=1.75)
ry = by + bh + 58
for k in (1, 2, 3):
    cx = xs[k] + bw_ / 2
    cv.line(cx, by + bh + 2, cx, ry, color=RED, width=1.5, dash=True)
cv.line(xs[1] + bw_ / 2, ry, xs[0] + bw_ / 2, ry, color=RED, width=1.5, dash=True)
cv.line(xs[3] + bw_ / 2, ry, xs[1] + bw_ / 2, ry, color=RED, width=1.5, dash=True)
cv.arrow(xs[0] + bw_ / 2, ry, xs[0] + bw_ / 2, by + bh + 2, color=RED, width=1.5)
cv.text((xs[1] + xs[3] + bw_) / 2, ry + 22,
        'Не выдержало проверку: вернуться к гипотезе и изменить одно правило', size=13, anchor='middle', color=RED, weight=600)
cv.text(x0 + 2, ry + 56, 'Большинство гипотез отсеивается на первом этапе: убыток на отложенном отрезке — обычный результат.',
        size=12.5, color=MUTED)
cv.save('13-system-cycle.svg')

# ------------------------------------------------------------ 13.7 кривая капитала
rs = [t['r'] for t in trades]
cum, eq = [], 0.0
for r in rs:
    eq += r
    cum.append(eq)
n = len(rs)
peak_i = max(range(n), key=lambda k: cum[k])          # индекс сделки 113
assert peak_i + 1 == 113 and abs(cum[peak_i] - 31.69) < 0.01
end_v = cum[-1]
W_, H_ = 760, 400
cv = Canvas(W_, H_, title='Накопленный итог рос до 16 декабря 2024 года, затем просел на 9,6R',
            subtitle='Демонстрационный бэктест: 142 сделки, BTC/USDT и ETH/USDT, 2020 — октябрь 2026, результат в R после комиссии')
px0, px1 = 54, 640
py0, py1 = cv.y0 + 34, H_ - 56
ymin_, ymax_ = -5, 40
X = lambda k: px0 + (px1 - px0) * k / n          # k = число закрытых сделок
Y = lambda v: py1 - (py1 - py0) * (v - ymin_) / (ymax_ - ymin_)
for v in range(-5, 41, 5):
    cv.line(px0, Y(v), px1, Y(v), color=GRID if v else AXIS, width=1 if v else 1.5)
    cv.text(px0 - 8, Y(v) + 4, rfmt(v, 0, sign=False) if v else '0', size=11.5, anchor='end', color=MUTED)
cv.text(px0 - 8, py0 - 14, 'R', size=11.5, anchor='end', color=MUTED, weight=600)
# отрезки
sx = X(115)
cv.rect(sx, py0 - 6, px1 - sx, py1 - py0 + 6, fill=RED, stroke='none', opacity=0.07, rx=0)
cv.line(sx, py0 - 6, sx, py1, color=MUTED, width=1.25, dash=True)
cv.text(px0 + 8, py0 + 6, 'Разработка 2020–2024: 115 сделок, +29,6R', size=12, color=BLUE, weight=600)
cv.text(sx + 8, py0 + 6, 'Отложенный отрезок:', size=12, color=RED, weight=600)
cv.text(sx + 8, py0 + 22, '27 сделок, −7,5R', size=12, color=RED, weight=600)
# годы
for y in range(2020, 2027):
    k = next(i for i, t in enumerate(trades) if t['entry_date'][:4] == str(y))
    xx = X(k)
    cv.line(xx, py1, xx, py1 + 5, color=AXIS)
    cv.text(xx - 3 if y == 2022 else xx + 3, py1 + 18, str(y), size=11.5, anchor='end' if y == 2022 else 'start', color=MUTED)
cv.text((px0 + px1) / 2, py1 + 40, 'Сделки по порядку; подписи — год первой сделки', size=11.5, anchor='middle', color=MUTED)
# кривая
pts = [(X(0), Y(0))] + [(X(k + 1), Y(c)) for k, c in enumerate(cum)]
cv.polyline(pts, color=BLUE, width=2)
# пик и просадка
xp, yp = X(peak_i + 1), Y(cum[peak_i])
cv.line(xp, yp, px1 + 22, yp, color=MUTED, width=1.25, dash=True)
cv.line(X(n), Y(end_v), px1 + 22, Y(end_v), color=MUTED, width=1.25, dash=True)
cv.arrow(px1 + 20, yp + 1, px1 + 20, Y(end_v) - 1, color=RED, width=1.75)
cv.text(px1 + 28, (yp + Y(end_v)) / 2 - 2, '−9,6R', size=12.5, color=RED, weight=700)
cv.text(px1 + 28, (yp + Y(end_v)) / 2 + 14, 'просадка', size=11.5, color=RED)
cv.circle(xp, yp, 4.5, fill=BLUE)
cv.text(xp - 10, yp - 12, 'Пик +31,7R: сделка 113, 16 декабря 2024', size=12, anchor='end', color=INK, weight=600)
cv.circle(X(n), Y(end_v), 4.5, fill=RED)
cv.text(X(n) + 4, Y(15.5), 'Конец данных: +22,1R', size=12, anchor='end', color=INK, weight=600)
# максимальная просадка на разработке
k0, k1 = 56, 87
cv.line(X(k0), Y(cum[k0 - 1]), X(k1), Y(cum[k0 - 1]), color=MUTED, width=1.25, dash=True)
cv.circle(X(k0), Y(cum[k0 - 1]), 3.5, fill=BLUE)
cv.circle(X(k1), Y(cum[k1 - 1]), 3.5, fill=BLUE)
cv.text(X(82), Y(6), 'Просадка 8,7R на разработке (точки): ноябрь 2021 — январь 2024', size=11.5, anchor='middle', color=MUTED)
cv.save('13-equity-curve.svg')

# ------------------------------------------------------------ 13.7 две сделки на 4H
full = load('btc', '4h')
e50 = ema([c['c'] for c in full], 50)
a, b = find(full, '2024-10-25 00:00'), find(full, '2024-11-10 00:00') - 1
seg = full[a:b + 1]
t1, t2 = trades[108], trades[109]
assert t1['entry_date'].startswith('2024-11-01') and t2['entry_date'].startswith('2024-11-05')
ch = Chart(seg, title='BTC/USDT, 4H: одинаковый сигнал у EMA 50 дал сначала стоп −1,08R, затем цель +1,96R',
           subtitle='25 октября — 9 ноября 2024, время свечей UTC', main_h=340, extra_bars=10, ymin=65500, ymax=79500)
ch.series(e50[a:b + 1], color=BLUE, label='EMA 50')
for t, res, first in ((t1, '−1,08R', True), (t2, '+1,96R', False)):
    ie, ix = find(full, t['entry_date']) - a, find(full, t['exit_date']) - a
    isg = find(full, t['signal_date']) - a
    if first:
        ch.trade(ie, t['entry'], t['stop'], t['target'], ix)
    else:
        # вторая сделка рисуется вручную: ценники входов 70 002 и 69 640 на шкале слипаются
        ch.zone(t['stop'], t['entry'], x0=ie - 0.5, x1=ix + 0.5, kind='resistance')
        ch.zone(t['entry'], t['target'], x0=ie - 0.5, x1=ix + 0.5, kind='support')
        for p_, nm, col, tg in ((t['entry'], 'Вход 69 640', BLUE, False), (t['stop'], 'Стоп', RED, True), (t['target'], 'Цель', GREEN, True)):
            ch.hline(p_, ie - 0.5, ix + 0.5, color=col, dash=False, tag=tg)
        ch.text(ix + 0.3, t['entry'] + 130, 'Вход 69 640', anchor='end', size=11.5, color=BLUE, weight=600)
        ch.text(ix + 0.3, t['stop'] + 130, 'Стоп 66 362', anchor='end', size=11.5, color=RED, weight=600)
        ch.text(ix + 0.3, t['target'] + 130, 'Цель 76 197', anchor='end', size=11.5, color=GREEN, weight=600)
    ch.highlight(isg, isg, color=AMBER, label='Сигнал')
    ch.text(ie if first else ix, t['target'] + 700, f"Сделка {109 if first else 110}: {res}", anchor='start' if first else 'end',
            size=13, color=RED if first else GREEN, weight=700)
ch.save('13-backtest-trades.svg')
