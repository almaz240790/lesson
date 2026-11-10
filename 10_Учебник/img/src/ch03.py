from figlib import *
import datetime as dt
from collections import defaultdict

# ---------------------------------------------------------------- 3.1 анатомия свечи
def fig_anatomy():
    cv = Canvas(760, 380, title='Свеча хранит четыре цены: тело лежит между открытием и закрытием',
                subtitle='Бычья свеча закрылась выше открытия, медвежья — ниже')
    top, bot = 100, 330          # High и Low в пикселях
    hi_y, lo_y = 92, 338
    def draw(x, up, name):
        # цены: бычья O внизу тела, C вверху; медвежья наоборот
        yb, yt = 270, 160        # границы тела
        o, c = (yb, yt) if up else (yt, yb)
        cv.candle(x, o, hi_y, lo_y, c, w=56)
        col = UP if up else DOWN
        cv.text(x, 372, name, size=14, anchor='middle', weight=600, color=col if False else INK)
        return o, c
    xb, xr = 190, 570
    o1, c1 = draw(xb, True, 'Бычья: закрытие выше открытия')
    o2, c2 = draw(xr, False, 'Медвежья: закрытие ниже открытия')
    # подписи цен — слева от свечи; выноски — справа
    for x, o, c, up in ((xb, o1, c1, True), (xr, o2, c2, False)):
        lx = x - 44
        for y, s in ((hi_y, 'High (максимум)'), (lo_y, 'Low (минимум)')):
            cv.line(lx, y, x - 3, y, color=AXIS, dash=True)
            cv.text(lx - 6, y + 4, s, size=12, anchor='end')
        for y, s in ((o, 'Open (открытие)'), (c, 'Close (закрытие)')):
            cv.line(lx, y, x - 28, y, color=AXIS, dash=True)
            cv.text(lx - 6, y + 4, s, size=12, anchor='end')
    # тело и тени справа от бычьей и медвежьей
    for x in (xb, xr):
        rx = x + 44
        cv.line(x + 30, 160, rx, 160, color=AXIS, width=1) if False else None
        cv.text(rx, 215 + 4, 'Тело', size=13, weight=600, color=BLUE)
        cv.line(x + 32, 160, x + 38, 160, color=BLUE); cv.line(x + 32, 270, x + 38, 270, color=BLUE)
        cv.line(x + 38, 160, x + 38, 270, color=BLUE)
        cv.line(x + 8, 125, rx + 6, 125, color=AXIS, width=1)
        cv.text(rx + 10, 129, 'Верхняя тень', size=13, weight=600, color=ORANGE)
        cv.line(x + 8, 305, rx + 6, 305, color=AXIS, width=1)
        cv.text(rx + 10, 309, 'Нижняя тень', size=13, weight=600, color=ORANGE)
    cv.save('03-candle-anatomy.svg')

# ---------------------------------------------------------------- 3.2 типы свечей
def fig_types():
    cv = Canvas(760, 400, title='Тип свечи определяют тело, тени и положение закрытия',
                subtitle='Положение закрытия = (Close − Low) / (High − Low)')
    H, L = 90, 270      # диапазон в пикселях (180 px)
    def pos(y_close):
        return (L - y_close) / (L - H) * 100
    # (имя, open_y, close_y)
    specs = [
        ('Длинное тело', 244, 112, ['Одна сторона вела цену', 'весь период']),
        ('Длинная нижняя тень', 120, 100, ['Падение выкуплено', 'покупателями']),
        ('Длинная верхняя тень', 240, 258, ['Рост возвращён', 'продавцами']),
        ('Доджи', 183, 178, ['Ни одна сторона', 'не победила']),
    ]
    xs = [105, 275, 445, 615]
    for x, (name, o, c, note) in zip(xs, specs):
        cv.candle(x, o, H, L, c, w=40)
        p = pos(c)
        cv.text(x, 62 + 8 if False else 300, name, size=13, anchor='middle', weight=600)
        cv.text(x, 322, f'закрытие на {p:.0f}%', size=13, anchor='middle', color=BLUE, weight=600)
        cv.text(x, 345, note[0], size=12, anchor='middle', color=MUTED)
        cv.text(x, 361, note[1], size=12, anchor='middle', color=MUTED)
        # метка закрытия
        cv.line(x + 24, c, x + 46, c, color=BLUE, width=1.25)
        cv.circle(x + 46, c, 3, fill=BLUE)
    cv.text(14, 385, 'Тонкая линия справа от свечи — цена закрытия.', size=11, color=MUTED)
    cv.save('03-candle-types.svg')

