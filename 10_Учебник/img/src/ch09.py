from figlib import *

# ------------------------------------------------------------ 9.1 блок-схема
cv = Canvas(760, 606, title='Десять шагов: ответ «нет» на семи из них заканчивается записью «ждать»',
            subtitle='Шаги идут сверху вниз; сделка открывается только после шага 10')
steps = [
    ('1. Календарь', 'Вне окна ±30 минут от новости?', 'новости', True, MUTED),
    ('2. Тренд', 'Есть ли тренд вверх или вниз?', '1D', True, BLUE),
    ('3. Зоны', 'Где поддержка и сопротивление?', '1D, 1W', False, BLUE),
    ('4. Место цены', 'Цена у зоны по тренду?', '1D', True, BLUE),
    ('5. Сетап', 'Есть ли откат к зоне?', '4H', True, GREEN),
    ('6. Триггер', 'Закрылась ли свеча подтверждения?', '4H', True, GREEN),
    ('7. Вход, стоп, цель', 'R:R не меньше 1:2?', '4H', True, GREEN),
    ('8. Размер позиции', 'Лимиты риска не нарушены?', 'расчёт', True, AMBER),
    ('9. Журнал', 'Идея записана, скриншоты сделаны?', 'запись', False, AMBER),
    ('10. Ордера', 'Стоп и цель стоят на бирже?', 'биржа', False, AMBER),
]
x0, bw_, bh, gap = 14, 540, 36, 12
y0 = cv.y0 + 2
ys = [y0 + k * (bh + gap) for k in range(10)]
for k, (name, q, where, stop, col) in enumerate(steps):
    y = ys[k]
    cv.rect(x0, y, bw_, bh, fill=col, stroke=col, opacity=0.10)
    cv.rect(x0, y, bw_, bh, stroke=col, sw=1.5)
    cv.text(x0 + 12, y + bh / 2 + 5, name, size=14, color=INK, weight=700)
    cv.text(x0 + 190, y + bh / 2 + 5, q, size=13.5, color=INK)
    cv.text(x0 + bw_ - 12, y + bh / 2 + 5, where, size=12.5, anchor='end', color=col, weight=600)
    if k < 9:
        cv.arrow(x0 + 100, y + bh + 1, x0 + 100, y + bh + gap - 1, color=MUTED, width=1.5)
    if stop:
        cv.arrow(x0 + bw_ + 2, y + bh / 2, 628, y + bh / 2, color=RED, width=1.5)
        cv.text(x0 + bw_ + 38, y + bh / 2 - 6, 'нет', size=12.5, anchor='middle', color=RED, weight=600)
wy0, wy1 = ys[0], ys[7] + bh
cv.rect(630, wy0, 116, wy1 - wy0, fill='#f59e0b', stroke=AMBER, opacity=0.14, sw=1.5)
cv.rect(630, wy0, 116, wy1 - wy0, stroke=AMBER, sw=1.5)
cv.text(688, (wy0 + wy1) / 2 - 8, 'Ждать', size=20, anchor='middle', color=AMBER, weight=700)
cv.text(688, (wy0 + wy1) / 2 + 14, 'и оповещение', size=12.5, anchor='middle', color=MUTED)
cv.text(688, (wy0 + wy1) / 2 + 31, 'у зоны', size=12.5, anchor='middle', color=MUTED)
ye = ys[9] + bh
cv.rect(x0, ye + 14, bw_, 34, fill='#16a34a', stroke=GREEN, opacity=0.14, sw=1.5)
cv.rect(x0, ye + 14, bw_, 34, stroke=GREEN, sw=1.5)
cv.arrow(x0 + 100, ye + 1, x0 + 100, ye + 13, color=MUTED, width=1.5)
cv.text(x0 + bw_ / 2, ye + 36, 'Сделка открыта: вход, стоп и тейк-профит на бирже', size=13.5, anchor='middle', color=GREEN, weight=700)
cv.save('09-algorithm-flow.svg')

# ------------------------------------------------------------ данные
d = load('btc', '1d')
cl = [c['c'] for c in d]
e50, e200 = ema(cl, 50), ema(cl, 200)
h = load('btc', '4h')
hc = [c['c'] for c in h]
hr = rsi(hc, 14)

# ------------------------------------------------------------ 9.2 контекст 1D
a, b = find(d, '2025-05-01'), find(d, '2025-08-02')
seg = d[a:b + 1]
i = lambda s: find(seg, s)
ch = Chart(seg, title='BTC/USDT, 1D: тренд вверх, цена вернулась к пробитому сопротивлению 110 500–112 000',
           subtitle='1 мая — 2 августа 2025', main_h=330, extra_bars=8, ymin=92000, ymax=127000)
ch.series(e50[a:b + 1], color=ORANGE, label='EMA 50')
ch.series(e200[a:b + 1], color=PURPLE, label='EMA 200')
ch.zone(110500, 112000, kind='support')
ch.zone(119950, 121000, kind='resistance', label='Сопротивление 119 950–121 000', label_at='left')
ch.text(0.3, 110700, 'Поддержка', size=11, color=GREEN, weight=600)
ch.mark(i('2025-07-14'), 123218, '123 218', where='above', color=BLUE)
ch.mark(i('2025-06-22'), 98200, '98 200', where='below', color=GREEN)
ch.mark(i('2025-05-22'), 111980, '111 980', where='above', color=BLUE)
ch.arrow((i('2025-07-28'), 104800), (i('2025-07-28'), 117200), color=INK)
ch.text(i('2025-07-28'), 103000, '28 июля: «ждать»', anchor='middle', size=11.5, color=INK, weight=600)
ch.mark(i('2025-08-02'), 112003, '112 003', where='below', color=GREEN)
ch.save('09-btc-1d-context.svg')

