import textwrap
from figlib import *

LIGHT = {BLUE: '#eff6ff', AMBER: '#fffbeb', GREEN: '#f0fdf4'}


def wrap_dots(s, n):
    parts, out, cur = s.split(' · '), [], ''
    for p in parts:
        t = p if not cur else cur + ' · ' + p
        if cur and len(t) > n:
            out.append(cur); cur = p
        else:
            cur = t
    out.append(cur)
    return out


def roadmap():
    cv = Canvas(760, 760, title='На следующий этап ведёт условие, а не дата',
                subtitle='Шесть этапов за 12 месяцев при 30–60 минутах в день')
    y0 = cv.y0
    X0, X1 = 40, 720
    px = lambda m: X0 + (X1 - X0) * m / 12
    stages = [(0, 0.7, BLUE), (0.7, 2.1, BLUE), (2.1, 2.8, BLUE), (2.8, 4.0, BLUE), (4.0, 10.0, AMBER), (10.0, 12.0, GREEN)]
    # легенда
    lx = 14
    for col, t in [(BLUE, 'учёба'), (AMBER, '100 сделок на демо'), (GREEN, 'реальный счёт')]:
        cv.rect(lx, y0 + 2, 14, 12, fill=col, stroke=col, rx=2)
        cv.text(lx + 20, y0 + 13, t, size=12, color=INK)
        lx += 20 + len(t) * 6.6 + 22
    # стрелка «дольше»
    ya = y0 + 50
    cv.arrow(px(10), ya, px(12) + 22, ya, color=AMBER, width=1.75, dash=True)
    cv.text(746, ya - 8, 'дольше, если сделок меньше 4 в неделю', size=12, anchor='end', color=AMBER)
    yb = y0 + 88
    for k, (a, b, col) in enumerate(stages):
        cv.rect(px(a), yb, px(b) - px(a), 22, fill=col, stroke='#ffffff', rx=0, sw=1.5, opacity=0.9)
        cv.text((px(a) + px(b)) / 2, yb - 6, str(k + 1), size=13, anchor='middle', weight=600, color=col)
    ya2 = yb + 22
    cv.line(X0, ya2, X1, ya2, color=AXIS, width=1.5)
    for m in range(13):
        cv.line(px(m), ya2, px(m), ya2 + 5, color=AXIS)
        if m < 12:
            cv.text(px(m + .5), ya2 + 19, str(m + 1), size=12, anchor='middle', color=MUTED)
    cv.text(X1, ya2 + 36, 'месяц', size=12, anchor='end', color=MUTED)

    # блоки
    bw, bh, gap, mx = 220, 186, 38, 12
    r1 = ya2 + 62
    r2 = r1 + bh + 52
    pos = [(mx + i * (bw + gap), r1) for i in range(3)] + [(mx + i * (bw + gap), r2) for i in range(3)]
    blocks = [
        ('1. Фундамент', 'недели 1–3 · главы 1–3 · ступень 01', 'Условие:', 'тест ступени на 80%+; практика выполнена'),
        ('2. Анализ графика', 'недели 4–9 · главы 4–9 · ступень 02', 'Условие:', 'тест на 80%+; бланк анализа 10 дней подряд'),
        ('3. Вход и риск', 'недели 10–12 · главы 10–12 · ступень 03', 'Условие:', 'тест на 80%+; 20 расчётов позиции без ошибки; 10 учебных сделок'),
        ('4. Система', 'недели 13–16 · главы 13–15 · ступени 04–06', 'Условие:', 'тест 04 на 80%+; практика 05; план и карточка сетапа; бэктест от 100 сделок, E > 0'),
        ('5. Сто сделок на демо', 'месяцы 5–10 · уровень профи 09', 'Условие:', 'тесты 01–05 на 80%+; 100 сделок по плану; 95% по правилам; итог 2 месяцев > 0; нет нарушений дневного лимита за месяц'),
        ('6. Первый реальный счёт', 'месяцы 11–12 · риск 0,5–1%, без плеча', 'Условие роста:', '100 сделок по тем же критериям → капитал ×1,5'),
    ]
    for (x, y), (name, sub, cl, ct), (_, _, col) in zip(pos, blocks, [stages[i] for i in range(6)]):
        # в блоке 4 цвет — как у отрезка этапа 4
        cv.rect(x, y, bw, bh, fill='#ffffff', stroke=col, rx=8, sw=2)
        cv.text(x + 12, y + 22, name, size=14, weight=600)
        sl = wrap_dots(sub, 30)
        for j, s in enumerate(sl):
            cv.text(x + 12, y + 41 + j * 16, s, size=12, color=MUTED)
        yd = y + 41 + len(sl) * 16 + 4
        cv.rect(x + 1, yd, bw - 2, y + bh - 1 - yd, fill=LIGHT[col], stroke='none', rx=0)
        cv.line(x + 1, yd, x + bw - 1, yd, color=col, width=1)
        cv.text(x + 12, yd + 18, cl, size=12, weight=600)
        # условие: перенос по «;»
        lines = []
        for part in ct.split('; '):
            seg = part + (';' if part != ct.split('; ')[-1] else '')
            lines += textwrap.wrap(seg, 28)
        yy = yd + 34
        for s in lines:
            cv.text(x + 12, yy, s, size=12)
            yy += 15
        assert yy - 15 < y + bh - 4, (name, yy, y + bh)
    # стрелки 1→2→3, 4→5→6
    for i in (0, 1):
        for r in (r1, r2):
            xa = mx + i * (bw + gap) + bw
            cv.arrow(xa + 2, r + 40, xa + gap - 2, r + 40, color=INK, width=1.75)
    # перенос 3→4
    x3 = pos[2][0] + bw / 2
    x4 = pos[3][0] + bw / 2
    ym = r1 + bh + 26
    cv.line(x3, r1 + bh, x3, ym, color=INK, width=1.75)
    cv.line(x3, ym, x4, ym, color=INK, width=1.75)
    cv.arrow(x4, ym, x4, r2 - 2, color=INK, width=1.75)
    # возврат 6→5
    x6 = pos[5][0] + bw / 2
    x5 = pos[4][0] + bw / 2
    yr = r2 + bh + 26
    cv.line(x6, r2 + bh, x6, yr, color=RED, width=1.75, dash=True)
    cv.line(x6, yr, x5, yr, color=RED, width=1.75, dash=True)
    cv.arrow(x5, yr, x5, r2 + bh + 2, color=RED, width=1.75, dash=True)
    cv.text((x5 + x6) / 2, yr + 18, 'правила нарушаются — назад на демо', size=12, anchor='middle', color=RED)
    cv.H = int(yr + 34)
    cv.save('15-roadmap.svg')


roadmap()
