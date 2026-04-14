package repository

import (
	"context"
	"os"
	"testing"
	"time"

	"github.com/lamauspex/recipes/backend/service_search/internal/config"
	"github.com/lamauspex/recipes/backend/service_search/internal/repository"
	"log/slog"
)

var (
	testRepo *repository.MeiliSearchRepository
	testCfg  *config.MeiliSearchConfig
)

func TestMain(m *testing.M) {
	// Пропускать тесты если TESTING=false
	if os.Getenv("TESTING") != "true" {
		os.Exit(0)
	}

	// Настроить тестовую конфигурацию
	testCfg = &config.MeiliSearchConfig{
		Host:      getEnv("TEST_MEILISEARCH_HOST", "http://localhost:7700"),
		APIKey:    getEnv("TEST_MEILISEARCH_API_KEY", "masterKey"),
		IndexName: "test_recipes_" + time.Now().Format("20060102150405"),
		Timeout:   30 * time.Second,
	}

	// Создать репозиторий
	logger := slog.New(slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{
		Level: slog.LevelDebug,
	}))

	var err error
	testRepo, err = repository.NewMeiliSearchRepository(testCfg, logger)
	if err != nil {
		println("Failed to create MeiliSearch repository:", err.Error())
		os.Exit(1)
	}

	// Запустить тесты
	code := m.Run()

	// Очистка
	testRepo.DeleteIndex(context.Background())

	os.Exit(code)
}

func TestIndexRecipe(t *testing.T) {
	doc := &repository.RecipeDocument{
		ID:           "test-recipe-1",
		Title:        "Паста Карбонара",
		Description:  "Классическая итальянская паста с беконом и яйцами",
		Cuisine:      "итальянская",
		PrepTime:     30,
		Difficulty:   "easy",
		Ingredients:  []string{"паста", "бекон", "яйца", "пармезан"},
		Tags:         []string{"обед", "ужин", "быстро"},
		Instructions: "Сварить пасту, обжарить бекон, смешать...",
		AuthorID:     "user-123",
		Rating:       4.8,
		ReviewsCount: 150,
		CreatedAt:    time.Now().Format(time.RFC3339),
		UpdatedAt:    time.Now().Format(time.RFC3339),
	}

	err := testRepo.IndexRecipe(context.Background(), doc)
	if err != nil {
		t.Fatalf("Failed to index recipe: %v", err)
	}

	// Проверить, что рецепт был найден
	found, err := testRepo.GetRecipeByID(context.Background(), doc.ID)
	if err != nil {
		t.Fatalf("Failed to get recipe: %v", err)
	}

	if found.ID != doc.ID {
		t.Errorf("Expected ID %s, got %s", doc.ID, found.ID)
	}

	if found.Title != doc.Title {
		t.Errorf("Expected title %s, got %s", doc.Title, found.Title)
	}
}

func TestDeleteRecipe(t *testing.T) {
	// Сначала создать рецепт
	doc := &repository.RecipeDocument{
		ID:           "test-recipe-delete",
		Title:        "Борщ",
		Description:  "Тестовый рецепт для удаления",
		Cuisine:      "русская",
		PrepTime:     90,
		Difficulty:   "medium",
		Ingredients:  []string{"свёкла", "капуста", "картофель"},
		Tags:         []string{"обед"},
		Instructions: "Приготовить борщ...",
		AuthorID:     "user-123",
		Rating:       4.5,
		ReviewsCount: 50,
		CreatedAt:    time.Now().Format(time.RFC3339),
		UpdatedAt:    time.Now().Format(time.RFC3339),
	}

	err := testRepo.IndexRecipe(context.Background(), doc)
	if err != nil {
		t.Fatalf("Failed to index recipe: %v", err)
	}

	// Удалить рецепт
	err = testRepo.DeleteRecipe(context.Background(), doc.ID)
	if err != nil {
		t.Fatalf("Failed to delete recipe: %v", err)
	}

	// Проверить, что рецепт не найден
	_, err = testRepo.GetRecipeByID(context.Background(), doc.ID)
	if err == nil {
		t.Error("Expected error when getting deleted recipe, got nil")
	}
}

