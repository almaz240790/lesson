import stepsJson from './steps.generated.json'
import referenceJson from './reference.generated.json'
import lessonTasksJson from './lessonTasks.json'
import test01 from './tests/01.json'
import test02 from './tests/02.json'
import test03 from './tests/03.json'
import test04 from './tests/04.json'
import test09 from './tests/09.json'

export interface Lesson {
  id: string
  file: string
  title: string
  body: string
}
export interface Practice {
  title: string
  items: string[]
  note: string | null
}
export interface Step {
  id: string
  dir: string
  title: string
  short: string
  lessons: Lesson[]
  practice: Practice | null
  hasTest: boolean
  /** Отдельный трек: открыт всегда, не входит в цепочку ступеней 01–06. */
  standalone?: boolean
}
export interface ChoiceQuestion {
  id: string
  type: 'choice'
  lesson?: string
  question: string
  options: string[]
  answer: number
  explanation: string
}
export interface CalcQuestion {
  id: string
  type: 'calc'
  question: string
  /** Правильное число. */
  answer: number
  /** Допуск в долях от ответа (0.01 = ±1%). */
  tolerance: number
  unit?: string
  explanation: string
}
export type LessonTask = ChoiceQuestion | CalcQuestion

export interface Test {
  stepId: string
  title: string
  passPercent: number
  questions: ChoiceQuestion[]
}

export const steps: Step[] = stepsJson as Step[]
export const tests: Record<string, Test> = {
  '01': test01 as Test,
  '02': test02 as Test,
  '03': test03 as Test,
  '04': test04 as Test,
  '09': test09 as Test,
}
export const lessonTasks: Record<string, LessonTask> = lessonTasksJson as Record<string, LessonTask>
export const reference = referenceJson as {
  glossary: { term: string; def: string }[]
  indicators: { title: string; body: string }
  checklist: { title: string; intro: string; items: string[] }
}

/** Ступени, доступные в текущей версии приложения (версия 1: ступень 01 и уровень профи). */
export const AVAILABLE_STEPS = new Set(['01', '09'])

/** Уроки, в которых показывается учебный график. */
export const lessonCharts: Record<string, { symbol: 'btc' | 'eth'; interval: '1d' | '4h'; title: string }> = {
  '01-05': { symbol: 'btc', interval: '1d', title: 'BTC/USDT — переключайте таймфрейм и находите свечи с длинными тенями' },
}

export const stepById = (id: string) => steps.find((s) => s.id === id)
export const lessonById = (stepId: string, lessonId: string) => stepById(stepId)?.lessons.find((l) => l.id === lessonId)
