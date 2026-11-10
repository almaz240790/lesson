from figlib import *

# ============================================================ общие помощники для схем в Canvas
def panel_draw(cv, candles, x0, x1, y0, y1, pmin, pmax, w=6, extra=0):
    """Рисует свечи в прямоугольнике (x0..x1, y0..y1); возвращает функции X(i), Y(p)."""
    n = len(candles)
    step = (x1 - x0) / (n + 1 + extra)
    X = lambda i: x0 + step * (i + 1)
    Y = lambda p: y1 - (p - pmin) / (pmax - pmin) * (y1 - y0)
    for i, c in enumerate(candles):
        cv.candle(X(i), Y(c['o']), Y(c['h']), Y(c['l']), Y(c['c']), w=w)
    return X, Y


def build(legs, bars, noise=0.15, seed=3):
    cs = synth(legs, bars_per_leg=bars, noise=noise, seed=seed)
    ends, k = [], -1
    for n in bars:
        k += n
        ends.append(k)
    return cs, ends


# ============================================================ рис. 6.1 свечные паттерны
cv = Canvas(760, 470, title='У каждого свечного паттерна есть критерий, который считается по четырём ценам',
            subtitle='Бычьи формы; медвежьи зеркальны. Зелёная свеча — закрытие выше открытия, красная — ниже')
cells = [(14, 'Пин-бар', 'Нижняя тень ≥ 2/3 диапазона'),
         (265, 'Поглощение', 'Зелёное тело закрылось выше открытия красной'),
         (516, 'Внутренний бар', 'Максимум ниже, минимум выше предыдущей')]
cells2 = [(14, 'Утренняя звезда', 'Тело 1-й ≥ 0,5 ATR, тело 2-й ≤ 1/3 тела 1-й'),
          (265, 'Доджи', 'Тело ≤ 10% диапазона'),
          (516, 'Вечерняя звезда', 'Зеркальная форма на вершине')]
CW, CH = 230, 190
rowy = [cv.y0 + 4, cv.y0 + 4 + CH + 14]


def frame(x, y, name, rule):
    cv.rect(x, y, CW, CH, stroke=GRID, rx=8)
    cv.text(x + CW / 2, y + 22, name, size=15, anchor='middle', weight=700)
    cv.text(x + CW / 2, y + CH - 12, rule, size=11, anchor='middle', color=MUTED)


# 1 пин-бар: диапазон 100, тело наверху, нижняя тень 78
x, y = cells[0][0], rowy[0]
frame(x, y, cells[0][1], cells[0][2] if len(cells[0][2]) < 34 else cells[0][2])
top, bot = y + 46, y + 146
cx = x + 100
cv.candle(cx, top + 12, top, bot, top + 22, w=34, up=False)   # красная: тело маленькое у верха
cv.line(cx + 26, top, cx + 40, top, color=AXIS); cv.line(cx + 26, bot, cx + 40, bot, color=AXIS)
cv.line(cx + 38, top, cx + 38, bot, color=MUTED)
cv.text(cx + 46, (top + bot) / 2 - 18, 'Диапазон', size=11, color=MUTED)
cv.line(cx + 26, top + 22, cx + 26, top + 22, color=AXIS)
cv.polyline([(cx - 38, top + 22), (cx - 62, top + 22)], color=BLUE, width=1.25)
cv.line(cx - 52, top + 22, cx - 52, bot, color=BLUE, width=1.75)
cv.text(cx - 58, (top + 22 + bot) / 2 + 4, 'Тень', size=11, anchor='end', color=BLUE, weight=600)
cv.text(cx - 58, (top + 22 + bot) / 2 + 18, '78%', size=11, anchor='end', color=BLUE, weight=600)

# 2 поглощение
x, y = cells[1][0], rowy[0]
frame(x, y, cells[1][1], 'Закрытие выше открытия красной')
cx = x + 85
cv.candle(cx, y + 80, y + 66, y + 118, y + 108, w=30, up=False)    # красная: o 80 -> c 108 (вниз)
cv.candle(cx + 60, y + 108, y + 56, y + 124, y + 64, w=30, up=True)  # зелёная: o 108 -> c 64
cv.line(cx + 10, y + 80, cx + 92, y + 80, color=BLUE, width=1.25, dash=True)
cv.line(cx + 46, y + 64, cx + 92, y + 64, color=BLUE, width=1.25, dash=True)
cv.text(cx + 98, y + 84, 'открытие 1-й', size=11, color=BLUE)
cv.text(cx + 98, y + 64, 'закрытие 2-й', size=11, color=BLUE, weight=600)
cv.text(cx - 26, y + 140, '1', size=12, anchor='middle', color=MUTED)
cv.text(cx + 60, y + 140, '2', size=12, anchor='middle', color=MUTED)