func TestSearch(t *testing.T) {
	// Индексировать тестовые рецепты
	recipes := []*repository.RecipeDocument{
		{
			ID:          "search-test-1",
			Title:       "Паста Карбонара",
			Description: "Итальянская паста с беконом",
			Cuisine:     "итальянская",
			PrepTime:    30,
			Difficulty:  "easy",
			Tags:        []string{"обед", "ужин"},
		},
		{
			ID:          "search-test-2",
			Title:       "Борщ",
			Description: "Русский суп со свёклой",
			Cuisine:     "русская",
			PrepTime:    90,
			Difficulty:  "medium",
			Tags:        []string{"обед", "суп"},
		},
		{
			ID:          "search-test-3",
			Title:       "Салат Цезарь",
			Description: "Лёгкий салат с курицей",
			Cuisine:     "американская",
			PrepTime:    20,
			Difficulty:  "easy",
			Tags:        []string{"завтрак", "салат"},
		},
	}

	for _, doc := range recipes {
		doc.AuthorID = "user-123"
		doc.Ingredients = []string{"тест"}
		doc.Instructions = "тест"
		doc.Rating = 4.5
		doc.ReviewsCount = 10
		doc.CreatedAt = time.Now().Format(time.RFC3339)
		doc.UpdatedAt = time.Now().Format(time.RFC3339)

		if err := testRepo.IndexRecipe(context.Background(), doc); err != nil {
			t.Fatalf("Failed to index recipe %s: %v", doc.ID, err)
		}
	}

	// Тест 1: Поиск по запросу
	result, err := testRepo.Search(context.Background(), "паста", nil, 1, 10)
	if err != nil {
		t.Fatalf("Search failed: %v", err)
	}

	if len(result.Recipes) == 0 {
		t.Error("Expected at least one result for 'паста'")
	}

	// Тест 2: Поиск с фильтром по кухне
	filters := &repository.SearchFilters{
		Cuisine: "итальянская",
	}
	result, err = testRepo.Search(context.Background(), "", filters, 1, 10)
	if err != nil {
		t.Fatalf("Search with filter failed: %v", err)
	}

	for _, recipe := range result.Recipes {
		if recipe.Cuisine != "итальянская" {
			t.Errorf("Expected cuisine 'итальянская', got %s", recipe.Cuisine)
		}
	}

	// Тест 3: Поиск с фильтром по времени
	filters = &repository.SearchFilters{
		MaxPrepTime: 30,
	}
	result, err = testRepo.Search(context.Background(), "", filters, 1, 10)
	if err != nil {
		t.Fatalf("Search with prep time filter failed: %v", err)
	}

	for _, recipe := range result.Recipes {
		if recipe.PrepTime > 30 {
			t.Errorf("Expected prep_time <= 30, got %d", recipe.PrepTime)
		}
	}

	// Тест 4: Пагинация
	result, err = testRepo.Search(context.Background(), "", nil, 2, 1)
	if err != nil {
		t.Fatalf("Pagination search failed: %v", err)
	}

	if result.Page != 2 {
		t.Errorf("Expected page 2, got %d", result.Page)
	}
}

func TestSuggestions(t *testing.T) {
	// Индексировать рецепты для тестов suggestions
	doc := &repository.RecipeDocument{
		ID:           "suggestion-test",
		Title:        "Паста Карбонара",
		Description:  "Итальянская паста",
		Cuisine:      "итальянская",
		PrepTime:     30,
		Difficulty:   "easy",
		Ingredients:  []string{"паста", "бекон", "яйца"},
		Tags:         []string{"обед", "ужин"},
		Instructions: "Приготовить пасту",
		AuthorID:     "user-123",
		Rating:       4.5,
		ReviewsCount: 10,
		CreatedAt:    time.Now().Format(time.RFC3339),
		UpdatedAt:    time.Now().Format(time.RFC3339),
	}

	if err := testRepo.IndexRecipe(context.Background(), doc); err != nil {
		t.Fatalf("Failed to index recipe: %v", err)
	}

	// Тест: Автодополнение по названию
	suggestions, err := testRepo.GetSuggestions(context.Background(), "паст", "title", 10)
	if err != nil {
		t.Fatalf("Suggestions failed: %v", err)
	}

	if len(suggestions) == 0 {
		t.Error("Expected suggestions for 'паст'")
	}
}

func TestHealth(t *testing.T) {
	health, err := testRepo.Health(context.Background())
	if err != nil {
		t.Fatalf("Health check failed: %v", err)
	}

	if !health.Healthy {
		t.Error("Expected MeiliSearch to be healthy")
	}
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}
