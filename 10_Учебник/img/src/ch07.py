from figlib import *

full = load('btc', '1d')
cl = [c['c'] for c in full]
E20, E50, E200 = ema(cl, 20), ema(cl, 50), ema(cl, 200)
RSI = rsi(cl, 14)
ATR = atr(full, 14)
M, SIG, HIST = macd(cl)
VAVG = [None] + [None] * 19 + [sum(full[j]['v'] for j in range(i - 20, i)) / 20 for i in range(20, len(full))]
VOL = [c['v'] for c in full]


def rng(a, b):
    i, j = find(full, a), find(full, b)
    return i, j, slice(i, j + 1)


def idx(a, d):
    return find(full, d) - a


# ---- 7.1 золотой крест
a, b, s = rng('2022-11-15', '2023-03-14')
c = full[s]
ch = Chart(c, title='Золотой крест пришёл, когда цена уже выросла на 59%',
           subtitle='BTC/USDT, 1D, 15 ноября 2022 — 14 марта 2023', main_h=330, ymax=28200)
ch.series(E50[s], color=BLUE, label='EMA 50')
ch.series(E200[s], color=ORANGE, label='EMA 200')
lo_i = idx(a, '2022-11-21'); cr = idx(a, '2023-02-18'); lo2 = idx(a, '2023-03-10')
ch.mark(lo_i, full[a + lo_i]['l'], 'Минимум 15 476', where='right', color=RED)
ch.mark(cr, E50[a + cr], '', where='above', color=GREEN)
ch.text(cr - 1, 27000, 'Золотой крест 18 февраля, закрытие 24 632', anchor='end', color=GREEN, weight=600)
ch.mark(lo2, full[a + lo2]['l'], '10 марта: 19 549 (−21%)', where='below', color=RED)
ch.vline(cr, color=GREEN)
ch.save('07-ema-cross.svg')

# ---- 7.4 RSI в тренде
a, b, s = rng('2023-09-20', '2023-12-15')
c = full[s]
ch = Chart(c, title='RSI выше 70 двадцать пять дней, а цена продолжает расти',
           subtitle='BTC/USDT, 1D, 20 сентября — 15 декабря 2023', main_h=270, extra_bars=3)
i0, i1 = idx(a, '2023-10-20'), idx(a, '2023-11-13')
ch.highlight(i0, i1, color='#2563eb')
for d, t in [('2023-10-24', '35 280'), ('2023-11-09', '37 972'), ('2023-11-15', '37 980')]:
    i = idx(a, d)
    ch.mark(i, full[a + i]['h'], t, where='above', color=INK)
p = ch.panel(RSI[s], label='RSI 14', height=110, ymin=10, ymax=95, hlines=(30, 70))
for d in ['2023-10-24', '2023-11-09', '2023-11-15']:
    i = idx(a, d)
    p.mark(i, RSI[a + i], f"{RSI[a+i]:.1f}".replace('.', ','), where='above', color=RED)
ch.save('07-rsi-trend.svg')

# ---- 7.5 дивергенция
a, b, s = rng('2023-06-10', '2023-10-05')
c = full[s]
ch = Chart(c, title='Цена обновила минимум, RSI нет: бычья дивергенция у поддержки',
           subtitle='BTC/USDT, 1D, 10 июня — 5 октября 2023', main_h=290, extra_bars=2, ymin=24200)
ch.zone(24800, 25250, kind='support')
ch.text(30, 24450, 'Поддержка 24 800–25 250', color=GREEN, weight=600)
i1_, i2_ = idx(a, '2023-08-17'), idx(a, '2023-09-11')
l1, l2 = full[a + i1_]['l'], full[a + i2_]['l']
ch.line([(i1_, l1), (i2_, l2)], color=RED, width=1.75, dash=True)
ch.mark(i1_, l1, '25 166', where='below', color=RED)
ch.mark(i2_, l2, '24 901', where='below', color=RED)
ch.mark(idx(a, '2023-10-02'), full[a + idx(a, '2023-10-02')]['h'], '28 580', where='above', color=GREEN)
p = ch.panel(RSI[s], label='RSI 14', height=110, ymin=5, ymax=80, hlines=(30, 70))
r1, r2 = RSI[a + i1_], RSI[a + i2_]
p.line((i1_, r1), (i2_, r2), color=GREEN, dash=True)
p.mark(i1_, r1, '21,0', where='below', color=RED)
p.mark(i2_, r2, '32,8', where='above', color=GREEN)
ch.save('07-rsi-divergence.svg')

# ---- 7.6 MACD
a, b, s = rng('2024-01-15', '2024-04-30')
c = full[s]
ch = Chart(c, title='Гистограмма MACD слабеет раньше, чем цена разворачивается',
           subtitle='BTC/USDT, 1D, 15 января — 30 апреля 2024', main_h=270, extra_bars=2)
for d, t in [('2024-03-04', '68 250'), ('2024-03-13', '73 070')]:
    i = idx(a, d)
    ch.mark(i, full[a + i]['c'], t, where='above', color=INK)
i = idx(a, '2024-03-16')
ch.mark(i, full[a + i]['c'], '', where='below', color=RED)
ch.arrow((i - 1.5, 52000), (i - 0.3, 64800), color=RED)
ch.text(i - 4.5, 50500, 'Линии MACD пересеклись вниз 16 марта: 65 300', anchor='start', color=RED, weight=600)
p = ch.panel(HIST[s], label='MACD 12, 26, 9', height=130, kind='bars', ymin=-1500, ymax=5800, hlines=(0,))
p.series(M[s], color=BLUE).series(SIG[s], color=ORANGE)
for d in ['2024-03-04', '2024-03-13']:
    i = idx(a, d)
    p.mark(i, HIST[a + i], f"{HIST[a+i]:,.0f}".replace(',', ' '), where='above', color=INK)
ch.save('07-macd.svg')

# ---- 7.7 ATR и объём
a, b, s = rng('2023-07-25', '2023-11-10')
c = full[s]
ch = Chart(c, title='Тихий рынок сменился резким: ATR и объём выросли вместе',
           subtitle='BTC/USDT, 1D, 25 июля — 10 ноября 2023', main_h=250, extra_bars=2)
for d in ['2023-08-17', '2023-10-23']:
    i = idx(a, d)
    ch.highlight(i, i, color='#f59e0b')
i = idx(a, '2023-08-17')
ch.mark(i, full[a + i]['l'], '17 августа: 25 166', where='below', color=RED)
i = idx(a, '2023-10-23')
ch.mark(i, full[a + i]['c'], '23 октября: закрытие 33 070', where='left', color=GREEN)
p = ch.panel(ATR[s], label='ATR 14, $', height=80, ymin=0, ymax=1500)
for d in ['2023-08-15', '2023-10-25']:
    i = idx(a, d)
    p.mark(i, ATR[a + i], f"{ATR[a+i]:,.0f}".replace(',', ' '), where='above', color=INK)
v = ch.panel(VOL[s], label='Объём, BTC; оранжевая — средняя за 20 дней', height=80, kind='bars', ymin=0, ymax=max(VOL[s]) * 1.05)
v.series(VAVG[s], color=ORANGE)
ch.save('07-atr-volume.svg')
