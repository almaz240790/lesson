import { Link, Navigate, useParams } from 'react-router-dom'
import { stepById, tests } from '../content'
import { useProgress } from '../lib/progress'
import { ProgressBar } from '../components/ProgressBar'

export function StepPage() {
  const { stepId = '' } = useParams()
  const step = stepById(stepId)
  const progress = useProgress()
  if (!step) return <Navigate to="/" replace />
  if (!progress) return null
  const sp = progress.steps.find((s) => s.step.id === stepId)!
  if (!sp.unlocked || !sp.available) return <Navigate to="/" replace />
  const test = tests[stepId]
  const allLessonsDone = sp.lessonsDone === sp.lessonsTotal
  const practiceDone = sp.practiceDone === sp.practiceTotal

  return (
    <>
      <div className="page-title">
        <Link to="/" className="btn btn-sm" aria-label="Назад к ступеням">
          ‹ Ступени
        </Link>
      </div>
      <h1>{step.standalone ? step.title : `Ступень ${step.id}. ${step.title}`}</h1>
      <p className="muted">{step.short}</p>
      <div style={{ margin: '12px 0 20px' }}>
        <ProgressBar percent={sp.percent} label="Прогресс ступени" />
        <div className="small muted" style={{ marginTop: 4 }}>
          {sp.completed ? (step.standalone ? 'Уровень пройден' : 'Ступень пройдена') : `${sp.percent}% — уроки, практика и тест на 80%+ ${step.standalone ? 'завершают уровень' : 'открывают следующую ступень'}`}
        </div>
      </div>

      <h2>Уроки</h2>
      <div className="list" style={{ marginBottom: 20 }}>
        {step.lessons.map((l, i) => {
          const done = progress.doneLessonIds.has(l.id)
          return (
            <Link key={l.id} to={`/step/${step.id}/lesson/${l.id}`} className="item">
              <div className={`num ${done ? 'done' : ''}`}>{done ? '✓' : i + 1}</div>
              <div className="body">
                <div className="title">{l.title.replace(/^Урок \d+\.\s*/, '')}</div>
              </div>
              <span className="chev" aria-hidden="true">
                ›
              </span>
            </Link>
          )
        })}
      </div>

      {step.practice && (
        <>
          <h2>Практика</h2>
          <div className="list" style={{ marginBottom: 20 }}>
            <Link to={`/step/${step.id}/practice`} className="item">
              <div className={`num ${practiceDone ? 'done' : ''}`}>{practiceDone ? '✓' : `${sp.practiceDone}/${sp.practiceTotal}`}</div>
              <div className="body">
                <div className="title">Задания на демосчёте</div>
                <div className="small muted">{allLessonsDone ? 'Отмечайте выполненные пункты' : 'Рекомендуем сначала пройти все уроки'}</div>
              </div>
              <span className="chev" aria-hidden="true">
                ›
              </span>
            </Link>
          </div>
        </>
      )}

      {test && (
        <>
          <h2>Тест</h2>
          <div className="list">
            {(() => {
              const inner = (
                <>
                  <div className={`num ${sp.testPassed ? 'done' : ''}`}>{sp.testPassed ? '✓' : '?'}</div>
                  <div className="body">
                    <div className="title">{test.title}</div>
                    <div className="small muted">
                      {!sp.testAvailable
                        ? 'Откроется после всех уроков и практики'
                        : sp.bestTest
                          ? `Лучший результат: ${sp.bestTest.percent}% (${sp.bestTest.correct} из ${sp.bestTest.total}). ${sp.testPassed ? 'Сдан.' : 'Нужно 80%.'}`
                          : `${test.questions.length} вопросов, порог 80%, пересдача без ограничений`}
                    </div>
                  </div>
                  {sp.testAvailable ? (
                    <span className="chev" aria-hidden="true">
                      ›
                    </span>
                  ) : (
                    <svg className="chev" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" aria-label="Закрыто">
                      <rect x="5" y="11" width="14" height="10" rx="2" />
                      <path d="M8 11V7a4 4 0 0 1 8 0v4" />
                    </svg>
                  )}
                </>
              )
              return sp.testAvailable ? (
                <Link to={`/step/${step.id}/test`} className="item">
                  {inner}
                </Link>
              ) : (
                <div className="item locked" aria-disabled="true">
                  {inner}
                </div>
              )
            })()}
          </div>
          <p className="muted small" style={{ marginTop: 10 }}>
            Порядок прохождения: уроки → практика → тест. Тест открывается, когда отмечены все уроки и выполнена практика.
          </p>
        </>
      )}
    </>
  )
}
