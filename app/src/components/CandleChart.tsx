import { useEffect, useRef, useState } from 'react'
import { createChart, CandlestickSeries, HistogramSeries, LineSeries, type IChartApi, type UTCTimestamp } from 'lightweight-charts'
import { ema, type Candle } from '../lib/indicators'
import { useIsDark } from '../lib/theme'

interface Props {
  symbol: 'btc' | 'eth'
  interval: '1d' | '4h'
  /** Сколько последних свечей показать сразу. */
  visible?: number
}

const EMA_COLORS: Record<number, string> = { 20: '#e0a800', 50: '#2b5fd9', 200: '#9b59b6' }
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

export function CandleChart({ symbol: initialSymbol, interval: initialInterval, visible = 120 }: Props) {
  const [symbol, setSymbol] = useState(initialSymbol)
  const [interval, setInterval] = useState(initialInterval)
  const [emas, setEmas] = useState<Set<number>>(() => new Set())
  const [showVolume, setShowVolume] = useState(true)
  const [status, setStatus] = useState<'loading' | 'ok' | 'error'>('loading')
  const [candles, setCandles] = useState<Candle[]>([])
  const ref = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const dark = useIsDark()

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

    const chart = createChart(el, {
      autoSize: true,
      layout: { background: { color: 'transparent' }, textColor: text, attributionLogo: false },
      grid: { vertLines: { color: border }, horzLines: { color: border } },
      rightPriceScale: { borderColor: border },
      timeScale: { borderColor: border, timeVisible: interval === '4h', secondsVisible: false },
      crosshair: { mode: 0 },
      localization: { locale: 'ru-RU' },
      handleScroll: true,
      handleScale: true,
    })
    chartRef.current = chart

    const series = chart.addSeries(CandlestickSeries, {
      upColor: up,
      downColor: down,
      borderUpColor: up,
      borderDownColor: down,
      wickUpColor: up,
      wickDownColor: down,
    })
    series.setData(candles.map((c) => ({ time: c[0] as UTCTimestamp, open: c[1], high: c[2], low: c[3], close: c[4] })))

    if (showVolume) {
      const vol = chart.addSeries(HistogramSeries, { priceFormat: { type: 'volume' }, priceScaleId: 'vol', priceLineVisible: false, lastValueVisible: false })
      chart.priceScale('vol').applyOptions({ scaleMargins: { top: 0.82, bottom: 0 } })
      vol.setData(candles.map((c) => ({ time: c[0] as UTCTimestamp, value: c[5], color: c[4] >= c[1] ? up + '66' : down + '66' })))
    }

    for (const p of emas) {
      const line = chart.addSeries(LineSeries, { color: EMA_COLORS[p], lineWidth: 2, priceLineVisible: false, lastValueVisible: false })
      line.setData(ema(candles, p).map((d) => ({ time: d.time as UTCTimestamp, value: d.value })))
    }

    const total = candles.length
    chart.timeScale().setVisibleLogicalRange({ from: Math.max(0, total - visible), to: total + 2 })

    return () => {
      chart.remove()
      chartRef.current = null
    }
  }, [candles, status, emas, showVolume, interval, visible, dark])

  const toggleEma = (p: number) =>
    setEmas((s) => {
      const n = new Set(s)
      if (n.has(p)) n.delete(p)
      else n.add(p)
      return n
    })

  return (
    <div className="chart-wrap">
      <div className="chart-bar">
        <div className="grp" role="group" aria-label="Монета">
          {(['btc', 'eth'] as const).map((s) => (
            <button key={s} type="button" className={symbol === s ? 'active' : ''} onClick={() => setSymbol(s)}>
              {s.toUpperCase()}
            </button>
          ))}
        </div>
        <div className="grp" role="group" aria-label="Таймфрейм">
          {(['1d', '4h'] as const).map((i) => (
            <button key={i} type="button" className={interval === i ? 'active' : ''} onClick={() => setInterval(i)}>
              {i.toUpperCase()}
            </button>
          ))}
        </div>
        <div className="grp" role="group" aria-label="Индикаторы">
          {[20, 50, 200].map((p) => (
            <button key={p} type="button" className={emas.has(p) ? 'active' : ''} onClick={() => toggleEma(p)}>
              EMA {p}
            </button>
          ))}
          <button type="button" className={showVolume ? 'active' : ''} onClick={() => setShowVolume((v) => !v)}>
            Объём
          </button>
        </div>
      </div>
      <div className="chart-area" style={{ position: 'relative' }}>
        <div ref={ref} style={{ position: 'absolute', inset: 0 }} />
        {status === 'loading' && <p className="muted" style={{ padding: 16, position: 'relative' }}>Загрузка графика…</p>}
        {status === 'error' && <p className="muted" style={{ padding: 16, position: 'relative' }}>Данные графика недоступны.</p>}
      </div>
      <div className="chart-legend">
        <span>Исторические данные {symbol.toUpperCase()}/USDT, {interval.toUpperCase()}. Колесо мыши или два пальца — масштаб.</span>
        {[...emas].sort((a, b) => a - b).map((p) => (
          <span key={p}>
            <i className="legend-dot" style={{ background: EMA_COLORS[p] }} />
            EMA {p}
          </span>
        ))}
      </div>
    </div>
  )
}
