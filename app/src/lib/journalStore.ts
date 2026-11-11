import { useLiveQuery } from 'dexie-react-hooks'
import { db, getSetting } from './db'
import { DEFAULT_DAILY_LIMIT, sortTrades, type Trade, type TradeClose, type TradeEntry } from './journal'

export interface TradeSettings {
  /** Размер демосчёта, $. null — ещё не введён. */
  deposit: number | null
  riskPercent: number
  dailyLimitPercent: number
}

/** Все сделки по порядку записи. undefined — база ещё читается. */
export const useTrades = (): Trade[] | undefined => useLiveQuery(async () => sortTrades(await db.trades.toArray()))

export const useTrade = (id: number): Trade | null | undefined =>
  useLiveQuery(async () => (Number.isFinite(id) ? ((await db.trades.get(id)) ?? null) : null), [id])

export const useTradeSettings = (): TradeSettings | undefined =>
  useLiveQuery(async () => {
    const [deposit, riskPercent, dailyLimitPercent] = await Promise.all([
      getSetting<number | null>('deposit', null),
      getSetting<number>('riskPercent', 1),
      getSetting<number>('dailyLimitPercent', DEFAULT_DAILY_LIMIT),
    ])
    return { deposit, riskPercent, dailyLimitPercent }
  })

export const addTrade = (entry: TradeEntry) =>
  db.trades.add({ ...entry, closedDate: null, exit: null, resultR: null, rulesFollowed: null, conclusion: '', createdAt: Date.now() })

export const updateTrade = (id: number, patch: Partial<TradeEntry & TradeClose>) => db.trades.update(id, patch)

export const deleteTrade = (id: number) => db.trades.delete(id)
