// Проверка рисунков: превращает SVG в PNG, чтобы посмотреть на результат глазами.
// Запуск: node render.cjs <папка для PNG> <файл.svg> [ещё.svg ...]
const { chromium } = require('playwright')
const fs = require('node:fs')
const path = require('node:path')

async function main() {
  const [outDir, ...files] = process.argv.slice(2)
  if (!outDir || !files.length) {
    console.error('usage: node render.cjs <out dir> <file.svg> [...]')
    process.exit(2)
  }
  fs.mkdirSync(outDir, { recursive: true })
  const browser = await chromium.launch()
  for (const file of files) {
    const svg = fs.readFileSync(file, 'utf8')
    const m = svg.match(/viewBox="0 0 (\d+(?:\.\d+)?) (\d+(?:\.\d+)?)"/)
    const width = m ? Math.ceil(Number(m[1])) : 760
    const height = m ? Math.ceil(Number(m[2])) : 420
    const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 })
    await page.goto('file://' + path.resolve(file))
    const out = path.join(outDir, path.basename(file).replace(/\.svg$/i, '') + '.png')
    await page.screenshot({ path: out })
    await page.close()
    console.log('png', out)
  }
  await browser.close()
}

main().catch((e) => {
  console.error(e)
  process.exit(1)
})
