# Интеграционные тесты Service Search

## 🚀 Запуск

### Предварительные требования
- Docker и Docker Compose
- Go 1.21+

### 1. Запустить инфраструктуру

```bash
# Запустить MeiliSearch и RabbitMQ
docker compose -f docker/compose.infra.yml up -d

# Проверить что сервисы работают
docker compose -f docker/compose.infra.yml ps
```

### 2. Запустить тесты

```bash
# Все интеграционные тесты
INTEGRATION=true go test -v -tags=integration ./tests/integration/...

# Конкретный тест
INTEGRATION=true go test -v -tags=integration ./tests/integration/ -run TestSearch

# С покрытием кода
INTEGRATION=true go test -v -cover -tags=integration ./tests/integration/...
```

### 3. Остановить инфраструктуру

```bash
docker compose -f docker/compose.infra.yml down
```

## 📝 Тесты

### MeiliSearch тесты (`meilisearch_test.go`)
- `TestIndexRecipe` — индексация рецепта
- `TestDeleteRecipe` — удаление рецепта
- `TestSearch` — поиск с фильтрами и пагинацией
- `TestSuggestions` — автодополнение
- `TestHealth` — проверка здоровья

## 🔧 Переменные окружения

```env
# MeiliSearch
TEST_MEILISEARCH_HOST=http://localhost:7700
TEST_MEILISEARCH_API_KEY=masterKey

# Флаги
INTEGRATION=true
```

## ⚠️ Важно

- Тесты создают временный индекс `test_recipes_*`
- Индекс удаляется после выполнения тестов
- Не запускайте тесты на продакшене!
