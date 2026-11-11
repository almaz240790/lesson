import Dexie, { type EntityTable } from 'dexie'
import type { Trade } from './journal'

export interface LessonDone {
  id: string // lessonId, напр. "01-03"
  stepId: string
  doneAt: number
}
export interface PracticeDone {
  id: string // `${stepId}:${index}`
  stepId: string
  doneAt: number
}
export interface TestResult {
  id?: number
  stepId: string
  correct: number
  total: number
  percent: number
  passed: boolean
  finishedAt: number
  answers: { questionId: string; chosen: string; correct: boolean }[]
}
export interface Setting {
  key: string
  value: unknown
}

export const db = new Dexie('trading-from-zero') as Dexie & {
  lessons: EntityTable<LessonDone, 'id'>
  practice: EntityTable<PracticeDone, 'id'>
  tests: EntityTable<TestResult, 'id'>
  settings: EntityTable<Setting, 'key'>
  trades: EntityTable<Trade, 'id'>
}

db.version(1).stores({
  lessons: 'id, stepId',
  practice: 'id, stepId',
  tests: '++id, stepId, finishedAt',
  settings: 'key',
})
// Версия 2 приложения: журнал сделок. Остальные таблицы переходят без изменений.
db.version(2).stores({
  trades: '++id, date, closedDate, strategy',
})

export async function getSetting<T>(key: string, fallback: T): Promise<T> {
  const row = await db.settings.get(key)
  return row ? (row.value as T) : fallback
}
export const setSetting = (key: string, value: unknown) => db.settings.put({ key, value })

export interface ExportFile {
  app: 'trading-from-zero'
  /** 1 — без журнала, 2 — с журналом сделок. */
  version: 1 | 2
  exportedAt: string
  lessons: LessonDone[]
  practice: PracticeDone[]
  tests: TestResult[]
  settings: Setting[]
  trades?: Trade[]
}

export async function exportAll(): Promise<ExportFile> {
  const [lessons, practice, tests, settings, trades] = await Promise.all([
    db.lessons.toArray(),
    db.practice.toArray(),
    db.tests.toArray(),
    db.settings.toArray(),
    db.trades.toArray(),
  ])
  return { app: 'trading-from-zero', version: 2, exportedAt: new Date().toISOString(), lessons, practice, tests, settings, trades }
}

export async function importAll(data: unknown): Promise<void> {
  const d = data as Partial<ExportFile>
  if (!d || d.app !== 'trading-from-zero' || !Array.isArray(d.lessons)) {
    throw new Error('Это не файл экспорта приложения «Трейдинг с нуля».')
  }
  if (d.trades !== undefined && !Array.isArray(d.trades)) {
    throw new Error('В файле экспорта повреждён журнал сделок.')
  }
  await db.transaction('rw', [db.lessons, db.practice, db.tests, db.settings, db.trades], async () => {
    await Promise.all([db.lessons.clear(), db.practice.clear(), db.tests.clear(), db.settings.clear()])
    await db.lessons.bulkPut(d.lessons ?? [])
    await db.practice.bulkPut(d.practice ?? [])
    await db.tests.bulkPut((d.tests ?? []).map(({ id: _id, ...t }) => t))
    await db.settings.bulkPut(d.settings ?? [])
    // Файл версии 1 журнала не содержит: сделки на устройстве остаются как были.
    if (d.trades) {
      await db.trades.clear()
      await db.trades.bulkPut(d.trades)
    }
  })
}

/** Сбрасывает учебный прогресс. Журнал сделок и настройки остаются. */
export async function resetAll(): Promise<void> {
  await db.transaction('rw', [db.lessons, db.practice, db.tests, db.settings], async () => {
    await Promise.all([db.lessons.clear(), db.practice.clear(), db.tests.clear()])
  })
}

export const clearJournal = () => db.trades.clear()