# 3 внутренний бар
x, y = cells[2][0], rowy[0]
frame(x, y, cells[2][1], 'Диапазон внутри материнской свечи')
cx = x + 66
cv.candle(cx, y + 130, y + 46, y + 150, y + 62, w=34, up=True)      # материнская: длинная зелёная
cv.rect(cx + 36, y + 46, 76, 104, stroke=MUTED, rx=3)
cv.candle(cx + 76, y + 100, y + 80, y + 118, y + 92, w=22, up=True)
cv.text(cx, y + 164, 'материнская', size=11, anchor='middle', color=MUTED)
cv.text(cx + 76, y + 164, 'внутренний', size=11, anchor='middle', color=MUTED)

# 4 утренняя звезда
x, y = cells[0][0], rowy[1]
frame(x, y, cells2[0][1], 'Тела: 1-я ≥ 0,5 ATR, 2-я ≤ 1/3 первой')
cx = x + 52
cv.candle(cx, y + 46, y + 40, y + 120, y + 112, w=26, up=False)     # длинная красная
cv.candle(cx + 56, y + 126, y + 112, y + 142, y + 122, w=20, up=False)  # малое тело
cv.candle(cx + 112, y + 124, y + 58, y + 130, y + 66, w=26, up=True)    # зелёная выше середины тела 1
mid = (46 + 112) / 2
cv.line(cx - 16, y + mid, cx + 130, y + mid, color=BLUE, width=1.25, dash=True)
cv.text(cx + 92, y + mid - 6, 'середина 1-й', size=11, anchor='end', color=BLUE)

# 5 доджи
x, y = cells2[1][0], rowy[1]
frame(x, y, cells2[1][1], cells2[1][2])
cx = x + 100
cv.candle(cx, y + 90, y + 50, y + 130, y + 91.5, w=34, up=False)
cv.text(cx + 30, y + 94, 'тело ≤ 10%', size=11, color=BLUE, weight=600)
cv.text(cx + 30, y + 108, 'диапазона', size=11, color=BLUE)

# 6 вечерняя звезда
x, y = cells2[2][0], rowy[1]
frame(x, y, cells2[2][1], 'Длинная зелёная, малое тело, красная')
cx = x + 52
cv.candle(cx, y + 112, y + 40, y + 120, y + 46, w=26, up=True)
cv.candle(cx + 56, y + 38, y + 28 + 6, y + 50, y + 44, w=20, up=True)
cv.candle(cx + 112, y + 42, y + 36, y + 110, y + 104, w=26, up=False)
cv.save('06-candle-patterns.svg')

# ============================================================ рис. 6.2 фигуры продолжения
def trade_lines(cv, X, Y, i0, entry, stop, target, i1, lab_x, dy_stop=4):
    cv.rect(X(i0), Y(target), X(i1) - X(i0), Y(entry) - Y(target), fill=GREEN, stroke='none', rx=0, opacity=0.10)
    cv.rect(X(i0), Y(entry), X(i1) - X(i0), Y(stop) - Y(entry), fill=RED, stroke='none', rx=0, opacity=0.10)
    cv.line(X(i0), Y(entry), X(i1), Y(entry), color=BLUE, width=1.5)
    cv.line(X(i0), Y(stop), X(i1), Y(stop), color=RED, width=1.5, dash=True)
    cv.line(X(i0), Y(target), X(i1), Y(target), color=GREEN, width=1.5, dash=True)
    cv.circle(X(i0), Y(entry), 4, fill=BLUE)
    cv.text(lab_x, Y(entry) - 5, 'Вход', size=12, anchor='end', color=BLUE, weight=700)
    cv.text(lab_x, Y(stop) + 15, 'Стоп', size=12, anchor='end', color=RED, weight=700)
    cv.text(lab_x, Y(target) - 5, 'Цель', size=12, anchor='end', color=GREEN, weight=700)


def ext(p0, p1, i):
    return p0[1] + (p1[1] - p0[1]) * (i - p0[0]) / (p1[0] - p0[0])


cv = Canvas(760, 400, title='Выход из фигуры продолжения: вход за границей, стоп за минимумом, цель по высоте фигуры',
            subtitle='Схема на условных ценах: слева флаг после импульса, справа восходящий треугольник')
