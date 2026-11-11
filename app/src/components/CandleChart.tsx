import { useEffect, useMemo, useRef, useState, type CSSProperties } from 'react'
import { createChart, CandlestickSeries, HistogramSeries, LineSeries, LineStyle, type IChartApi, type UTCTimestamp } from 'lightweight-charts'
import { ema, macd, rsi, type Candle } from '../lib/indicators'
import { useIsDark } from '../lib/theme'

export interface ChartRange {
  /** Первый день фрагмента, ГГГГ-ММ-ДД. */
  from: string
  /** Последний день фрагмента включительно. */
  to: string
}

interface Props {
  symbol: 'btc' | 'eth'
  interval: '1d' | '4h'
  /** Сколько последних свечей показать сразу. */
  visible?: number
  /** Индикаторы, включённые при открытии. */
  emas?: number[]
  rsi?: boolean
  macd?: boolean
  /** Фрагмент истории для задания: только эти даты, без переключателей и прокрутки. */
  range?: ChartRange
}

const EMA_COLORS: Record<number, string> = { 20: '#e0a800', 50: '#2b5fd9', 200: '#9b59b6' }
const SIGNAL_COLOR = '#e0a800'
/** Высота панели RSI или MACD под графиком цены. */
const PANE_H = 120
const cache = new Map<string, Promise<Candle[]>>()

function loadCandles(symbol: string, interval: string): Promise<Candle[]> {
  const key = `${symbol}_${interval}`
  if (!cache.has(key)) {
    cache.set(
      key,
      fetch(`${import.meta.env.BASE_URL}charts/${key}.json`)
        .then((r) => {
          if (!r.ok) throw new Error('Не удалось загрузить данные графика')
          return r.json()
        })
        .then((d) => d.candles as Candle[]),
    )
  }
  return cache.get(key)!
}

const dayStart = (date: string) => Date.parse(`${date}T00:00:00Z`) / 1000
const ruDate = (date: string) => date.split('-').reverse().join('.')

