import math
import sys

from figlib import *

sys.path.insert(0, '/tmp/claude-0/-home-user/f927aebb-32a8-5440-8354-c5b0107d38ec/scratchpad/book/analysis')
import ch11_equity as eqm  # make_seq и run: те же 100 сделок, что в разделе 11.7


def num(x, d=1, sign=False):
    s = f'{x:+,.{d}f}' if sign else f'{x:,.{d}f}'
    return s.replace('-', '−').replace(',', ' ').replace('.', ',')


def usd(x):
    return num(x, 0) + ' $'


# ------------------------------------------------------------ 11.1 асимметрия потерь
pairs = [5, 10, 20, 25, 30, 50, 75]
cv = Canvas(760, 420, title='Чем глубже потеря, тем непропорционально больше нужно заработать для возврата',
            subtitle='Нужный рост = Потеря / (1 − Потеря)')
zero = cv.y0 + 262
scale = 230 / 300          # пикселей на 1 процентный пункт
px0, px1 = 74, 744
# легенда
cv.rect(px0, cv.y0 + 2, 12, 12, fill=GREEN, stroke=GREEN, rx=2)
cv.text(px0 + 18, cv.y0 + 13, 'нужно заработать для возврата', size=12.5, color=MUTED)
cv.rect(px0 + 250, cv.y0 + 2, 12, 12, fill=RED, stroke=RED, rx=2)
cv.text(px0 + 268, cv.y0 + 13, 'потеря счёта', size=12.5, color=MUTED)
# шкала
for v in (0, 100, 200, 300):
    y = zero - v * scale
    cv.line(px0, y, px1, y, color=GRID if v else AXIS, width=1 if v else 1.5)
    cv.text(px0 - 8, y + 4, f'{v}%', size=11.5, anchor='end', color=MUTED)
slot = (px1 - px0) / len(pairs)
bw = 30
for k, loss in enumerate(pairs):
    need = 100 * (loss / 100) / (1 - loss / 100)
    cx = px0 + slot * (k + 0.5)
    hr, hg = loss * scale, need * scale
    cv.rect(cx - bw - 2, zero, bw, hr, fill=RED, stroke=RED, rx=2, opacity=0.85)
    cv.rect(cx + 2, zero - hg, bw, hg, fill=GREEN, stroke=GREEN, rx=2, opacity=0.85)
    cv.text(cx + 2 + bw / 2, zero - hg - 6, '+' + num(need, 1 if need < 100 else 0), size=12, anchor='middle', color=GREEN, weight=700)
    cv.text(cx - 2 - bw / 2, zero + hr + 16, f'−{loss}%', size=12, anchor='middle', color=RED, weight=700)
cv.text(px0, cv.y0 + 40, 'нужно заработать для возврата', size=12.5, color=MUTED) if False else None
cv.text(px1, cv.y0 + 40, '', size=1)
cv.text(px0 + 330, zero - 205, '−80% → +400%, −90% → +900%', size=12.5, color=INK, weight=600)
cv.text(px0 + 330, zero - 187, '— за пределами шкалы', size=12.5, color=MUTED)
cv.text(px0 + 330, zero - 165, 'До −10% столбики почти равны.', size=12, color=MUTED)
cv.save('11-loss-asymmetry.svg')

# ------------------------------------------------------------ 11.3 стоп и размер позиции
cv = Canvas(760, 640, title='Стоп вдвое дальше — позиция вдвое меньше, убыток в долларах тот же',
            subtitle='Депозит 1 000 $, риск 1% = 10 $, лонг от 60 000')
P0, P1 = 57200, 60800
ptop = cv.y0 + 40
ph = 260
PY = lambda p: ptop + (P1 - p) / (P1 - P0) * ph
cols = [
    dict(x=14, title='Близкий стоп, 2%', path=[59300, 60000, 60500, 59600, 58800], stop=58800, pct='−2%',
         size=500, btc='0,00833', bar='Позиция 500 $ (0,00833 BTC)'),
    dict(x=392, title='Далёкий стоп, 4%', path=[59300, 60000, 60500, 58900, 59500, 57600], stop=57600, pct='−4%',
         size=250, btc='0,00416', bar='Позиция 250 $ (0,00416 BTC)'),
]
CW = 354
for c in cols:
    x0 = c['x']
    cv.text(x0 + CW / 2, ptop - 14, c['title'], size=14, anchor='middle', weight=700)
    cv.rect(x0, ptop, CW, ph, stroke=GRID, rx=0, sw=1)
    cv.rect(x0, PY(60000), CW, PY(c['stop']) - PY(60000), fill='#dc2626', stroke='none', rx=0, opacity=0.15)
    cv.line(x0, PY(60000), x0 + CW, PY(60000), color=BLUE, width=1.5)
    cv.line(x0, PY(c['stop']), x0 + CW, PY(c['stop']), color=RED, width=1.5)
    cv.text(x0 + CW - 6, PY(60000) - 6, 'вход 60 000', size=12, anchor='end', color=BLUE, weight=600)
    cv.text(x0 + CW - 6, PY(c['stop']) + 16, f'стоп {fmt_price(c["stop"])}', size=12, anchor='end', color=RED, weight=600)
    n = len(c['path'])
    xs = [x0 + 20 + k * (CW * 0.62) / (n - 1) for k in range(n)]
    cv.polyline([(xs[k], PY(p)) for k, p in enumerate(c['path'])], color=INK, width=2)
    cv.circle(xs[1], PY(60000), 4.5, fill=BLUE)
    cv.circle(xs[-1], PY(c['stop']), 4.5, fill=RED)
    cv.text(x0 + CW - 40, (PY(60000) + PY(c['stop'])) / 2 + 5, c['pct'], size=16, anchor='middle', color=RED, weight=700)
