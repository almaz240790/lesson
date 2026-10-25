import { useLiveQuery } from 'dexie-react-hooks'
import { db, type TestResult } from './db'
import { steps, tests, AVAILABLE_STEPS, type Step } from '../content'

export const PASS_PERCENT = 80

export interface StepProgress {
  step: Step
  lessonsDone: number
  lessonsTotal: number
  practiceDone: number
  practiceTotal: number
  bestTest: TestResult | null
  testPassed: boolean
  /** Все условия ступени выполнены. */
  completed: boolean
  /** Предыдущая ступень пройдена (или это первая, или отдельный трек). */
  unlocked: boolean
  /** Все уроки и практика выполнены — тест открыт. */
  testAvailable: boolean
  /** Ступень есть в текущей версии приложения. */
  available: boolean
  percent: number
}

export interface Progress {
  steps: StepProgress[]
  doneLessonIds: Set<string>
  donePracticeIds: Set<string>
  /** Ближайший непройденный урок доступной ступени. */
  next: { stepId: string; lessonId: string | null; kind: 'lesson' | 'practice' | 'test' | 'done' } | null
}

export function useProgress(): Progress | undefined {
  return useLiveQuery(async () => {
    const [lessons, practice, results] = await Promise.all([db.lessons.toArray(), db.practice.toArray(), db.tests.toArray()])
    const doneLessonIds = new Set(lessons.map((l) => l.id))
    const donePracticeIds = new Set(practice.map((p) => p.id))

    let prevCompleted = true
    const sp: StepProgress[] = steps.map((step) => {
      const lessonsDone = step.lessons.filter((l) => doneLessonIds.has(l.id)).length
      const practiceTotal = step.practice?.items.length ?? 0
      const practiceDone = step.practice ? step.practice.items.filter((_, i) => donePracticeIds.has(`${step.id}:${i}`)).length : 0
      const stepResults = results.filter((r) => r.stepId === step.id)
      const bestTest = stepResults.reduce<TestResult | null>((b, r) => (!b || r.percent > b.percent ? r : b), null)
      const hasTest = Boolean(tests[step.id])
      const testPassed = hasTest ? Boolean(bestTest && bestTest.percent >= PASS_PERCENT) : true
      const theoryDone = lessonsDone === step.lessons.length && practiceDone === practiceTotal
      const completed = theoryDone && testPassed
      const unlocked = step.standalone ? true : prevCompleted
      if (!step.standalone) prevCompleted = completed
      const units = step.lessons.length + practiceTotal + (hasTest ? 1 : 0)
      const doneUnits = lessonsDone + practiceDone + (hasTest && testPassed ? 1 : 0)
      return {
        step,
        lessonsDone,
        lessonsTotal: step.lessons.length,
        practiceDone,
        practiceTotal,
        bestTest,
        testPassed,
        testAvailable: theoryDone,
        completed,
        unlocked,
        available: AVAILABLE_STEPS.has(step.id),
        percent: units ? Math.round((doneUnits / units) * 100) : 0,
      }
    })

    let next: Progress['next'] = null
    const ordered = [...sp.filter((s) => !s.step.standalone), ...sp.filter((s) => s.step.standalone)]
    for (const s of ordered) {
      if (!s.unlocked || !s.available) continue
      if (s.completed) continue
      const lesson = s.step.lessons.find((l) => !doneLessonIds.has(l.id))
      if (lesson) next = { stepId: s.step.id, lessonId: lesson.id, kind: 'lesson' }
      else if (s.practiceDone < s.practiceTotal) next = { stepId: s.step.id, lessonId: null, kind: 'practice' }
      else next = { stepId: s.step.id, lessonId: null, kind: 'test' }
      break
    }
    if (!next && sp.every((s) => !s.available || s.completed)) {
      const last = sp.filter((s) => s.available).at(-1)
      if (last) next = { stepId: last.step.id, lessonId: null, kind: 'done' }
    }

    return { steps: sp, doneLessonIds, donePracticeIds, next }
  })
}

export const markLessonDone = (stepId: string, lessonId: string) => db.lessons.put({ id: lessonId, stepId, doneAt: Date.now() })
export const unmarkLessonDone = (lessonId: string) => db.lessons.delete(lessonId)
export const togglePractice = async (stepId: string, index: number) => {
  const id = `${stepId}:${index}`
  const row = await db.practice.get(id)
  if (row) await db.practice.delete(id)
  else await db.practice.put({ id, stepId, doneAt: Date.now() })
}
export const saveTestResult = (r: Omit<TestResult, 'id'>) => db.tests.add(r)
