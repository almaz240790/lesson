from figlib import *


def alt_swings(candles, k):
    """swings(k) с чередованием: из двух максимумов подряд оставляем высший, из двух минимумов подряд — низший."""
    out = []
    for p in swings(candles, k):
        if out and out[-1]['kind'] == p['kind']:
            if (p['kind'] == 'H' and p['price'] > out[-1]['price']) or (p['kind'] == 'L' and p['price'] < out[-1]['price']):
                out[-1] = p
        else:
            out.append(p)
    return out


# ---------------------------------------------------------------- 4.1 три состояния (схема)
path = [100, 112, 106, 120, 113, 128, 119, 127, 119.5, 127.5, 119, 127, 113, 119, 104, 110, 95]
c = synth(path, bars_per_leg=5)
ix = lambda k: 5 * k - 1          # свеча, на которой заканчивается k-й отрезок
ch = Chart(c, title='В тренде экстремумы идут ступенями, в боковике стоят на месте',
           subtitle='Схема: три состояния рынка', schematic=True, main_h=320, ymin=86, ymax=140)
ch.highlight(0, 24, GREEN, 'Восходящий тренд')
ch.highlight(25, 54, AMBER, 'Боковик (флэт, диапазон)')
ch.highlight(55, 79, RED, 'Нисходящий тренд')
ch.zone(126.5, 128.5, 25, 54, kind='neutral', label='верхняя граница', label_at='right')
ch.zone(118.5, 120, 25, 54, kind='neutral', label='нижняя граница')
for k, t, kind in [(2, 'HL', 'L'), (3, 'HH', 'H'), (4, 'HL', 'L'), (5, 'HH', 'H'),
                   (12, 'LL', 'L'), (13, 'LH', 'H'), (14, 'LL', 'L'), (15, 'LH', 'H'), (16, 'LL', 'L')]:
    i = ix(k)
    ch.mark(i, c[i]['h'] if kind == 'H' else c[i]['l'], t, where='above' if kind == 'H' else 'below',
            color=BLUE if kind == 'H' else GREEN)
ch.save('04-three-states.svg')

# ---------------------------------------------------------------- 4.2 восходящий тренд (реальный)
c = load('btc', '1d', '2020-12-05', '2021-04-02')
piv = alt_swings(c, 5)
assert len(piv) == 7, piv
spec = {'2020-12-11': ('минимум 17 572', None), '2021-01-08': ('HH 41 950', None), '2021-01-22': ('HL 28 850', '53,7%'),
        '2021-02-21': ('HH 58 353', None), '2021-02-28': ('HL 43 000', '52,0%'), '2021-03-13': ('HH 61 844', None),
        '2021-03-25': ('HL 50 428', '60,6%')}
assert [c[p['i']]['date'][:10] for p in piv] == list(spec), [c[p['i']]['date'] for p in piv]
ch = Chart(c, title='Восходящий тренд: каждый максимум и каждый минимум выше предыдущего',
           subtitle='BTC/USDT, 1D, 5 декабря 2020 — 2 апреля 2021; экстремумы по правилу k = 5',
           main_h=340, ymin=9000, ymax=68000)
ch.line([(p['i'], p['price']) for p in piv], color=MUTED, width=1.25, dash=True)
for p in piv:
    t, depth = spec[c[p['i']]['date'][:10]]
    if p is piv[0]:
        ch.mark(p['i'], p['price'], '', color=GREEN)
        ch.text(0.2, p['price'] - 3300, t, anchor='start', size=12, color=GREEN, weight=600)
    else:
        ch.mark(p['i'], p['price'], t, where='above' if p['kind'] == 'H' else 'below',
                color=BLUE if p['kind'] == 'H' else GREEN)
    if depth:
        ch.text(p['i'], p['price'] - 5600, f'откат {depth}', anchor='middle', size=11, color=MUTED)
ch.save('04-uptrend-real.svg')

# ---------------------------------------------------------------- 4.3 прокол, слом, подтверждение
c = load('btc', '1d', '2021-03-08', '2021-06-06')
D = lambda d: find(c, d)
ch = Chart(c, title='Слом — закрытие ниже последнего HL; прокол тенью не считается',
           subtitle='BTC/USDT, 1D, 8 марта — 6 июня 2021', main_h=380, ymin=24000, ymax=70000)
marks = [('2021-03-13', 'H', 'HH 61 844', 61844), ('2021-03-25', 'L', 'HL 50 428', 50427.56), ('2021-04-02', 'H', 'LH 60 200', 60200),
         ('2021-04-07', 'L', 'HL 55 473', 55473), ('2021-04-14', 'H', 'HH 64 854', 64854), ('2021-04-25', 'L', '46 930', 46930),
         ('2021-05-10', 'H', 'LH 59 500', 59500), ('2021-05-19', 'L', 'LL 30 000', 30000)]
for d, k, t, p in marks:
    i = D(d)
    assert abs((c[i]['h'] if k == 'H' else c[i]['l']) - p) < 1, (d, p)
    ch.mark(i, p, t, where='above' if k == 'H' else 'below', color=BLUE if k == 'H' else GREEN)
