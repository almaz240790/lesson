export interface McInput {
  winRate: number // 0..1
  avgWin: number // R
  avgLoss: number // R, положительное число
  riskPercent: number // % от счёта на сделку
  trades: number
  simulations: number
}

export interface McResult {
  expectancyR: number
  medianReturn: number // %
  p5Return: number // %
  p95Return: number // %
  medianDD: number // %
  p95DD: number // %
  worstDD: number // %
  probNegative: number // 0..1
  probDDOver: (limit: number) => number
  expectedLongestLoss: number
  ddSamples: number[]
}

export function runMonteCarlo(i: McInput): McResult {
  const r = i.riskPercent / 100
  const sims = Math.max(100, Math.min(20000, Math.floor(i.simulations)))
  const n = Math.max(1, Math.floor(i.trades))
  const finals: number[] = new Array(sims)
  const dds: number[] = new Array(sims)
  for (let s = 0; s < sims; s++) {
    let eq = 1
    let peak = 1
    let maxDD = 0
    for (let t = 0; t < n; t++) {
      if (Math.random() < i.winRate) eq *= 1 + r * i.avgWin
      else eq *= 1 - r * i.avgLoss
      if (eq > peak) peak = eq
      const dd = 1 - eq / peak
      if (dd > maxDD) maxDD = dd
      if (eq <= 0) {
        eq = 0
        maxDD = 1
        break
      }
    }
    finals[s] = (eq - 1) * 100
    dds[s] = maxDD * 100
  }
  const sortedF = finals.slice().sort((a, b) => a - b)
  const sortedDD = dds.slice().sort((a, b) => a - b)
  const q = (arr: number[], p: number) => arr[Math.min(arr.length - 1, Math.floor(p * arr.length))]
  const lossRate = 1 - i.winRate
  return {
    expectancyR: i.winRate * i.avgWin - lossRate * i.avgLoss,
    medianReturn: q(sortedF, 0.5),
    p5Return: q(sortedF, 0.05),
    p95Return: q(sortedF, 0.95),
    medianDD: q(sortedDD, 0.5),
    p95DD: q(sortedDD, 0.95),
    worstDD: sortedDD[sortedDD.length - 1],
    probNegative: sortedF.filter((v) => v < 0).length / sims,
    probDDOver: (limit) => sortedDD.filter((v) => v > limit).length / sims,
    expectedLongestLoss: lossRate > 0 && lossRate < 1 ? Math.log(n) / Math.log(1 / lossRate) : 0,
    ddSamples: sortedDD,
  }
}
