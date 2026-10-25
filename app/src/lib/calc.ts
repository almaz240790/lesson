/**
 * Формула из урока 03_Риск_менеджмент/04_Размер_позиции:
 *   Размер позиции = (Депозит × Риск%) / Расстояние до стопа в %
 */
export interface RiskInput {
  deposit: number
  riskPercent: number
  entry: number
  stop: number
  take?: number | null
}

export interface RiskResult {
  side: 'long' | 'short'
  riskMoney: number
  stopDistancePercent: number
  positionSize: number
  quantity: number
  rr: number | null
  takeDistancePercent: number | null
  profitMoney: number | null
}

export function calcPosition(i: RiskInput): RiskResult | null {
  if (!(i.deposit > 0) || !(i.riskPercent > 0) || !(i.entry > 0) || !(i.stop > 0) || i.stop === i.entry) return null
  const side: RiskResult['side'] = i.stop < i.entry ? 'long' : 'short'
  const riskMoney = (i.deposit * i.riskPercent) / 100
  const stopDistancePercent = (Math.abs(i.entry - i.stop) / i.entry) * 100
  const positionSize = riskMoney / (stopDistancePercent / 100)
  const quantity = positionSize / i.entry

  let rr: number | null = null
  let takeDistancePercent: number | null = null
  let profitMoney: number | null = null
  if (i.take && i.take > 0) {
    const goodSide = side === 'long' ? i.take > i.entry : i.take < i.entry
    if (goodSide) {
      takeDistancePercent = (Math.abs(i.take - i.entry) / i.entry) * 100
      rr = takeDistancePercent / stopDistancePercent
      profitMoney = riskMoney * rr
    }
  }
  return { side, riskMoney, stopDistancePercent, positionSize, quantity, rr, takeDistancePercent, profitMoney }
}

export const fmtMoney = (v: number, digits = 2) =>
  v.toLocaleString('ru-RU', { minimumFractionDigits: digits, maximumFractionDigits: digits })
export const fmtNum = (v: number, digits = 2) => v.toLocaleString('ru-RU', { maximumFractionDigits: digits })
