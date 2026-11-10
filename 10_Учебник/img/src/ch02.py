from figlib import *

# ---------------------------------------------------------------- 2.1 стакан до и после
asks0 = [(60040, 2.0, 0), (60030, 1.5, 0.4), (60020, 1.0, 1.0), (60010, 0.6, 0.6)]  # цена, объём, съедено
bids = [(60000, 0.5), (59990, 0.8), (59980, 1.2), (59970, 2.0)]
cv = Canvas(760, 420, title='Рыночная покупка 2 BTC съедает три уровня продавцов',
            subtitle='Упрощённый стакан BTC/USDT до и после ордера; средняя цена исполнения 60 019')
SC = 78  # пикселей на 1 BTC
top = cv.y0 + 26
RH = 30


def book(x0, title, asks, after):
    cv.text(x0 + 150, top - 10, title, size=14, anchor='middle', weight=600)
    y = top
    for p, v, eaten in asks:
        rem = v - eaten if after else v
        cv.text(x0 + 62, y + 20, fmt_price(p), size=13, anchor='end')
        if rem > 0:
            cv.rect(x0 + 72, y + 4, rem * SC, RH - 8, fill=DOWN, stroke='none', rx=3, opacity=0.8)
            cv.text(x0 + 72 + rem * SC + 6, y + 20, fmt_price(rem, 1).replace(',0', ',0'), size=12, color=MUTED)
        if not after and eaten > 0:
            cv.rect(x0 + 72, y + 4, eaten * SC, RH - 8, fill=AMBER, stroke='none', rx=3, opacity=0.85)
        if after and eaten > 0 and rem <= 0:
            cv.text(x0 + 72, y + 20, 'исполнено', size=12, color=AMBER)
        y += RH
    y += 6
    for p, v in bids:
        cv.text(x0 + 62, y + 20, fmt_price(p), size=13, anchor='end')
        cv.rect(x0 + 72, y + 4, v * SC, RH - 8, fill=UP, stroke='none', rx=3, opacity=0.8)
        cv.text(x0 + 72 + v * SC + 6, y + 20, fmt_price(v, 1), size=12, color=MUTED)
        y += RH
    return y


# после: уровни 60010 и 60020 исполнены целиком, на 60030 остаётся 1,1
asks1 = [(60040, 2.0, 0), (60030, 1.5, 0.4), (60020, 1.0, 1.0), (60010, 0.6, 0.6)]
yend = book(14, 'До ордера', asks0, False)
book(394, 'После ордера', asks1, True)
cv.line(380, top - 24, 380, yend, color=GRID)
# подписи спреда и лучших цен
cv.text(14 + 150, yend + 24, 'Лучший ask 60 010, лучший bid 60 000, спред 10 $', size=12, anchor='middle', color=MUTED)
cv.text(394 + 150, yend + 24, 'Лучший ask 60 030, последняя сделка по 60 030', size=12, anchor='middle', color=MUTED)
# легенда
ly = yend + 52
cv.rect(14, ly, 14, 14, fill=AMBER, stroke='none', rx=2, opacity=0.85)
cv.text(34, ly + 12, 'объём, который заберёт ордер: 0,6 по 60 010, 1,0 по 60 020, 0,4 по 60 030', size=12, color=MUTED)
cv.text(14, ly + 36, 'Красное — продавцы (ask), зелёное — покупатели (bid). Объём справа от полосы указан в BTC.', size=12, color=MUTED)
cv.H = int(ly + 52)
cv.save('02-order-book.svg')

# ---------------------------------------------------------------- 2.2 три ордера
c = synth([60400, 60000, 60700, 61300, 60900, 61700, 62400], bars_per_leg=[6, 8, 8, 6, 8, 8], noise=0.5, seed=3)
n = len(c)
ch = Chart(c, title='Один план, три ордера: вход 60 000, стоп 58 800, тейк 62 400',
           subtitle='Схема для лонга по BTC/USDT: риск 1R = 100 $, цель +2R = 200 $',
           schematic=True, extra_bars=22, main_h=330, ymin=58300, ymax=63000)
ie = 5
ch.trade(ie, 60000, 58800, 62400, i_end=n + 14, labels=('Вход', 'Стоп', 'Тейк'), show_rr=True, prices=True)
ch.text(n + 15, 62700, 'Тейк-профит: лимитный, reduce-only, +2R', anchor='end', size=12, color=GREEN, weight=600)
ch.text(n + 15, 59350, 'Вход: лимитный, post-only, 0,0833 BTC', anchor='end', size=12, color=BLUE, weight=600)
ch.text(n + 15, 58550, 'Стоп-маркет: триггер 58 800, reduce-only, −1R', anchor='end', size=12, color=RED, weight=600)
ch.text(n + 15, 61450, 'Стоп и тейк связаны как OCO', anchor='end', size=12, color=MUTED)
ch.save('02-three-orders.svg')

# ---------------------------------------------------------------- 2.3 расстояние до ликвидации
cv = Canvas(760, 380, title='При плече 50x до ликвидации ближе, чем обычный дневной ход BTC',
            subtitle='Расстояние до ликвидации лонга от входа и ход цены BTC/USDT за день, 2019–2026, %')
X0, SCW = 150, 540 / 50.0
rows = [('Плечо 2x', 49.6, BLUE), ('Плечо 5x', 19.6, BLUE), ('Плечо 10x', 9.6, BLUE), ('Плечо 50x', 1.6, RED)]
y = cv.y0 + 16
for k, (lab, v, col) in enumerate(rows):
    yy = y + k * 40
    cv.text(X0 - 10, yy + 20, lab, size=13, anchor='end')
    cv.rect(X0, yy + 5, v * SCW, 22, fill=col, stroke='none', rx=3, opacity=0.85)
    cv.text(X0 + max(v * SCW, 4.1 * SCW + 4) + 8, yy + 21, fmt_price(v, 1) + '%', size=13, weight=600, color=col)
ybar = y + 4 * 40 + 6
cv.line(X0, y - 6, X0, ybar + 36, color=AXIS)
# референс: обычный дневной ход
xm = X0 + 4.1 * SCW
cv.line(xm, y - 6, xm, y + 4 * 40 + 22, color=ORANGE, width=2, dash=True)
cv.text(xm + 8, y + 4 * 40 + 22, 'Обычный дневной ход BTC: 4,1% (медиана)', size=13, color=ORANGE, weight=600)
ybar = y + 4 * 40 + 6
# худший день
wy = ybar + 36
cv.text(X0 - 10, wy + 20, 'Худший день', size=13, anchor='end')
cv.rect(X0, wy + 5, 44.4 * SCW, 22, fill=DOWN, stroke='none', rx=3, opacity=0.55)
cv.text(X0 + 44.4 * SCW + 8, wy + 21, '', size=1)
cv.text(X0 + 10, wy + 21, '12 марта 2020: падение от открытия до минимума −44,4%', size=13, weight=600, color=INK)
cv.text(X0, wy + 52, 'Плечо 3x уже не выдержало бы этот день, плечо 2x выдержало бы.', size=12, color=MUTED)
cv.text(X0 + 540, wy + 74, 'шкала: 0–50% от цены входа', size=11, anchor='end', color=MUTED)
cv.H = int(wy + 90)
cv.save('02-liquidation-distance.svg')
