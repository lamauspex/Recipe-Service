package api

import (
	"context"
	"os"
	"testing"
	"time"

	"github.com/lamauspex/recipes/backend/service_search/internal/api"
	"github.com/lamauspex/recipes/backend/service_search/internal/config"
	"github.com/lamauspex/recipes/backend/service_search/internal/consumer"
	"github.com/lamauspex/recipes/backend/service_search/internal/repository"
	"github.com/lamauspex/recipes/backend/service_search/pkg/proto"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
	"google.golang.org/grpc/test/bufconn"
	emptypb "google.golang.org/protobuf/types/known/emptypb"
	"log/slog"
)

const bufSize = 1024 * 1024

var (
	lis   *bufconn.Listener
	server *api.SearchServer
)

func bufDialer(context.Context, string) (net.Conn, error) {
	return lis.Dial()
}

func TestMain(m *testing.M) {
	if os.Getenv("TESTING") != "true" {
		os.Exit(0)
	}

	// Настроить конфигурацию
	cfg := &config.Config{
		Server: config.ServerConfig{
			Host: "localhost",
			Port: 0, // Не используем реальный порт для буферного тестирования
		},
		MeiliSearch: config.MeiliSearchConfig{
			Host:      getEnv("TEST_MEILISEARCH_HOST", "http://localhost:7700"),
			APIKey:    getEnv("TEST_MEILISEARCH_API_KEY", "masterKey"),
			IndexName: "test_grpc_" + time.Now().Format("20060102150405"),
			Timeout:   30 * time.Second,
		},
		RabbitMQ: config.RabbitMQConfig{
			URL:       getEnv("TEST_RABBITMQ_URL", "amqp://admin:rabbitmq-password@localhost:5672/"),
			Exchange:  "test_events",
			QueueName: "test_queue",
		},
	}

	logger := slog.New(slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{
		Level: slog.LevelDebug,
	}))

	// Создать репозиторий
	repo, err := repository.NewMeiliSearchRepository(&cfg.MeiliSearch, logger)
	if err != nil {
		println("Failed to create MeiliSearch repository:", err.Error())
		os.Exit(1)
	}

	// Создать mock consumer
	mockConsumer := &consumer.RabbitMQConsumer{}

	// Создать сервер
	server = api.NewSearchServer(cfg, repo, mockConsumer, logger)

	// Буферный listener для тестов
	lis = bufconn.Listen(bufSize)

	// Запустить gRPC сервер в фоне
	grpcServer := grpc.NewServer()
	proto.RegisterSearchServiceServer(grpcServer, server)

	go func() {
		if err := grpcServer.Serve(lis); err != nil {
			println("gRPC server error:", err.Error())
		}
	}()

	// Запустить тесты
	code := m.Run()

	// Очистка
	grpcServer.Stop()
	repo.DeleteIndex(context.Background())

	os.Exit(code)
}

func TestSearchRecipes(t *testing.T) {
	// Индексировать тестовый рецепт
	doc := &repository.RecipeDocument{
		ID:          "grpc-test-1",
		Title:       "Паста Карбонара",
		Description: "Итальянская паста с беконом",
		Cuisine:     "итальянская",
		PrepTime:    30,
		Difficulty:  "easy",
		Ingredients: []string{"паста", "бекон", "яйца"},
		Tags:        []string{"обед", "ужин"},
		AuthorID:    "user-123",
		Rating:      4.8,
		ReviewsCount: 150,
	}

	ctx := context.Background()
	if err := server.(*api.SearchServer).Repo.IndexRecipe(ctx, doc); err != nil {
		t.Fatalf("Failed to index recipe: %v", err)
	}

	// Создать gRPC client
	conn, err := grpc.DialContext(ctx, "bufnet",
		grpc.WithContextDialer(bufDialer),
		grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		t.Fatalf("Failed to dial gRPC server: %v", err)
	}
	defer conn.Close()

	client := proto.NewSearchServiceClient(conn)

	// Тест: поиск с запросом
	searchReq := &proto.SearchRequest{
		Query: "паста",
		Page:  1,
		PageSize: 10,
	}

	resp, err := client.SearchRecipes(ctx, searchReq)
	if err != nil {
		t.Fatalf("SearchRecipes failed: %v", err)
	}

	if len(resp.Results) == 0 {
		t.Error("Expected at least one result")
	}

	if resp.Total < 1 {
		t.Error("Expected total >= 1")
	}

	// Тест: поиск с фильтрами
	filterReq := &proto.SearchRequest{
		Query: "",
		Page:  1,
		PageSize: 10,
		Cuisine: stringPtr("итальянская"),
		Difficulty: stringPtr("easy"),
	}

	filterResp, err := client.SearchRecipes(ctx, filterReq)
	if err != nil {
		t.Fatalf("SearchRecipes with filters failed: %v", err)
	}

	for _, recipe := range filterResp.Results {
		if recipe.Cuisine != "итальянская" {
			t.Errorf("Expected cuisine 'итальянская', got %s", recipe.Cuisine)
		}
		if recipe.Difficulty != "easy" {
			t.Errorf("Expected difficulty 'easy', got %s", recipe.Difficulty)
		}
	}

	// Тест: пагинация
	paginatedReq := &proto.SearchRequest{
		Query: "",
		Page:  2,
		PageSize: 1,
	}

	paginatedResp, err := client.SearchRecipes(ctx, paginatedReq)
	if err != nil {
		t.Fatalf("Paginated search failed: %v", err)
	}

	if paginatedResp.Page != 2 {
		t.Errorf("Expected page 2, got %d", paginatedResp.Page)
	}
}

