# Search Service

Сервис поиска и индексации рецептов на Go с использованием MeiliSearch и RabbitMQ.

## 🟢 Технологический стек

| Компонент | Технология |
|-----------|------------|
| Язык | Go 1.23 |
| gRPC | grpc-go |
| Поиск | MeiliSearch v1.11 |
| Очереди | RabbitMQ (amqp091-go) |
| Конфигурация | Viper |

## 🟢 Функциональность

- **Полнотекстовый поиск** рецептов по названию, описанию, ингредиентам
- **Фильтрация** по кухне, времени приготовления, сложности
- **Автодополнение** (suggestions) для title, ingredients, tags, cuisine
- **Ранжирование** результатов по релевантности
- **Индексация в реальном времени** через RabbitMQ события

## 🟢 gRPC Endpoints

### SearchRecipes
```protobuf
rpc SearchRecipes (SearchRequest) returns (SearchResponse);
```

**SearchRequest:**
- `query` - полнотекстовый запрос
- `page` - номер страницы (начинается с 1)
- `page_size` - размер страницы (макс. 100)
- `cuisine` - фильтр по кухне (опционально)
- `max_prep_time` - максимальное время приготовления (опционально)
- `difficulty` - сложность: easy, medium, hard (опционально)
- `ingredients` - список ингредиентов (опционально)
- `tags` - список тегов (опционально)

**SearchResponse:**
- `results` - список рецептов
- `total` - общее количество результатов
- `page` - текущая страница
- `page_size` - размер страницы
- `total_pages` - всего страниц

### GetRecipe
```protobuf
rpc GetRecipe (GetRecipeRequest) returns (RecipeResponse);
```

### GetSuggestions
```protobuf
rpc GetSuggestions (SuggestionsRequest) returns (SuggestionsResponse);
```

**SuggestionsRequest:**
- `query` - частичный запрос
- `type` - тип: "title", "ingredients", "tags", "cuisine" (опционально)
- `limit` - максимальное количество предложений (по умолчанию 10)

### Health
```protobuf
rpc Health (google.protobuf.Empty) returns (HealthResponse);
```

## 🟢 RabbitMQ События

Сервис подписывается на события из обменника `recipe_events`:

| Тип события | Описание |
|-------------|----------|
| `recipe.created` | Новый рецепт создан |
| `recipe.updated` | Рецепт обновлён |
| `recipe.deleted` | Рецепт удалён |

## 🟢 Переменные окружения

```env
# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8002

# gRPC
GRPC_PORT=50052

# MeiliSearch
MEILISEARCH_HOST=http://meilisearch:7700
MEILISEARCH_API_KEY=meili-master-key-secure-change-me
MEILISEARCH_INDEX=recipes
MEILISEARCH_TIMEOUT=30

# RabbitMQ
RABBITMQ_URL=amqp://admin:rabbitmq-password@rabbitmq:5672/
RABBITMQ_EXCHANGE=recipe_events
RABBITMQ_QUEUE=search_service_queue

# Logging
LOG_LEVEL=info
LOG_FORMAT=json
```

## 🟢 Запуск

### Локально (разработка)

```bash
# Установка зависимостей
go mod download

# Запуск
go run ./cmd/server/main.go
```

### Docker

```bash
# Сборка и запуск
docker compose -f docker/compose.yaml up -d service_search

# Просмотр логов
docker logs -f service_search
```

## 🟢 Интеграция с Recipe Service

Для отправки событий из Recipe Service в RabbitMQ:

```go
// Пример публикации события
event := consumer.RecipeEvent{
    Type:     consumer.RecipeCreated,
    RecipeID: recipe.ID,
    Payload: consumer.RecipePayload{
        ID:          recipe.ID,
        Title:       recipe.Title,
        // ... остальные поля
    },
    Timestamp: time.Now(),
}

body, _ := json.Marshal(event)
channel.Publish(
    "recipe_events",
    "recipe.created",
    false,
    false,
    amqp091.Publishing{
        ContentType: "application/json",
        Body:        body,
    },
)
```

## 🟢 MeiliSearch настройки

После запуска MeiliSearch создаёт индекс `recipes` со следующими настройками:

- **Фильтруемые атрибуты**: `cuisine`, `difficulty`, `prep_time`, `tags`, `ingredients`
- **Сортируемые атрибуты**: `rating`, `reviews_count`, `prep_time`
- **Поисковые атрибуты**: `title`, `description`, `ingredients`, `tags`
- **Синонимы**: настраиваются при необходимости

## 🟢 Тестирование

```bash
# gRPC клиент тест
go run ./tests/client/main.go

# Интеграционные тесты
go test -v ./tests/...
```

---

**Автор**: Резник Кирилл  
**Email**: lamauspex@yandex.ru
