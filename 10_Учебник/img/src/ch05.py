from figlib import *

# ---------------------------------------------------------------- схемы: помощник
def build(path, bars, noise=0.2, seed=3):
    cs = synth(path, bars_per_leg=bars, noise=noise, seed=seed)
    ends, k = [], -1
    for n in bars:
        k += n
        ends.append(k)
    return cs, ends


def setc(cs, i, o=None, h=None, l=None, c=None):
    x = cs[i]
    if o is not None: x['o'] = o
    if c is not None: x['c'] = c
    if l is not None: x['l'] = l
    if h is not None: x['h'] = h
    x['h'] = max(x['h'], x['o'], x['c'])
    x['l'] = min(x['l'], x['o'], x['c'])


# ================================================================ рис. 5.1 границы зоны (схема)
cs, e = build([112, 103, 111, 103, 111, 103, 113], [6, 5, 6, 5, 6, 6], noise=0.15, seed=4)
# три касания поддержки: тени уходят вниз, закрытия — у верхней границы
setc(cs, e[0], o=106.5, c=104.5, l=101.5)
setc(cs, e[2], o=106.0, c=103.0, l=100.0)
setc(cs, e[4], o=106.5, c=104.0, l=100.8)
ch = Chart(cs, title='Зону ведут по самой дальней тени и по крайнему закрытию',
           subtitle='Схема: три касания поддержки', schematic=True, extra_bars=7, main_h=300, ymin=97, ymax=116)
ch.zone(100.0, 103.0, kind='support', label='Зона поддержки')
ch.hline(101.5, x0=e[0] - 1, x1=len(cs) + 6, color=RED, dash=True, label='Линия по первому минимуму', label_at='right', tag=False)
ch.mark(e[0], 101.5, '1', where='below', color=INK)
ch.mark(e[2], 100.0, '2', where='below', color=INK)
ch.mark(e[4], 100.8, '3', where='below', color=INK)
ch.text(len(cs) + 6, 103.0 + 0.5, 'крайнее закрытие', anchor='end', size=11.5, color=GREEN)
ch.text(len(cs) + 6, 100.0 - 1.4, 'самая дальняя тень', anchor='end', size=11.5, color=GREEN)
ch.save('05-zone-borders.svg')

# ================================================================ рис. 5.2 смена ролей, BTC 1D
full = load('btc', '1d')
a, b = find(full, '2023-11-01'), find(full, '2024-02-10')
cs = full[a:b + 1]
ix = lambda d: find(full, d) - a
ch = Chart(cs, title='Пробитое сопротивление 37 850–38 450 через 53 дня сработало поддержкой',
           subtitle='BTC/USDT, 1D, 1 ноября 2023 — 10 февраля 2024', main_h=330, extra_bars=3, ymin=33500, ymax=50200)
brk = ix('2023-12-01')
ch.zone(37850, 38450, x0=0, x1=brk + 0.5, kind='resistance')
ch.zone(37850, 38450, x0=brk + 0.5, x1=len(cs) + 2, kind='support')
ch.text(0.5, 44500, 'Сопротивление 37 850–38 450,', anchor='start', size=12, color=RED, weight=600)
ch.text(0.5, 43600, 'касания 1–4 в ноябре', anchor='start', size=12, color=RED, weight=600)
ch.text(70, 36600, 'После пробоя — поддержка', anchor='end', size=12, color=GREEN, weight=600)
for n, d, hi in ((1, '2023-11-09', 37972.24), (2, '2023-11-15', 37980), (3, '2023-11-24', 38414), (4, '2023-11-29', 38450)):
    ch.mark(ix(d), hi, str(n), where='above', color=RED)
ch.mark(brk, 38999, 'Пробой 1 дек', where='above', color=INK)
ch.mark(ix('2024-01-11'), 48969.48, '48 969', where='above', color=INK)
ch.mark(ix('2024-01-23'), 38555, 'Ретест 23 янв', where='below', color=GREEN)
ch.save('05-role-reversal-btc.svg')

