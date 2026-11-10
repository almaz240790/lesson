from figlib import *


def rf(x, d=1):
    return f'{x:+.{d}f}'.replace('-', '−').replace('.', ',')


# ---------------------------------------------------- 14.1 журнал: правила против нарушений
rule_wins = [2.2] * 7 + [2.0] * 4 + [1.9]
assert len(rule_wins) == 12 and abs(sum(rule_wins) - 25.3) < 1e-9
rule_r = rule_wins + [-1.0] * 19
viol_r = [1.2, 1.2, 1.2, -1.5, -2.5, -1.2, -1.8, -1.6, -2.0]
assert abs(sum(rule_r) - 6.3) < 1e-9 and abs(sum(viol_r) - (-7.0)) < 1e-9
losses = [x for x in viol_r if x < 0]
assert abs(-sum(losses) / len(losses) - 1.77) < 0.005
# порядок: номера (1..40) сделок с нарушением
vpos = [4, 9, 13, 17, 22, 26, 30, 34, 38]
# распределяем выигрыши и проигрыши по правилам равномерно и детерминированно
import random
rnd = random.Random(14)
rl = rule_r[:]
rnd.shuffle(rl)
seq = []
ri = vi = 0
for n in range(1, 41):
    if n in vpos:
        seq.append(('v', viol_r[vi])); vi += 1
    else:
        seq.append(('r', rl[ri])); ri += 1
cr = cv_ = ct = 0.0
pr, pv, pt = [(0, 0)], [(0, 0)], [(0, 0)]
for n, (k, r) in enumerate(seq, 1):
    ct += r
    if k == 'r':
        cr += r
    else:
        cv_ += r
    pr.append((n, cr)); pv.append((n, cv_)); pt.append((n, ct))
assert abs(cr - 6.3) < 1e-9 and abs(cv_ + 7.0) < 1e-9 and abs(ct + 0.7) < 1e-9

W, H = 760, 400
c = Canvas(W, H, title='Сделки по правилам заработали +6,3R, девять нарушений забрали −7,0R',
           subtitle='Учебный журнал, 40 сделок на демосчёте, накопленный результат в R')
L, R_, T, B = 62, 700, c.y0 + 12, H - 70
ymin, ymax = -8, 8
X = lambda n: L + (R_ - L) * n / 40
Y = lambda v: T + (B - T) * (ymax - v) / (ymax - ymin)
for v in range(-8, 9, 4):
    c.line(L, Y(v), R_, Y(v), color=AXIS if v == 0 else GRID, width=1.5 if v == 0 else 1)
    c.text(L - 8, Y(v) + 4, rf(v, 0) if v else '0', size=11.5, anchor='end', color=MUTED)
for n in (1, 10, 20, 30, 40):
    c.text(X(n), B + 18, str(n), size=11.5, anchor='middle', color=MUTED)
c.text((L + R_) / 2, B + 38, 'Номер сделки в журнале', size=12, anchor='middle', color=MUTED)


def stepline(pts):
    out = []
    for k, (n, v) in enumerate(pts):
        if k:
            out.append((X(n), Y(pts[k - 1][1])))
        out.append((X(n), Y(v)))
    return out


c.polyline(stepline(pt), color=MUTED, width=1.75, dash=True)
c.polyline(stepline(pr), color=GREEN, width=2.5)
c.polyline(stepline(pv), color=RED, width=2.5)
for n in vpos:
    c.circle(X(n), Y(pv[n][1]), r=3.5, fill=RED)
c.text(R_ + 8, Y(cr) + 4, '+6,3R', size=12.5, color=GREEN, weight=700)
c.text(R_ + 8, Y(ct) + 16, '−0,7R', size=12.5, color=MUTED, weight=700)
c.text(R_ + 8, Y(cv_) + 4, '−7,0R', size=12.5, color=RED, weight=700)
# легенда под графиком
lx = L
for col, txt, d, w in [(GREEN, 'По правилам: 31 сделка', False, 190), (RED, 'С нарушением: 9 сделок (точки)', False, 235),
                       (MUTED, 'Весь журнал: 40 сделок', True, 200)]:
    c.line(lx, H - 12, lx + 26, H - 12, color=col, width=2.5, dash=d)
    c.text(lx + 34, H - 8, txt, size=12, color=INK)
    lx += w
