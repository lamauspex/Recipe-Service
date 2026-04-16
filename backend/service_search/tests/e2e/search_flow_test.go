package e2e

import (
	"context"
	"encoding/json"
	"net"
	"os"
	"testing"
	"time"

	"log/slog"

	"github.com/lamauspex/recipes/backend/service_search/internal/config"
	"github.com/lamauspex/recipes/backend/service_search/internal/consumer"
	"github.com/lamauspex/recipes/backend/service_search/internal/repository"
	"github.com/lamauspex/recipes/backend/service_search/proto"
	"github.com/rabbitmq/amqp091-go"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
	"google.golang.org/grpc/test/bufconn"
)

// E2E тест: Полный цикл создания рецепта → индексация → поиск

const bufSize = 1024 * 1024

func TestFullRecipeSearchFlow(t *testing.T) {
	if os.Getenv("TESTING") != "true" {
		os.Exit(0)
	}

	// 1. Настройка инфраструктуры
	cfg := &config.Config{
		MeiliSearch: config.MeiliSearchConfig{
			Host:      getEnv("TEST_MEILISEARCH_HOST", "http://localhost:7700"),
			APIKey:    getEnv("TEST_MEILISEARCH_API_KEY", "masterKey"),
			IndexName: "test_e2e_" + time.Now().Format("20060102150405"),
			Timeout:   30 * time.Second,
		},
		RabbitMQ: config.RabbitMQConfig{
			URL:       getEnv("TEST_RABBITMQ_URL", "amqp://admin:rabbitmq-password@localhost:5672/"),
			Exchange:  "test_e2e_events",
			QueueName: "test_e2e_queue",
			Reconnect: 5 * time.Second,
		},
	}

	logger := slog.New(slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{
		Level: slog.LevelInfo,
	}))

	// 2. Создать MeiliSearch репозиторий
	repo, err := repository.NewMeiliSearchRepository(&cfg.MeiliSearch, logger)
	if err != nil {
		t.Fatalf("Failed to create MeiliSearch repository: %v", err)
	}
	defer repo.DeleteIndex(context.Background())

	// 3. Создать соединение с RabbitMQ
	conn, err := amqp091.Dial(cfg.RabbitMQ.URL)
	if err != nil {
		t.Skipf("Skipping E2E test - RabbitMQ not available: %v", err)
	}
	defer conn.Close()

	ch, err := conn.Channel()
	if err != nil {
		t.Fatalf("Failed to open channel: %v", err)
	}
	defer ch.Close()

	// 4. Создать exchange и queue
	err = ch.ExchangeDeclare(cfg.RabbitMQ.Exchange, "topic", true, false, false, false, nil)
	if err != nil {
		t.Fatalf("Failed to declare exchange: %v", err)
	}

	queue, err := ch.QueueDeclare(cfg.RabbitMQ.QueueName, true, false, false, false, nil)
	if err != nil {
		t.Fatalf("Failed to declare queue: %v", err)
	}

	err = ch.QueueBind(queue.Name, "recipe.#", cfg.RabbitMQ.Exchange, false, nil)
	if err != nil {
		t.Fatalf("Failed to bind queue: %v", err)
	}

	// 5. Запустить consumer в фоне
	consumer, err := consumer.NewRabbitMQConsumer(&cfg.RabbitMQ, repo, logger)
	if err != nil {
		t.Fatalf("Failed to create consumer: %v", err)
	}

	go func() {
		if err := consumer.Start(); err != nil {
			t.Errorf("Consumer error: %v", err)
		}
	}()
	defer consumer.Stop()

	// 6. ЗАПУСК ТЕСТА: Recipe Service создаёт рецепт и публикует событие
	t.Log("Step 1: Recipe Service создаёт рецепт")

	event := consumer.RecipeEvent{
		Type:     consumer.RecipeCreated,
		RecipeID: "e2e-test-recipe-1",
		Payload: consumer.RecipePayload{
			ID:           "e2e-test-recipe-1",
			Title:        "ДомашняяPizza Маргарита",
			Description:  "Классическая итальянская пицца с томатами и моцареллой",
			Cuisine:      "итальянская",
			PrepTime:     45,
			Difficulty:   "medium",
			Ingredients:  []string{"тесто", "томаты", "моцарелла", "базилик"},
			Tags:         []string{"ужин", "пицца", "италия"},
			Instructions: "Приготовить тесто, добавить томаты и моцареллу, запекать 15 минут",
			AuthorID:     "user-e2e-123",
			Rating:       4.9,
			ReviewsCount: 250,
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
		t.Fatalf("Failed to publish event: %v", err)
	}

	t.Log("Step 2: Событие опубликовано в RabbitMQ")

	// 7. Ожидать обработки события
	time.Sleep(3 * time.Second)

	// 8. Проверяем: Search Service проиндексировал рецепт
	t.Log("Step 3: Search Service обработал событие")

	doc, err := repo.GetRecipeByID(context.Background(), event.RecipeID)
	if err != nil {
		t.Fatalf("Recipe should be indexed: %v", err)
	}

	if doc.Title != event.Payload.Title {
		t.Errorf("Title mismatch: expected %s, got %s", event.Payload.Title, doc.Title)
	}

	if doc.Cuisine != event.Payload.Cuisine {
		t.Errorf("Cuisine mismatch: expected %s, got %s", event.Payload.Cuisine, doc.Cuisine)
	}

	t.Log("Step 4: Рецепт успешно проиндексирован")

	// 9. Тестируем поиск через gRPC
	t.Log("Step 5: Тестирование gRPC поиска")

	// Буферный listener для gRPC
	lis := bufconn.Listen(bufSize)
	grpcServer := grpc.NewServer()
	defer grpcServer.Stop()

	// TODO: зарегистрировать сервер (требует refactoring)

	go func() {
		_ = grpcServer.Serve(lis)
	}()

	connGRPC, err := grpc.DialContext(context.Background(), "bufnet",
		grpc.WithContextDialer(func(ctx context.Context, s string) (net.Conn, error) {
			return lis.Dial()
		}),
		grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		t.Fatalf("Failed to dial gRPC: %v", err)
	}
	defer connGRPC.Close()

	client := proto.NewSearchServiceClient(connGRPC)

	// Поиск по названию
	searchResp, err := client.SearchRecipes(context.Background(), &proto.SearchRequest{
		Query:    "пицца",
		Page:     1,
		PageSize: 10,
	})
	if err != nil {
		t.Fatalf("Search failed: %v", err)
	}

	if len(searchResp.Results) == 0 {
		t.Error("Expected search results for 'пицца'")
	}

	found := false
	for _, result := range searchResp.Results {
		if result.Id == event.RecipeID {
			found = true
			break
		}
	}

	if !found {
		t.Error("Expected to find our recipe in search results")
	}

	t.Log("Step 6: Поиск работает корректно")

	// 10. Тест: обновление рецепта
	t.Log("Step 7: Обновление рецепта")

	updateEvent := consumer.RecipeEvent{
		Type:     consumer.RecipeUpdated,
		RecipeID: "e2e-test-recipe-1",
		Payload: consumer.RecipePayload{
			ID:           "e2e-test-recipe-1",
			Title:        "Домашняя Пицца Маргарита (Обновлённая)",
			Description:  "Обновлённое описание",
			Cuisine:      "итальянская",
			PrepTime:     40,
			Difficulty:   "easy",
			Ingredients:  []string{"тесто", "томаты", "моцарелла", "базилик", "оливковое масло"},
			Tags:         []string{"ужин", "пицца", "италия", "лёгко"},
			Instructions: "Новые инструкции",
			AuthorID:     "user-e2e-123",
			Rating:       5.0,
			ReviewsCount: 300,
		},
		Timestamp: time.Now(),
	}

	body, err = json.Marshal(updateEvent)
	if err != nil {
		t.Fatalf("Failed to marshal update event: %v", err)
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
		t.Fatalf("Failed to publish update event: %v", err)
	}

	time.Sleep(3 * time.Second)

	updatedDoc, err := repo.GetRecipeByID(context.Background(), updateEvent.RecipeID)
	if err != nil {
		t.Fatalf("Recipe should exist after update: %v", err)
	}

	if updatedDoc.Rating != updateEvent.Payload.Rating {
		t.Errorf("Rating not updated: expected %f, got %f", updateEvent.Payload.Rating, updatedDoc.Rating)
	}

	t.Log("Step 8: Рецепт успешно обновлён")

	// 11. Тест: удаление рецепта
	t.Log("Step 9: Удаление рецепта")

	deleteEvent := consumer.RecipeEvent{
		Type:      consumer.RecipeDeleted,
		RecipeID:  "e2e-test-recipe-1",
		Timestamp: time.Now(),
	}

	body, err = json.Marshal(deleteEvent)
	if err != nil {
		t.Fatalf("Failed to marshal delete event: %v", err)
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
		t.Fatalf("Failed to publish delete event: %v", err)
	}

	time.Sleep(3 * time.Second)

	_, err = repo.GetRecipeByID(context.Background(), deleteEvent.RecipeID)
	if err == nil {
		t.Error("Recipe should be deleted")
	}

	t.Log("Step 10: Рецепт успешно удалён")

	t.Log("✓ E2E тест пройден: создание → индексация → поиск → обновление → удаление")
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}
