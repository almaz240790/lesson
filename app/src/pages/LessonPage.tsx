import { lazy, Suspense } from 'react'
import { Link, Navigate, useNavigate, useParams } from 'react-router-dom'
import { lessonCharts, lessonTasks, stepById } from '../content'
import { markLessonDone, unmarkLessonDone, useProgress } from '../lib/progress'
import { Markdown } from '../components/Markdown'
import { ChoiceTask } from '../components/ChoiceTask'
import { NumericTask } from '../components/NumericTask'

const CandleChart = lazy(() => import('../components/CandleChart').then((m) => ({ default: m.CandleChart })))

export function LessonPage() {
  const { stepId = '', lessonId = '' } = useParams()
  const navigate = useNavigate()
  const step = stepById(stepId)
  const idx = step?.lessons.findIndex((l) => l.id === lessonId) ?? -1
  const lesson = step?.lessons[idx]
  const progress = useProgress()
  if (!step || !lesson) return <Navigate to="/" replace />
  if (!progress) return null
  const done = progress.doneLessonIds.has(lesson.id)
  const nextLesson = step.lessons[idx + 1]
  const chart = lessonCharts[lesson.id]
  const task = lessonTasks[lesson.id]

  const finish = async () => {
    await markLessonDone(step.id, lesson.id)
    if (nextLesson) navigate(`/step/${step.id}/lesson/${nextLesson.id}`)
    else navigate(`/step/${step.id}`)
  }

  const side = (chart || task) && (
    <div>
      {chart && (
        <div className="card">
          <h3>График</h3>
          <p className="muted small">{chart.title}</p>
          <Suspense fallback={<p className="muted">Загрузка графика…</p>}>
            <CandleChart symbol={chart.symbol} interval={chart.interval} />
          </Suspense>
        </div>
      )}
      {task && (
        <div className="card">
          <h3>Задание</h3>
          {task.type === 'calc' ? <NumericTask key={task.id} q={task} /> : <ChoiceTask key={task.id} q={task} />}
        </div>
      )}
    </div>
  )

  return (
    <>
      <div className="page-title">
        <Link to={`/step/${step.id}`} className="btn btn-sm">
          ‹ Ступень {step.id}
        </Link>
        <span className="muted small">
          Урок {idx + 1} из {step.lessons.length}
        </span>
      </div>
      <h1>{lesson.title}</h1>
      <div className={side ? 'grid-2' : ''}>
        <div className="card">
          <Markdown>{lesson.body}</Markdown>
        </div>
        {side}
      </div>
      <div className="stack" style={{ marginTop: 8 }}>
        {done ? (
          <>
            <div className="notice up">Урок отмечен как пройденный.</div>
            <div className="row">
              {nextLesson ? (
                <Link to={`/step/${step.id}/lesson/${nextLesson.id}`} className="btn btn-primary" style={{ flex: 1 }}>
                  Следующий урок ›
                </Link>
              ) : (
                <Link to={`/step/${step.id}`} className="btn btn-primary" style={{ flex: 1 }}>
                  К практике и тесту ›
                </Link>
              )}
              <button type="button" className="btn btn-sm" onClick={() => unmarkLessonDone(lesson.id)}>
                Снять отметку
              </button>
            </div>
          </>
        ) : (
          <button type="button" className="btn btn-up btn-block" onClick={finish}>
            Урок пройден
          </button>
        )}
      </div>
    </>
  )
}
