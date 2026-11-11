import { Link, useNavigate } from 'react-router-dom'
import { strategyTitle } from '../content'
import { fmtMoney, fmtNum, fmtPrice } from '../lib/calc'
import { dayState, fmtDate, fmtR, fmtSignedPercent, isClosed, summarize, todayStr, tradeNumbers, type DayState, type Trade } from '../lib/journal'
import { useTrades, useTradeSettings } from '../lib/journalStore'

const sideLabel = (t: Trade) => (t.side === 'long' ? 'Лонг' : 'Шорт')
const resultClass = (r: number) => (r > 0 ? 'text-up' : r < 0 ? 'text-down' : '')

/** Состояние дневного лимита: общий блок для журнала и главной. */
export function DayLimitNotice({ day }: { day: DayState }) {
  if (day.hit) {
    return (
      <div className="notice down" role="status">
        <strong>Дневной лимит потерь достигнут.</strong> Сегодня {fmtSignedPercent(day.resultPercent)} депозита при лимите {fmtNum(day.limitPercent, 2)}%. Новые сделки закрыты до
        завтра: закройте терминал, рынок будет и завтра.
      </div>
    )
  }
  if (day.closed > 0) {
    return (
      <div className="notice" role="status">
        Сегодня закрыто сделок: {day.closed}, итог {fmtR(day.resultR)} ({fmtSignedPercent(day.resultPercent)} депозита). Дневной лимит потерь — {fmtNum(day.limitPercent, 2)}%.
      </div>
    )
  }
  return null
}

