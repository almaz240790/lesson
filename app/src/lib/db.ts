import Dexie, { type EntityTable } from 'dexie'

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
}

db.version(1).stores({
  lessons: 'id, stepId',
  practice: 'id, stepId',
  tests: '++id, stepId, finishedAt',
  settings: 'key',
})

export async function getSetting<T>(key: string, fallback: T): Promise<T> {
  const row = await db.settings.get(key)
  return row ? (row.value as T) : fallback
}
export const setSetting = (key: string, value: unknown) => db.settings.put({ key, value })

export interface ExportFile {
  app: 'trading-from-zero'
  version: 1
  exportedAt: string
  lessons: LessonDone[]
  practice: PracticeDone[]
  tests: TestResult[]
  settings: Setting[]
}

export async function exportAll(): Promise<ExportFile> {
  const [lessons, practice, tests, settings] = await Promise.all([
    db.lessons.toArray(),
    db.practice.toArray(),
    db.tests.toArray(),
    db.settings.toArray(),
  ])
  return { app: 'trading-from-zero', version: 1, exportedAt: new Date().toISOString(), lessons, practice, tests, settings }
}

export async function importAll(data: unknown): Promise<void> {
  const d = data as Partial<ExportFile>
  if (!d || d.app !== 'trading-from-zero' || !Array.isArray(d.lessons)) {
    throw new Error('Это не файл экспорта приложения «Трейдинг с нуля».')
  }
  await db.transaction('rw', [db.lessons, db.practice, db.tests, db.settings], async () => {
    await Promise.all([db.lessons.clear(), db.practice.clear(), db.tests.clear(), db.settings.clear()])
    await db.lessons.bulkPut(d.lessons ?? [])
    await db.practice.bulkPut(d.practice ?? [])
    await db.tests.bulkPut((d.tests ?? []).map(({ id: _id, ...t }) => t))
    await db.settings.bulkPut(d.settings ?? [])
  })
}

export async function resetAll(): Promise<void> {
  await db.transaction('rw', [db.lessons, db.practice, db.tests, db.settings], async () => {
    await Promise.all([db.lessons.clear(), db.practice.clear(), db.tests.clear()])
  })
}
