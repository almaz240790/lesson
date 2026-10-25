import { useMemo, useState } from 'react'
import { Link, Navigate, useParams } from 'react-router-dom'
import { stepById, tests, type ChoiceQuestion } from '../content'
import { PASS_PERCENT, saveTestResult, useProgress } from '../lib/progress'
import { shuffle } from '../lib/shuffle'
import { ChoiceTask } from '../components/ChoiceTask'
import { ProgressBar } from '../components/ProgressBar'

type Answer = { q: ChoiceQuestion; chosen: string; correct: boolean }

export function TestPage() {
  const { stepId = '' } = useParams()
  const step = stepById(stepId)
  const test = tests[stepId]
  const progress = useProgress()
  const [attempt, setAttempt] = useState(0)
  const questions = useMemo(() => (test ? shuffle(test.questions) : []), [test, attempt])
  const [i, setI] = useState(0)
  const [answers, setAnswers] = useState<Answer[]>([])
  const [finished, setFinished] = useState(false)
  const [started, setStarted] = useState(false)

  if (!step || !test) return <Navigate to="/" replace />
  if (!progress) return null
  const sp = progress.steps.find((s) => s.step.id === stepId)!

  const restart = () => {
    setAttempt((a) => a + 1)
    setI(0)
    setAnswers([])
    setFinished(false)
    setStarted(true)
  }

  const onAnswer = (correct: boolean, chosen: string) => {
    setAnswers((a) => [...a, { q: questions[i], chosen, correct }])
  }

  const onNext = async () => {
    if (i + 1 < questions.length) {
      setI(i + 1)
      return
    }
    const correct = answers.filter((a) => a.correct).length
    const total = questions.length
    const percent = Math.round((correct / total) * 100)
    await saveTestResult({
      stepId,
      correct,
      total,
      percent,
      passed: percent >= PASS_PERCENT,
      finishedAt: Date.now(),
      answers: answers.map((a) => ({ questionId: a.q.id, chosen: a.chosen, correct: a.correct })),
    })
    setFinished(true)
  }

  const back = (
    <div className="page-title">
      <Link to={`/step/${step.id}`} className="btn btn-sm">
        ‹ Ступень {step.id}
      </Link>
    </div>
  )

  if (!sp.testAvailable) {
    return (
      <>
        {back}
        <h1>{test.title}</h1>
        <div className="card">
          <p>Тест откроется после прохождения теории и практики этой ступени.</p>
          <p className="muted small">
            Уроки: {sp.lessonsDone} из {sp.lessonsTotal}. Практика: {sp.practiceDone} из {sp.practiceTotal}.
          </p>
          <Link to={`/step/${step.id}`} className="btn btn-primary btn-block">
            К урокам и практике
          </Link>
        </div>
      </>
    )
  }

  if (!started) {
    return (
      <>
        {back}
        <h1>{test.title}</h1>
        <div className="card">
          <p>
            {test.questions.length} вопросов с вариантами ответа. Порог прохождения — {PASS_PERCENT}%. Порядок вопросов и вариантов каждый раз
            перемешивается, пересдавать можно без ограничений.
          </p>
          {sp.bestTest && (
            <p className="muted small">
              Лучший результат: {sp.bestTest.percent}% ({sp.bestTest.correct} из {sp.bestTest.total}). {sp.testPassed ? 'Тест сдан.' : ''}
            </p>
          )}
          <button type="button" className="btn btn-primary btn-block" onClick={restart}>
            {sp.bestTest ? 'Пересдать тест' : 'Начать тест'}
          </button>
        </div>
      </>
    )
  }

  if (finished) {
    const correct = answers.filter((a) => a.correct).length
    const percent = Math.round((correct / questions.length) * 100)
    const passed = percent >= PASS_PERCENT
    const wrong = answers.filter((a) => !a.correct)
    return (
      <>
        {back}
        <h1>Результат</h1>
        <div className="card">
          <div className="row spread">
            <h2 className={passed ? 'text-up' : 'text-down'} style={{ margin: 0 }}>
              {passed ? 'Тест сдан' : 'Тест не сдан'}
            </h2>
            <span className={`badge ${passed ? 'badge-up' : 'badge-down'}`}>{percent}%</span>
          </div>
          <p className="muted" style={{ margin: '8px 0 0' }}>
            Правильно {correct} из {questions.length}. {passed ? '' : `Нужно не меньше ${PASS_PERCENT}%. Повторите уроки и пересдайте.`}
          </p>
        </div>
        {wrong.length > 0 && (
          <>
            <h2>Разбор ошибок</h2>
            {wrong.map((a) => (
              <div key={a.q.id} className="card">
                <p style={{ fontWeight: 600 }}>{a.q.question}</p>
                <p>
                  <span className="text-down">Ваш ответ:</span> {a.chosen}
                </p>
                <p>
                  <span className="text-up">Правильно:</span> {a.q.options[a.q.answer]}
                </p>
                <p className="muted small" style={{ margin: 0 }}>
                  {a.q.explanation}
                </p>
              </div>
            ))}
          </>
        )}
        <div className="row" style={{ marginTop: 8 }}>
          {passed ? (
            <Link to="/" className="btn btn-primary" style={{ flex: 1 }}>
              На главную ›
            </Link>
          ) : (
            <Link to={`/step/${step.id}`} className="btn" style={{ flex: 1 }}>
              К урокам
            </Link>
          )}
          <button type="button" className="btn" onClick={restart}>
            Пересдать
          </button>
        </div>
      </>
    )
  }

  const q = questions[i]
  return (
    <>
      {back}
      <div className="row spread small muted" style={{ marginBottom: 6 }}>
        <span>
          Вопрос {i + 1} из {questions.length}
        </span>
        <span>Верно: {answers.filter((a) => a.correct).length}</span>
      </div>
      <ProgressBar percent={(i / questions.length) * 100} label="Прогресс теста" />
      <div className="card" style={{ marginTop: 14 }}>
        <ChoiceTask key={`${attempt}-${q.id}`} q={q} onAnswer={onAnswer} onNext={onNext} nextLabel={i + 1 < questions.length ? 'Следующий вопрос' : 'Показать результат'} />
      </div>
    </>
  )
}
