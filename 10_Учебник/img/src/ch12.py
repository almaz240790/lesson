from figlib import *

# ---------------------------------------------------------------- 12.1 схема: близкий стоп и стоп с запасом
def fig1():
    path = [100, 112, 105, 108, 104, 110, 118]
    bars = [10, 8, 4, 5, 6, 11]
    cs = synth(path, bars, noise=0.15, seed=11)
    ends = []
    k = -1
    for b in bars:
        k += b
        ends.append(k)          # индексы свечей в точках излома
    i_low, i_ent, i_drop, i_end = ends[1], ends[2], ends[3], ends[5]
    # проверки
    assert 103.8 <= cs[i_drop]['l'] <= 104.6, cs[i_drop]['l']
    assert min(c['l'] for c in cs[i_ent:]) > 103.5
    i_hit = next(i for i in range(i_ent + 1, i_drop + 1) if cs[i]['l'] <= 106.5)
    assert min(c['l'] for c in cs[i_ent + 1:i_hit]) > 106.5 - 3
    ch = Chart(cs, title='Близкий стоп выбит обычным колебанием, стоп за структурой с запасом остался на месте',
               schematic=True, main_h=320, ymin=98, ymax=122, extra_bars=6)
    ch.hline(105, i_low, i_end + 6, color=AXIS, dash=True, width=1)
    ch.mark(i_low, cs[i_low]['l'], 'минимум отката 105', where='below', color=MUTED)
    ch.mark(i_ent, 108, 'вход', where='above')
    ch.hline(106.5, i_ent, i_hit + 3, color=RED, dash=True)
    ch.mark(i_hit, 106.5, '', where='above', color=RED)
    ch.text(i_hit + 1.5, 107.6, 'выбит: −1R', size=12, color=RED, weight=600)
    ch.text(i_ent + 1, 112.5, 'близкий стоп 106,5: внутри шума', size=11.5, color=RED, weight=600)
    ch.arrow((i_hit + 1, 112), (i_hit + 1, 108.8), RED, 1)
    ch.hline(103.5, i_ent, i_end + 6, color=RED, dash=False)
    ch.text(i_end + 5, 102.3, 'стоп = минимум − 0,5 × ATR', anchor='end', size=11.5, color=RED, weight=600)
    ch.hline(117, i_ent, i_end + 6, color=GREEN, dash=False, label='цель 2R для стопа с запасом', label_at='left')
    xb = i_end - 6
    ch.arrow((xb, 104.2), (xb, 105), INK, 1.25)
    ch.arrow((xb, 104.3), (xb, 103.5), INK, 1.25)
    ch.text(xb + 1, 104.5, 'запас 0,5 × ATR', size=11.5, weight=600)
    ch.mark(i_end, 117, '', where='above', color=GREEN)
    ch.text(i_end + 6, 118.4, 'цель: +2R', anchor='end', size=12, color=GREEN, weight=600)
    ch.save('12-stop-close-vs-structure.svg')

