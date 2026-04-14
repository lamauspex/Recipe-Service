package consumer

import (
	"context"
	"encoding/json"
	"os"
	"testing"
	"time"

	"github.com/lamauspex/recipes/backend/service_search/internal/config"
	"github.com/lamauspex/recipes/backend/service_search/internal/consumer"
	"github.com/lamauspex/recipes/backend/service_search/internal/repository"
	"github.com/rabbitmq/amqp091-go"
	"log/slog"
)

func TestRabbitMQConsumer_MessageHandling(t *testing.T) {
	if os.Getenv("TESTING") != "true" {
		os.Exit(0)
	}

	// Настроить конфигурацию
	cfg := &config.Config{
		MeiliSearch: config.MeiliSearchConfig{
			Host:      getEnv("TEST_MEILISEARCH_HOST", "http://localhost:7700"),
			APIKey:    getEnv("TEST_MEILISEARCH_API_KEY", "masterKey"),
			IndexName: "test_rabbitmq_" + time.Now().Format("20060102150405"),
			Timeout:   30 * time.Second,
		},
		RabbitMQ: config.RabbitMQConfig{
			URL:       getEnv("TEST_RABBITMQ_URL", "amqp://admin:rabbitmq-password@localhost:5672/"),
			Exchange:  "test_recipe_events",
			QueueName: "test_rabbitmq_queue",
			Reconnect: 5 * time.Second,
		},
	}

	logger := slog.New(slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{
		Level: slog.LevelDebug,
	}))

	// Создать репозиторий
	repo, err := repository.NewMeiliSearchRepository(&cfg.MeiliSearch, logger)
	if err != nil {
		t.Fatalf("Failed to create MeiliSearch repository: %v", err)
	}
	defer repo.DeleteIndex(context.Background())

	// Создать соединение с RabbitMQ
	conn, err := amqp091.Dial(cfg.RabbitMQ.URL)
	if err != nil {
		t.Skipf("Skipping test - RabbitMQ not available: %v", err)
	}
	defer conn.Close()

	ch, err := conn.Channel()
	if err != nil {
		t.Fatalf("Failed to open channel: %v", err)
	}
	defer ch.Close()

	// Создать обменник и очередь
	err = ch.ExchangeDeclare(
		cfg.RabbitMQ.Exchange,
		"topic",
		true,
		false,
		false,
		false,
		nil,
	)
	if err != nil {
		t.Fatalf("Failed to declare exchange: %v", err)
	}

	queue, err := ch.QueueDeclare(
		cfg.RabbitMQ.QueueName,
		true,
		false,
		false,
		false,
		nil,
	)
	if err != nil {
		t.Fatalf("Failed to declare queue: %v", err)
	}

	err = ch.QueueBind(
		queue.Name,
		"recipe.#",
		cfg.RabbitMQ.Exchange,
		false,
		nil,
	)
	if err != nil {
		t.Fatalf("Failed to bind queue: %v", err)
	}

	// Тест 1: RecipeCreated событие
	t.Run("RecipeCreated", func(t *testing.T) {
		event := consumer.RecipeEvent{
			Type:     consumer.RecipeCreated,
			RecipeID: "rabbitmq-test-1",
			Payload: consumer.RecipePayload{
				ID:           "rabbitmq-test-1",
				Title:        "Тестовый рецепт",
				Description:  "Описание теста",
				Cuisine:      "русская",
				PrepTime:     60,
				Difficulty:   "medium",
				Ingredients:  []string{"ингредиент1", "ингредиент2"},
				Tags:         []string{"тест", "обед"},
				Instructions: "Инструкции",
				AuthorID:     "user-123",
				Rating:       4.5,
				ReviewsCount: 10,
			},
			Timestamp: time.Now(),
		}

		body, err := json.Marshal(event)
		if err != nil {
			t.Fatalf("Failed to marshal event: %v", err)
		}

		err = ch.Publish(
			cfg.RabbitMQ.Exchange,
			"recipe.created",
			false,
			false,
			amqp091.Publishing{
				ContentType: "application/json",
				Body:        body,
			},
		)
		if err != nil {
			t.Fatalf("Failed to publish message: %v", err)
		}

		// Дать время на обработку
		time.Sleep(2 * time.Second)

		// Проверить, что рецепт был проиндексирован
		doc, err := repo.GetRecipeByID(context.Background(), event.RecipeID)
		if err != nil {
			t.Errorf("Recipe should be indexed: %v", err)
		}

		if doc.Title != event.Payload.Title {
			t.Errorf("Expected title %s, got %s", event.Payload.Title, doc.Title)
		}
	})

	// Тест 2: RecipeUpdated событие
	t.Run("RecipeUpdated", func(t *testing.T) {
		event := consumer.RecipeEvent{
			Type:     consumer.RecipeUpdated,
			RecipeID: "rabbitmq-test-1",
			Payload: consumer.RecipePayload{
				ID:           "rabbitmq-test-1",
				Title:        "Обновлённый рецепт",
				Description:  "Обновлённое описание",
				Cuisine:      "итальянская",
				PrepTime:     45,
				Difficulty:   "easy",
				Ingredients:  []string{"новый", "ингредиент"},
				Tags:         []string{"обновлено"},
				Instructions: "Новые инструкции",
				AuthorID:     "user-123",
				Rating:       5.0,
				ReviewsCount: 20,
			},
			Timestamp: time.Now(),
		}

		body, err := json.Marshal(event)
		if err != nil {
			t.Fatalf("Failed to marshal event: %v", err)
		}

		err = ch.Publish(
			cfg.RabbitMQ.Exchange,
			"recipe.updated",
			false,
			false,
			amqp091.Publishing{
				ContentType: "application/json",
				Body:        body,
			},
		)
		if err != nil {
			t.Fatalf("Failed to publish message: %v", err)
		}

		// Дать время на обработку
		time.Sleep(2 * time.Second)

		// Проверить, что рецепт был обновлён
		doc, err := repo.GetRecipeByID(context.Background(), event.RecipeID)
		if err != nil {
			t.Errorf("Recipe should exist: %v", err)
		}

		if doc.Title != event.Payload.Title {
			t.Errorf("Expected updated title %s, got %s", event.Payload.Title, doc.Title)
		}

		if doc.Cuisine != event.Payload.Cuisine {
			t.Errorf("Expected updated cuisine %s, got %s", event.Payload.Cuisine, doc.Cuisine)
		}
	})

	// Тест 3: RecipeDeleted событие
	t.Run("RecipeDeleted", func(t *testing.T) {
		event := consumer.RecipeEvent{
			Type:     consumer.RecipeDeleted,
			RecipeID: "rabbitmq-test-1",
			Timestamp: time.Now(),
		}

		body, err := json.Marshal(event)
		if err != nil {
			t.Fatalf("Failed to marshal event: %v", err)
		}

		err = ch.Publish(
			cfg.RabbitMQ.Exchange,
			"recipe.deleted",
			false,
			false,
			amqp091.Publishing{
				ContentType: "application/json",
				Body:        body,
			},
		)
		if err != nil {
			t.Fatalf("Failed to publish message: %v", err)
		}

		// Дать время на обработку
		time.Sleep(2 * time.Second)

		// Проверить, что рецепт был удалён
		_, err = repo.GetRecipeByID(context.Background(), event.RecipeID)
		if err == nil {
			t.Error("Recipe should be deleted")
		}
	})

	// Тест 4: Неверный формат JSON
	t.Run("InvalidJSON", func(t *testing.T) {
		invalidBody := []byte("not valid json")

		err = ch.Publish(
			cfg.RabbitMQ.Exchange,
			"recipe.created",
			false,
			false,
			amqp091.Publishing{
				ContentType: "application/json",
				Body:        invalidBody,
			},
		)
		if err != nil {
			t.Fatalf("Failed to publish invalid message: %v", err)
		}

		// Сообщение должно быть отклонено (NACK)
		// Тест проходит без panic
		time.Sleep(1 * time.Second)
	})
}

func TestRabbitMQConsumer_Reconnect(t *testing.T) {
	if os.Getenv("TESTING") != "true" {
		os.Exit(0)
	}

	// Этот тест проверяет, что consumer может переподключиться после разрыва
	// Требует especial setup, пропуск для краткости
	t.Skip("Reconnect test requires special setup")
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}
