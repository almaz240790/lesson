"""figlib — рисунки для учебника: свечные графики и схемы в SVG, без внешних библиотек.

Два класса:
  Chart  — свечной график (реальные свечи из app/public/charts или синтетические) с разметкой;
  Canvas — свободная схема (блоки, стрелки, крупные свечи).

Минимальный пример:
    from figlib import *
    c = load('btc', '1d', '2023-01-01', '2023-04-01')
    ch = Chart(c, title='BTC/USDT, 1D', subtitle='январь — март 2023')
    ch.zone(21400, 22300, kind='support', label='Поддержка')
    ch.save('04-example.svg')

Координаты Chart: x — номер свечи (0 — первая, можно дробный), y — цена.
Координаты Canvas: пиксели, начало слева сверху.
"""
from __future__ import annotations

import datetime as _dt
import json
import math
import os
import random
from html import escape as _esc

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(_HERE, '..', '..', '..'))
DATA_DIR = os.path.join(REPO, 'app', 'public', 'charts')
IMG_DIR = os.path.abspath(os.path.join(_HERE, '..'))

UP, DOWN = '#26a69a', '#ef5350'
INK, MUTED, GRID, AXIS = '#1f2937', '#6b7280', '#e5e7eb', '#9ca3af'
BLUE, ORANGE, PURPLE, GREEN, RED, AMBER = '#2563eb', '#ea580c', '#7c3aed', '#15803d', '#b91c1c', '#b45309'
FONT = "system-ui,-apple-system,'Segoe UI',Roboto,'Helvetica Neue',Arial,'DejaVu Sans',sans-serif"
ZONE = {
    'support': ('#16a34a', GREEN),
    'resistance': ('#dc2626', RED),
    'neutral': ('#2563eb', BLUE),
    'warn': ('#f59e0b', AMBER),
}


# ----------------------------------------------------------------------------- данные и индикаторы

def load(symbol, interval, start=None, end=None):
    """Свечи из app/public/charts. symbol: 'btc' | 'eth'; interval: '1d' | '4h'.
    start, end — 'YYYY-MM-DD' или 'YYYY-MM-DD HH:MM' (UTC), обе границы включительно; None — без границы.
    Возвращает список словарей {t, o, h, l, c, v, date}."""
    path = os.path.join(DATA_DIR, f'{symbol.lower()}_{interval.lower()}.json')
    with open(path, encoding='utf-8') as f:
        raw = json.load(f)['candles']

    def ts(s):
        if s is None:
            return None
        fmt = '%Y-%m-%d %H:%M' if ' ' in s else '%Y-%m-%d'
        return int(_dt.datetime.strptime(s, fmt).replace(tzinfo=_dt.timezone.utc).timestamp())

    a, b = ts(start), ts(end)
    daily = interval.lower() == '1d'
    out = []
    for t, o, h, l, c, v in raw:
        if a is not None and t < a:
            continue
        if b is not None and t > b:
            continue
        d = _dt.datetime.fromtimestamp(t, _dt.timezone.utc)
        out.append({'t': t, 'o': o, 'h': h, 'l': l, 'c': c, 'v': v,
                    'date': d.strftime('%Y-%m-%d' if daily else '%Y-%m-%d %H:%M')})
    return out


def find(candles, date):
    """Индекс первой свечи с датой >= date ('YYYY-MM-DD' или 'YYYY-MM-DD HH:MM')."""
    for i, c in enumerate(candles):
        if c['date'] >= date:
            return i
    raise ValueError(f'нет свечи с датой >= {date}')


def sma(values, n):
    out = [None] * len(values)
    s = 0.0
    for i, v in enumerate(values):
        s += v
        if i >= n:
            s -= values[i - n]
        if i >= n - 1:
            out[i] = s / n
    return out


def ema(values, n):
    """EMA с затравкой SMA по первым n значениям. Первые n-1 значений — None."""
    out = [None] * len(values)
    if len(values) < n:
        return out
    k = 2 / (n + 1)
    s = sum(values[:n]) / n
    out[n - 1] = s
    for i in range(n, len(values)):
        s = values[i] * k + s * (1 - k)
        out[i] = s
    return out