# ---------------------------------------------------------------- 12.2 схема: половина на 2R, безубыток, трейлинг
def fig2():
    path = [98, 100, 105, 103, 110, 107, 120, 115, 123, 112]
    bars = [8, 8, 4, 10, 6, 10, 6, 8, 10]
    cs = synth(path, bars, noise=0.15, seed=5)
    ends = []
    k = -1
    for b in bars:
        k += b
        ends.append(k)
    e_in, e_dip, e_half, e_hl1, e_top1, e_hl2, e_top2 = ends[0], ends[2], ends[3], ends[4], ends[5], ends[6], ends[7]
    # стартовые индексы ступеней
    s1, s2, s3 = e_half, e_hl1 + 3, ends[6] + 3
    i_exit = next(i for i in range(ends[7] + 1, len(cs)) if cs[i]['l'] <= 114)
    assert min(c['l'] for c in cs[e_in + 1:e_half]) > 95
    assert min(c['l'] for c in cs[s1 + 1:s2]) > 100
    assert min(c['l'] for c in cs[s2:s3]) > 106 and min(c['l'] for c in cs[s3:i_exit]) > 114, (min(c['l'] for c in cs[s3:i_exit]))
    ch = Chart(cs, title='Половина закрыта на 2R, стоп остатка — на вход, затем под новыми минимумами',
               schematic=True, main_h=320, extra_bars=16, ymin=92, ymax=127)
    ch.hline(100, e_in, len(cs) - 1, color=AXIS, dash=False, width=1)
    ch.mark(e_in, 100, 'вход 100', where='below')
    stops = [(95, e_in, s1, 'стоп 95 (−1R)'), (100, s1, s2, 'безубыток: стоп на входе'),
             (106, s2, s3, 'стоп под HL: 106'), (114, s3, i_exit, 'стоп под HL: 114')]
    for p, a, b, lab in stops:
        ch.hline(p, a, b, color=RED, dash=True)
        ch.text(a + 1, p - 1.8, lab, size=11.5, color=RED, weight=600)
    ch.hline(110, e_in, e_half, color=GREEN, dash=False, label='цель 1: 110 (+2R)', label_at='left')
    ch.mark(e_half, 110, 'половина закрыта: +2R', where='above', color=GREEN)
    ch.mark(e_hl1, cs[e_hl1]['l'], 'HL', where='below', color=MUTED)
    ch.mark(e_hl2, cs[e_hl2]['l'], 'HL', where='below', color=MUTED)
    ch.mark(i_exit, 114, 'остаток закрыт: +2,8R', where='right', color=GREEN)
    ch.text(len(cs) + 15, 94.5, 'Итог: 0,5 × 2R + 0,5 × 2,8R = +2,4R', anchor='end', size=13, weight=600)
    ch.save('12-partial-breakeven.svg')

# ---------------------------------------------------------------- 12.3 реальный график
def fig3():
    full = load('btc', '4h')
    e50 = ema([c['c'] for c in full], 50)
    a, b = find(full, '2025-05-03 04:00'), find(full, '2025-05-13 20:00')
    cs = full[a:b + 1]
    assert len(cs) == 65, len(cs)
    X = lambda d: find(full, d) - a
    i0, i_t, i_x = X('2025-05-06 20:00'), X('2025-05-08 00:00'), X('2025-05-12 12:00')
    assert abs(full[a + i0]['o'] - 94963.5) < 1, full[a + i0]['o']
    ch = Chart(cs, title='Стоп поднимается ступенями под каждый новый минимум и закрывает сделку на +3,67R',
               subtitle='BTC/USDT, 4H, 3–13 мая 2025', main_h=340)
    ch.series(e50[a:b + 1], BLUE, 'EMA 50')
    # линия входа с разрывом под меткой HL 7 мая, чтобы подпись не лежала на линии
    ch.hline(94964, i0, X('2025-05-07 08:00'), color=MUTED, dash=False, width=1, tag=False)
    ch.hline(94964, X('2025-05-08 00:00'), i_x, color=MUTED, dash=False, width=1, tag=False)
    ch.mark(i0, 94963.5, '', where='above', color=INK)
    ch.text(i0 - 1, 96900, 'вход 94 964', anchor='end', size=12, weight=600)
    ch.arrow((i0 - 2, 96500), (i0 - 0.3, 95250), INK, 1)
    ch.hline(99025, i0, i_t, color=GREEN, dash=False, tag=False)
    ch.text(i0 + 1, 99025 + 350, '2R = 99 025', size=11.5, color=GREEN, weight=600)
    ch.mark(i_t, 99025, '2R: А закрыт, Б — половина', where='left', color=GREEN)
    levels = [(92933, '2025-05-06 20:00', '2025-05-08 08:00'), (95255, '2025-05-08 08:00', '2025-05-10 08:00'),
              (101726, '2025-05-10 08:00', '2025-05-11 08:00'), (102427, '2025-05-11 08:00', '2025-05-12 12:00')]
    for p, s, e in levels:
        ch.hline(p, X(s), X(e), color=RED, dash=True, tag=False)
    ch.text(i0 + 1, 92933 - 700, '92 933', size=11.5, color=RED, weight=600)
    ch.text(X('2025-05-08 08:00') + 1, 95255 - 700, '95 255', size=11.5, color=RED, weight=600)
    ch.text(X('2025-05-10 08:00') - 1, 101726 - 700, '101 726', size=11.5, color=RED, weight=600, anchor='end')
    ch.text(X('2025-05-11 08:00') + 1, 102427 - 1100, '102 427', size=11.5, color=RED, weight=600)
    for d in ('2025-05-07 16:00', '2025-05-09 16:00', '2025-05-10 16:00'):
        j = X(d)
        ch.mark(j, cs[j]['l'], 'HL', where='below', color=MUTED)
    ch.mark(i_x, 102427, '', where='above', color=RED)
    ch.text(i_x + 2, 99000, 'выход +3,67R', anchor='end', size=12, color=RED, weight=600)
    ch.arrow((i_x, 99300), (i_x, 102100), RED, 1)
    jm = X('2025-05-12 04:00')
    ch.mark(jm, cs[jm]['h'], 'максимум 105 819 (+5,35R)', where='above', color=INK)
    ch.save('12-trail-structure-real.svg')