# ---------------------------------------------------------------- 3.3 шесть свечей 4H
def fig_day():
    d = load('btc', '4h', '2025-01-13 00:00', '2025-01-13 23:59')
    assert len(d) == 6
    ch = Chart(d, title='Шесть свечей 4H складываются в одну дневную: упали до 89 257 $ и вернулись',
               subtitle='BTC/USDT, 4H, 13 января 2025 (UTC)', extra_bars=3, width=960, main_h=300, ymin=88000, ymax=97000)
    o, h, l, c = d[0]['o'], max(x['h'] for x in d), min(x['l'] for x in d), d[-1]['c']
    assert (o, h, l, c) == (94545.07, 95940.0, 89256.69, 94536.1)
    ch.hline(h, 0, 5, color=ORANGE, label=None, tag=False)
    ch.hline(l, 0, 5, color=ORANGE, label=None, tag=False)
    ch.mark(0, h, f'High дня {fmt_price(h)}', where='above', color=ORANGE)
    ch.mark(3, l, f'Low дня {fmt_price(l)}', where='below', color=ORANGE)
    ch.hline(o, 0, 5, color=BLUE, label=None, tag=False)
    ch.text(5.6, o + 650, f'Open дня {fmt_price(o)} (с первой свечи)', anchor='start', color=BLUE, size=12, weight=600)
    ch.mark(5, c, f'Close дня {fmt_price(c)}', where='right', color=BLUE)
    for i, t in enumerate(['00:00', '04:00', '08:00', '12:00', '16:00', '20:00']):
        pass
    ch.save('03-day-six-candles.svg')

# ---------------------------------------------------------------- 3.4 объём по времени суток
def fig_volume():
    d = load('btc', '4h', '2024-01-01', '2026-10-24 23:59')
    wd, we = defaultdict(list), defaultdict(list)
    for c in d:
        x = dt.datetime.fromtimestamp(c['t'], dt.timezone.utc)
        (we if x.weekday() >= 5 else wd)[x.hour].append(c['v'])
    hours = list(range(0, 24, 4))
    a = [sum(wd[h]) / len(wd[h]) for h in hours]
    b = [sum(we[h]) / len(we[h]) for h in hours]
    cv = Canvas(760, 380, title='В будни объём сосредоточен в свечах 12:00 и 16:00 UTC, в выходные он ровнее и вдвое ниже',
                subtitle='BTC/USDT, 4H, 1 января 2024 — 24 октября 2026: средний объём свечи, BTC')
    x0, x1, yb, yt = 70, 735, 330, 105
    vmax = 8000
    for v in range(0, vmax + 1, 2000):
        y = yb - (yb - yt) * v / vmax
        cv.line(x0, y, x1, y, color=GRID)
        cv.text(x0 - 8, y + 4, (fmt_price(v) if v else '0'), size=11, anchor='end', color=MUTED)
    cv.line(x0, yb, x1, yb, color=AXIS)
    slot = (x1 - x0) / 6
    bw = 36
    # легенда
    cv.rect(x0 + 8, 88 - 10 + 0, 12, 12, fill=BLUE, stroke='none', rx=2)
    cv.text(x0 + 26, 88, 'Будни', size=12)
    cv.rect(x0 + 90, 78, 12, 12, fill=AMBER, stroke='none', rx=2, opacity=0.8)
    cv.text(x0 + 108, 88, 'Выходные', size=12)
    for k, h in enumerate(hours):
        cx = x0 + slot * (k + 0.5)
        for dx, v, col, op in ((-bw / 2 - 1, a[k], BLUE, 1.0), (bw / 2 + 1, b[k], AMBER, 0.8)):
            hgt = (yb - yt) * v / vmax
            cv.rect(cx + dx - bw / 2, yb - hgt, bw, hgt, fill=col, stroke='none', rx=2, opacity=op)
            cv.text(cx + dx, yb - hgt - 5, fmt_price(v), size=11, anchor='middle')
        cv.text(cx, yb + 18, f'{h:02d}:00', size=12, anchor='middle', weight=600)
    cv.text((x0 + x1) / 2, yb + 38, 'Время открытия свечи 4H, UTC', size=12, anchor='middle', color=MUTED)
    cv.save('03-volume-by-slot.svg')

fig_anatomy(); fig_types(); fig_day(); fig_volume()