# ------------------------------------------------------------ 9.3 сделка 4H
a, b = find(h, '2025-07-27 00:00'), find(h, '2025-08-12 00:00')
seg = h[a:b]
i = lambda s: find(seg, s)
ie, iend = i('2025-08-03 04:00'), i('2025-08-11 00:00')
ch = Chart(seg, title='BTC/USDT, 4H: свеча вне зоны не триггер, свеча в зоне дала вход, цель достигнута',
           subtitle='27 июля — 11 августа 2025, время свечей UTC', main_h=330, extra_bars=16, ymin=108600, ymax=122600)
ch.zone(110500, 112000, kind='support', x0=0, x1=len(seg) - 1)
ch.zone(119950, 121000, kind='resistance', x0=0, x1=len(seg) - 1, label='Сопротивление 119 950–121 000', label_at='left')
ch.trade(ie, 113604, 111300, 119800, i_end=iend, labels=('', '', ''), show_rr=False, prices=False)
N = len(seg)
ch.text(N + 0.5, 113604 - 120, 'Вход 113 604', size=11.5, color=BLUE, weight=600)
ch.text(N + 0.5, 111300 - 120, 'Стоп 111 300', size=11.5, color=RED, weight=600)
ch.text(N + 0.5, 119800 - 120, 'Цель 119 800', size=11.5, color=GREEN, weight=600)
ch.text(ie + 8, 118300, 'R:R 1:2,7', size=12, color=GREEN, weight=600)
ch.arrow((i('2025-08-03 00:00'), 109900), (i('2025-08-03 00:00'), 111750), color=GREEN)
ch.text(i('2025-08-03 00:00'), 109150, 'Триггер 3 авг, 00:00', anchor='middle', size=11.5, color=GREEN, weight=600)
ch.arrow((i('2025-08-02 04:00'), 116500), (i('2025-08-02 04:00'), 114200), color=MUTED)
ch.text(i('2025-08-02 04:00') - 5, 116900, 'Не триггер: вне зоны', size=11.5, color=MUTED, weight=600)
ch.text(1, 111200, 'Поддержка 110 500–112 000', size=11.5, color=GREEN, weight=600)
p = ch.panel(hr[a:b], label='RSI 14', height=80, hlines=(30, 70), ymin=10, ymax=90, color=PURPLE)
j = min(range(len(seg)), key=lambda k: hr[a + k] if hr[a + k] is not None else 999)
p.mark(j, hr[a + j], f'{hr[a + j]:.0f}', where='below', color=PURPLE)
ch.save('09-btc-4h-trade.svg')

# ------------------------------------------------------------ 9.4 убыток 4H
a, b = find(h, '2024-06-05 00:00'), find(h, '2024-06-17 00:00')
seg = h[a:b]
i = lambda s: find(seg, s)
ch = Chart(seg, title='BTC/USDT, 4H: те же шаги, но цена дошла до +1,49R и вернулась на стоп: −1R',
           subtitle='5–16 июня 2024, время свечей UTC', main_h=330, extra_bars=16, ymin=64000, ymax=72600)
ch.zone(66300, 67550, kind='support', x0=0, x1=len(seg) - 1)
ch.hline(71900, x0=0, x1=len(seg) - 1, color=RED, dash=True, tag=False)
ch.trade(i('2024-06-11 20:00'), 67407, 65670, 71900, i_end=i('2024-06-14 16:00'), labels=('', '', ''), show_rr=False, prices=False)
N = len(seg)
ch.text(N + 0.5, 67407 - 110, 'Вход 67 407', size=11.5, color=BLUE, weight=600)
ch.text(N + 0.5, 65670 - 110, 'Стоп 65 670', size=11.5, color=RED, weight=600)
ch.text(N + 0.5, 71900 - 110, 'Цель 71 900', size=11.5, color=GREEN, weight=600)
ch.text(i('2024-06-12 20:00'), 71300, 'R:R 1:2,6', size=12, color=GREEN, weight=600)
ch.arrow((i('2024-06-11 16:00'), 64800), (i('2024-06-11 16:00'), 66000), color=GREEN)
ch.text(i('2024-06-11 16:00'), 64300, 'Триггер 11 июня', anchor='middle', size=11.5, color=GREEN, weight=600)
ch.mark(i('2024-06-12 12:00') if False else max(range(len(seg)), key=lambda k: seg[k]['h'] if seg[k]['date'] < '2024-06-14' and seg[k]['date'] > '2024-06-11' else 0),
        69999, 'До 69 999 (+1,49R)', where='above', color=BLUE)
ch.mark(i('2024-06-14 16:00'), 65078, 'Стоп 14 июня', where='below', color=RED)
ch.text(1, 66900, 'Поддержка 66 300–67 550', size=11.5, color=GREEN, weight=600)
ch.save('09-btc-4h-loss.svg')