top0, bot0 = cv.y0 + 26, 380
# --- флаг
legs = [100, 130, 126, 128, 123.5, 125.5, 121, 127.5, 134]
bars = [8, 2, 2, 2, 2, 2, 2, 5]
fl, ends = build(legs, bars, noise=0.1, seed=5)
n = len(fl)
X, Y = panel_draw(cv, fl, 14, 372, top0, bot0, 94, 166, w=7, extra=6)
hp = [(ends[0], 130), (ends[2], 128), (ends[4], 125.5)]
lp = [(ends[1], 126), (ends[3], 123.5), (ends[5], 121)]
cv.line(X(hp[0][0]), Y(130), X(ends[5] + 3), Y(ext(hp[0], hp[2], ends[5] + 3)), color=AMBER, width=1.5)
cv.line(X(lp[0][0]), Y(126), X(ends[5] + 1), Y(ext(lp[0], lp[2], ends[5] + 1)), color=AMBER, width=1.5)
ib = next(i for i in range(ends[5] + 1, n) if fl[i]['c'] > ext(hp[0], hp[2], i))
entry = fl[ib]['c']
stop = 121 - 2
target = entry + 30
trade_lines(cv, X, Y, ib, entry, stop, target, n + 5, X(n + 5) - 6)
cv.line(X(n + 5) - 22, Y(entry), X(n + 5) - 22, Y(target), color=GREEN, width=1.5)
cv.text(X(n + 5) - 28, (Y(entry) + Y(target)) / 2, 'высота', size=11, anchor='end', color=GREEN)
cv.text(X(n + 5) - 28, (Y(entry) + Y(target)) / 2 + 13, 'древка', size=11, anchor='end', color=GREEN)
cv.text(X(0), Y(131), 'Древко (импульс)', size=12, color=MUTED, weight=600)
cv.text(X(ends[2]), Y(137), 'Флаг', size=13, color=AMBER, weight=700, anchor='middle')
cv.line(386, top0 - 10, 386, bot0 + 4, color=GRID)

# --- восходящий треугольник
legs = [104, 120, 110, 120, 114, 120, 117.5, 120, 118.5, 131]
bars = [5, 4, 4, 4, 3, 3, 2, 2, 7]
legs = legs[:9] + [123, 131]
bars = [5, 4, 4, 4, 3, 3, 2, 2, 2, 4]
legs = [104, 120, 110, 120, 114, 120, 117.5, 120, 118.5, 123, 126.5]
tr, ends = build(legs, bars, noise=0.1, seed=11)
n = len(tr)
X, Y = panel_draw(cv, tr, 400, 746, top0, bot0, 94, 138, w=8, extra=6)
cv.line(X(ends[0]), Y(120), X(ends[7] + 3), Y(120), color=AMBER, width=1.5)
lp = [(ends[1], 110), (ends[3], 114), (ends[5], 117.5)]
cv.line(X(ends[1]), Y(110), X(ends[7] + 1), Y(ext(lp[0], lp[2], ends[7] + 1)), color=AMBER, width=1.5)
ib = next(i for i in range(ends[7] + 1, n) if tr[i]['c'] > 120.8)
entry = tr[ib]['c']
stop = 117.5 - 1.5
target = entry + 10
trade_lines(cv, X, Y, ib, entry, stop, target, n + 5, X(n + 5) - 6)
cv.line(X(n + 5) - 22, Y(entry), X(n + 5) - 22, Y(target), color=GREEN, width=1.5)
cv.text(X(n + 5) - 28, Y(target) + 17, 'высота', size=11, anchor='end', color=GREEN)
cv.text(X(n + 5) - 28, Y(target) + 30, 'основания', size=11, anchor='end', color=GREEN)
cv.text(X(ends[2]), Y(126), 'Восходящий треугольник', size=13, color=AMBER, weight=700, anchor='middle')
xb = X(ends[1]) - 10
cv.line(xb, Y(120), xb, Y(110), color=MUTED, width=1.5)
cv.line(xb - 4, Y(120), xb + 4, Y(120), color=MUTED, width=1.5)
cv.line(xb - 4, Y(110), xb + 4, Y(110), color=MUTED, width=1.5)
cv.text(xb, Y(110) + 22, 'основание', size=11, anchor='middle', color=MUTED)
cv.save('06-continuation.svg')

# ============================================================ рис. 6.3 разворотные фигуры
cv = Canvas(760, 400, title='Фигура завершена, когда свеча закрылась за линией шеи; цель — высота фигуры от шеи',
            subtitle='Схема на условных ценах: слева двойная вершина, справа голова и плечи')
top0, bot0 = cv.y0 + 26, 380