def rsi(closes, n=14):
    """RSI по Уайлдеру."""
    out = [None] * len(closes)
    if len(closes) <= n:
        return out
    g = l = 0.0
    for i in range(1, n + 1):
        d = closes[i] - closes[i - 1]
        g += max(d, 0)
        l += max(-d, 0)
    ag, al = g / n, l / n
    out[n] = 100.0 if al == 0 else 100 - 100 / (1 + ag / al)
    for i in range(n + 1, len(closes)):
        d = closes[i] - closes[i - 1]
        ag = (ag * (n - 1) + max(d, 0)) / n
        al = (al * (n - 1) + max(-d, 0)) / n
        out[i] = 100.0 if al == 0 else 100 - 100 / (1 + ag / al)
    return out


def true_range(candles):
    tr = []
    for i, c in enumerate(candles):
        if i == 0:
            tr.append(c['h'] - c['l'])
        else:
            pc = candles[i - 1]['c']
            tr.append(max(c['h'] - c['l'], abs(c['h'] - pc), abs(c['l'] - pc)))
    return tr


def atr(candles, n=14):
    """ATR по Уайлдеру. Первое значение — на свече с индексом n."""
    tr = true_range(candles)
    out = [None] * len(candles)
    if len(candles) <= n:
        return out
    a = sum(tr[1:n + 1]) / n
    out[n] = a
    for i in range(n + 1, len(candles)):
        a = (a * (n - 1) + tr[i]) / n
        out[i] = a
    return out


def macd(closes, fast=12, slow=26, signal=9):
    """Возвращает (линия MACD, сигнальная, гистограмма)."""
    ef, es = ema(closes, fast), ema(closes, slow)
    line = [None if a is None or b is None else a - b for a, b in zip(ef, es)]
    first = next((i for i, v in enumerate(line) if v is not None), len(line))
    sig_tail = ema(line[first:], signal) if first < len(line) else []
    sig = [None] * first + sig_tail
    hist = [None if a is None or b is None else a - b for a, b in zip(line, sig)]
    return line, sig, hist


def swings(candles, k=3):
    """Значимые экстремумы: максимум (минимум) выше (ниже) k свечей слева и k справа.
    Возвращает список {i, kind: 'H' | 'L', price} по порядку."""
    out = []
    for i in range(k, len(candles) - k):
        hi, lo = candles[i]['h'], candles[i]['l']
        rng = [j for j in range(i - k, i + k + 1) if j != i]
        if all(hi > candles[j]['h'] for j in rng):
            out.append({'i': i, 'kind': 'H', 'price': hi})
        if all(lo < candles[j]['l'] for j in rng):
            out.append({'i': i, 'kind': 'L', 'price': lo})
    return out


def synth(path, bars_per_leg=6, noise=0.3, seed=7):
    """Синтетические свечи для схем: цена идёт по ломаной path (список цен в точках разворота).
    bars_per_leg — число свечей на отрезок (число или список по отрезкам). Результат детерминирован."""
    rnd = random.Random(seed)
    legs = list(zip(path[:-1], path[1:]))
    bpl = list(bars_per_leg) if isinstance(bars_per_leg, (list, tuple)) else [bars_per_leg] * len(legs)
    span = (max(path) - min(path)) or 1.0
    eps = span * 0.006
    out = []
    price = path[0]
    for (a, b), n in zip(legs, bpl):
        step = (b - a) / n
        for j in range(n):
            o = price
            last = j == n - 1
            c = a + step * (j + 1) + (0 if last else rnd.uniform(-1, 1) * abs(step) * noise)
            wick = abs(step) * (0.2 + 0.5 * rnd.random()) + eps
            h = max(o, c) + wick * rnd.random()
            l = min(o, c) - wick * rnd.random()
            hi_cap, lo_cap = max(a, b) + eps, min(a, b) - eps
            if last:
                if b > a:
                    h, hi_cap = b + eps, b + eps
                else:
                    l, lo_cap = b - eps, b - eps
            h = max(min(h, hi_cap), o, c)
            l = min(max(l, lo_cap), o, c)
            out.append({'o': o, 'h': h, 'l': l, 'c': c, 'v': 0})
            price = c
    return out


