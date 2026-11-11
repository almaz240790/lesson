import { lazy, Suspense } from 'react'
import { Link, Navigate, useNavigate, useParams } from 'react-router-dom'
import { lessonCharts, stepById, tasksOf } from '../content'
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
  // Учебник читается одной страницей: старые адреса глав ведут на нужное место в ней.
  if (step.book) return <Navigate to={`/step/${step.id}`} state={{ chapter: lesson.id }} replace />
  if (!progress) return null
  const done = progress.doneLessonIds.has(lesson.id)
  const nextLesson = step.lessons[idx + 1]
  const chart = lessonCharts[lesson.id]
  const tasks = tasksOf(lesson.id)

  const finish = async () => {
    await markLessonDone(step.id, lesson.id)
    if (nextLesson) navigate(`/step/${step.id}/lesson/${nextLesson.id}`)
    else navigate(`/step/${step.id}`)
  }

  const side = (chart || tasks.length > 0) && (
    <div>
      {chart && (
        <div className="card">
          <h3>График</h3>
          <p className="muted small">{chart.title}</p>
          <Suspense fallback={<p className="muted">Загрузка графика…</p>}>
            <CandleChart key={lesson.id} symbol={chart.symbol} interval={chart.interval} emas={chart.emas} rsi={chart.rsi} macd={chart.macd} />
          </Suspense>
        </div>
      )}
      {tasks.map((task, i) => (
        <div key={task.id} className="card">
          <h3>{tasks.length > 1 ? `Задание ${i + 1} из ${tasks.length}` : 'Задание'}</h3>
          {task.type === 'choice' && task.chart && (
            <div style={{ marginBottom: 12 }}>
              <Suspense fallback={<p className="muted">Загрузка графика…</p>}>
                <CandleChart
                  symbol={task.chart.symbol}
                  interval={task.chart.interval}
                  emas={task.chart.emas}
                  range={{ from: task.chart.from, to: task.chart.to }}
                />
              </Suspense>
            </div>
          )}
          {task.type === 'calc' ? <NumericTask q={task} /> : <ChoiceTask q={task} />}
        </div>
      ))}
    </div>
  )

  return (
    <>
      <div className="page-title">
        <Link to={`/step/${step.id}`} className="btn btn-sm">
          ‹ {step.book ? step.title : `Ступень ${step.id}`}
        </Link>
        <span className="muted small">
          {step.book ? 'Глава' : 'Урок'} {idx + 1} из {step.lessons.length}
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
            <div className="notice up">{step.book ? 'Глава отмечена как прочитанная.' : 'Урок отмечен как пройденный.'}</div>
            <div className="row">
              {nextLesson ? (
                <Link to={`/step/${step.id}/lesson/${nextLesson.id}`} className="btn btn-primary" style={{ flex: 1 }}>
                  {step.book ? 'Следующая глава ›' : 'Следующий урок ›'}
                </Link>
              ) : (
                <Link to={`/step/${step.id}`} className="btn btn-primary" style={{ flex: 1 }}>
                  {step.book ? 'К оглавлению ›' : 'К практике и тесту ›'}
                </Link>
              )}
              <button type="button" className="btn btn-sm" onClick={() => unmarkLessonDone(lesson.id)}>
                Снять отметку
              </button>
            </div>
          </>
        ) : (
          <button type="button" className="btn btn-up btn-block" onClick={finish}>
            {step.book ? 'Глава прочитана' : 'Урок пройден'}
          </button>
        )}
      </div>
    </>
  )
}
