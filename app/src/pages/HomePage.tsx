import { Link } from 'react-router-dom'
import { useProgress, type StepProgress } from '../lib/progress'
import { ProgressBar } from '../components/ProgressBar'
import { lessonById } from '../content'

export function HomePage() {
  const progress = useProgress()
  if (!progress) return null
  const { next } = progress
  const nextLesson = next?.lessonId ? lessonById(next.stepId, next.lessonId) : null
  const nextStep = next ? progress.steps.find((s) => s.step.id === next.stepId) : null

  let cta: { to: string; label: string; title: string } | null = null
  if (next && nextStep) {
    if (next.kind === 'lesson' && nextLesson) cta = { to: `/step/${next.stepId}/lesson/${next.lessonId}`, label: 'Продолжить обучение', title: nextLesson.title }
    else if (next.kind === 'practice') cta = { to: `/step/${next.stepId}/practice`, label: 'Перейти к практике', title: `Практика: ${nextStep.step.title}` }
    else if (next.kind === 'test') cta = { to: `/step/${next.stepId}/test`, label: 'Пройти тест', title: `Тест: ${nextStep.step.title}` }
    else cta = { to: `/step/${next.stepId}`, label: 'Открыть ступень', title: 'Все доступные ступени пройдены' }
  }

  const mainSteps = progress.steps.filter((s) => !s.step.standalone)
  const extraSteps = progress.steps.filter((s) => s.step.standalone)
  const stepsDone = mainSteps.filter((s) => s.completed).length

  const renderStep = (s: StepProgress) => {
    const locked = !s.unlocked || !s.available
    const inner = (
      <>
        <div className={`num ${s.completed ? 'done' : ''}`}>{s.completed ? '✓' : s.step.id}</div>
        <div className="body">
          <div className="title">{s.step.title}</div>
          <div className="small muted">{s.step.short}</div>
          {!locked && !s.completed && (
            <div style={{ marginTop: 8 }}>
              <ProgressBar percent={s.percent} label={`Прогресс ступени ${s.step.id}`} />
            </div>
          )}
          {!s.available && s.unlocked && <div className="small muted" style={{ marginTop: 4 }}>Появится в следующей версии приложения</div>}
        </div>
        {locked ? (
          <svg className="chev" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" aria-label="Закрыто">
            <rect x="5" y="11" width="14" height="10" rx="2" />
            <path d="M8 11V7a4 4 0 0 1 8 0v4" />
          </svg>
        ) : (
          <span className="chev" aria-hidden="true">
            ›
          </span>
        )}
      </>
    )
    return locked ? (
      <div key={s.step.id} className="item locked" aria-disabled="true">
        {inner}
      </div>
    ) : (
      <Link key={s.step.id} to={`/step/${s.step.id}`} className="item">
        {inner}
      </Link>
    )
  }

  return (
    <>
      <div className="page-title">
        <h1>Трейдинг с нуля</h1>
        <Link to="/settings" className="btn btn-sm" aria-label="Настройки">
          Настройки
        </Link>
      </div>

      {cta && (
        <div className="card">
          <div className="small muted">{next?.kind === 'done' ? 'Поздравляем' : 'Сейчас'}</div>
          <h2 style={{ marginBottom: 12 }}>{cta.title}</h2>
          {nextStep && (
            <div style={{ marginBottom: 12 }}>
              <div className="row spread small muted" style={{ marginBottom: 4 }}>
                <span>{nextStep.step.standalone ? nextStep.step.title : `Ступень ${nextStep.step.id} · ${nextStep.step.title}`}</span>
                <span>{nextStep.percent}%</span>
              </div>
              <ProgressBar percent={nextStep.percent} label="Прогресс ступени" />
            </div>
          )}
          {next?.kind !== 'done' && (
            <Link to={cta.to} className="btn btn-primary btn-block">
              {cta.label}
            </Link>
          )}
        </div>
      )}

      <div className="card">
        <div className="row spread">
          <h2 style={{ margin: 0 }}>Журнал за неделю</h2>
          <span className="badge">Версия 2</span>
        </div>
        <p className="muted small" style={{ margin: '8px 0 0' }}>
          Статистика сделок появится вместе с журналом. Пока записывайте сделки с демосчёта в таблицу из папки «06_Своя_система».
        </p>
      </div>

      <div className="row spread" style={{ margin: '20px 0 10px' }}>
        <h2 style={{ margin: 0 }}>Ступени</h2>
        <span className="muted small">
          Пройдено {stepsDone} из {mainSteps.length}
        </span>
      </div>
      <div className="list">{mainSteps.map(renderStep)}</div>

      {extraSteps.length > 0 && (
        <>
          <div className="row spread" style={{ margin: '24px 0 6px' }}>
            <h2 style={{ margin: 0 }}>Следующий уровень</h2>
          </div>
          <p className="muted small" style={{ marginBottom: 10 }}>
            Для тех, кто уже торгует по своей системе и ведёт журнал. Открыт без прохождения ступеней 01–06.
          </p>
          <div className="list">{extraSteps.map(renderStep)}</div>
        </>
      )}

      <p className="muted small" style={{ marginTop: 20 }}>
        Это учебный материал, а не финансовая консультация. Практика только на демосчёте. Большинство начинающих трейдеров теряют деньги.
      </p>
    </>
  )
}