func TestGetRecipe(t *testing.T) {
	// Индексировать рецепт
	doc := &repository.RecipeDocument{
		ID:           "grpc-get-test",
		Title:        "Борщ",
		Description:  "Русский суп",
		Cuisine:      "русская",
		PrepTime:     90,
		Difficulty:   "medium",
		Ingredients:  []string{"свёкла", "капуста"},
		Tags:         []string{"обед", "суп"},
		Instructions: "Приготовить борщ",
		AuthorID:     "user-123",
		Rating:       4.5,
		ReviewsCount: 50,
	}

	ctx := context.Background()
	if err := server.(*api.SearchServer).Repo.IndexRecipe(ctx, doc); err != nil {
		t.Fatalf("Failed to index recipe: %v", err)
	}

	// Создать client
	conn, err := grpc.DialContext(ctx, "bufnet",
		grpc.WithContextDialer(bufDialer),
		grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		t.Fatalf("Failed to dial: %v", err)
	}
	defer conn.Close()

	client := proto.NewSearchServiceClient(conn)

	// Тест: получить существующий рецепт
	req := &proto.GetRecipeRequest{
		Id: doc.ID,
	}

	resp, err := client.GetRecipe(ctx, req)
	if err != nil {
		t.Fatalf("GetRecipe failed: %v", err)
	}

	if resp.Id != doc.ID {
		t.Errorf("Expected ID %s, got %s", doc.ID, resp.Id)
	}

	if resp.Title != doc.Title {
		t.Errorf("Expected title %s, got %s", doc.Title, resp.Title)
	}

	// Тест: получить несуществующий рецепт
	invalidReq := &proto.GetRecipeRequest{
		Id: "non-existent-id",
	}

	_, err = client.GetRecipe(ctx, invalidReq)
	if err == nil {
		t.Error("Expected error for non-existent recipe")
	}
}

func TestGetSuggestions(t *testing.T) {
	// Индексировать рецепт
	doc := &repository.RecipeDocument{
		ID:          "grpc-suggestion-test",
		Title:       "Паста Карбонара",
		Description: "Итальянская паста",
		Cuisine:     "итальянская",
		PrepTime:    30,
		Difficulty:  "easy",
		Ingredients: []string{"паста", "бекон"},
		Tags:        []string{"обед"},
		AuthorID:    "user-123",
		Rating:      4.5,
		ReviewsCount: 10,
	}

	ctx := context.Background()
	if err := server.(*api.SearchServer).Repo.IndexRecipe(ctx, doc); err != nil {
		t.Fatalf("Failed to index recipe: %v", err)
	}

	// Создать client
	conn, err := grpc.DialContext(ctx, "bufnet",
		grpc.WithContextDialer(bufDialer),
		grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		t.Fatalf("Failed to dial: %v", err)
	}
	defer conn.Close()

	client := proto.NewSearchServiceClient(conn)

	// Тест: автодополнение
	req := &proto.SuggestionsRequest{
		Query: "паст",
		Type:  stringPtr("title"),
		Limit: 10,
	}

	resp, err := client.GetSuggestions(ctx, req)
	if err != nil {
		t.Fatalf("GetSuggestions failed: %v", err)
	}

	if len(resp.Suggestions) == 0 {
		t.Error("Expected suggestions")
	}
}

func TestHealth(t *testing.T) {
	ctx := context.Background()

	conn, err := grpc.DialContext(ctx, "bufnet",
		grpc.WithContextDialer(bufDialer),
		grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		t.Fatalf("Failed to dial: %v", err)
	}
	defer conn.Close()

	client := proto.NewSearchServiceClient(conn)

	resp, err := client.Health(ctx, &emptypb.Empty{})
	if err != nil {
		t.Fatalf("Health check failed: %v", err)
	}

	if resp.Status != "ok" && resp.Status != "degraded" {
		t.Errorf("Expected status 'ok' or 'degraded', got %s", resp.Status)
	}

	if resp.UptimeSeconds < 0 {
		t.Error("Expected uptime >= 0")
	}
}

// Helper функции
func stringPtr(s string) *string {
	return &s
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}
