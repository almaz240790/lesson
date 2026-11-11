import { useState, type FormEvent } from 'react'
import { STRATEGIES } from '../content'
import { calcPosition, fmtMoney, fmtNum, parseNum } from '../lib/calc'
import { MAX_RISK_PERCENT, isRRTooLow, isRiskTooHigh, plannedRR, riskPercentOf, round2, sideOf, todayStr, violations, type TradeEntry } from '../lib/journal'

export interface TradeFormDefaults {
  deposit?: number | null
  riskPercent?: number
  entry?: number
  stop?: number
  take?: number
}

interface Props {
  /** Запись для правки. Без неё форма новая. */
  initial?: TradeEntry
  /** Значения из настроек и калькулятора для новой сделки. */
  defaults?: TradeFormDefaults
  submitLabel: string
  /** plannedRisk — риск в %, который пользователь ввёл для расчёта размера. */
  onSubmit: (entry: TradeEntry, plannedRisk: number) => void | Promise<void>
  onCancel: () => void
}

const text = (v: number | null | undefined) => (v != null && v > 0 ? String(v) : '')
const round4 = (v: number) => Math.round(v * 1e4) / 1e4

export function TradeForm({ initial, defaults, submitLabel, onSubmit, onCancel }: Props) {
  const knownCoin = !initial || initial.symbol === 'BTC' || initial.symbol === 'ETH'
  const [date, setDate] = useState(initial?.date ?? todayStr())
  const [coin, setCoin] = useState<'BTC' | 'ETH' | 'other'>(initial ? (knownCoin ? (initial.symbol as 'BTC' | 'ETH') : 'other') : 'BTC')
  const [otherSymbol, setOtherSymbol] = useState(initial && !knownCoin ? initial.symbol : '')
  const [strategy, setStrategy] = useState(initial?.strategy ?? '')
  const [deposit, setDeposit] = useState(text(initial?.deposit ?? defaults?.deposit))
  const [risk, setRisk] = useState(text(initial ? round2(initial.riskPercent) : (defaults?.riskPercent ?? 1)))
  const [entry, setEntry] = useState(text(initial?.entry ?? defaults?.entry))
  const [stop, setStop] = useState(text(initial?.stop ?? defaults?.stop))
  const [take, setTake] = useState(text(initial?.take ?? defaults?.take))
  // Пока размер не трогали, он считается по формуле из депозита, риска и стопа.
  const [size, setSize] = useState(text(initial?.size))
  const [sizeTouched, setSizeTouched] = useState(Boolean(initial))
  const [mood, setMood] = useState<number | null>(initial?.mood ?? null)
  const [reason, setReason] = useState(initial?.reason ?? '')
  const [showErrors, setShowErrors] = useState(false)
  const [saving, setSaving] = useState(false)

  const dep = parseNum(deposit)
  const rk = parseNum(risk)
  const e = parseNum(entry)
  const s = parseNum(stop)
  const tk = parseNum(take)
  const pricesOk = e > 0 && s > 0 && e !== s
  const side = pricesOk ? sideOf(e, s) : null
  const formula = calcPosition({ deposit: dep, riskPercent: rk, entry: e, stop: s })
  const formulaSize = formula ? round2(formula.positionSize) : null
  const sizeNum = sizeTouched ? parseNum(size) : (formulaSize ?? NaN)
  const sizeText = sizeTouched ? size : formulaSize != null ? String(formulaSize) : ''
  const rr = pricesOk && tk > 0 ? plannedRR(e, s, tk) : null
  const actualRisk = pricesOk && dep > 0 && sizeNum > 0 ? riskPercentOf(sizeNum, e, s, dep) : null
  const broken = rr != null && actualRisk != null ? violations({ rr, riskPercent: actualRisk }) : []

  const errors: Record<string, string> = {}
  if (!date) errors.date = 'Укажите день входа.'
  else if (date > todayStr()) errors.date = 'День входа не может быть в будущем.'
  if (coin === 'other' && !otherSymbol.trim()) errors.symbol = 'Напишите название монеты.'
  if (!strategy) errors.strategy = 'Выберите стратегию.'
  if (!(e > 0)) errors.entry = 'Введите цену входа.'
  if (!(s > 0)) errors.stop = 'Введите цену стопа.'
  else if (e === s) errors.stop = 'Стоп не может равняться входу.'
  if (!(tk > 0)) errors.take = 'Введите цену тейка.'
  else if (pricesOk && rr == null) errors.take = side === 'long' ? 'Для лонга тейк должен быть выше входа.' : 'Для шорта тейк должен быть ниже входа.'
  if (!(dep > 0)) errors.deposit = 'Введите размер демосчёта.'
  if (!(rk > 0)) errors.risk = 'Введите риск на сделку.'
  if (!(sizeNum > 0)) errors.size = 'Введите размер позиции.'
  if (mood == null) errors.mood = 'Оцените настроение.'
  if (!reason.trim()) errors.reason = 'Запишите причину входа: без неё сделку не разобрать.'
  const err = (key: string) => (showErrors && errors[key] ? <span className="err">{errors[key]}</span> : null)

  const submit = async (ev: FormEvent) => {
    ev.preventDefault()
    if (Object.keys(errors).length > 0 || rr == null || actualRisk == null || mood == null) {
      setShowErrors(true)
      requestAnimationFrame(() => document.querySelector('.field .err')?.scrollIntoView({ block: 'center', behavior: 'smooth' }))
      return
    }
    setSaving(true)
    try {
      await onSubmit(
        {
          date,
          symbol: coin === 'other' ? otherSymbol.trim().toUpperCase() : coin,
          side: sideOf(e, s),
          strategy,
          entry: e,
          stop: s,
          take: tk,
          size: round2(sizeNum),
          deposit: dep,
          riskPercent: round4(actualRisk),
          rr: round4(rr),
          mood,
          reason: reason.trim(),
        },
        rk,
      )
    } finally {
      setSaving(false)
    }
  }

  return (
    <form onSubmit={submit} noValidate>
      <div className="grid-2">
        <div className="card">
          <h2>Сделка</h2>
          <div className="field">
            <label htmlFor="t-date">День входа</label>
            <input id="t-date" type="date" value={date} max={todayStr()} onChange={(ev) => setDate(ev.target.value)} />
            {err('date')}
          </div>
          <div className="field">
            <span className="label" id="t-coin">Монета</span>
            <div className="tabs" role="radiogroup" aria-labelledby="t-coin" style={{ marginBottom: 0 }}>
              {(['BTC', 'ETH', 'other'] as const).map((c) => (
                <button key={c} type="button" role="radio" aria-checked={coin === c} className={coin === c ? 'active' : ''} onClick={() => setCoin(c)}>
                  {c === 'other' ? 'Другая' : c}
                </button>
              ))}
            </div>
            {coin === 'other' && (
              <>
                <input aria-label="Название монеты" placeholder="Например, SOL" value={otherSymbol} onChange={(ev) => setOtherSymbol(ev.target.value)} />
                <span className="hint">Программа советует новичку торговать только BTC и ETH.</span>
              </>
            )}
            {err('symbol')}
          </div>
          <div className="field">
            <label htmlFor="t-strategy">Стратегия</label>
            <select id="t-strategy" value={strategy} onChange={(ev) => setStrategy(ev.target.value)}>
              <option value="" disabled>
                Выберите стратегию
              </option>
              {STRATEGIES.map((st) => (
                <option key={st.id} value={st.id}>
                  {st.title}
                </option>
              ))}
            </select>
            {err('strategy')}
          </div>
          <div className="field">
            <label htmlFor="t-entry">Цена входа</label>
            <input id="t-entry" inputMode="decimal" placeholder="60000" value={entry} onChange={(ev) => setEntry(ev.target.value)} />
            {err('entry')}
          </div>
          <div className="field">
            <label htmlFor="t-stop">Цена стопа</label>
            <input id="t-stop" inputMode="decimal" placeholder="58800" value={stop} onChange={(ev) => setStop(ev.target.value)} />
            <span className="hint">Стоп ниже входа — лонг, выше — шорт.</span>
            {err('stop')}
          </div>
          <div className="field" style={{ marginBottom: 0 }}>
            <label htmlFor="t-take">Цена тейка</label>
            <input id="t-take" inputMode="decimal" placeholder="62400" value={take} onChange={(ev) => setTake(ev.target.value)} />
            {err('take')}
          </div>
        </div>

        <div>
          <div className="card">
            <h2>Риск и размер</h2>
            <div className="field">
              <label htmlFor="t-dep">Депозит, $</label>
              <input id="t-dep" inputMode="decimal" placeholder="1000" value={deposit} onChange={(ev) => setDeposit(ev.target.value)} />
              <span className="hint">Размер демосчёта на момент входа.</span>
              {err('deposit')}
            </div>
            <div className="field">
              <label htmlFor="t-risk">Риск на сделку, %</label>
              <input id="t-risk" inputMode="decimal" placeholder="1" value={risk} onChange={(ev) => setRisk(ev.target.value)} />
              <span className="hint">Правило программы: 1–{MAX_RISK_PERCENT}%.</span>
              {err('risk')}
            </div>
            <div className="field">
              <label htmlFor="t-size">Размер позиции, $</label>
              <input
                id="t-size"
                inputMode="decimal"
                placeholder="500"
                value={sizeText}
                onChange={(ev) => {
                  setSizeTouched(true)
                  setSize(ev.target.value)
                }}
              />
              {formulaSize != null && (
                <span className="hint">
                  По формуле: {fmtMoney(formulaSize)} $.{' '}
                  {sizeTouched && sizeNum !== formulaSize && (
                    <button type="button" className="link" onClick={() => setSizeTouched(false)}>
                      Подставить
                    </button>
                  )}
                </span>
              )}
              {err('size')}
            </div>
            <div className="result-grid">
              <div className="stat">
                <div className="label">Направление</div>
                <div className="value">{side == null ? '—' : side === 'long' ? 'Лонг' : 'Шорт'}</div>
              </div>
              <div className="stat">
                <div className="label">R:R</div>
                <div className={`value ${rr == null ? '' : isRRTooLow(rr) ? 'text-down' : 'text-up'}`}>{rr == null ? '—' : `1:${fmtNum(rr, 2)}`}</div>
              </div>
              <div className="stat big">
                <div className="label">Риск сделки, если сработает стоп</div>
                <div className={`value ${actualRisk != null && isRiskTooHigh(actualRisk) ? 'text-down' : ''}`}>
                  {actualRisk == null ? '—' : `${fmtNum(actualRisk, 2)}% · ${fmtMoney((dep * actualRisk) / 100)} $`}
                </div>
              </div>
            </div>
            {broken.length > 0 && (
              <div className="notice down" style={{ marginTop: 12 }}>
                Нарушение правил программы: {broken.join(', ')}. В такую сделку не входим. Если она уже открыта, запишите её как есть и при закрытии отметьте, что правила нарушены.
              </div>
            )}
          </div>

          <div className="card">
            <h2>Перед входом</h2>
            <div className="field">
              <span className="label" id="t-mood">Настроение: 1 — плохо, 5 — отлично</span>
              <div className="tabs" role="radiogroup" aria-labelledby="t-mood" style={{ marginBottom: 0 }}>
                {[1, 2, 3, 4, 5].map((m) => (
                  <button key={m} type="button" role="radio" aria-checked={mood === m} className={mood === m ? 'active' : ''} onClick={() => setMood(m)}>
                    {m}
                  </button>
                ))}
              </div>
              {err('mood')}
            </div>
            <div className="field" style={{ marginBottom: 0 }}>
              <label htmlFor="t-reason">Почему вхожу</label>
              <textarea id="t-reason" placeholder="Тренд на 1D вверх, откат к поддержке на 4H, стоп под минимумом отката" value={reason} onChange={(ev) => setReason(ev.target.value)} />
              {err('reason')}
            </div>
          </div>
        </div>
      </div>

      {showErrors && Object.keys(errors).length > 0 && (
        <div className="notice down" style={{ marginBottom: 12 }} role="alert">
          Заполните отмеченные поля.
        </div>
      )}
      <div className="row">
        <button type="submit" className="btn btn-primary" style={{ flex: 1 }} disabled={saving}>
          {submitLabel}
        </button>
        <button type="button" className="btn" onClick={onCancel}>
          Отмена
        </button>
      </div>
    </form>
  )
}
