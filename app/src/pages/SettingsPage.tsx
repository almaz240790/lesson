import { useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { useTheme, type ThemeSetting } from '../lib/theme'
import { exportAll, importAll, resetAll } from '../lib/db'

export function SettingsPage() {
  const { theme, setTheme } = useTheme()
  const [msg, setMsg] = useState<{ text: string; ok: boolean } | null>(null)
  const fileRef = useRef<HTMLInputElement>(null)

  const doExport = async () => {
    const data = await exportAll()
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `trading-from-zero-${new Date().toISOString().slice(0, 10)}.json`
    a.click()
    URL.revokeObjectURL(url)
    setMsg({ text: 'Файл экспорта сохранён.', ok: true })
  }

  const doImport = async (file: File) => {
    try {
      const data = JSON.parse(await file.text())
      await importAll(data)
      setMsg({ text: 'Данные импортированы.', ok: true })
    } catch (e) {
      setMsg({ text: e instanceof Error ? e.message : 'Не удалось прочитать файл.', ok: false })
    }
  }

  const doReset = async () => {
    if (!window.confirm('Сбросить весь прогресс: уроки, практику и результаты тестов? Настройки останутся.')) return
    await resetAll()
    setMsg({ text: 'Прогресс сброшен.', ok: true })
  }

  return (
    <>
      <div className="page-title">
        <Link to="/" className="btn btn-sm">
          ‹ Учёба
        </Link>
      </div>
      <h1>Настройки</h1>

      <div className="card">
        <h2>Тема</h2>
        <div className="tabs" style={{ marginBottom: 0 }}>
          {(
            [
              ['system', 'Как в системе'],
              ['light', 'Светлая'],
              ['dark', 'Тёмная'],
            ] as [ThemeSetting, string][]
          ).map(([v, label]) => (
            <button key={v} type="button" className={theme === v ? 'active' : ''} onClick={() => setTheme(v)}>
              {label}
            </button>
          ))}
        </div>
      </div>

      <div className="card">
        <h2>Данные</h2>
        <p className="muted small">Всё хранится на этом устройстве. Чтобы перенести прогресс на другое устройство, экспортируйте файл и импортируйте его там.</p>
        <div className="stack">
          <button type="button" className="btn" onClick={doExport}>
            Экспорт в файл JSON
          </button>
          <button type="button" className="btn" onClick={() => fileRef.current?.click()}>
            Импорт из файла JSON
          </button>
          <input
            ref={fileRef}
            type="file"
            accept="application/json,.json"
            className="sr-only"
            onChange={(e) => {
              const f = e.target.files?.[0]
              if (f) doImport(f)
              e.target.value = ''
            }}
          />
          <button type="button" className="btn" style={{ color: 'var(--down)' }} onClick={doReset}>
            Сбросить прогресс
          </button>
        </div>
        {msg && (
          <div className={`notice ${msg.ok ? 'up' : 'down'}`} style={{ marginTop: 12 }}>
            {msg.text}
          </div>
        )}
      </div>

      <div className="card">
        <h2>О приложении</h2>
        <p className="muted small" style={{ margin: 0 }}>
          «Трейдинг с нуля», версия 1. Учебный материал, а не финансовая консультация. Без регистрации, без подключения к бирже и без реальных торговых функций.
        </p>
      </div>
    </>
  )
}