# формула между панелями цен и полосами позиций
fy = ptop + ph + 18
cv.rect(14, fy, 732, 54, fill=BLUE, stroke=BLUE, opacity=0.07)
cv.text(380, fy + 22, 'Размер позиции = Риск $ / Расстояние до стопа', size=14, anchor='middle', weight=700)
cv.text(380, fy + 43, '10 / 0,02 = 500 $;      10 / 0,04 = 250 $', size=14, anchor='middle', color=BLUE, weight=600)
by = fy + 54 + 22
unit = 300 / 500
for c in cols:
    x0 = c['x']
    w = c['size'] * unit
    cv.rect(x0, by, w, 26, fill=BLUE, stroke=BLUE, rx=3, opacity=0.8)
    cv.text(x0, by + 46, c['bar'], size=12.5, color=INK, weight=600)
    cv.rect(x0, by + 62, CW, 34, fill=RED, stroke=RED, rx=6, opacity=0.12)
    cv.rect(x0, by + 62, CW, 34, stroke=RED, rx=6, sw=1.25)
    cv.text(x0 + CW / 2, by + 84, 'Убыток по стопу: 10 $ = 1% счёта', size=13, anchor='middle', color=RED, weight=700)
cv.H = int(by + 96 + 14)
cv.save('11-stop-distance-size.svg')

# ------------------------------------------------------------ 11.7 кривые капитала
seq = eqm.make_seq(3)
risks = [(1, BLUE), (2, GREEN), (5, ORANGE), (10, RED)]
curves = {}
for r, _ in risks:
    curve, mdd, dd_at, low = eqm.run(seq, r)
    curves[r] = curve
ends = {r: round(curves[r][-1]) for r in curves}
assert ends == {1: 12081, 2: 14286, 5: 20851, 10: 26412}, ends
assert round(curves[10][13]) == 19042 and round(curves[10][32]) == 6097
assert round(max(curves[10])) == 56138
cv = Canvas(760, 520, title='Одни и те же 100 сделок: чем выше риск, тем глубже провал на тех же убытках',
            subtitle='40 сделок по +2R и 60 по −1R, порядок фиксирован (seed 3); старт 10 000 $, риск — доля текущего счёта')
L, R_, T = 72, 640, cv.y0 + 8
H = 380
lo, hi = math.log(5000), math.log(60000)
X = lambda i: L + i / 100 * (R_ - L)
Y = lambda v: T + (hi - math.log(v)) / (hi - lo) * H
cv.rect(L, T, R_ - L, H, stroke=GRID, rx=0, sw=1)
for v in (5000, 10000, 20000, 40000):
    cv.line(L, Y(v), R_, Y(v), color=GRID if v != 10000 else AXIS, width=1, dash=(v == 10000))
    cv.text(L - 8, Y(v) + 4, usd(v), size=11.5, anchor='end', color=MUTED)
cv.text(X(78), Y(10000) + 16, 'старт 10 000 $', size=11.5, color=MUTED)
for t in range(0, 101, 10):
    cv.line(X(t), T + H, X(t), T + H + 5, color=AXIS)
    cv.text(X(t), T + H + 20, str(t), size=11.5, anchor='middle', color=MUTED)
cv.text((L + R_) / 2, T + H + 40, 'номер сделки', size=12, anchor='middle', color=MUTED)
cv.rect(X(19), T, X(27) - X(19), H, fill='#6b7280', stroke='none', rx=0, opacity=0.13)
cv.text((X(19) + X(27)) / 2, T + 14, '8 убытков подряд', size=11.5, anchor='middle', color=INK, weight=600)
for r, col in risks:
    cv.polyline([(X(i), Y(v)) for i, v in enumerate(curves[r])], color=col, width=2)
