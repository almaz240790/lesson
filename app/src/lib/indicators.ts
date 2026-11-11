export type Candle = [time: number, open: number, high: number, low: number, close: number, volume: number]

export function ema(candles: Candle[], period: number): { time: number; value: number }[] {
  const k = 2 / (period + 1)
  const out: { time: number; value: number }[] = []
  let prev: number | null = null
  for (let i = 0; i < candles.length; i++) {
    const close = candles[i][4]
    if (prev === null) {
      if (i + 1 < period) continue
      let sum = 0
      for (let j = i + 1 - period; j <= i; j++) sum += candles[j][4]
      prev = sum / period
    } else {
      prev = close * k + prev * (1 - k)
    }
    out.push({ time: candles[i][0], value: prev })
  }
  return out
}

export type Point = { time: number; value: number }

/** EMA по ряду чисел. Первое значение — простая средняя за period, до него — null. */
function emaSeries(values: number[], period: number): (number | null)[] {
  const k = 2 / (period + 1)
  const out: (number | null)[] = []
  let prev: number | null = null
  let sum = 0
  for (let i = 0; i < values.length; i++) {
    if (prev === null) {
      sum += values[i]
      if (i + 1 < period) {
        out.push(null)
        continue
      }
      prev = sum / period
    } else {
      prev = values[i] * k + prev * (1 - k)
    }
    out.push(prev)
  }
  return out
}

/** RSI по Уайлдеру: первое значение — по простой средней за period, дальше сглаживание. */
export function rsi(candles: Candle[], period = 14): Point[] {
  const out: Point[] = []
  let avgGain = 0
  let avgLoss = 0
  for (let i = 1; i < candles.length; i++) {
    const change = candles[i][4] - candles[i - 1][4]
    const gain = Math.max(change, 0)
    const loss = Math.max(-change, 0)
    if (i <= period) {
      avgGain += gain / period
      avgLoss += loss / period
      if (i < period) continue
    } else {
      avgGain = (avgGain * (period - 1) + gain) / period
      avgLoss = (avgLoss * (period - 1) + loss) / period
    }
    const value = avgLoss === 0 ? (avgGain === 0 ? 50 : 100) : 100 - 100 / (1 + avgGain / avgLoss)
    out.push({ time: candles[i][0], value })
  }
  return out
}

export interface MacdPoint {
  time: number
  macd: number
  signal: number
  hist: number
}

/** MACD: разница быстрой и медленной EMA, сигнальная линия — EMA от этой разницы. */
export function macd(candles: Candle[], fast = 12, slow = 26, signalPeriod = 9): MacdPoint[] {
  const closes = candles.map((c) => c[4])
  const f = emaSeries(closes, fast)
  const s = emaSeries(closes, slow)
  const start = slow - 1
  if (candles.length <= start) return []
  const line = closes.slice(start).map((_, i) => (f[start + i] as number) - (s[start + i] as number))
  const sig = emaSeries(line, signalPeriod)
  const out: MacdPoint[] = []
  for (let i = 0; i < line.length; i++) {
    const signal = sig[i]
    if (signal === null) continue
    out.push({ time: candles[start + i][0], macd: line[i], signal, hist: line[i] - signal })
  }
  return out
}
