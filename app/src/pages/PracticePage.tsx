import { Link, Navigate, useParams } from 'react-router-dom'
import { stepById } from '../content'
import { togglePractice, useProgress } from '../lib/progress'

export function PracticePage() {
  const { stepId = '' } = useParams()
  const step = stepById(stepId)
  const progress = useProgress()
  if (!step || !step.practice) return <Navigate to="/" replace />
  if (!progress) return null
  const sp = progress.steps.find((s) => s.step.id === stepId)!
  const all = sp.practiceDone === sp.practiceTotal

  return (
    <>
      <div className="page-title">
        <Link to={`/step/${step.id}`} className="btn btn-sm">
          ‹ Ступень {step.id}
        </Link>
      </div>
      <h1>{step.practice.title}</h1>
      <p className="muted">{step.standalone ? 'Задания по вашему журналу и демосчёту. Отмечайте сделанное после записи результата в торговый план.' : 'Выполняйте задания на демосчёте своей биржи и отмечайте сделанное. Реальные деньги не нужны.'}</p>
      <div className="stack">
        {step.practice.items.map((text, i) => {
          const done = progress.donePracticeIds.has(`${step.id}:${i}`)
          return (
            <label key={i} className={`check ${done ? 'done' : ''}`}>
              <input type="checkbox" checked={done} onChange={() => togglePractice(step.id, i)} />
              <span>{text}</span>
            </label>
          )
        })}
      </div>
      {step.practice.note && <p className="muted small" style={{ marginTop: 14 }}>{step.practice.note}</p>}
      <div style={{ marginTop: 16 }}>
        {all ? (
          <>
            <div className="notice up" style={{ marginBottom: 12 }}>
              Практика выполнена: {sp.practiceDone} из {sp.practiceTotal}.
            </div>
            <Link to={`/step/${step.id}/test`} className="btn btn-primary btn-block">
              Перейти к тесту ›
            </Link>
          </>
        ) : (
          <div className="notice">
            Выполнено {sp.practiceDone} из {sp.practiceTotal}.
          </div>
        )}
      </div>
    </>
  )
}
