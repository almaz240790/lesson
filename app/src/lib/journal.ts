/**
 * Журнал сделок: расчёты без базы и интерфейса.
 * Файл не импортирует другие модули приложения, чтобы его проверяли тесты из папки tests.
 */

export type Side = 'long' | 'short'

/** То, что записывается при входе в сделку. */
export interface TradeEntry {
  /** День входа, ГГГГ-ММ-ДД по времени устройства. */
  date: string
  symbol: string
  side: Side
  /** Метка стратегии: id урока ступени 04 или 'other'. */
  strategy: string
  entry: number
  stop: number
  take: number
  /** Размер позиции, $. */
  size: number
  /** Депозит на момент входа, $. */
  deposit: number
  /** Фактический риск сделки, % депозита. */
  riskPercent: number
  /** Плановое соотношение: расстояние до тейка в R. */
  rr: number
  /** Настроение перед сделкой, 1–5. */
  mood: number
  reason: string
}

/** То, что дописывается при закрытии сделки. */
export interface TradeClose {
  /** День закрытия, ГГГГ-ММ-ДД. У открытой сделки null. */
  closedDate: string | null
  exit: number | null
  resultR: number | null
  rulesFollowed: boolean | null
  conclusion: string
}

export interface Trade extends TradeEntry, TradeClose {
  id?: number
  createdAt: number
}

/** Правила программы. */
export const MAX_RISK_PERCENT = 2
export const MIN_RR = 2
/** Дневной лимит потерь по умолчанию, % депозита (урок «Эмоции и правила»). */
export const DEFAULT_DAILY_LIMIT = 3

const EPS = 1e-9

// ---------- Даты ----------

export const toDateStr = (d: Date) =>
  `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`

export const todayStr = () => toDateStr(new Date())

export function shiftDate(date: string, days: number): string {
  const [y, m, d] = date.split('-').map(Number)
  return toDateStr(new Date(y, m - 1, d + days))
}

/** 2026-11-05 → 05.11.2026 */
export const fmtDate = (date: string) => date.split('-').reverse().join('.')

// ---------- Расчёты по одной сделке ----------

export const round2 = (v: number) => Math.round(v * 100) / 100

/** Стоп ниже входа — лонг, выше — шорт. */
export const sideOf = (entry: number, stop: number): Side => (stop < entry ? 'long' : 'short')

/** Во сколько раз расстояние до тейка больше расстояния до стопа. null — тейк стоит не с той стороны от входа. */
export function plannedRR(entry: number, stop: number, take: number): number | null {
  if (!(entry > 0) || !(stop > 0) || !(take > 0) || entry === stop) return null
  const rr = (take - entry) / (entry - stop)
  return rr > 0 ? rr : null
}

/** Результат в R при выходе по цене exit: −1 — сработал стоп, +2 — взято два риска. */
export const resultFromExit = (entry: number, stop: number, exit: number) => (exit - entry) / (entry - stop)

/** Фактический риск сделки в % депозита: сколько теряется, если сработает стоп. */
export const riskPercentOf = (size: number, entry: number, stop: number, deposit: number) =>
  ((size * Math.abs(entry - stop)) / entry / deposit) * 100

export const isRRTooLow = (rr: number) => rr < MIN_RR - EPS
/** Размер вводится с копейками, поэтому 2,004% — это всё ещё «2%». */
export const isRiskTooHigh = (riskPercent: number) => riskPercent >= MAX_RISK_PERCENT + 0.005

/** Нарушения правил программы, которые видны по цифрам записи. */
export function violations(t: Pick<TradeEntry, 'rr' | 'riskPercent'>): string[] {
  const out: string[] = []
  if (isRRTooLow(t.rr)) out.push('R:R меньше 1:2')
  if (isRiskTooHigh(t.riskPercent)) out.push('риск больше 2% депозита')
  return out
}

export const isClosed = (t: Trade): t is Trade & { closedDate: string; resultR: number } => t.closedDate != null && t.resultR != null

// ---------- Списки ----------

/** По порядку записи: день входа, затем время создания. */
export function sortTrades<T extends Pick<Trade, 'date' | 'createdAt' | 'id'>>(trades: T[]): T[] {
  return trades.slice().sort((a, b) => (a.date < b.date ? -1 : a.date > b.date ? 1 : a.createdAt - b.createdAt || (a.id ?? 0) - (b.id ?? 0)))
}

/** Номера сделок в журнале: id → порядковый номер с единицы. */
export function tradeNumbers(trades: Trade[]): Map<number, number> {
  const map = new Map<number, number>()
  sortTrades(trades).forEach((t, i) => {
    if (t.id != null) map.set(t.id, i + 1)
  })
  return map
}

/** Сделки, закрытые в дни от from до to включительно. */
export const closedBetween = (trades: Trade[], from: string, to: string) =>
  trades.filter((t) => isClosed(t) && t.closedDate >= from && t.closedDate <= to)

// ---------- Дневной лимит ----------

export interface DayState {
  day: string
  /** Сколько сделок закрыто за день. */
  closed: number
  /** Итог дня в R. */
  resultR: number
  /** Итог дня в % депозита: сумма «результат в R × риск сделки». */
  resultPercent: number
  limitPercent: number
  /** Убыток за день достиг лимита: новые сделки закрыты до следующего дня. */
  hit: boolean
}

export function dayState(trades: Trade[], day: string, limitPercent: number): DayState {
  let closed = 0
  let resultR = 0
  let resultPercent = 0
  for (const t of trades) {
    if (!isClosed(t) || t.closedDate !== day) continue
    closed++
    resultR += t.resultR
    resultPercent += t.resultR * t.riskPercent
  }
  const hit = limitPercent > 0 && resultPercent <= -limitPercent + EPS
  return { day, closed, resultR, resultPercent, limitPercent, hit }
}

// ---------- Сводка ----------

export interface Summary {
  total: number
  open: number
  closed: number
  wins: number
  losses: number
  /** Доля прибыльных среди закрытых, %. null — закрытых сделок нет. */
  winrate: number | null
  totalR: number
  /** Доля закрытых сделок с соблюдёнными правилами, %. */
  rulesPercent: number | null
}

export function summarize(trades: Trade[]): Summary {
  const done = trades.filter(isClosed)
  const wins = done.filter((t) => t.resultR > EPS).length
  const losses = done.filter((t) => t.resultR < -EPS).length
  const followed = done.filter((t) => t.rulesFollowed === true).length
  return {
    total: trades.length,
    open: trades.length - done.length,
    closed: done.length,
    wins,
    losses,
    winrate: done.length ? (wins / done.length) * 100 : null,
    totalR: done.reduce((s, t) => s + t.resultR, 0),
    rulesPercent: done.length ? (followed / done.length) * 100 : null,
  }
}

// ---------- Вывод чисел ----------

const signed = (v: number, digits: number, unit: string) => {
  const r = Math.round(v * 10 ** digits) / 10 ** digits
  const body = Math.abs(r).toLocaleString('ru-RU', { maximumFractionDigits: digits })
  return `${r > 0 ? '+' : r < 0 ? '−' : ''}${body}${unit}`
}
/** +2R, −1R, 0R */
export const fmtR = (v: number) => signed(v, 2, 'R')
/** +1,5%, −3% */
export const fmtSignedPercent = (v: number) => signed(v, 2, '%')
