import { useMemo, useState } from 'react'
import type { ChoiceQuestion } from '../content'
import { shuffle } from '../lib/shuffle'

interface Props {
  q: ChoiceQuestion
  /** Вызывается после ответа. */
  onAnswer?: (correct: boolean, chosen: string) => void
  /** Показывать кнопку «Дальше» после ответа. */
  nextLabel?: string
  onNext?: () => void
  shuffleOptions?: boolean
}

export function ChoiceTask({ q, onAnswer, nextLabel, onNext, shuffleOptions = true }: Props) {
  const options = useMemo(() => {
    const withIdx = q.options.map((text, i) => ({ text, correct: i === q.answer }))
    return shuffleOptions ? shuffle(withIdx) : withIdx
  }, [q, shuffleOptions])
  const [chosen, setChosen] = useState<number | null>(null)
  const answered = chosen !== null
  const isCorrect = answered && options[chosen].correct

  const pick = (i: number) => {
    if (answered) return
    setChosen(i)
    onAnswer?.(options[i].correct, options[i].text)
  }

  return (
    <div>
      <p style={{ fontWeight: 600 }}>{q.question}</p>
      {options.map((o, i) => {
        let cls = 'option'
        if (answered) {
          if (o.correct) cls += ' correct'
          else if (i === chosen) cls += ' wrong'
        }
        return (
          <button key={i} type="button" className={cls} disabled={answered} onClick={() => pick(i)}>
            {o.text}
          </button>
        )
      })}
      {answered && (
        <div className={`explain`}>
          <strong className={isCorrect ? 'text-up' : 'text-down'}>{isCorrect ? 'Верно.' : 'Неверно.'}</strong> {q.explanation}
        </div>
      )}
      {answered && onNext && (
        <button type="button" className="btn btn-primary btn-block" style={{ marginTop: 12 }} onClick={onNext}>
          {nextLabel ?? 'Дальше'}
        </button>
      )}
    </div>
  )
}
