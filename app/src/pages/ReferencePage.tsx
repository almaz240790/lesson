import { useMemo, useState, type ReactNode } from 'react'
import { reference } from '../content'
import { Markdown } from '../components/Markdown'

type Tab = 'glossary' | 'indicators' | 'checklist'

function highlight(text: string, q: string): ReactNode {
  if (!q) return text
  const i = text.toLowerCase().indexOf(q.toLowerCase())
  if (i < 0) return text
  return (
    <>
      {text.slice(0, i)}
      <mark>{text.slice(i, i + q.length)}</mark>
      {text.slice(i + q.length)}
    </>
  )
}

export function ReferencePage() {
  const [tab, setTab] = useState<Tab>('glossary')
  const [q, setQ] = useState('')
  const items = useMemo(() => {
    const s = q.trim().toLowerCase()
    const list = reference.glossary
    if (!s) return list
    return list.filter((g) => g.term.toLowerCase().includes(s) || g.def.toLowerCase().includes(s))
  }, [q])

  return (
    <>
      <h1>Справочник</h1>
      <div className="tabs" role="tablist">
        <button type="button" role="tab" aria-selected={tab === 'glossary'} className={tab === 'glossary' ? 'active' : ''} onClick={() => setTab('glossary')}>
          Глоссарий
        </button>
        <button type="button" role="tab" aria-selected={tab === 'indicators'} className={tab === 'indicators' ? 'active' : ''} onClick={() => setTab('indicators')}>
          Индикаторы
        </button>
        <button type="button" role="tab" aria-selected={tab === 'checklist'} className={tab === 'checklist' ? 'active' : ''} onClick={() => setTab('checklist')}>
          Чек-лист
        </button>
      </div>

      {tab === 'glossary' && (
        <>
          <input className="search" type="search" placeholder="Поиск по глоссарию" value={q} onChange={(e) => setQ(e.target.value)} aria-label="Поиск по глоссарию" />
          <div className="card">
            {items.length === 0 ? (
              <p className="muted">Ничего не найдено.</p>
            ) : (
              <dl className="glossary">
                {items.map((g) => (
                  <div key={g.term}>
                    <dt>{highlight(g.term, q.trim())}</dt>
                    <dd>{highlight(g.def, q.trim())}</dd>
                  </div>
                ))}
              </dl>
            )}
          </div>
        </>
      )}

      {tab === 'indicators' && (
        <div className="card">
          <h2>{reference.indicators.title.replace(/^Шпаргалка:\s*/, '')}</h2>
          <Markdown>{reference.indicators.body}</Markdown>
        </div>
      )}

      {tab === 'checklist' && (
        <div className="card">
          <h2>{reference.checklist.title}</h2>
          <p className="muted">{reference.checklist.intro}</p>
          <ol style={{ paddingLeft: '1.3em', margin: 0 }}>
            {reference.checklist.items.map((it) => (
              <li key={it} style={{ marginBottom: 8 }}>
                {it}
              </li>
            ))}
          </ol>
          <p className="muted small" style={{ margin: '12px 0 0' }}>
            В версии 2 этот чек-лист станет обязательным шагом перед записью сделки в журнал.
          </p>
        </div>
      )}
    </>
  )
}