def rev_panel(cv, legs, bars, x0, x1, pmin, pmax, neck, peak_hi, name, name_at, seed, stop_p, extra=6):
    cs, ends = build(legs, bars, noise=0.1, seed=seed)
    n = len(cs)
    X, Y = panel_draw(cv, cs, x0, x1, top0, bot0, pmin, pmax, w=8, extra=extra)
    ib = next(i for i in range(ends[-3], n) if cs[i]['c'] < neck)
    entry = cs[ib]['c']
    height = peak_hi - neck
    target = neck - height
    i1 = n + extra - 1
    cv.line(X(ends[0]) - 20, Y(neck), X(i1), Y(neck), color=AMBER, width=1.75)
    cv.rect(X(ib), Y(entry), X(i1) - X(ib), Y(target) - Y(entry), fill=GREEN, stroke='none', rx=0, opacity=0.10)
    cv.rect(X(ib), Y(stop_p), X(i1) - X(ib), Y(entry) - Y(stop_p), fill=RED, stroke='none', rx=0, opacity=0.10)
    cv.line(X(ib), Y(entry), X(i1), Y(entry), color=BLUE, width=1.5)
    cv.line(X(ib), Y(stop_p), X(i1), Y(stop_p), color=RED, width=1.5, dash=True)
    cv.line(X(ib), Y(target), X(i1), Y(target), color=GREEN, width=1.5, dash=True)
    cv.circle(X(ib), Y(entry), 4, fill=BLUE)
    lx = X(i1) - 4
    cv.text(lx, Y(entry) + 15, 'Вход', size=12, anchor='end', color=BLUE, weight=700)
    cv.text(lx, Y(stop_p) - 5, 'Стоп', size=12, anchor='end', color=RED, weight=700)
    cv.text(lx, Y(target) - 5, 'Цель', size=12, anchor='end', color=GREEN, weight=700)
    cv.line(X(i1) - 46, Y(neck), X(i1) - 46, Y(target), color=GREEN, width=1.5)
    cv.text(X(i1) - 4, Y(target) + 16, 'стрелка — высота фигуры', size=11, anchor='end', color=GREEN)
    cv.text(X(name_at), Y(peak_hi) - 12, name, size=13, color=AMBER, weight=700, anchor='middle')
    cv.text(X(ends[0]) - 20, Y(neck) + 15, 'линия шеи', size=11, color=AMBER, weight=600)
    # высота фигуры: скобка от вершины до шеи слева от первой вершины
    return cs, ends, X, Y, ib, entry, target


# двойная вершина
legs = [100, 130, 116, 129, 112, 104]
bars = [8, 5, 5, 5, 5]
cs, ends, X, Y, ib, entry, target = rev_panel(cv, legs, bars, 14, 372, 74, 142, 116, 130, 'Двойная вершина',
                                              ends[0] if False else 10, 1, 132)
cv.line(386, top0 - 10, 386, bot0 + 4, color=GRID)

# голова и плечи
legs = [100, 116, 108, 126, 108, 116, 100, 92]
bars = [6, 4, 5, 5, 4, 4, 4]
cs, ends, X, Y, ib, entry, target = rev_panel(cv, legs, bars, 400, 746, 74, 142, 108, 126, 'Голова и плечи',
                                              14, 2, 118.5)
cv.save('06-reversal.svg')

# ============================================================ рис. 6.4 двойное дно, BTC/USDT 1D
full = load('btc', '1d')
a, b = find(full, '2021-06-08'), find(full, '2021-08-12')
seg = full[a:b + 1]
e200 = ema([c['c'] for c in full], 200)[a:b + 1]
ix = lambda d: find(full, d) - a
i_b1, i_neck, i_b2, i_brk, i_rt, i_tgt = (ix(d) for d in
    ['2021-06-22', '2021-06-29', '2021-07-20', '2021-07-26', '2021-07-27', '2021-08-07'])
ch = Chart(seg, title='Двойное дно у поддержки: пробой шеи 36 600 довёл цену до цели 44 395',
           subtitle='BTC/USDT, 1D, 8 июня — 12 августа 2021', main_h=330, extra_bars=6, ymin=26500, ymax=47000)
ch.zone(28100, 30000, kind='support', label='Поддержка 28 100–30 000', label_at='right')
ch.series(e200, color=ORANGE, label='EMA 200')
ch.hline(36600, x0=i_neck, color=AMBER, dash=False, width=1.75)
ch.mark(i_b1, 28805, '', where='below', color=GREEN)
ch.mark(i_b2, 29278, '', where='below', color=GREEN)
ch.text(i_b1, 27000, 'Дно 1: 28 805', anchor='middle', color=GREEN, weight=600)
ch.text(i_b2, 27000, 'Дно 2: 29 278', anchor='middle', color=GREEN, weight=600)
ch.mark(i_neck, 36600, 'Шея 36 600 (29 июня)', where='above', color=AMBER)
ch.mark(i_brk, 37238, 'Пробой 26 июля', where='left', color=BLUE)
ch.trade(i_brk, 37238, 34176, 44395, i_end=i_tgt + 3, labels=('Вход', 'Стоп', 'Цель'), show_rr=False)
ch.mark(i_rt, 36383, 'Ретест 36 383', where='right', color=BLUE)
ch.text(i_brk + 9, 35300, 'R:R 1:2,34', anchor='middle', color=GREEN, weight=600)
ch.save('06-double-bottom-real.svg')
