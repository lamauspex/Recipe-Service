# Тесты Search Service

## 🚀 Типы тестов

### Unit тесты
Тестируют отдельные компоненты без внешних зависимостей:
- Конфигурация
- Мапперы и валидаторы
- Утилиты

**Запуск:**
```bash
go test -v ./tests/unit/...
```

### Integration тесты
Тестируют взаимодействие с реальными сервисами:
- MeiliSearch репозиторий
- RabbitMQ consumer
- gRPC сервер

**Запуск (требуется Docker):**
```bash
# Запустить инфраструктуру
docker compose -f docker/compose.infra.yml up -d

# Запустить тесты
go test -v ./tests/integration/...

# Остановить инфраструктуру
docker compose -f docker/compose.infra.yml down
```

### E2E тесты
Полный цикл: событие → индексация → поиск

**Запуск:**
```bash
go test -v ./tests/e2e/...
```

## 📊 Покрытие кода

```bash
# С покрытием
go test -cover ./tests/...

# С генерацией HTML отчёта
go test -coverprofile=coverage.out ./tests/...
go tool cover -html=coverage.out -o coverage.html
```

## 🎯 Фильтрация тестов

```bash
# Только unit тесты
go test -v -run "TestUnit" ./tests/...

# Только интеграционные тесты
go test -v -run "TestIntegration" ./tests/...

# Конкретный тест
go test -v -run "TestSearchRecipes" ./tests/integration/...
```

## 🔧 Тестовые данные

Все тестовые данные находятся в `testdata/`:
- `recipes.json` — примеры рецептов
- `events.json` — примеры RabbitMQ событий

## ⚙️ Переменные окружения

Для интеграционных тестов:
```env
TEST_MEILISEARCH_HOST=http://localhost:7700
TEST_RABBITMQ_URL=amqp://admin:rabbitmq-password@localhost:5672/
TESTING=true
```
