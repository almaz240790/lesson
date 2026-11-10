from figlib import *
import random

# Симуляция: винрейт 40%, +2R / -1R, три серии по 100 сделок (зёрна подобраны под цифры текста).
def series(seed, n=100):
    r = random.Random(seed)
    return [2 if r.random() < 0.4 else -1 for _ in range(n)]

def worst_streak(s):
    best = cur = end = 0
    for i, x in enumerate(s):
        cur = cur + 1 if x < 0 else 0
        if cur > best:
            best, end = cur, i
    return best, end - best + 1, end   # длина, первый индекс, последний индекс

runs = [(14, BLUE), (10, GREEN), (1, ORANGE)]
cv = Canvas(760, 430, title='Одна система, три серии: итог от −1R до +41R',
            subtitle='Симуляция: винрейт 40%, прибыль +2R, убыток −1R, по 100 сделок. Красным — самая длинная полоса убытков')
L, R, T, B = 60, 690, cv.y0 + 14, 380
ymin, ymax = -20, 60
X = lambda i: L + (R - L) * i / 100
Y = lambda v: B - (B - T) * (v - ymin) / (ymax - ymin)
for v in range(ymin, ymax + 1, 20):
    cv.line(L, Y(v), R, Y(v), color=GRID if v else AXIS, width=1 if v else 1.5)
    cv.text(L - 8, Y(v) + 4, f'{v:+d}R' if v else '0', size=12, anchor='end', color=MUTED)
for i in range(0, 101, 20):
    cv.text(X(i), B + 20, str(i), size=12, anchor='middle', color=MUTED)
cv.text((L + R) / 2, B + 40, 'Номер сделки', size=12, anchor='middle', color=MUTED)
# линия ожидания +20R за 100 сделок
cv.line(X(0), Y(0), X(100), Y(20), color=MUTED, dash=True)
cv.text(X(1), Y(50), 'Пунктир — ожидание системы: +0,2R на сделку, +20R за 100 сделок', size=12, color=MUTED)

labels_y = {}
for seed, col in runs:
    s = series(seed)
    eq = [0]
    for x in s:
        eq.append(eq[-1] + x)
    ln, a, b = worst_streak(s)
    cv.polyline([(X(i), Y(v)) for i, v in enumerate(eq)], color=col, width=1.75)
    cv.polyline([(X(i), Y(eq[i])) for i in range(a, b + 2)], color=RED, width=4)
    print(seed, eq[-1], ln, a + 1, b + 1)
    sign = f'{eq[-1]:+d}R'.replace('-', '−')
    cv.circle(X(100), Y(eq[-1]), 4, fill=col)
    cv.text(X(100) + 10, Y(eq[-1]) + 4, f'{sign}', size=13, color=col, weight=600)
    if seed == 1:
        cv.text(X(a) - 4, Y(-3), f'{ln} убытков подряд', size=12, anchor='end', color=RED)
    elif seed == 10:
        cv.text(X(100) + 10, Y(-13), f'{ln} убытков подряд (зелёная серия)', size=12, anchor='end', color=RED)
    else:
        cv.text(X(a + ln / 2 + 0.5) - (0 if seed == 14 else 14), Y(eq[a]) - 10, f'{ln} убытков подряд', size=12, anchor='middle', color=RED)
cv.save('01-equity-curves.svg')