def fmt_price(p, digits=None):
    """Цена по-русски: пробел между тысячами, запятая в дробной части."""
    a = abs(p)
    if digits is None:
        digits = 0 if a >= 1000 else 1 if a >= 100 else 2 if a >= 1 else 4
    return f'{p:,.{digits}f}'.replace(',', ' ').replace('.', ',')


def _nice_ticks(lo, hi, n=5):
    span = hi - lo
    if span <= 0:
        return [lo]
    raw = span / n
    mag = 10 ** math.floor(math.log10(raw))
    step = 10 * mag
    for m in (1, 2, 2.5, 5, 10):
        if raw <= m * mag:
            step = m * mag
            break
    x = math.ceil(lo / step) * step
    out = []
    while x <= hi + 1e-9:
        out.append(round(x, 10))
        x += step
    return out


# ----------------------------------------------------------------------------- SVG

class _Svg:
    LAYERS = ('zones', 'grid', 'candles', 'lines', 'labels')

    def __init__(self):
        self.layers = {k: [] for k in self.LAYERS}
        self.markers = {}

    def add(self, layer, s):
        self.layers[layer].append(s)

    def marker(self, color):
        if color not in self.markers:
            self.markers[color] = f'arr{len(self.markers)}'
        return self.markers[color]

    def text(self, x, y, s, size=12, anchor='start', color=INK, weight=400, halo=True, layer='labels'):
        a = f'x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{color}"'
        if weight != 400:
            a += f' font-weight="{weight}"'
        if halo:
            a += ' stroke="#ffffff" stroke-width="3" paint-order="stroke" stroke-linejoin="round"'
        self.add(layer, f'<text {a}>{_esc(str(s))}</text>')

    def line(self, x1, y1, x2, y2, color=AXIS, width=1.25, dash=False, arrow=False, layer='lines'):
        a = f'x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{width}"'
        if dash:
            a += ' stroke-dasharray="5 4"'
        if arrow:
            a += f' marker-end="url(#{self.marker(color)})"'
        self.add(layer, f'<line {a}/>')

    def polyline(self, pts, color=BLUE, width=1.5, dash=False, fill='none', opacity=1.0, layer='lines'):
        p = ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts)
        a = f'points="{p}" fill="{fill}" stroke="{color}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"'
        if dash:
            a += ' stroke-dasharray="5 4"'
        if opacity != 1.0:
            a += f' fill-opacity="{opacity}"'
        self.add(layer, f'<polyline {a}/>')

    def rect(self, x, y, w, h, fill='none', stroke='none', rx=0, sw=1.25, opacity=1.0, layer='zones'):
        a = f'x="{x:.1f}" y="{y:.1f}" width="{max(w, 0):.1f}" height="{max(h, 0):.1f}" fill="{fill}" stroke="{stroke}"'
        if rx:
            a += f' rx="{rx}"'
        if stroke != 'none':
            a += f' stroke-width="{sw}"'
        if opacity != 1.0:
            a += f' fill-opacity="{opacity}"'
        self.add(layer, f'<rect {a}/>')

    def circle(self, x, y, r, fill=INK, stroke='#ffffff', sw=1.5, layer='labels'):
        self.add(layer, f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def render(self, w, h, label):
        defs = ''.join(
            f'<marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0 0L10 5L0 10z" fill="{color}"/></marker>'
            for color, mid in self.markers.items())
        body = '\n'.join(s for k in self.LAYERS for s in self.layers[k])
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
                f'font-family="{FONT}" role="img" aria-label="{_esc(label, quote=True)}">\n'
                f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
                + (f'<defs>{defs}</defs>\n' if defs else '') + body + '\n</svg>\n')