# ---------------------------------------------------------------- 12.4 столбики
def fig4():
    groups = [(['30 последних входов', '(ноябрь 2024 — октябрь 2026)'], [-4.87, -1.61, 6.32]),
              (['те же 30 без лучшей сделки', '(вход 5 ноября 2024)'], [-6.82, -6.67, -1.84]),
              (['все 104 входа', '(2020 — октябрь 2026)'], [4.51, 15.03, 12.00])]
    cols = [MUTED, BLUE, ORANGE]
    names = ['А — вся позиция на 2R', 'Б — половина на 2R, остаток по структуре', 'В — только трейлинг по структуре']
    W, H = 760, 520
    cv = Canvas(W, H, title='Лучший способ сопровождения меняется от выборки к выборке',
                subtitle='BTC/USDT, 4H, лонг по правилу раздела 12.8; итог в R с комиссией 0,1% + 0,1%')
    # легенда
    lx, ly = 14, cv.y0 + 4
    for c, n in zip(cols, names):
        cv.rect(lx, ly, 14, 14, fill=c, stroke='none', rx=2)
        cv.text(lx + 20, ly + 12, n, size=12, color=INK)
        lx += 20 + 6.6 * len(n) + 22
    top, bot = ly + 48, 420          # пиксели для +16 и -8
    left, right = 52, W - 14
    Y = lambda v: top + (16 - v) / 24 * (bot - top)
    for v in range(-8, 17, 4):
        cv.line(left, Y(v), right, Y(v), color=GRID, width=1)
        cv.text(left - 8, Y(v) + 4, ('+' if v > 0 else '−' if v < 0 else '') + str(abs(v)), size=11, anchor='end', color=MUTED)
    cv.text(left - 8, top - 14, 'R', size=11, anchor='end', color=MUTED)
    cv.line(left, Y(0), right, Y(0), color=INK, width=2)
    gw = (right - left) / 3
    bw, gap = 52, 10
    for g, (lab, vals) in enumerate(groups):
        gx = left + g * gw + gw / 2 - (3 * bw + 2 * gap) / 2
        for k, v in enumerate(vals):
            x = gx + k * (bw + gap)
            y0, y1 = Y(0), Y(v)
            cv.rect(x, min(y0, y1), bw, abs(y1 - y0), fill=cols[k], stroke='none', rx=0)
            s = ('+' if v > 0 else '−') + f'{abs(v):.2f}'.replace('.', ',') + 'R'
            if v >= 0:
                cv.text(x + bw / 2, y1 - 6, s, size=12, anchor='middle', weight=600)
            else:
                cv.text(x + bw / 2, y1 + 15, s, size=12, anchor='middle', weight=600)
        cx = left + g * gw + gw / 2
        cv.text(cx, bot + 22, lab[0], size=12.5, anchor='middle', weight=600)
        cv.text(cx, bot + 40, lab[1], size=11.5, anchor='middle', color=MUTED)
    cv.save('12-management-compare.svg')

fig1(); fig2(); fig3(); fig4()
