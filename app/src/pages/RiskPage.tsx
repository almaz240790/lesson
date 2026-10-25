import { useEffect, useState } from 'react'
import { calcPosition, fmtMoney, fmtNum } from '../lib/calc'
import { getSetting, setSetting } from '../lib/db'
import { MonteCarlo } from '../components/MonteCarlo'

const num = (s: string) => {
  const v = parseFloat(s.replace(',', '.').replace(/\s/g, ''))
  return Number.isFinite(v) ? v : NaN
}

export function RiskPage() {
  const [deposit, setDeposit] = useState('')
  const [risk, setRisk] = useState('1')
  const [entry, setEntry] = useState('')
  const [stop, setStop] = useState('')
  const [take, setTake] = useState('')
  const [loaded, setLoaded] = useState(false)
  const [tab, setTab] = useState<'calc' | 'mc'>('calc')

  useEffect(() => {
    Promise.all([getSetting<number | null>('deposit', null), getSetting<number>('riskPercent', 1)]).then(([d, r]) => {
      if (d) setDeposit(String(d))
      setRisk(String(r))
      setLoaded(true)
    })
  }, [])

  useEffect(() => {
    if (!loaded) return
    const d = num(deposit)
    const r = num(risk)
    if (d > 0) setSetting('deposit', d)
    if (r > 0) setSetting('riskPercent', r)
  }, [deposit, risk, loaded])

  const res = calcPosition({ deposit: num(deposit), riskPercent: num(risk), entry: num(entry), stop: num(stop), take: take ? num(take) : null })
  const riskTooHigh = num(risk) > 2
  const rrTooLow = res?.rr != null && res.rr < 2

  return (
    <>
      <h1>{tab === 'calc' ? 'Калькулятор риска' : 'Монте-Карло'}</h1>
      <div className="tabs" role="tablist">
        <button type="button" role="tab" aria-selected={tab === 'calc'} className={tab === 'calc' ? 'active' : ''} onClick={() => setTab('calc')}>
          Размер позиции
        </button>
        <button type="button" role="tab" aria-selected={tab === 'mc'} className={tab === 'mc' ? 'active' : ''} onClick={() => setTab('mc')}>
          Монте-Карло
        </button>
      </div>
      {tab === 'mc' && <MonteCarlo />}
      {tab === 'calc' && (
        <>
      <p className="muted">
        Размер позиции = (Депозит × Риск%) / Расстояние до стопа в %. Риск в деньгах одинаковый при любом стопе: чем дальше стоп, тем меньше позиция.
      </p>
      <div className="grid-2">
        <div className="card">
          <div className="field">
            <label htmlFor="dep">Депозит, $</label>
            <input id="dep" inputMode="decimal" placeholder="1000" value={deposit} onChange={(e) => setDeposit(e.target.value)} />
            <span className="hint">Размер демосчёта. Запоминается.</span>
          </div>
          <div className="field">
            <label htmlFor="risk">Риск на сделку, %</label>
            <input id="risk" inputMode="decimal" placeholder="1" value={risk} onChange={(e) => setRisk(e.target.value)} />
            <span className={`hint ${riskTooHigh ? 'text-down' : ''}`}>{riskTooHigh ? 'Больше 2% — нарушение правила программы.' : 'Правило программы: 1–2%.'}</span>
          </div>
          <div className="field">
            <label htmlFor="entry">Цена входа</label>
            <input id="entry" inputMode="decimal" placeholder="60000" value={entry} onChange={(e) => setEntry(e.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="stop">Цена стопа</label>
            <input id="stop" inputMode="decimal" placeholder="58800" value={stop} onChange={(e) => setStop(e.target.value)} />
            <span className="hint">Стоп ниже входа — лонг, выше — шорт.</span>
          </div>
          <div className="field" style={{ marginBottom: 0 }}>
            <label htmlFor="take">Цена тейка (не обязательно)</label>
            <input id="take" inputMode="decimal" placeholder="62400" value={take} onChange={(e) => setTake(e.target.value)} />
          </div>
        </div>

        <div className="card">
          <h2>Результат</h2>
          {!res ? (
            <p className="muted">Заполните депозит, риск, вход и стоп. Стоп не может равняться входу.</p>
          ) : (
            <>
              <div className="result-grid">
                <div className="stat big">
                  <div className="label">Размер позиции</div>
                  <div className="value">{fmtMoney(res.positionSize)} $</div>
                  <div className="small muted">≈ {fmtNum(res.quantity, 6)} монет по цене входа</div>
                </div>
                <div className="stat">
                  <div className="label">Риск в деньгах (1R)</div>
                  <div className="value text-down">−{fmtMoney(res.riskMoney)} $</div>
                </div>
                <div className="stat">
                  <div className="label">Расстояние до стопа</div>
                  <div className="value">{fmtNum(res.stopDistancePercent, 2)}%</div>
                </div>
                <div className="stat">
                  <div className="label">Направление</div>
                  <div className="value">{res.side === 'long' ? 'Лонг' : 'Шорт'}</div>
                </div>
                <div className="stat">
                  <div className="label">R:R</div>
                  <div className={`value ${res.rr == null ? '' : rrTooLow ? 'text-down' : 'text-up'}`}>{res.rr == null ? '—' : `1:${fmtNum(res.rr, 2)}`}</div>
                </div>
                {res.profitMoney != null && (
                  <div className="stat big">
                    <div className="label">Прибыль при тейке</div>
                    <div className="value text-up">+{fmtMoney(res.profitMoney)} $</div>
                  </div>
                )}
              </div>
              {take && res.rr == null && <div className="notice down" style={{ marginTop: 12 }}>Тейк стоит не с той стороны от входа для этого направления.</div>}
              {rrTooLow && <div className="notice down" style={{ marginTop: 12 }}>R:R меньше 1:2 — по правилам программы в такую сделку не входим.</div>}
              {res.rr != null && !rrTooLow && <div className="notice up" style={{ marginTop: 12 }}>R:R не меньше 1:2 — соотношение проходит правило программы.</div>}
              <p className="muted small" style={{ margin: '12px 0 0' }}>
                Комиссии и проскальзывание в расчёт не входят: фактическая потеря при стопе будет немного больше.
              </p>
            </>
          )}
        </div>
      </div>
        </>
      )}
    </>
  )
}