def _out_path(path):
    if not os.path.isabs(path):
        path = os.path.join(IMG_DIR, path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


# ----------------------------------------------------------------------------- Chart

class _Panel:
    def __init__(self, chart, values, label, height, ymin, ymax, hlines, color, kind):
        self.chart, self.label, self.height, self.kind = chart, label, height, kind
        self.ymin, self.ymax, self.hlines = ymin, ymax, list(hlines)
        self.items = [(values, color, None)]
        self.marks = []

    def series(self, values, color=ORANGE, label=None):
        """Вторая линия в той же панели (например, сигнальная линия MACD)."""
        self.items.append((values, color, label))
        return self

    def mark(self, i, value, text, where='above', color=INK):
        self.marks.append((i, value, text, where, color))
        return self

    def line(self, p0, p1, color=INK, dash=False):
        """Отрезок между точками (i, значение), например линия дивергенции."""
        self.marks.append(('line', p0, p1, color, dash))
        return self


class Chart:
    """Свечной график с разметкой.

    candles — список свечей ({o,h,l,c[,v,t]}) из load() или synth().
    schematic=True — схема: без шкалы цен и дат.
    extra_bars — пустое место справа (в свечах) для подписей и «будущего».
    main_h — высота панели цены в пикселях."""

    def __init__(self, candles, *, title='', subtitle='', width=760, main_h=300, schematic=False,
                 extra_bars=0, ymin=None, ymax=None, pad=0.08):
        self.c = list(candles)
        self.n = len(self.c) + extra_bars
        self.title, self.subtitle, self.W, self.main_h = title, subtitle, width, main_h
        self.schematic, self.pad = schematic, pad
        self._ymin, self._ymax = ymin, ymax
        self._yvals = [v for c in self.c for v in (c['h'], c['l'])]
        self.ops, self.legend, self.panels = [], [], []
        self._volume = None

    # --- разметка на панели цены -------------------------------------------------
    def zone(self, lo, hi, x0=None, x1=None, kind='support', label=None, label_at='left'):
        """Горизонтальная зона между ценами lo и hi. kind: support | resistance | neutral | warn."""
        self._yvals += [lo, hi]
        self.ops.append(('zone', lo, hi, x0, x1, kind, label, label_at))
        return self

    def hline(self, price, x0=None, x1=None, color=MUTED, dash=True, label=None, label_at='left', width=1.25, tag=True):
        """Горизонтальная линия на цене. label — подпись над линией; tag — ценник на шкале справа."""
        self._yvals.append(price)
        self.ops.append(('hline', price, x0, x1, color, dash, label, label_at, width, tag))
        return self

    def vline(self, i, color=MUTED, dash=True, label=None):
        self.ops.append(('vline', i, color, dash, label))
        return self

    def line(self, points, color=BLUE, width=1.75, dash=False):
        """Ломаная по точкам [(i, цена), ...] — трендовая линия, канал, схема движения."""
        self._yvals += [p for _, p in points]
        self.ops.append(('line', points, color, width, dash))
        return self

    def arrow(self, p0, p1, color=INK, width=1.5, dash=False):
        """Стрелка из (i, цена) в (i, цена)."""
        self._yvals += [p0[1], p1[1]]
        self.ops.append(('arrow', p0, p1, color, width, dash))
        return self

    def series(self, values, color=BLUE, label=None, width=1.5, dash=False):
        """Линия индикатора поверх цены (EMA и т.п.). values выровнены по свечам, None пропускаются."""
        self.ops.append(('series', values, color, width, dash))
        if label:
            self.legend.append((color, label))
        return self

    def mark(self, i, price, text, where='above', color=INK, dot=True, size=12, weight=600):
        """Точка с подписью над или под ней. where: above | below | left | right."""
        self._yvals.append(price)
        self.ops.append(('mark', i, price, text, where, color, dot, size, weight))
        return self

    def text(self, i, price, s, anchor='start', size=12, color=INK, weight=400):
        self._yvals.append(price)
        self.ops.append(('text', i, price, s, anchor, size, color, weight))
        return self

    def trade(self, i_entry, entry, stop, target, i_end=None, labels=('Вход', 'Стоп', 'Цель'), show_rr=True, prices=True):
        """Сделка: линии входа, стопа и цели, зоны риска и прибыли от свечи i_entry до i_end."""
        self._yvals += [entry, stop, target]
        self.ops.append(('trade', i_entry, entry, stop, target, i_end, labels, show_rr, prices))
        return self

    def highlight(self, i0, i1, color='#2563eb', label=None):
        """Вертикальная подсветка свечей с i0 по i1 включительно."""
        self.ops.append(('highlight', i0, i1, color, label))
        return self

    # --- нижние панели -----------------------------------------------------------
    def volume(self, height=58, label='Объём'):
        self._volume = (height, label)
        return self

    def panel(self, values, *, label='', height=84, ymin=None, ymax=None, hlines=(), color=BLUE, kind='line'):
        """Нижняя панель (RSI, MACD, ATR). kind: line | bars. hlines — уровни, например (30, 70).
        Возвращает панель: .series(values, color, label), .mark(i, value, text), .line((i, v), (i, v))."""
        p = _Panel(self, values, label, height, ymin, ymax, hlines, color, kind)
        self.panels.append(p)
        return p

    # --- вывод ---------------------------------------------------------------------
    def save(self, path):
        svg = _Svg()
        W = self.W
        left = 14
        right = 20 if self.schematic else 74
        y = 12
        if self.title:
            svg.text(left, y + 17, self.title, size=15, weight=600, halo=False)
            y += 26
        if self.subtitle:
            svg.text(left, y + 12, self.subtitle, size=12, color=MUTED, halo=False)
            y += 20
        if self.legend:
            lx = left
            for color, label in self.legend:
                svg.line(lx, y + 9, lx + 18, y + 9, color=color, width=2, layer='labels')
                svg.text(lx + 23, y + 13, label, size=11.5, color=MUTED, halo=False)
                lx += 23 + 6.6 * len(label) + 18
            y += 22
        top = y + 6
        H0 = self.main_h
        lo = min(self._yvals) if self._ymin is None else self._ymin
        hi = max(self._yvals) if self._ymax is None else self._ymax
        if self._ymin is None:
            lo -= (hi - lo) * self.pad
        if self._ymax is None:
            hi += (hi - lo) * self.pad
        pw = W - left - right
        bw = pw / max(self.n, 1)
        X = lambda i: left + (i + 0.5) * bw
        Y = lambda p: top + (hi - p) / (hi - lo) * H0
        x_lo, x_hi = left, left + pw

        # сетка и шкала цен
        svg.rect(left, top, pw, H0, fill='none', stroke=GRID, sw=1, layer='grid')
        if not self.schematic:
            for t in _nice_ticks(lo, hi, 5):
                yy = Y(t)
                if top + 6 < yy < top + H0 - 6:
                    svg.line(left, yy, x_hi, yy, color=GRID, width=1, layer='grid')
                    svg.text(x_hi + 6, yy + 4, fmt_price(t), size=11, color=MUTED, halo=False, layer='grid')

        # свечи
        body = max(1.0, bw * 0.62)
        for i, c in enumerate(self.c):
            col = UP if c['c'] >= c['o'] else DOWN
            x = X(i)
            svg.line(x, Y(c['h']), x, Y(c['l']), color=col, width=1, layer='candles')
            y0, y1 = Y(max(c['o'], c['c'])), Y(min(c['o'], c['c']))
            svg.rect(x - body / 2, y0, body, max(y1 - y0, 1), fill=col, layer='candles')

        tags = []
        for op in self.ops:
            k = op[0]
            if k == 'zone':
                _, zlo, zhi, x0, x1, kind, label, label_at = op
                fill, ink = ZONE[kind]
                xa = x_lo if x0 is None else X(x0) - bw / 2
                xb = x_hi if x1 is None else X(x1) + bw / 2
                svg.rect(xa, Y(zhi), xb - xa, Y(zlo) - Y(zhi), fill=fill, opacity=0.16)
                svg.line(xa, Y(zhi), xb, Y(zhi), color=fill, width=1, layer='zones')
                svg.line(xa, Y(zlo), xb, Y(zlo), color=fill, width=1, layer='zones')
                if label:
                    if label_at == 'right':
                        svg.text(xb - 6, Y(zhi) - 5, label, size=11.5, color=ink, weight=600, anchor='end')
                    else:
                        svg.text(xa + 6, Y(zhi) - 5, label, size=11.5, color=ink, weight=600)
            elif k == 'hline':
                _, price, x0, x1, color, dash, label, label_at, width, tag = op
                xa = x_lo if x0 is None else X(x0) - bw / 2
                xb = x_hi if x1 is None else X(x1) + bw / 2
                svg.line(xa, Y(price), xb, Y(price), color=color, width=width, dash=dash)
                if label:
                    if label_at == 'right':
                        svg.text(xb - 6, Y(price) - 5, label, size=11.5, color=color, weight=600, anchor='end')
                    else:
                        svg.text(xa + 6, Y(price) - 5, label, size=11.5, color=color, weight=600)
                if tag and not self.schematic:
                    tags.append((Y(price), fmt_price(price), color))
            elif k == 'vline':
                _, i, color, dash, label = op
                svg.line(X(i), top, X(i), top + H0, color=color, width=1.25, dash=dash)
                if label:
                    svg.text(X(i) + 5, top + 14, label, size=11.5, color=color, weight=600)
            elif k == 'line':
                _, pts, color, width, dash = op
                svg.polyline([(X(i), Y(p)) for i, p in pts], color=color, width=width, dash=dash)
            elif k == 'arrow':
                _, p0, p1, color, width, dash = op
                svg.line(X(p0[0]), Y(p0[1]), X(p1[0]), Y(p1[1]), color=color, width=width, dash=dash, arrow=True)
            elif k == 'series':
                _, values, color, width, dash = op
                seg = []
                for i, v in enumerate(values[:len(self.c)]):
                    if v is None or not (lo <= v <= hi):
                        if len(seg) > 1:
                            svg.polyline(seg, color=color, width=width, dash=dash)
                        seg = []
                    else:
                        seg.append((X(i), Y(v)))
                if len(seg) > 1:
                    svg.polyline(seg, color=color, width=width, dash=dash)
            elif k == 'mark':
                _, i, price, text, where, color, dot, size, weight = op
                x, yy = X(i), Y(price)
                if dot:
                    svg.circle(x, yy, 3.2, fill=color)
                if where == 'above':
                    svg.text(x, yy - 9, text, size=size, anchor='middle', color=color, weight=weight)
                elif where == 'below':
                    svg.text(x, yy + 9 + size * 0.8, text, size=size, anchor='middle', color=color, weight=weight)
                elif where == 'left':
                    svg.text(x - 8, yy + size * 0.35, text, size=size, anchor='end', color=color, weight=weight)
                else:
                    svg.text(x + 8, yy + size * 0.35, text, size=size, anchor='start', color=color, weight=weight)
            elif k == 'text':
                _, i, price, s, anchor, size, color, weight = op
                svg.text(X(i), Y(price), s, size=size, anchor=anchor, color=color, weight=weight)
            elif k == 'trade':
                _, ie, entry, stop, target, i_end, labels, show_rr, prices = op
                xa = X(ie) - bw / 2
                xb = x_hi if i_end is None else X(i_end) + bw / 2
                svg.rect(xa, min(Y(entry), Y(stop)), xb - xa, abs(Y(entry) - Y(stop)), fill='#dc2626', opacity=0.13)
                svg.rect(xa, min(Y(entry), Y(target)), xb - xa, abs(Y(entry) - Y(target)), fill='#16a34a', opacity=0.13)
                for price, name, color in ((entry, labels[0], BLUE), (stop, labels[1], RED), (target, labels[2], GREEN)):
                    svg.line(xa, Y(price), xb, Y(price), color=color, width=1.5)
                    cap = f'{name} {fmt_price(price)}' if prices and not self.schematic else name
                    svg.text(xb - 6, Y(price) - 5, cap, size=11.5, color=color, weight=600, anchor='end')
                    if not self.schematic:
                        tags.append((Y(price), fmt_price(price), color))
                if show_rr and entry != stop:
                    rr = abs(target - entry) / abs(entry - stop)
                    svg.text(xa + 6, (Y(entry) + Y(target)) / 2 + 4, 'R:R 1:' + f'{rr:.1f}'.replace('.', ','), size=11.5, color=GREEN, weight=600)
            elif k == 'highlight':
                _, i0, i1, color, label = op
                xa, xb = X(i0) - bw / 2, X(i1) + bw / 2
                svg.rect(xa, top, xb - xa, H0, fill=color, opacity=0.09)
                if label:
                    svg.text((xa + xb) / 2, top + 14, label, size=11.5, color=color, weight=600, anchor='middle')

        for yy, s, color in tags:
            w = 7 + 6.4 * len(s)
            svg.rect(x_hi + 2, yy - 9, w, 18, fill=color, rx=3, layer='labels')
            svg.text(x_hi + 6, yy + 4, s, size=11, color='#ffffff', weight=600, halo=False)

        y = top + H0

        def frame(h, label):
            nonlocal y
            y += 12
            ptop = y
            svg.rect(left, ptop, pw, h, fill='none', stroke=GRID, sw=1, layer='grid')
            if label:
                svg.text(left + 6, ptop + 13, label, size=11, color=MUTED)
            y += h
            return ptop

        if self._volume:
            h, label = self._volume
            ptop = frame(h, label)
            vmax = max((c.get('v', 0) for c in self.c), default=0) or 1
            for i, c in enumerate(self.c):
                bh = c.get('v', 0) / vmax * (h - 16)
                col = UP if c['c'] >= c['o'] else DOWN
                svg.rect(X(i) - body / 2, ptop + h - bh, body, bh, fill=col, opacity=0.75, layer='candles')

        for p in self.panels:
            ptop = frame(p.height, p.label)
            vals = [v for values, _, _ in p.items for v in values[:len(self.c)] if v is not None]
            vals += [m[2] for m in p.marks if m[0] != 'line'] + [q[1] for m in p.marks if m[0] == 'line' for q in (m[1], m[2])]
            vals += list(p.hlines)
            plo = min(vals) if p.ymin is None else p.ymin
            phi = max(vals) if p.ymax is None else p.ymax
            if p.ymin is None and p.ymax is None:
                d = (phi - plo) * 0.12 or 1
                plo, phi = plo - d, phi + d
            PY = lambda v, ptop=ptop, plo=plo, phi=phi, h=p.height: ptop + (phi - v) / (phi - plo) * h
            for hv in p.hlines:
                svg.line(left, PY(hv), x_hi, PY(hv), color=AXIS, width=1, dash=True, layer='grid')
                svg.text(x_hi + 6, PY(hv) + 4, fmt_price(hv, 0 if abs(hv) >= 10 else 2), size=11, color=MUTED, halo=False, layer='grid')
            for n_item, (values, color, label) in enumerate(p.items):
                if p.kind == 'bars' and n_item == 0:
                    zero = PY(0) if plo <= 0 <= phi else ptop + p.height
                    for i, v in enumerate(values[:len(self.c)]):
                        if v is None:
                            continue
                        yy = PY(v)
                        svg.rect(X(i) - body / 2, min(yy, zero), body, abs(zero - yy), fill=UP if v >= 0 else DOWN, opacity=0.6, layer='candles')
                else:
                    seg = []
                    for i, v in enumerate(values[:len(self.c)]):
                        if v is None:
                            if len(seg) > 1:
                                svg.polyline(seg, color=color, width=1.5)
                            seg = []
                        else:
                            seg.append((X(i), PY(v)))
                    if len(seg) > 1:
                        svg.polyline(seg, color=color, width=1.5)
            for m in p.marks:
                if m[0] == 'line':
                    _, p0, p1, color, dash = m
                    svg.line(X(p0[0]), PY(p0[1]), X(p1[0]), PY(p1[1]), color=color, width=1.5, dash=dash)
                else:
                    i, v, text, where, color = m
                    svg.circle(X(i), PY(v), 3, fill=color)
                    svg.text(X(i), PY(v) - 8 if where == 'above' else PY(v) + 17, text, size=11.5, anchor='middle', color=color, weight=600)

        # шкала дат
        if not self.schematic and self.c and 't' in self.c[0]:
            daily = len(self.c) < 2 or (self.c[1]['t'] - self.c[0]['t']) >= 86400
            m = len(self.c)
            count = min(6, m)
            idx = sorted({round(j * (m - 1) / max(count - 1, 1)) for j in range(count)})
            for j, i in enumerate(idx):
                d = _dt.datetime.fromtimestamp(self.c[i]['t'], _dt.timezone.utc)
                s = d.strftime('%d.%m.%y') if daily else d.strftime('%d.%m %H:%M')
                anchor = 'start' if j == 0 else 'end' if (i == m - 1 and self.n == m) else 'middle'
                svg.text(X(i), y + 16, s, size=11, color=MUTED, anchor=anchor, halo=False, layer='grid')
            y += 22
        H = int(y + 12)
        path = _out_path(path)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(svg.render(W, H, self.title or 'График'))
        print(f'saved {path} ({W}x{H})')
        return path


# ----------------------------------------------------------------------------- Canvas

class Canvas:
    """Свободная схема в пикселях. self.y0 — первая свободная строка под заголовком."""

    def __init__(self, width=760, height=360, title='', subtitle=''):
        self.W, self.H, self.title = width, height, title
        self.svg = _Svg()
        y = 12
        if title:
            self.svg.text(14, y + 17, title, size=15, weight=600, halo=False)
            y += 26
        if subtitle:
            self.svg.text(14, y + 12, subtitle, size=12, color=MUTED, halo=False)
            y += 20
        self.y0 = y + 8

    def rect(self, x, y, w, h, fill='none', stroke=AXIS, rx=8, sw=1.25, opacity=1.0):
        self.svg.rect(x, y, w, h, fill=fill, stroke=stroke, rx=rx, sw=sw, opacity=opacity)
        return self

    def box(self, x, y, w, h, lines, fill='none', stroke=AXIS, size=13, color=INK, bold_first=True, opacity=1.0, sw=1.25):
        """Блок с центрированными строками текста. lines — список строк (перенос делаете сами)."""
        self.svg.rect(x, y, w, h, fill=fill, stroke=stroke, rx=8, sw=sw, opacity=opacity)
        if isinstance(lines, str):
            lines = [lines]
        lh = size + 5
        yy = y + h / 2 - lh * (len(lines) - 1) / 2 + size * 0.35
        for j, s in enumerate(lines):
            self.svg.text(x + w / 2, yy + j * lh, s, size=size if j == 0 or not bold_first else size - 1.5, anchor='middle',
                          color=color if j == 0 or not bold_first else MUTED, weight=600 if (j == 0 and bold_first) else 400, halo=False)
        return self

    def text(self, x, y, s, size=13, anchor='start', color=INK, weight=400):
        self.svg.text(x, y, s, size=size, anchor=anchor, color=color, weight=weight, halo=False)
        return self

    def line(self, x1, y1, x2, y2, color=AXIS, width=1.25, dash=False):
        self.svg.line(x1, y1, x2, y2, color=color, width=width, dash=dash)
        return self

    def arrow(self, x1, y1, x2, y2, color=AXIS, width=1.25, dash=False):
        self.svg.line(x1, y1, x2, y2, color=color, width=width, dash=dash, arrow=True)
        return self

    def polyline(self, points, color=BLUE, width=1.75, dash=False, fill='none', opacity=1.0):
        self.svg.polyline(points, color=color, width=width, dash=dash, fill=fill, opacity=opacity)
        return self

    def circle(self, x, y, r=4, fill=INK, stroke='#ffffff'):
        self.svg.circle(x, y, r, fill=fill, stroke=stroke)
        return self

    def candle(self, x, y_open, y_high, y_low, y_close, w=28, up=None):
        """Крупная свеча в пикселях (y растёт вниз). up=None — цвет по соотношению открытия и закрытия."""
        if up is None:
            up = y_close <= y_open
        col = UP if up else DOWN
        self.svg.line(x, y_high, x, y_low, color=col, width=2, layer='candles')
        ytop, ybot = min(y_open, y_close), max(y_open, y_close)
        self.svg.rect(x - w / 2, ytop, w, max(ybot - ytop, 2), fill=col, layer='candles')
        return self

    def save(self, path):
        path = _out_path(path)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(self.svg.render(self.W, self.H, self.title or 'Схема'))
        print(f'saved {path} ({self.W}x{self.H})')
        return path