export function JournalPage() {
  const trades = useTrades()
  const settings = useTradeSettings()
  const navigate = useNavigate()
  if (!trades || !settings) return null

  const day = dayState(trades, todayStr(), settings.dailyLimitPercent)
  const sum = summarize(trades)
  const numbers = tradeNumbers(trades)
  const list = trades.slice().reverse()

  const result = (t: Trade) =>
    isClosed(t) ? <span className={`badge ${t.resultR > 0 ? 'badge-up' : t.resultR < 0 ? 'badge-down' : ''}`}>{fmtR(t.resultR)}</span> : <span className="badge">Открыта</span>

  return (
    <>
      <div className="page-title">
        <h1>Журнал сделок</h1>
        {day.hit ? (
          <button type="button" className="btn btn-primary" disabled>
            Добавить сделку
          </button>
        ) : (
          <Link to="/journal/new" className="btn btn-primary">
            Добавить сделку
          </Link>
        )}
      </div>

      <div style={{ marginBottom: 14 }}>
        <DayLimitNotice day={day} />
      </div>

      {trades.length === 0 ? (
        <div className="card">
          <h2>Сделок пока нет</h2>
          <p className="muted">
            Сюда записывается каждая сделка с демосчёта. Перед записью — чек-лист: любой ответ «нет» значит, что сделки нет. Затем вход, стоп, тейк, размер и причина входа. Когда сделка
            закроется, допишите результат и вывод.
          </p>
          <p className="muted small" style={{ margin: 0 }}>
            Дневной лимит потерь — {fmtNum(settings.dailyLimitPercent, 2)}% депозита. Если убыток за день его достигает, запись новых сделок закрывается до следующего дня. Лимит меняется в{' '}
            <Link to="/settings">настройках</Link>.
          </p>
        </div>
      ) : (
        <>
          <div className="result-grid journal-stats">
            <div className="stat">
              <div className="label">Закрыто сделок</div>
              <div className="value">{sum.closed}</div>
              <div className="small muted">{sum.open > 0 ? `открыто: ${sum.open}` : 'открытых нет'}</div>
            </div>
            <div className="stat">
              <div className="label">Винрейт</div>
              <div className="value">{sum.winrate == null ? '—' : `${fmtNum(sum.winrate, 0)}%`}</div>
              <div className="small muted">
                {sum.wins} в плюс, {sum.losses} в минус
              </div>
            </div>
            <div className="stat">
              <div className="label">Итог в R</div>
              <div className={`value ${resultClass(sum.totalR)}`}>{sum.closed ? fmtR(sum.totalR) : '—'}</div>
              <div className="small muted">1R — риск одной сделки</div>
            </div>
            <div className="stat">
              <div className="label">Правила соблюдены</div>
              <div className={`value ${sum.rulesPercent == null ? '' : sum.rulesPercent >= 95 ? 'text-up' : 'text-down'}`}>
                {sum.rulesPercent == null ? '—' : `${fmtNum(sum.rulesPercent, 0)}%`}
              </div>
              <div className="small muted">цель программы — 95%</div>
            </div>
          </div>

          <div className="list narrow-only" style={{ marginTop: 14 }}>
            {list.map((t) => (
              <Link key={t.id} to={`/journal/${t.id}`} className="item">
                <div className="num">{numbers.get(t.id!)}</div>
                <div className="body">
                  <div className="title">
                    {t.symbol} · {sideLabel(t)}
                  </div>
                  <div className="small muted">
                    {fmtDate(t.date)} · {strategyTitle(t.strategy)}
                  </div>
                  <div className="small muted">
                    R:R 1:{fmtNum(t.rr, 2)}
                    {t.rulesFollowed === false && <span className="text-down"> · правила нарушены</span>}
                  </div>
                </div>
                {result(t)}
              </Link>
            ))}
          </div>

          <div className="card wide-only" style={{ marginTop: 14, padding: 0 }}>
            <div className="table-scroll">
              <table className="jtable">
                <thead>
                  <tr>
                    <th>№</th>
                    <th>Дата</th>
                    <th>Монета</th>
                    <th>Лонг/Шорт</th>
                    <th>Стратегия</th>
                    <th className="n">Вход</th>
                    <th className="n">Стоп</th>
                    <th className="n">Тейк</th>
                    <th className="n">Размер, $</th>
                    <th className="n">R:R</th>
                    <th className="n">Результат</th>
                    <th>Правила</th>
                    <th className="n">Настроение</th>
                    <th>Почему вошёл</th>
                    <th>Вывод</th>
                  </tr>
                </thead>
                <tbody>
                  {list.map((t) => (
                    <tr key={t.id} onClick={() => navigate(`/journal/${t.id}`)}>
                      <td>
                        <Link to={`/journal/${t.id}`} onClick={(e) => e.stopPropagation()} aria-label={`Сделка № ${numbers.get(t.id!)}`}>
                          {numbers.get(t.id!)}
                        </Link>
                      </td>
                      <td>{fmtDate(t.date)}</td>
                      <td>{t.symbol}</td>
                      <td>{sideLabel(t)}</td>
                      <td>{strategyTitle(t.strategy)}</td>
                      <td className="n">{fmtPrice(t.entry)}</td>
                      <td className="n">{fmtPrice(t.stop)}</td>
                      <td className="n">{fmtPrice(t.take)}</td>
                      <td className="n">{fmtMoney(t.size)}</td>
                      <td className="n">1:{fmtNum(t.rr, 2)}</td>
                      <td className={`n ${isClosed(t) ? resultClass(t.resultR) : 'muted'}`}>{isClosed(t) ? fmtR(t.resultR) : 'открыта'}</td>
                      <td className={t.rulesFollowed === false ? 'text-down' : ''}>{t.rulesFollowed == null ? '—' : t.rulesFollowed ? 'да' : 'нет'}</td>
                      <td className="n">{t.mood}</td>
                      <td className="long">{t.reason}</td>
                      <td className="long">{t.conclusion || '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      <p className="muted small" style={{ marginTop: 16 }}>
        Журнал хранится на этом устройстве и попадает в файл экспорта из <Link to="/settings">настроек</Link>. Убыток по правилам — хорошая сделка. Прибыль с нарушением правил — плохая: она
        учит нарушать.
      </p>
    </>
  )
}
