import { useEffect, useMemo, useState } from 'react'
import { runMonteCarlo } from '../lib/montecarlo'
import { fmtNum } from '../lib/calc'
import { getSetting, setSetting } from '../lib/db'

const num = (s: string) => {
  const v = parseFloat(s.replace(',', '.').replace(/\s/g, ''))
  return Number.isFinite(v) ? v : NaN
}

export function MonteCarlo() {
  const [winRate, setWinRate] = useState('40')
  const [avgWin, setAvgWin] = useState('2')
  const [avgLoss, setAvgLoss] = useState('1')
  const [risk, setRisk] = useState('1')
  const [trades, setTrades] = useState('200')
  const [ddLimit, setDdLimit] = useState('20')
  const [seed, setSeed] = useState(0)
  const [loaded, setLoaded] = useState(false)

  useEffect(() => {
    getSetting<Record<string, string> | null>('monteCarlo', null).then((v) => {
      if (v) {
        setWinRate(v.winRate ?? '40')
        setAvgWin(v.avgWin ?? '2')
        setAvgLoss(v.avgLoss ?? '1')
        setRisk(v.risk ?? '1')
        setTrades(v.trades ?? '200')
        setDdLimit(v.ddLimit ?? '20')
      }
      setLoaded(true)
    })
  }, [])
  useEffect(() => {
    if (loaded) setSetting('monteCarlo', { winRate, avgWin, avgLoss, risk, trades, ddLimit })
  }, [winRate, avgWin, avgLoss, risk, trades, ddLimit, loaded])

  const input = {
    winRate: num(winRate) / 100,
    avgWin: num(avgWin),
    avgLoss: num(avgLoss),
    riskPercent: num(risk),
    trades: num(trades),
    simulations: 3000,
  }
  const valid =
    input.winRate >= 0 && input.winRate <= 1 && input.avgWin > 0 && input.avgLoss > 0 && input.riskPercent > 0 && input.riskPercent < 100 && input.trades >= 10 && input.trades <= 5000

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const res = useMemo(() => (valid ? runMonteCarlo(input) : null), [winRate, avgWin, avgLoss, risk, trades, seed, valid])
  const limit = num(ddLimit)
  const overLimit = res && limit > 0 ? res.probDDOver(limit) : null
  const tooRisky = res && limit > 0 && res.p95DD > limit

  return (
    <div className="grid-2">
      <div className="card">
        <p className="muted small">
          Введите статистику своей системы из журнала. Симуляция перемешивает результаты сделок 3000 раз и показывает, какие просадки
          реалистичны.
        </p>
        <div className="field">
          <label htmlFor="mc-wr">Винрейт, %</label>
          <input id="mc-wr" inputMode="decimal" value={winRate} onChange={(e) => setWinRate(e.target.value)} />
        </div>
        <div className="row" style={{ alignItems: 'stretch' }}>
          <div className="field" style={{ flex: 1 }}>
            <label htmlFor="mc-w">Средняя прибыль, R</label>
            <input id="mc-w" inputMode="decimal" value={avgWin} onChange={(e) => setAvgWin(e.target.value)} />
          </div>
          <div className="field" style={{ flex: 1 }}>
            <label htmlFor="mc-l">Средний убыток, R</label>
            <input id="mc-l" inputMode="decimal" value={avgLoss} onChange={(e) => setAvgLoss(e.target.value)} />
          </div>
        </div>
        <div className="row" style={{ alignItems: 'stretch' }}>
          <div className="field" style={{ flex: 1 }}>
            <label htmlFor="mc-r">Риск на сделку, %</label>
            <input id="mc-r" inputMode="decimal" value={risk} onChange={(e) => setRisk(e.target.value)} />
          </div>
          <div className="field" style={{ flex: 1 }}>
            <label htmlFor="mc-n">Сделок</label>
            <input id="mc-n" inputMode="numeric" value={trades} onChange={(e) => setTrades(e.target.value)} />
          </div>
        </div>
        <div className="field" style={{ marginBottom: 0 }}>
          <label htmlFor="mc-dd">Мой предел просадки, %</label>
          <input id="mc-dd" inputMode="decimal" value={ddLimit} onChange={(e) => setDdLimit(e.target.value)} />
          <span className="hint">Правило: риск на сделку такой, чтобы 95-й процентиль просадки был не больше предела.</span>
        </div>
      </div>

      <div className="card">
        <div className="row spread">
          <h2 style={{ margin: 0 }}>Результат</h2>
          <button type="button" className="btn btn-sm" onClick={() => setSeed((s) => s + 1)} disabled={!valid}>
            Пересчитать
          </button>
        </div>
        {!res ? (
          <p className="muted" style={{ marginTop: 10 }}>
            Проверьте поля: винрейт 0–100, прибыль и убыток больше 0, риск 0–100, сделок от 10 до 5000.
          </p>
        ) : (
          <>
            <div className="result-grid" style={{ marginTop: 12 }}>
              <div className="stat big">
                <div className="label">Ожидание на сделку</div>
                <div className={`value ${res.expectancyR > 0 ? 'text-up' : 'text-down'}`}>
                  {res.expectancyR > 0 ? '+' : ''}
                  {fmtNum(res.expectancyR, 2)}R
                </div>
                <div className="small muted">Серия убытков подряд, ожидаемая за {fmtNum(input.trades, 0)} сделок: около {fmtNum(res.expectedLongestLoss, 0)}</div>
              </div>
              <div className="stat">
                <div className="label">Просадка: медиана</div>
                <div className="value">−{fmtNum(res.medianDD, 1)}%</div>
              </div>
              <div className="stat">
                <div className="label">Просадка: худшие 5%</div>
                <div className={`value ${tooRisky ? 'text-down' : ''}`}>−{fmtNum(res.p95DD, 1)}%</div>
              </div>
              <div className="stat">
                <div className="label">Итог: медиана</div>
                <div className={`value ${res.medianReturn >= 0 ? 'text-up' : 'text-down'}`}>
                  {res.medianReturn >= 0 ? '+' : ''}
                  {fmtNum(res.medianReturn, 0)}%
                </div>
              </div>
              <div className="stat">
                <div className="label">Итог: худшие 5%</div>
                <div className={`value ${res.p5Return >= 0 ? 'text-up' : 'text-down'}`}>
                  {res.p5Return >= 0 ? '+' : ''}
                  {fmtNum(res.p5Return, 0)}%
                </div>
              </div>
              <div className="stat">
                <div className="label">Шанс закончить в минусе</div>
                <div className="value">{fmtNum(res.probNegative * 100, 0)}%</div>
              </div>
              <div className="stat">
                <div className="label">Шанс просадки больше предела</div>
                <div className={`value ${overLimit != null && overLimit > 0.05 ? 'text-down' : ''}`}>{overLimit == null ? '—' : `${fmtNum(overLimit * 100, 0)}%`}</div>
              </div>
            </div>
            {limit > 0 && (
              <div className={`notice ${tooRisky ? 'down' : 'up'}`} style={{ marginTop: 12 }}>
                {tooRisky
                  ? `При риске ${risk}% худшие 5% сценариев дают просадку глубже предела ${ddLimit}%. Снизьте риск на сделку.`
                  : `Риск ${risk}% проходит: в 95% сценариев просадка не глубже ${ddLimit}%.`}
              </div>
            )}
            <p className="muted small" style={{ margin: '12px 0 0' }}>
              Модель: фиксированная доля риска от текущего счёта, результаты сделок независимы, издержки должны быть уже учтены в W и L.
            </p>
          </>
        )}
      </div>
    </div>
  )
}
