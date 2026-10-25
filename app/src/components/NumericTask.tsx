import { useState } from 'react'
import type { CalcQuestion } from '../content'

interface Props {
  q: CalcQuestion
  onAnswer?: (correct: boolean, chosen: string) => void
}

const parse = (s: string) => {
  const v = parseFloat(s.replace(',', '.').replace(/\s/g, ''))
  return Number.isFinite(v) ? v : NaN
}

export function NumericTask({ q, onAnswer }: Props) {
  const [value, setValue] = useState('')
  const [checked, setChecked] = useState<null | boolean>(null)

  const check = () => {
    const v = parse(value)
    if (Number.isNaN(v)) return
    const tol = Math.max(Math.abs(q.answer) * q.tolerance, 1e-9)
    const ok = Math.abs(v - q.answer) <= tol
    setChecked(ok)
    onAnswer?.(ok, value)
  }

  return (
    <div>
      <p style={{ fontWeight: 600 }}>{q.question}</p>
      <div className="row">
        <input
          className="search"
          style={{ flex: 1, marginBottom: 0 }}
          inputMode="decimal"
          placeholder="Ваш ответ"
          aria-label="Ответ"
          value={value}
          disabled={checked !== null}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && check()}
        />
        {q.unit && <span className="muted">{q.unit}</span>}
        <button type="button" className="btn btn-primary" disabled={checked !== null || !value} onClick={check}>
          Проверить
        </button>
      </div>
      {checked !== null && (
        <div className="explain">
          <strong className={checked ? 'text-up' : 'text-down'}>{checked ? 'Верно.' : `Неверно. Правильный ответ: ${q.answer.toLocaleString('ru-RU')}${q.unit ? ' ' + q.unit : ''}.`}</strong>{' '}
          {q.explanation}
          {checked !== null && (
            <div style={{ marginTop: 8 }}>
              <button
                type="button"
                className="btn btn-sm"
                onClick={() => {
                  setChecked(null)
                  setValue('')
                }}
              >
                Решить ещё раз
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
