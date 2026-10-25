// Иконка 1024×1024 без альфа-канала и экран запуска 2732×2732 для iOS, без внешних зависимостей.
import { writeFileSync } from 'node:fs'
import { deflateSync } from 'node:zlib'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const assets = join(here, '..', 'ios', 'App', 'App', 'Assets.xcassets')

const crcTable = new Int32Array(256).map((_, n) => {
  let c = n
  for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1
  return c
})
const crc32 = (buf) => {
  let c = -1
  for (const b of buf) c = crcTable[(c ^ b) & 0xff] ^ (c >>> 8)
  return (c ^ -1) >>> 0
}
const chunk = (type, data) => {
  const len = Buffer.alloc(4)
  len.writeUInt32BE(data.length)
  const td = Buffer.concat([Buffer.from(type), data])
  const crc = Buffer.alloc(4)
  crc.writeUInt32BE(crc32(td))
  return Buffer.concat([len, td, crc])
}

const BLUE = [0x2b, 0x5f, 0xd9]
const WHITE = [0xff, 0xff, 0xff]
// Логотип: три свечи в координатах сетки 64×64
const LOGO = [
  [14, 26, 8, 18], [17, 18, 2, 30],
  [28, 16, 8, 22], [31, 10, 2, 36],
  [42, 22, 8, 14], [45, 14, 2, 30],
]

function pngRGB(size, bg, fg, logoScale, logoOffset) {
  const row = size * 3 + 1
  const raw = Buffer.alloc(row * size)
  const rects = LOGO.map(([x, y, w, h]) => [x * logoScale + logoOffset, y * logoScale + logoOffset, w * logoScale, h * logoScale])
  for (let y = 0; y < size; y++) {
    raw[y * row] = 0
    for (let x = 0; x < size; x++) {
      let c = bg
      for (const [rx, ry, rw, rh] of rects) if (x >= rx && x < rx + rw && y >= ry && y < ry + rh) { c = fg; break }
      const i = y * row + 1 + x * 3
      raw[i] = c[0]; raw[i + 1] = c[1]; raw[i + 2] = c[2]
    }
  }
  const ihdr = Buffer.alloc(13)
  ihdr.writeUInt32BE(size, 0); ihdr.writeUInt32BE(size, 4)
  ihdr[8] = 8; ihdr[9] = 2; ihdr[10] = 0; ihdr[11] = 0; ihdr[12] = 0
  return Buffer.concat([
    Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]),
    chunk('IHDR', ihdr),
    chunk('IDAT', deflateSync(raw, { level: 9 })),
    chunk('IEND', Buffer.alloc(0)),
  ])
}

// Иконка: логотип на весь квадрат (iOS сам скругляет углы)
writeFileSync(join(assets, 'AppIcon.appiconset', 'AppIcon-512@2x.png'), pngRGB(1024, BLUE, WHITE, 16, 0))
// Экран запуска: логотип по центру, размером ~ четверть экрана
const splash = pngRGB(2732, BLUE, WHITE, 10, (2732 - 640) / 2)
for (const name of ['splash-2732x2732.png', 'splash-2732x2732-1.png', 'splash-2732x2732-2.png']) {
  writeFileSync(join(assets, 'Splash.imageset', name), splash)
}
console.log('iOS-иконка и экран запуска созданы')
