# Админ-панель — frontend

React 19 · TypeScript 6 · Vite 8 · pnpm. Интерфейс администратора системы учёта посещаемости.

## Требования

- Node.js ≥ 22.12
- pnpm 10 (`corepack enable` — версия подтянется из `packageManager`)
- Запущенный бэкенд (`docker compose up` в корне репозитория → `http://localhost:8000`)

## Запуск

```bash
cd frontend
corepack enable
pnpm install
cp .env.example .env
pnpm dev                    # http://localhost:5173
```

## Команды

| Команда                                              | Что делает                               |
| ---------------------------------------------------- | ---------------------------------------- |
| `pnpm dev` / `pnpm build` / `pnpm preview`           | разработка / сборка / просмотр сборки    |
| `pnpm typecheck` · `pnpm lint` · `pnpm format:check` | проверки                                 |
| `pnpm check`                                         | все проверки подряд (запускать перед PR) |
| `pnpm format`                                        | автоформатирование Prettier              |
| `pnpm deps:outdated` · `pnpm deps:audit`             | устаревшие пакеты / уязвимости           |

## Структура

```
src/app       роутинг, стили, точка входа
src/layout    каркас с боковой навигацией
src/shared    api-клиент, ui-kit, утилиты
src/features  auth · catalog · students · codes · devices · events · apk
```
