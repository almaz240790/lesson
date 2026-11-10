// Собирает уроки, практику и глоссарий из Markdown-папок 01–07 в src/content/*.generated.json.
// Запуск: node scripts/build-content.mjs  (из папки app)
import { readdirSync, readFileSync, writeFileSync, mkdirSync, existsSync, copyFileSync, rmSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const root = join(here, '..', '..')
const out = join(here, '..', 'src', 'content')
mkdirSync(out, { recursive: true })

// На хостинге (Railway и т.п.) папок курса рядом нет: используем сохранённые JSON из src/content.
if (!existsSync(join(root, '01_Основы'))) {
  if (!existsSync(join(out, 'steps.generated.json'))) {
    console.error('Нет ни папок курса, ни сохранённого контента в src/content.')
    process.exit(1)
  }
  console.log('Папки курса не найдены, контент не пересобран: используются сохранённые JSON из src/content.')
  process.exit(0)
}

const STEPS = [
  { id: '01', dir: '01_Основы', title: 'Основы', short: 'Биржа, ордера, комиссии, свечи, таймфреймы' },
  { id: '02', dir: '02_Анализ_графика', title: 'Анализ графика', short: 'Тренд, уровни, объём, индикаторы, несколько таймфреймов' },
  { id: '03', dir: '03_Риск_менеджмент', title: 'Риск-менеджмент', short: 'Риск на сделку, стоп, размер позиции, плечо' },
  { id: '04', dir: '04_Стратегии', title: 'Стратегии', short: '5 стратегий от простой к сложной' },
  { id: '05', dir: '05_Психология', title: 'Психология', short: 'Эмоции, ошибки новичков, дисциплина' },
  { id: '06', dir: '06_Своя_система', title: 'Своя система', short: 'Торговый план, журнал, критерии перехода на реальные деньги' },
  { id: '09', dir: '09_Уровень_профи', title: 'Уровень профи', short: 'Ожидание, бэктест, Монте-Карло, микроструктура, портфель, процесс', standalone: true },
  { id: '10', dir: '10_Учебник', title: 'Учебник', short: '15 глав с примерами на реальных свечах: от устройства рынка до своей торговой системы', standalone: true, book: true },
]

const read = (p) => readFileSync(p, 'utf8').replace(/\r\n/g, '\n')
const titleOf = (md, fallback) => (md.match(/^#\s+(.+)$/m)?.[1] ?? fallback).trim()
const bodyOf = (md) => md.replace(/^#\s+.+\n/, '').trim()
// Учебник: рисунки копируются в public/textbook; ссылки между главами, на уроки, практику и тесты курса
// и на справочник ведут на экраны приложения; остальные относительные ссылки превращаются в обычный текст.
const bookBody = (md, stepId) =>
  md
    .replace(/\]\(img\/([0-9a-z-]+\.svg)\)/g, '](textbook/$1)')
    .replace(/(?<!!)\[([^\]]+)\]\((\d\d)_[^)\s]+\.md(?:#[^)]*)?\)/g, (_, label, n) => `[${label}](#/step/${stepId}/lesson/${stepId}-${n})`)
    .replace(/(?<!!)\[([^\]]+)\]\(\.\.\/(\d\d)_[^/)\s]+\/([^)\s]+?)\.md(?:#[^)]*)?\)/g, (all, label, dir, file) => {
      const step = STEPS.find((x) => x.id === dir)
      if (dir === '07') return `[${label}](#/reference)`
      if (!step) return label
      if (/^\d\d_/.test(file) && existsSync(join(root, step.dir, `${file}.md`))) return `[${label}](#/step/${dir}/lesson/${dir}-${file.slice(0, 2)})`
      if (file === 'Практика') return `[${label}](#/step/${dir}/practice)`
      if (file === 'Тест' && existsSync(join(here, '..', 'src', 'content', 'tests', `${dir}.json`))) return `[${label}](#/step/${dir}/test)`
      return `[${label}](#/step/${dir})`
    })
    .replace(/(?<!!)\[([^\]]+)\]\((?!https?:|#|mailto:)[^)\s]+\)/g, '$1')

const checklist = (md) => [...md.matchAll(/^- \[[ x]\]\s+(.+(?:\n {2}.+)*)$/gm)].map((m) => m[1].replace(/\n {2}/g, ' ').trim())

const steps = STEPS.map((s) => {
  const dir = join(root, s.dir)
  const files = readdirSync(dir).filter((f) => f.endsWith('.md')).sort()
  const lessons = files
    .filter((f) => /^\d\d_/.test(f))
    .map((f) => {
      const md = read(join(dir, f))
      const n = f.slice(0, 2)
      const body = bodyOf(md)
      return { id: `${s.id}-${n}`, file: `${s.dir}/${f.replace(/\.md$/, '')}`, title: titleOf(md, f), body: s.book ? bookBody(body, s.id) : body }
    })
  const practiceFile = files.find((f) => f === 'Практика.md')
  let practice = null
  if (practiceFile) {
    const md = read(join(dir, practiceFile))
    const lines = md.split('\n')
    const footer = lines.filter((l) => l.trim() && !l.startsWith('#') && !l.startsWith('- [')).join(' ').trim()
    practice = { title: titleOf(md, 'Практика'), items: checklist(md), note: footer || null }
  }
  const hasTest = files.includes('Тест.md')
  return { ...s, lessons, practice, hasTest }
})

writeFileSync(join(out, 'steps.generated.json'), JSON.stringify(steps, null, 2))

// Рисунки учебника
for (const s of STEPS.filter((x) => x.book)) {
  const src = join(root, s.dir, 'img')
  const dst = join(here, '..', 'public', 'textbook')
  rmSync(dst, { recursive: true, force: true })
  mkdirSync(dst, { recursive: true })
  for (const f of readdirSync(src).filter((x) => x.endsWith('.svg'))) copyFileSync(join(src, f), join(dst, f))
}

// Справочник
const refDir = join(root, '07_Справочник')
const glossaryMd = read(join(refDir, 'Глоссарий.md'))
const glossary = []
for (const line of glossaryMd.split('\n')) {
  if (!line.startsWith('- ')) continue
  for (const m of line.slice(2).matchAll(/\*\*(.+?)\*\*\s*—\s*([^*]+?)(?=\s*\*\*|$)/g)) {
    glossary.push({ term: m[1].trim(), def: m[2].trim().replace(/^на падение/, "сделка на падение") })
  }
}
const indicators = read(join(refDir, 'Таймфреймы_и_индикаторы.md'))
const checklistMd = read(join(refDir, 'Чек-лист_перед_сделкой.md'))
const reference = {
  glossary,
  indicators: { title: titleOf(indicators, 'Шпаргалка'), body: bodyOf(indicators) },
  checklist: { title: titleOf(checklistMd, 'Чек-лист'), intro: checklistMd.split('\n').find((l) => l && !l.startsWith('#') && !l.startsWith('- [')) ?? '', items: checklist(checklistMd) },
}
writeFileSync(join(out, 'reference.generated.json'), JSON.stringify(reference, null, 2))

console.log(`Ступеней: ${steps.length}, уроков: ${steps.reduce((a, s) => a + s.lessons.length, 0)}, терминов: ${glossary.length}`)