for r, col in sorted(risks, key=lambda t: -t[0]):
    cv.text(R_ + 8, Y(curves[r][-1]) + 4, f'{r}%: {usd(curves[r][-1])}', size=12.5, color=col, weight=700)
# просадка 10%
x13, x32 = X(13), X(32)
cv.circle(x13, Y(curves[10][13]), 4, fill=RED)
cv.circle(x32, Y(curves[10][32]), 4, fill=RED)
cv.text(x13 - 8, Y(curves[10][13]) - 8, '19 042 $', size=12, anchor='end', color=RED, weight=700)
cv.text(x32 - 8, Y(curves[10][32]) + 18, '6 097 $', size=12, anchor='end', color=RED, weight=700)
cv.arrow(x13 + 14, Y(curves[10][13]) + 6, x13 + 14, Y(curves[10][32]) - 10, color=RED, width=1.5, dash=True) if False else None
cv.text(X(34), Y(5600) , 'просадка −68,0%', size=12.5, color=RED, weight=700)
cv.text(X(34), Y(5600) + 0, '', size=1)
cv.circle(X(32), Y(curves[1][32]), 3.5, fill=BLUE)
cv.line(X(32) + 4, Y(curves[1][32]) + 3, X(41) - 4, Y(9000) - 4, color=BLUE, width=1, dash=True)
cv.text(X(41), Y(9000) + 2, 'просадка −9,6%', size=12.5, color=BLUE, weight=700)
cv.save('11-equity-risk.svg')

# ------------------------------------------------------------ 11.8 BTC и ETH вместе
btc, eth = load('btc', '1d'), load('eth', '1d')
a, b = find(btc, '2025-12-20'), find(btc, '2026-03-20')
cb, ce = btc[a:b + 1], eth[a:b + 1]
assert len(cb) == 91 and [c['date'] for c in cb] == [c['date'] for c in ce]
rb = [btc[i]['c'] / btc[i - 1]['c'] - 1 for i in range(a, b + 1)]
re_ = [eth[i]['c'] / eth[i - 1]['c'] - 1 for i in range(a, b + 1)]
mx, my = sum(rb) / 91, sum(re_) / 91
corr = sum((x - mx) * (y - my) for x, y in zip(rb, re_)) / math.sqrt(sum((x - mx) ** 2 for x in rb) * sum((y - my) ** 2 for y in re_))
same = sum(1 for x, y in zip(rb, re_) if x * y > 0)
assert round(corr, 2) == 0.93 and same == 78
big = [i for i in range(91) if abs(rb[i]) >= 0.05]
assert big == [40, 42, 47, 48, 67, 74], big
assert cb[46]['date'] == '2026-02-04' and round(cb[46]['c']) == 73166
assert round(ce[46]['c']) == 2148 and round(ce[47]['l']) == 1818 and round(cb[47]['l']) == 62345
ch = Chart(cb, title='BTC и ETH падают и растут в одни и те же дни',
           subtitle='BTC/USDT, 1D (свечи) и ETH/USDT, 1D (закрытия), 20.12.2025 — 20.03.2026; '
                    'корреляция 0,93, в одну сторону 78 дней из 91', width=800,
           main_h=330, ymin=58000, ymax=100000)
for i in big:
    ch.vline(i, color=PURPLE)
ch.text(49.6, 89000, '5 фев: BTC −14,0%, ETH −15,0%', anchor='start', size=12, color=RED, weight=700)
ch.text(49.6, 84000, '6 фев: BTC +12,2%, ETH +13,0%', anchor='start', size=12, color=GREEN, weight=700)
ch.mark(46, cb[46]['c'], '', where='right', color=BLUE)
ch.text(45.4, 69500, 'вход BTC по закрытию 4 фев: 73 166', anchor='end', size=12, color=BLUE, weight=700)
ch.hline(65968, 46, 49, color=RED, dash=True, label=None, tag=False)
ch.text(45.4, 64800, 'стоп BTC 65 968 — выбит 5 фев (минимум 62 345)', anchor='end', size=12, color=RED, weight=700)
p = ch.panel([c['c'] for c in ce], label='ETH/USDT, закрытие', height=150, color=INK, ymin=1500, ymax=3500)
p.mark(46, ce[46]['c'], 'вход 2 148', where='above', color=BLUE)
p.line((46, 1788), (49, 1788), color=RED, dash=True)
p.mark(46.5, 1788, 'стоп ETH 1 788 устоял (минимум 1 818)', where='below', color=RED)
ch.save('11-btc-eth-together.svg')
