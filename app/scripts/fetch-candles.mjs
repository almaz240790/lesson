// Однократная загрузка исторических свечей с публичного API Binance в public/charts/*.json.
// Приложение в работе к бирже не обращается — данные статические.
// Запуск: node scripts/fetch-candles.mjs
import { writeFileSync, mkdirSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const out = join(here, '..', 'public', 'charts')
mkdirSync(out, { recursive: true })

const BASE = 'https://data-api.binance.vision/api/v3/klines'
const START = Date.UTC(2019, 0, 1)
const r = (v, d) => Number(Number(v).toFixed(d))

async function fetchAll(symbol, interval) {
  const rows = []
  let start = START
  for (;;) {
    const url = `${BASE}?symbol=${symbol}&interval=${interval}&startTime=${start}&limit=1000`
    const res = await fetch(url)
    if (!res.ok) throw new Error(`${symbol} ${interval}: HTTP ${res.status}`)
    const batch = await res.json()
    if (!batch.length) break
    for (const k of batch) rows.push([k[0] / 1000, r(k[1], 2), r(k[2], 2), r(k[3], 2), r(k[4], 2), r(k[5], 0)])
    start = batch[batch.length - 1][0] + 1
    if (batch.length < 1000) break
  }
  return rows
}

for (const symbol of ['BTCUSDT', 'ETHUSDT']) {
  for (const interval of ['1d', '4h']) {
    const rows = await fetchAll(symbol, interval)
    const name = `${symbol.replace('USDT', '').toLowerCase()}_${interval}.json`
    writeFileSync(join(out, name), JSON.stringify({ symbol: symbol.replace('USDT', '/USDT'), interval, format: ['time', 'open', 'high', 'low', 'close', 'volume'], candles: rows }))
    console.log(`${name}: ${rows.length} свечей`)
  }
}