ch.hline(55473, x0=D('2021-04-07'), x1=D('2021-04-26'), color=RED, tag=False)
ch.text(D('2021-04-26'), 64000, 'последний HL 55 473', anchor='start', size=11.5, color=RED, weight=600)
ch.arrow((D('2021-04-27'), 63200), (D('2021-04-26') - 0.3, 55900), color=RED, width=1.2)
ch.hline(46930, x0=D('2021-04-25'), x1=D('2021-05-19'), color=RED, tag=False)
ch.text(D('2021-04-26'), 44000, 'минимум после', anchor='start', size=11.5, color=RED, weight=600)
ch.text(D('2021-04-26'), 41800, 'слома 46 930', anchor='start', size=11.5, color=RED, weight=600)
# события
i18, i21, i15 = D('2021-04-18'), D('2021-04-21'), D('2021-05-15')
assert abs(c[i18]['l'] - 50931) < 1 and round(c[i18]['c']) == 56150 and round(c[i21]['c']) == 53788 and round(c[i15]['c']) == 46763
ch.text(1, 40500, '18.04: тень до 50 931,', size=11.5, weight=600)
ch.text(1, 38300, 'закрытие 56 150 — прокол', size=11.5, weight=600)
ch.arrow((17, 41200), (i18 - 0.4, c[i18]['l'] - 400), color=INK)
ch.text(i21 - 1, 33500, '21.04: закрытие 53 788 — слом', anchor='middle', size=11.5, weight=600, color=RED)
ch.arrow((i21, 34800), (i21, c[i21]['c'] - 500), color=RED)
ch.text(i15 + 8, 55500, '15.05: закрытие 46 763 —', anchor='middle', size=11.5, weight=600, color=RED)
ch.text(i15 + 8, 53300, 'разворот подтверждён', anchor='middle', size=11.5, weight=600, color=RED)
ch.arrow((i15, 52200), (i15, c[i15]['c'] + 600), color=RED)
ch.save('04-break-real.svg')

# ---------------------------------------------------------------- 4.4 вложенность (схема)
cv = Canvas(760, 405, title='Коррекция на 1D выглядит нисходящим трендом на 4H')
top = cv.y0 + 26
cv.text(14, cv.y0 + 12, '1D', size=15, weight=700, color=BLUE)
cv.text(404, cv.y0 + 12, '4H: тот же отрезок', size=15, weight=700, color=BLUE)
cv.rect(14, top, 350, 250, stroke=GRID, rx=4)
cv.rect(404, top, 342, 250, stroke=GRID, rx=4)
# левая панель
L = [(40, top + 218, 'HL'), (118, top + 100, 'HH'), (190, top + 168, 'HL'), (262, top + 36, 'HH'), (332, top + 126, 'HL')]
cv.polyline([(x, y) for x, y, _ in L], color=INK, width=2)
for k, (x, y, t) in enumerate(L):
    hi = t == 'HH'
    cv.circle(x, y, 4, fill=BLUE if hi else GREEN)
    cv.text(x, y - 10 if hi else y + 20, t, size=13, anchor='middle', color=BLUE if hi else GREEN, weight=700)
rx0, rx1, ry0, ry1 = 244, 350, top + 14, top + 150
cv.rect(rx0, ry0, rx1 - rx0, ry1 - ry0, stroke=RED, rx=4, sw=1.75)
cv.text((rx0 + rx1) / 2, ry1 + 20, 'коррекция', size=13, anchor='middle', color=RED, weight=700)
# правая панель: границы = HH и HL левой панели
px0, px1 = 420, 730
yt, yb = top + 24, top + 226              # верх = HH, низ = HL
for yy in (yt, yb):
    cv.line(404, yy, 746, yy, color=AXIS, dash=True)
cv.text(740, yt - 5, 'HH', size=12, anchor='end', color=BLUE, weight=700)
cv.text(740, yb + 15, 'HL', size=12, anchor='end', color=GREEN, weight=700)
depth = [0, .75, .15, .49, .17, .56, .30, .775, .41, 1.0]
lab = [None, None, 'LH', None, 'LH', 'LL', 'LH', 'LL', 'LH', 'LL']
xs = [px0 + (px1 - 70 - px0) * k / 9 for k in range(10)]
pts = [(x, yt + d * (yb - yt)) for x, d in zip(xs, depth)]
cv.polyline(pts, color=INK, width=2)
for (x, y), t in zip(pts, lab):
    if t is None:
        continue
    hi = t == 'LH'
    col = BLUE if hi else GREEN
    cv.circle(x, y, 4, fill=col)
    cv.text(x, y - 9 if hi else y + 19, t, size=13, anchor='middle', color=col, weight=700)
last_lh = pts[8][1]
cv.line(pts[8][0], last_lh, px1 + 4, last_lh, color=RED, dash=True)
xe, ye = px1 - 22, yt + 0.30 * (yb - yt)
cv.arrow(pts[9][0], pts[9][1], xe, ye, color=RED, width=2)
for j, s_ in enumerate(['закрытие выше', 'последнего LH —', 'слом вверх']):
    cv.text(px1 + 8, yt + 17 + 13 * j, s_, size=11.5, anchor='end', color=RED, weight=600)
# увеличение
cv.line(rx1, ry0, 404, top, color=RED, dash=True)
cv.line(rx1, ry1, 404, top + 250, color=RED, dash=True)
# подписи под панелями
yy = top + 250 + 28
cv.text(189, yy, '1D: тренд восходящий — ищем покупку', size=13, anchor='middle', color=GREEN, weight=600)
cv.text(575, yy, '4H: нисходящий тренд внутри отката —', size=13, anchor='middle', color=RED, weight=600)
cv.text(575, yy + 18, 'не продаём, ждём слома вверх', size=13, anchor='middle', color=RED, weight=600)
cv.save('04-nested.svg')
