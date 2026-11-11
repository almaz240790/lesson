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
  /** Учебник: главы для чтения, без практики и теста; показывается отдельным блоком. */
  book?: boolean
}
/** Фрагмент учебного графика, по которому задан вопрос. */
export interface TaskChart {
  symbol: 'btc' | 'eth'
  interval: '1d' | '4h'
  /** Первый и последний день фрагмента, ГГГГ-ММ-ДД. */
  from: string
  to: string
  emas?: number[]
}
export interface ChoiceQuestion {
  id: string
  type: 'choice'
  lesson?: string
  question: string
  options: string[]
  answer: number
  explanation: string
  chart?: TaskChart
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
const lessonTasks = lessonTasksJson as Record<string, LessonTask | LessonTask[]>
/** Задания под уроком: одно или несколько подряд. */
export const tasksOf = (lessonId: string): LessonTask[] => {
  const t = lessonTasks[lessonId]
  return !t ? [] : Array.isArray(t) ? t : [t]
}
export const reference = referenceJson as {
  glossary: { term: string; def: string }[]
  indicators: { title: string; body: string }
  checklist: { title: string; intro: string; items: string[] }
}

/** Ступени, доступные в приложении. Замков нет: открыты все ступени, уровень профи и учебник. */
export const AVAILABLE_STEPS = new Set(steps.map((s) => s.id))

export interface LessonChart {
  symbol: 'btc' | 'eth'
  interval: '1d' | '4h'
  title: string
  /** Индикаторы, включённые при открытии урока. */
  emas?: number[]
  rsi?: boolean
  macd?: boolean
}
/** Уроки, в которых показывается учебный график. */
export const lessonCharts: Record<string, LessonChart> = {
  '01-05': { symbol: 'btc', interval: '1d', title: 'BTC/USDT — переключайте таймфрейм и находите свечи с длинными тенями' },
  '02-01': { symbol: 'btc', interval: '1d', title: 'BTC/USDT — отодвиньте график назад и найдите участки, где максимумы и минимумы растут, падают и где цена стоит в коридоре' },
  '02-02': { symbol: 'btc', interval: '1d', title: 'BTC/USDT — найдите 3–5 цен, от которых график разворачивался несколько раз' },
  '02-03': { symbol: 'btc', interval: '1d', title: 'BTC/USDT — столбики внизу показывают объём. Сравните объём на сильных движениях и на откатах' },
  '02-04': { symbol: 'btc', interval: '1d', emas: [50, 200], title: 'BTC/USDT с EMA 50 и EMA 200 — где цена была выше EMA 200 и где ниже' },
  '02-05': { symbol: 'btc', interval: '1d', rsi: true, title: 'BTC/USDT с RSI 14 — найдите моменты выше 70 и ниже 30 и посмотрите, что было после' },
  '02-06': { symbol: 'btc', interval: '1d', macd: true, title: 'BTC/USDT с MACD — найдите пересечения линий и сравните с движением цены' },
  '02-07': { symbol: 'btc', interval: '1d', emas: [50, 200], title: 'BTC/USDT — определите тренд на 1D, затем переключите на 4H и найдите цену относительно уровней' },
}

/** Метки стратегий для журнала сделок: стратегии ступени 04 и «другая». */
export const STRATEGIES: { id: string; title: string }[] = [
  ...(steps.find((s) => s.id === '04')?.lessons.map((l) => ({ id: l.id, title: l.title.replace(/^Стратегия \d+\.\s*/, '') })) ?? []),
  { id: 'other', title: 'Другая или учебная сделка' },
]
export const strategyTitle = (id: string) => STRATEGIES.find((s) => s.id === id)?.title ?? 'Другая'

export const stepById = (id: string) => steps.find((s) => s.id === id)
export const lessonById = (stepId: string, lessonId: string) => stepById(stepId)?.lessons.find((l) => l.id === lessonId)