export function CandleChart({ symbol: initialSymbol, interval: initialInterval, visible = 120, emas: initialEmas, rsi: initialRsi = false, macd: initialMacd = false, range }: Props) {
  const [symbol, setSymbol] = useState(initialSymbol)
  const [interval, setInterval] = useState(initialInterval)
  const [emas, setEmas] = useState<Set<number>>(() => new Set(initialEmas))
  const [showVolume, setShowVolume] = useState(true)
  const [showRsi, setShowRsi] = useState(initialRsi)
  const [showMacd, setShowMacd] = useState(initialMacd)
  const [status, setStatus] = useState<'loading' | 'ok' | 'error'>('loading')
  const [candles, setCandles] = useState<Candle[]>([])
  const ref = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const dark = useIsDark()
  const from = range ? dayStart(range.from) : null
  const to = range ? dayStart(range.to) + 86399 : null
  const inRange = useMemo(() => (from === null || to === null ? () => true : (time: number) => time >= from && time <= to), [from, to])

  useEffect(() => {
    let alive = true
    setStatus('loading')
    loadCandles(symbol, interval)
      .then((c) => {
        if (!alive) return
        setCandles(c)
        setStatus('ok')
      })
      .catch(() => alive && setStatus('error'))
    return () => {
      alive = false
    }
  }, [symbol, interval])

  useEffect(() => {
    const el = ref.current
    if (!el || status !== 'ok' || !candles.length) return
    const css = getComputedStyle(document.documentElement)
    const up = css.getPropertyValue('--up').trim()
    const down = css.getPropertyValue('--down').trim()
    const text = css.getPropertyValue('--text-muted').trim()
    const border = css.getPropertyValue('--border').trim()
    const accent = css.getPropertyValue('--accent').trim()
    const fragment = from !== null

    const chart = createChart(el, {
      autoSize: true,
      layout: { background: { color: 'transparent' }, textColor: text, attributionLogo: false, panes: { separatorColor: border, enableResize: false } },
      grid: { vertLines: { color: border }, horzLines: { color: border } },
      rightPriceScale: { borderColor: border },
      timeScale: { borderColor: border, timeVisible: interval === '4h', secondsVisible: false },
      crosshair: { mode: 0 },
      localization: { locale: 'ru-RU' },
      // Фрагмент задания неподвижен: палец на нём прокручивает страницу, а не график.
      handleScroll: !fragment,
      handleScale: !fragment,
    })
    chartRef.current = chart

    // Индикаторы считаются по всей истории и только потом обрезаются до фрагмента, иначе первые значения врут.
    const shown = candles.filter((c) => inRange(c[0]))
    const series = chart.addSeries(CandlestickSeries, {
      upColor: up,
      downColor: down,
      borderUpColor: up,
      borderDownColor: down,
      wickUpColor: up,
      wickDownColor: down,
    })
    series.setData(shown.map((c) => ({ time: c[0] as UTCTimestamp, open: c[1], high: c[2], low: c[3], close: c[4] })))

    if (showVolume) {
      const vol = chart.addSeries(HistogramSeries, { priceFormat: { type: 'volume' }, priceScaleId: 'vol', priceLineVisible: false, lastValueVisible: false })
      chart.priceScale('vol').applyOptions({ scaleMargins: { top: 0.82, bottom: 0 } })
      vol.setData(shown.map((c) => ({ time: c[0] as UTCTimestamp, value: c[5], color: c[4] >= c[1] ? up + '66' : down + '66' })))
    }

    for (const p of emas) {
      const line = chart.addSeries(LineSeries, { color: EMA_COLORS[p], lineWidth: 2, priceLineVisible: false, lastValueVisible: false })
      line.setData(
        ema(candles, p)
          .filter((d) => inRange(d.time))
          .map((d) => ({ time: d.time as UTCTimestamp, value: d.value })),
      )
    }

    let pane = 0
    if (showRsi) {
      pane++
      const line = chart.addSeries(
        LineSeries,
        {
          color: accent,
          lineWidth: 2,
          priceLineVisible: false,
          priceFormat: { type: 'price', precision: 0, minMove: 1 },
          autoscaleInfoProvider: () => ({ priceRange: { minValue: 0, maxValue: 100 } }),
        },
        pane,
      )
      line.setData(
        rsi(candles)
          .filter((d) => inRange(d.time))
          .map((d) => ({ time: d.time as UTCTimestamp, value: d.value })),
      )
      for (const level of [70, 30]) {
        line.createPriceLine({ price: level, color: text, lineWidth: 1, lineStyle: LineStyle.Dashed, axisLabelVisible: true, title: '' })
      }
    }
    if (showMacd) {
      pane++
      const data = macd(candles).filter((d) => inRange(d.time))
      const hist = chart.addSeries(HistogramSeries, { priceLineVisible: false, lastValueVisible: false }, pane)
      hist.setData(data.map((d) => ({ time: d.time as UTCTimestamp, value: d.hist, color: d.hist >= 0 ? up + '99' : down + '99' })))
      const main = chart.addSeries(LineSeries, { color: accent, lineWidth: 2, priceLineVisible: false, lastValueVisible: false }, pane)
      main.setData(data.map((d) => ({ time: d.time as UTCTimestamp, value: d.macd })))
      const signal = chart.addSeries(LineSeries, { color: SIGNAL_COLOR, lineWidth: 2, priceLineVisible: false, lastValueVisible: false }, pane)
      signal.setData(data.map((d) => ({ time: d.time as UTCTimestamp, value: d.signal })))
    }
    chart.panes().forEach((p, i) => {
      if (i > 0) p.setHeight(PANE_H)
    })

    if (fragment) {
      chart.timeScale().fitContent()
    } else {
      const total = shown.length
      chart.timeScale().setVisibleLogicalRange({ from: Math.max(0, total - visible), to: total + 2 })
    }

    return () => {
      chart.remove()
      chartRef.current = null
    }
  }, [candles, status, emas, showVolume, showRsi, showMacd, interval, visible, dark, from, inRange])

  const toggleEma = (p: number) =>
    setEmas((s) => {
      const n = new Set(s)
      if (n.has(p)) n.delete(p)
      else n.add(p)
      return n
    })

  const panes = Number(showRsi) + Number(showMacd)

  return (
    <div className="chart-wrap">
      {!range && (
        <div className="chart-bar">
          <div className="grp" role="group" aria-label="Монета">
            {(['btc', 'eth'] as const).map((s) => (
              <button key={s} type="button" className={symbol === s ? 'active' : ''} aria-pressed={symbol === s} onClick={() => setSymbol(s)}>
                {s.toUpperCase()}
              </button>
            ))}
          </div>
          <div className="grp" role="group" aria-label="Таймфрейм">
            {(['1d', '4h'] as const).map((i) => (
              <button key={i} type="button" className={interval === i ? 'active' : ''} aria-pressed={interval === i} onClick={() => setInterval(i)}>
                {i.toUpperCase()}
              </button>
            ))}
          </div>
          <div className="grp" role="group" aria-label="Индикаторы">
            {[20, 50, 200].map((p) => (
              <button key={p} type="button" className={emas.has(p) ? 'active' : ''} aria-pressed={emas.has(p)} onClick={() => toggleEma(p)}>
                EMA {p}
              </button>
            ))}
            <button type="button" className={showVolume ? 'active' : ''} aria-pressed={showVolume} onClick={() => setShowVolume((v) => !v)}>
              Объём
            </button>
            <button type="button" className={showRsi ? 'active' : ''} aria-pressed={showRsi} onClick={() => setShowRsi((v) => !v)}>
              RSI
            </button>
            <button type="button" className={showMacd ? 'active' : ''} aria-pressed={showMacd} onClick={() => setShowMacd((v) => !v)}>
              MACD
            </button>
          </div>
        </div>
      )}
      <div className={`chart-area ${range ? 'compact' : ''}`} style={{ position: 'relative', '--chart-extra': `${panes * PANE_H}px` } as CSSProperties}>
        <div ref={ref} style={{ position: 'absolute', inset: 0 }} />
        {status === 'loading' && <p className="muted" style={{ padding: 16, position: 'relative' }}>Загрузка графика…</p>}
        {status === 'error' && <p className="muted" style={{ padding: 16, position: 'relative' }}>Данные графика недоступны.</p>}
      </div>
      <div className="chart-legend">
        {range ? (
          <span>
            {symbol.toUpperCase()}/USDT, {interval.toUpperCase()}, {ruDate(range.from)} – {ruDate(range.to)}
          </span>
        ) : (
          <span>Исторические данные {symbol.toUpperCase()}/USDT, {interval.toUpperCase()}. Колесо мыши или два пальца — масштаб.</span>
        )}
        {[...emas].sort((a, b) => a - b).map((p) => (
          <span key={p}>
            <i className="legend-dot" style={{ background: EMA_COLORS[p] }} />
            EMA {p}
          </span>
        ))}
        {showRsi && (
          <span>
            <i className="legend-dot" style={{ background: 'var(--accent)' }} />
            RSI 14, пунктир — 70 и 30
          </span>
        )}
        {showMacd && (
          <>
            <span>
              <i className="legend-dot" style={{ background: 'var(--accent)' }} />
              MACD 12, 26, 9
            </span>
            <span>
              <i className="legend-dot" style={{ background: SIGNAL_COLOR }} />
              сигнальная
            </span>
          </>
        )}
      </div>
    </div>
  )
}
