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
