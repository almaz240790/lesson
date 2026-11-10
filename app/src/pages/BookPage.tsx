import { memo, useEffect, useRef, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import type { Lesson, Step } from '../content'
import { markLessonDone, useProgress } from '../lib/progress'
import { Markdown } from '../components/Markdown'
import { ProgressBar } from '../components/ProgressBar'

const POS_KEY = 'book-position'
const chapterDomId = (lessonId: string) => `chapter-${lessonId}`
const shortTitle = (title: string) => title.replace(/^Глава \d+\.\s*/, '')

interface SavedPosition {
  id: string
  /** Сколько пикселей главы уже прокручено. */
  offset: number
}

const readPosition = (): SavedPosition | null => {
  try {
    const raw = localStorage.getItem(POS_KEY)
    return raw ? (JSON.parse(raw) as SavedPosition) : null
  } catch {
    return null
  }
}

/** Глава рисуется один раз: при прокрутке и отметках прогресса текст не пересобирается. */
const Chapter = memo(function Chapter({ lesson }: { lesson: Lesson }) {
  return (
    <section id={chapterDomId(lesson.id)} className="card book-chapter">
      <h1>{lesson.title}</h1>
      <Markdown>{lesson.body}</Markdown>
      <div className="book-end" data-chapter-end={lesson.id} />
    </section>
  )
})

/** Учебник одной страницей: оглавление и все главы подряд. */
export function BookPage({ step }: { step: Step }) {
  const progress = useProgress()
  const location = useLocation()
  const wanted = (location.state as { chapter?: string } | null)?.chapter
  // Главы добавляются на страницу по одной, чтобы длинный текст не подвешивал телефон.
  const [shown, setShown] = useState(1)
  const restored = useRef(false)
  // Кнопка «к оглавлению» нужна только когда оглавление уже ушло с экрана.
  const [far, setFar] = useState(false)
  const allShown = shown >= step.lessons.length

  useEffect(() => {
    if (allShown) return
    const t = window.setTimeout(() => setShown((n) => n + 1), 30)
    return () => window.clearTimeout(t)
  }, [shown, allShown])

  // Когда все главы на месте — вернуться туда, где читатель остановился (или к главе из ссылки).
  useEffect(() => {
    if (!allShown || restored.current) return
    restored.current = true
    const target: SavedPosition | null = wanted ? { id: wanted, offset: 0 } : readPosition()
    if (!target) return
    const el = document.getElementById(chapterDomId(target.id))
    if (el) window.scrollTo(0, el.getBoundingClientRect().top + window.scrollY + target.offset - 8)
  }, [allShown, wanted])

  // Запоминать место чтения.
  useEffect(() => {
    if (!allShown) return
    let timer = 0
    const save = () => {
      setFar(window.scrollY > 900)
      window.clearTimeout(timer)
      timer = window.setTimeout(() => {
        if (!restored.current) return
        let current: SavedPosition | null = null
        for (const l of step.lessons) {
          const el = document.getElementById(chapterDomId(l.id))
          if (!el) continue
          const top = el.getBoundingClientRect().top
          if (top <= 80) current = { id: l.id, offset: Math.max(0, Math.round(-top)) }
        }
        try {
          if (current) localStorage.setItem(POS_KEY, JSON.stringify(current))
          else localStorage.removeItem(POS_KEY)
        } catch {
          /* место чтения не сохранится — читать это не мешает */
        }
      }, 250)
    }
    window.addEventListener('scroll', save, { passive: true })
    return () => {
      window.removeEventListener('scroll', save)
      window.clearTimeout(timer)
    }
  }, [allShown, step.lessons])

  // Глава отмечается прочитанной, когда читатель долистал до её конца.
  useEffect(() => {
    if (!allShown) return
    // Конец главы должен пробыть на экране полторы секунды: пролистывание мимо не считается чтением.
    const timers = new Map<string, number>()
    const io = new IntersectionObserver((entries) => {
      for (const e of entries) {
        const id = (e.target as HTMLElement).dataset.chapterEnd
        if (!id) continue
        window.clearTimeout(timers.get(id))
        if (e.isIntersecting && restored.current) timers.set(id, window.setTimeout(() => void markLessonDone(step.id, id), 1500))
      }
    })
    document.querySelectorAll('[data-chapter-end]').forEach((el) => io.observe(el))
    return () => {
      io.disconnect()
      timers.forEach((t) => window.clearTimeout(t))
    }
  }, [allShown, step.id])

  const goTo = (lessonId: string) => {
    const el = document.getElementById(chapterDomId(lessonId))
    if (el) el.scrollIntoView({ block: 'start' })
    else setShown(step.lessons.length)
  }

  const done = progress?.doneLessonIds ?? new Set<string>()
  const read = step.lessons.filter((l) => done.has(l.id)).length
  const percent = Math.round((read / step.lessons.length) * 100)

  return (
    <div>
      <div className="page-title">
        <Link to="/" className="btn btn-sm" aria-label="Назад к ступеням">
          ‹ Учёба
        </Link>
      </div>
      <h1>{step.title}</h1>
      <p className="muted">Все {step.lessons.length} глав подряд на одной странице. Листайте вниз; место, где вы остановились, запоминается.</p>
      <div style={{ margin: '12px 0 20px' }}>
        <ProgressBar percent={percent} label="Прочитано" />
        <div className="small muted" style={{ marginTop: 4 }}>
          Прочитано глав: {read} из {step.lessons.length}
        </div>
      </div>

      <h2 id="book-toc">Оглавление</h2>
      <div className="list" style={{ marginBottom: 20 }}>
        {step.lessons.map((l, i) => (
          <button key={l.id} type="button" className="item book-toc-item" onClick={() => goTo(l.id)}>
            <div className={`num ${done.has(l.id) ? 'done' : ''}`}>{done.has(l.id) ? '✓' : i + 1}</div>
            <div className="body">
              <div className="title">{shortTitle(l.title)}</div>
            </div>
          </button>
        ))}
      </div>

      {step.lessons.slice(0, shown).map((l) => (
        <Chapter key={l.id} lesson={l} />
      ))}
      {!allShown && <p className="muted small">Загружаются остальные главы…</p>}

      {far && (
      <button type="button" className="btn btn-sm book-up" onClick={() => document.getElementById('book-toc')?.scrollIntoView()} aria-label="К оглавлению">
        ↑ Оглавление
      </button>
      )}
    </div>
  )
}
