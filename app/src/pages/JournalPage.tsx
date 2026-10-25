import { Link } from 'react-router-dom'

export function JournalPage() {
  return (
    <>
      <h1>Журнал сделок</h1>
      <div className="card">
        <div className="row spread">
          <h2 style={{ margin: 0 }}>Появится в версии 2</h2>
          <span className="badge">Скоро</span>
        </div>
        <p className="muted" style={{ margin: '10px 0' }}>
          Здесь будет список сделок с демосчёта, обязательный чек-лист перед записью, статистика: винрейт, итог в R, соблюдение правил, просадка.
        </p>
        <p className="muted" style={{ margin: 0 }}>
          Пока ведите журнал в таблице по шаблону из папки «06_Своя_система/02_Журнал_сделок_шаблон.md»: дата, монета, лонг/шорт, стратегия, вход, стоп, тейк, размер, R:R, результат в R, соблюдены ли правила, настроение, почему вошёл, вывод.
        </p>
      </div>
      <Link to="/reference" className="btn btn-block">
        Открыть чек-лист перед сделкой
      </Link>
    </>
  )
}
