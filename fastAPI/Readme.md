# Spimex Trading API

FastAPI-приложение для получения данных о биржевых торгах с кэшированием в Redis и хранением в PostgreSQL.

## Запуск через Docker

### Предварительные требования

- Установленный Docker Desktop (или Docker Engine + Docker Compose)
- Git (опционально)
- 2-4 ГБ свободной оперативной памяти

### Старт приложения

1. **Клонируйте репозиторий** (или создайте папку с проектом):
   ```bash
   git clone https://github.com/your-username/spimex-trading-api.git
   cd spimex-trading-api
   
2. **Создайте файл** '.env' на основе .env.docker:
   ```bash
   cp .env.docker .env
При необходимости отредактируйте значения в .env.

3 **Запустите проект одной командой**```:
```bash
   docker-compose up -d