c.save('14-rules-vs-violations.svg')

# ---------------------------------------------------- 14.4 петля тильта
c = Canvas(W, 400, title='Тильт замыкается в круг, пока чек-лист и лимиты не разорвут его',
           subtitle='Чек-лист не пропускает сделку вне плана, лимиты не дают убытку запустить следующий круг')
bw, bh = 200, 62
cx1, cx2 = 70, 490
ty = c.y0 + 28
by_ = ty + 190
boxes = {
    'a': (cx1, ty, ['Убыток', 'стоп по плану, −1R'], RED),
    'b': (cx2, ty, ['Желание вернуть', '«сейчас точно отобью»'], AMBER),
    'c': (cx2, by_, ['Сделка вне плана', 'размер больше, без чек-листа'], RED),
    'd': (cx1, by_, ['Убыток больше прежнего', '−2R, затем −4R'], RED),
}
for k, (x, y, ls, col) in boxes.items():
    c.rect(x, y, bw, bh, fill=col, stroke=col, opacity=0.10)
    c.rect(x, y, bw, bh, stroke=col, sw=1.5)
    c.text(x + bw / 2, y + 26, ls[0], size=13.5, anchor='middle', weight=700)
    c.text(x + bw / 2, y + 46, ls[1], size=11.5, anchor='middle', color=MUTED)
mx = (cx1 + bw + cx2) / 2
# a -> b
c.arrow(cx1 + bw + 2, ty + bh / 2, cx2 - 2, ty + bh / 2, color=INK, width=1.75)
# b -> c (стоп-кран 1: чек-лист)
c.arrow(cx2 + bw / 2, ty + bh + 2, cx2 + bw / 2, by_ - 2, color=INK, width=1.75)
# c -> d
c.arrow(cx2 - 2, by_ + bh / 2, cx1 + bw + 2, by_ + bh / 2, color=INK, width=1.75)
# d -> a (стоп-кран 2: лимиты)
c.arrow(cx1 + bw / 2, by_ - 2, cx1 + bw / 2, ty + bh + 2, color=INK, width=1.75)
# стоп-краны
sy1 = (ty + bh + by_) / 2
sx1 = cx2 + bw / 2
c.rect(sx1 - 6, sy1 - 14, 12, 28, fill=GREEN, stroke=GREEN, rx=3)
c.text(sx1 + 16, sy1 - 2, 'Стоп-кран 1: чек-лист', size=12.5, weight=700, color=GREEN)
c.text(sx1 + 16, sy1 + 15, 'нет галочек — нет сделки', size=11.5, color=MUTED)
sx2 = cx1 + bw / 2
c.rect(sx2 - 6, sy1 - 14, 12, 28, fill=GREEN, stroke=GREEN, rx=3)
c.text(sx2 + 16, sy1 - 2, 'Стоп-кран 2: лимиты', size=12.5, weight=700, color=GREEN)
c.text(sx2 + 16, sy1 + 15, '2 убытка подряд, −3% день, −6% неделя', size=11.5, color=MUTED)
c.text((cx1 + bw + cx2) / 2, ty + bh / 2 - 8, 'отыгрыш', size=12, anchor='middle', color=MUTED)
c.text((cx1 + bw + cx2) / 2, by_ + bh / 2 - 8, 'круг повторяется', size=12, anchor='middle', color=MUTED)
c.text(14, by_ + bh + 40, 'Без кранов день заканчивается −7R вместо −2R: лишние 5R равны 18 сделкам по плану при ожидании +0,28R.',
       size=12, color=MUTED)
c.save('14-tilt-loop.svg')