# ================================================================ рис. 5.3 канал, BTC 1D 2022
a, b = find(full, '2022-06-05'), find(full, '2022-09-10')
cs = full[a:b + 1]
ix = lambda d: find(full, d) - a
i18, i30, i12, i13, i20 = (ix(d) for d in ('2022-06-18', '2022-06-30', '2022-07-12', '2022-07-13', '2022-07-20'))
p18, p13 = 17622.0, 18910.94
slope = (p13 - p18) / (i13 - i18)
low = lambda i: p18 + slope * (i - i18)
width = 24276.74 - low(i20)            # параллель через максимум 20 июля
n = len(cs)
ch = Chart(cs, title='Канал июня — августа 2022 держался два месяца и был пробит вниз',
           subtitle='BTC/USDT, 1D, 5 июня — 10 сентября 2022', main_h=330, extra_bars=2, ymin=16500, ymax=27800)
first = (17622.0, 18626.0)
s1 = (first[1] - first[0]) / (i30 - i18)
ch.line([(i18, 17622.0), (i12 + 3, 17622.0 + s1 * (i12 + 3 - i18))], color=MUTED, dash=True, width=1.5)
ch.line([(i18, low(i18)), (n + 1, low(n + 1))], color=BLUE, width=1.75)
ch.line([(i18, low(i18) + width), (n + 1, low(n + 1) + width)], color=BLUE, width=1.75)
ch.mark(i18, 17622, '17 622', where='below', color=INK)
ch.mark(i30, 18626, '18 626', where='left', color=INK)
ch.mark(i13, 18910.94, '18 911', where='below', color=INK)
ch.mark(i20, 24276.74, '24 277', where='above', color=INK)
ch.text(i12 + 4, 17622.0 + s1 * (i12 + 4 - i18) - 650, 'первая линия, снята 12 июля', size=11.5, color=MUTED, anchor='start')
ch.text(52, low(52) - 900, 'нижняя граница', size=11.5, color=BLUE, anchor='middle', weight=600)
ch.text(62, low(62) + width + 700, 'верхняя граница', size=11.5, color=BLUE, anchor='middle', weight=600)
ch.save('05-channel-btc-2022.svg')

# ================================================================ рис. 5.4 Фибоначчи + зона (схема)
cs, e = build([100, 152, 146, 200, 150, 192], [7, 4, 8, 8, 6], noise=0.15, seed=5)
setc(cs, e[2], h=200.0)
setc(cs, e[3], l=149.0, c=151.5)
top_i, n = e[2], len(cs)
hi_p, lo_p = 200.0, 100.0
lv = lambda f: hi_p - (hi_p - lo_p) * f
ch = Chart(cs, title='Уровень 50% даёт довод, потому что совпал с горизонтальной зоной',
           subtitle='Схема: коррекция импульса от 100 до 200', schematic=True, extra_bars=10, main_h=320, ymin=90, ymax=214)
ch.zone(146, 154, kind='support')
ch.text(0.5, 154 + 3, 'Горизонтальная зона', size=11.5, color=GREEN, weight=600)
ch.line([(0, 100), (top_i, 200)], color=PURPLE, dash=True, width=1.5)
for f, name in ((0.382, '38,2%'), (0.5, '50%'), (0.618, '61,8%')):
    ch.hline(lv(f), x0=top_i, x1=n + 9, color=PURPLE, dash=True, label=name, label_at='right', tag=False)
ch.mark(top_i, 200, 'Конец импульса', where='above', color=INK)
ch.text(2.5, 95, 'Начало импульса', size=11.5, anchor='start', color=INK)
ch.save('05-fib-confluence.svg')

# ================================================================ рис. 5.5 сбор стопов (схема)
cs, e = build([113, 104, 112, 104, 112, 104, 120], [6, 5, 6, 5, 6, 8], noise=0.15, seed=6)
setc(cs, e[0], o=107, c=105, l=102.5)
setc(cs, e[2], o=107, c=105, l=102.0)
setc(cs, e[4], o=107.0, c=103.5, l=93.5)   # прокол: тень под зоной, закрытие выше неё
ch = Chart(cs, title='Тень уходит под поддержку, исполняет стопы, и цена возвращается в диапазон',
           subtitle='Схема: сбор стопов', schematic=True, extra_bars=4, main_h=320, ymin=89, ymax=124)
ch.zone(101.5, 104.5, kind='support', label='Поддержка')
ch.zone(94.5, 101.5, kind='warn', label='Стопы покупателей')
ch.mark(e[4], 93.5, 'Прокол', where='below', color=INK)
ch.text(e[4] + 3, 102.4, '← закрытие вернулось в зону', size=11.5, anchor='start', color=GREEN, weight=600)
ch.save('05-stop-sweep.svg')
