from figlib import *
import datetime as dt

# ---------------------------------------------------------------- 8.1 схема трёх таймфреймов
cv = Canvas(760, 372, title='Три графика, три вопроса: зоны и направление, сетап, точка входа',
            subtitle='Учебная связка: 1D, 4H, 1H. Сверху вниз, по одному разу на каждом графике')
rows = [
    ('1D', 'Старший', 'Куда идёт рынок и где зоны?', 'Направление и две зоны:', 'поддержка снизу, сопротивление сверху', BLUE),
    ('4H', 'Рабочий', 'Есть ли у зоны сетап?', 'Вход, стоп и цель', 'либо запись «сделки нет»', GREEN),
    ('1H', 'Младший', 'Можно ли войти ближе к стопу?', 'Точная цена входа', 'шаг необязателен, стоп не меняется', AMBER),
]
y = cv.y0 + 4
H, G = 84, 24
for k, (tf, role, q, r1, r2, col) in enumerate(rows):
    yy = y + k * (H + G)
    cv.rect(14, yy, 120, H, fill=col, stroke=col, opacity=0.12)
    cv.text(74, yy + 40, tf, size=26, anchor='middle', color=col, weight=700)
    cv.text(74, yy + 64, role, size=13, anchor='middle', color=INK)
    cv.box(150, yy, 290, H, [q], stroke=col, size=14)
    cv.box(470, yy, 276, H, [r1, r2], stroke=col, size=14)
    cv.arrow(442, yy + H / 2, 468, yy + H / 2, color=MUTED)
    cv.text(456, yy - 5, '', size=1)
    if k < 2:
        cx = 74
        cv.arrow(cx, yy + H + 2, cx, yy + H + G - 2, color=MUTED, width=1.5)
        cv.text(cx + 12, yy + H + G - 7, 'в 4–6 раз мельче', size=12, color=MUTED)
cv.save('08-three-timeframes.svg')

# ---------------------------------------------------------------- 8.2 недельный график
d = load('btc', '1d')


def week_start(c):
    x = dt.date.fromisoformat(c['date'])
    return x - dt.timedelta(days=x.weekday())


W = []
for c in d:
    w = week_start(c)
    if W and W[-1]['w'] == w:
        k = W[-1]
        k['h'] = max(k['h'], c['h']); k['l'] = min(k['l'], c['l']); k['c'] = c['c']; k['v'] += c['v']
    else:
        W.append(dict(w=w, o=c['o'], h=c['h'], l=c['l'], c=c['c'], v=c['v'], date=str(w)))
wc = [k['c'] for k in W]
we50 = ema(wc, 50)
a = [i for i, k in enumerate(W) if k['date'] == '2022-10-10'][0]
b = [i for i, k in enumerate(W) if k['date'] == '2023-12-11'][0]
seg = W[a:b + 1]
ch = Chart(seg, title='BTC/USDT, 1W: тренд вверх, первая красная неделя после восьми зелёных',
           subtitle='1W из свечей 1D, октябрь 2022 — 17 декабря 2023', main_h=310, extra_bars=3, ymin=13000, ymax=52000)
ch.series(we50[a:b + 1], color=ORANGE, label='EMA 50 (1W)')
ch.hline(48190, x0=0, color=RED, label='Сопротивление 48 190 (максимум марта 2022)', label_at='left')
# повышающиеся минимумы и максимумы
lows = [('2022-11-21', 15476), ('2023-03-06', 19549), ('2023-06-12', 24800)]
highs = [('2023-04-10', 31000), ('2023-07-10', 31804), ('2023-12-04', 44700)]
idx = {k['date']: i - a for i, k in enumerate(W) if i >= a and i <= b}
for dd, p in lows:
    ch.mark(idx[dd], p, f'{p:,}'.replace(',', ' '), where='below', color=GREEN)
for dd, p in highs:
    ch.mark(idx[dd], p, f'{p:,}'.replace(',', ' '), where='above', color=BLUE)
ch.highlight(idx['2023-10-16'], idx['2023-12-04'], color='#16a34a', label='8 зелёных недель, +61%')
ch.mark(idx['2023-12-11'], 41375, 'Закрытие 41 375', where='left', color=RED)
ch.save('08-btc-1w-trend.svg')

# ---------------------------------------------------------------- 8.3 дневной график
cl = [c['c'] for c in d]
e50, e200 = ema(cl, 50), ema(cl, 200)
a, b = find(d, '2023-10-01'), find(d, '2023-12-17')
seg = d[a:b + 1]
ch = Chart(seg, title='BTC/USDT, 1D: после отката на 10% цена вернулась к поддержке 40 200–41 250',
           subtitle='1 октября — 17 декабря 2023', main_h=320, extra_bars=4, ymin=25500, ymax=46500)
ch.series(e50[a:b + 1], color=ORANGE, label='EMA 50')
ch.series(e200[a:b + 1], color=PURPLE, label='EMA 200')
ch.zone(40200, 41250, kind='support', label='Поддержка 40 200–41 250')
ch.zone(43000, 43500, kind='resistance', label='Сопротивление 43 000–43 500')
i = lambda s: find(seg, s)
ch.mark(i('2023-12-08'), 44700, '44 700', where='above', color=BLUE)
ch.mark(i('2023-12-11'), 40222, '40 222', where='left', color=GREEN)
ch.mark(i('2023-11-09'), 37972, '37 972', where='above', color=BLUE)
ch.mark(i('2023-11-24'), 38414, '38 414', where='above', color=BLUE)
ch.arrow((len(seg) - 1, 37600), (len(seg) - 1, 41000), color=INK)
ch.text(len(seg) - 1, 36900, 'Закрытие 41 375', anchor='end', size=12, color=INK)
ch.save('08-btc-1d-zone.svg')

# ---------------------------------------------------------------- 8.4 4H сетап
h4 = load('btc', '4h')
c4 = [c['c'] for c in h4]
f20, f50 = ema(c4, 20), ema(c4, 50)
a, b = find(h4, '2023-12-11 00:00'), find(h4, '2023-12-20 00:00')
seg = h4[a:b + 1]
sig = find(seg, '2023-12-18 08:00')
ch = Chart(seg, title='BTC/USDT, 4H: свеча отбоя в зоне 1D дала вход, цель 43 000 взята',
           subtitle='11–20 декабря 2023, время свечей UTC', main_h=330, extra_bars=9, ymin=39800, ymax=44200)
ch.series(f20[a:b + 1], color=ORANGE, label='EMA 20')
ch.series(f50[a:b + 1], color=PURPLE, label='EMA 50')
ch.zone(40200, 41250, kind='support')
ch.text(12, 40420, 'Поддержка 1D 40 200–41 250', size=12, color=GREEN, weight=600)
ch.zone(43000, 43500, kind='resistance', label='Сопротивление 1D 43 000–43 500', label_at='left')
ch.highlight(sig, sig, color='#2563eb', label='Свеча отбоя')
ch.trade(sig + 1, 41105, 40250, 43000, i_end=sig + 6, labels=('Вход A', 'Стоп', 'Цель'), show_rr=False)
ch.text(sig + 11, 42750, 'R:R 1:2,2', size=12, color=GREEN, weight=600)
ch.hline(40900, x0=sig + 1, x1=sig + 6, color=BLUE, dash=True, tag=False)
ch.text(sig + 6.3, 40760, 'Лимит B 40 900', anchor='start', size=11, color=BLUE)
ch.save('08-btc-4h-setup.svg')
