# Трейдинг с нуля — приложение (версия 1)

Учебное PWA-приложение по программе из папки `Трейдинг_с_нуля`. React + TypeScript + Vite,
данные на устройстве (IndexedDB через Dexie), без сервера и регистрации.

## Запуск
```bash
npm install
npm run dev       # http://localhost:5173
npm run build     # production-сборка в dist/ (сначала пересобирает контент)
npm run preview   # проверка production-сборки
```

## Что есть в версии 1 (+ уровень профи)
- Главная: текущий урок, кнопка «Продолжить обучение», прогресс, список ступеней (закрытые с замком).
- Ступень 01 полностью: 5 уроков с заданием под каждым, учебный график BTC/ETH (1D, 4H, EMA 20/50/200, объём),
  практика-чеклист для демосчёта, тест (8 вопросов, порог 80%, перемешивание, разбор ошибок).
- Уровень профи (папка `09_Уровень_профи`): 9 уроков, расчётные задания, практика по журналу, тест на 12 вопросов. Открыт без прохождения ступеней 01–06.
- Калькулятор риска: депозит, риск %, вход, стоп, тейк → размер позиции, 1R, R:R, прибыль при тейке.
- Монте-Карло: винрейт, средние W/L, риск, число сделок → распределение просадок и итогов, проверка риска по пределу просадки.
- Справочник: глоссарий с поиском, шпаргалка индикаторов, чек-лист перед сделкой.
- Настройки: тема (система/светлая/тёмная), экспорт и импорт JSON, сброс прогресса.
- PWA: устанавливается на главный экран, работает офлайн после первой загрузки.

## Контент
- `scripts/build-content.mjs` собирает уроки, практику и справочник из Markdown-папок `../01_…` — `../07_…`
  в `src/content/*.generated.json`. Правьте Markdown в папках курса, затем `npm run content`.
- Тесты: `src/content/tests/0X.json` (формат из `08_Приложение_ТЗ/06_Формат_заданий.md`).
  Задания под уроками: `src/content/lessonTasks.json`.
- Свечи: `public/charts/*.json`, загружены один раз скриптом `npm run candles` (Binance, с 2019 года).
  Приложение в работе к бирже не обращается.
- Какие ступени открыты в текущей версии: `AVAILABLE_STEPS` в `src/content/index.ts`.
- Порядок прохождения жёсткий: тест открывается только после всех уроков и практики ступени.

## Структура
```
src/
  content/      контент (JSON) и индекс
  lib/          db.ts (Dexie), progress.ts (логика открытия ступеней), calc.ts (формула позиции), theme.ts
  components/   Layout (нижнее/боковое меню), CandleChart, ChoiceTask, Markdown, ProgressBar
  pages/        Home, Step, Lesson, Practice, Test, Risk, Reference, Journal (заглушка), Settings
scripts/        build-content, fetch-candles, make-icons
```

## Публикация на Railway
Сайт: https://web-production-045f4.up.railway.app (проект `trading-from-zero`, сервис `web`).
Деплой идёт прямо из папки `app` через Railway CLI, GitHub не обязателен:
```bash
railway up --service web --detach   # загрузить и собрать текущую версию
railway logs --build --service web  # лог сборки
railway domain --service web        # показать или создать домен
```
Сборка на Railway использует сохранённый контент из `src/content/*.generated.json` (папок курса там нет),
поэтому после правок Markdown сначала `npm run content`, затем `railway up`.
На iPhone: открыть адрес в Safari → Поделиться → «На экран Домой».

## iOS (Capacitor)
Проект под iOS уже создан в папке `ios/` (Capacitor 6, пакеты через Swift Package Manager, CocoaPods не нужен).
Выбран Capacitor 6, потому что он работает с Xcode 15, а Capacitor 7–8 требуют Xcode 16 и macOS 14+.

Что нужно на Mac:
1. Xcode 15.2 (последний для macOS 13). В App Store его нет, скачайте вручную: https://developer.apple.com/download/all/ → «Xcode 15.2» (нужен бесплатный Apple ID).
   Распакуйте в /Applications, затем один раз:
   ```bash
   sudo xcode-select -s /Applications/Xcode.app
   sudo xcodebuild -runFirstLaunch
   ```
2. Для запуска на своём iPhone — бесплатный Apple ID в Xcode (Settings → Accounts). Для App Store — платный Apple Developer Program.

Сборка и запуск:
```bash
npm run build          # веб-сборка в dist/
npx cap sync ios       # копирует dist/ в ios/App/App/public
npx cap open ios       # открывает проект в Xcode
```
В Xcode: выберите симулятор или подключённый iPhone → Run. Подпись: Target App → Signing & Capabilities → Team.
Для публикации: Product → Archive → Distribute App (нужен аккаунт разработчика и запись приложения в App Store Connect).

Без Xcode приложение можно поставить на iPhone как PWA: откройте опубликованную веб-версию в Safari → Поделиться → «На экран Домой».
Для этого веб-сборка должна лежать на https-домене с `manifest.webmanifest` и `sw.js` (это обычный `npm run build`, папка `dist/`).

## Дальше (по 04_Этапы_разработки.md)
- Версия 2: ступени 02–03, журнал сделок с обязательным чек-листом, дневной лимит.
- Версия 3: ступени 04–05, статистика, разбор стратегий (20 сделок с меткой).
- Версия 4: ступень 06, экран допуска к реальным деньгам, недельный разбор.
- Магазины: Capacitor (Android, iOS).
