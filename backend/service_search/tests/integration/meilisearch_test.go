package integration

import (
	"context"
	"os"
	"testing"
	"time"

	"log/slog"

	"github.com/lamauspex/recipes/backend/service_search/internal/config"
	"github.com/lamauspex/recipes/backend/service_search/internal/repository/meilisearch"
)

var (
	testRepo *meilisearch.MeiliSearchRepository
	testCfg  *config.MeiliSearchConfig
)

func TestMain(m *testing.M) {
	// Пропускать тесты если TESTING=false или INTEGRATION=false
	if os.Getenv("INTEGRATION") != "true" {
		os.Exit(0)
	}

	// Настроить тестовую конфигурацию
	testCfg = &config.MeiliSearchConfig{
		Host:      getEnv("TEST_MEILISEARCH_HOST", "http://localhost:7700"),
		APIKey:    getEnv("TEST_MEILISEARCH_API_KEY", "masterKey"),
		IndexName: "test_recipes_" + time.Now().Format("20060102150405"),
	}

	// Создать репозиторий
	logger := slog.New(slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{
		Level: slog.LevelDebug,
	}))

	var err error
	testRepo, err = meilisearch.NewMeiliSearchRepository(testCfg, logger)
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
	ctx := context.Background()

	doc := &meilisearch.RecipeDocument{
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

	err := testRepo.IndexRecipe(ctx, doc)
	if err != nil {
		t.Fatalf("Failed to index recipe: %v", err)
	}

	// Проверить, что рецепт был найден
	found, err := testRepo.GetRecipeByID(ctx, doc.ID)
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
	ctx := context.Background()

	// Сначала создать рецепт
	doc := &meilisearch.RecipeDocument{
		ID:           "test-recipe-delete",
		Title:        "Борщ",
		Description:  "Тестовый рецепт для удаления",
		Cuisine:      "русская",
		PrepTime:     90,
		Difficulty:   "medium",
		Ingredients:  []string{"свёкла", "капуста", "картофель"},
		Tags:         []string{"обед", "суп"},
		Instructions: "Приготовить борщ...",
		AuthorID:     "user-123",
		Rating:       4.5,
		ReviewsCount: 50,
		CreatedAt:    time.Now().Format(time.RFC3339),
		UpdatedAt:    time.Now().Format(time.RFC3339),
	}

	err := testRepo.IndexRecipe(ctx, doc)
	if err != nil {
		t.Fatalf("Failed to index recipe: %v", err)
	}

	// Удалить рецепт
	err = testRepo.DeleteRecipe(ctx, doc.ID)
	if err != nil {
		t.Fatalf("Failed to delete recipe: %v", err)
	}

	// Проверить, что рецепт не найден
	_, err = testRepo.GetRecipeByID(ctx, doc.ID)
	if err == nil {
		t.Error("Expected error when getting deleted recipe, got nil")
	}
}

func TestSearch(t *testing.T) {
	ctx := context.Background()

	// Индексировать тестовые рецепты
	recipes := []*meilisearch.RecipeDocument{
		{
			ID:           "search-test-1",
			Title:        "Паста Карбонара",
			Description:  "Итальянская паста с беконом",
			Cuisine:      "итальянская",
			PrepTime:     30,
			Difficulty:   "easy",
			Ingredients:  []string{"паста", "бекон"},
			Tags:         []string{"обед", "ужин"},
			Instructions: "Приготовить пасту",
			AuthorID:     "user-123",
			Rating:       4.5,
			ReviewsCount: 10,
			CreatedAt:    time.Now().Format(time.RFC3339),
			UpdatedAt:    time.Now().Format(time.RFC3339),
		},
		{
			ID:           "search-test-2",
			Title:        "Борщ",
			Description:  "Русский суп со свёклой",
			Cuisine:      "русская",
			PrepTime:     90,
			Difficulty:   "medium",
			Ingredients:  []string{"свёкла", "капуста"},
			Tags:         []string{"обед", "суп"},
			Instructions: "Приготовить борщ",
			AuthorID:     "user-123",
			Rating:       4.5,
			ReviewsCount: 10,
			CreatedAt:    time.Now().Format(time.RFC3339),
			UpdatedAt:    time.Now().Format(time.RFC3339),
		},
		{
			ID:           "search-test-3",
			Title:        "Салат Цезарь",
			Description:  "Лёгкий салат с курицей",
			Cuisine:      "американская",
			PrepTime:     20,
			Difficulty:   "easy",
			Ingredients:  []string{"салат", "курица"},
			Tags:         []string{"завтрак", "салат"},
			Instructions: "Приготовить салат",
			AuthorID:     "user-123",
			Rating:       4.5,
			ReviewsCount: 10,
			CreatedAt:    time.Now().Format(time.RFC3339),
			UpdatedAt:    time.Now().Format(time.RFC3339),
		},
	}

	for _, doc := range recipes {
		if err := testRepo.IndexRecipe(ctx, doc); err != nil {
			t.Fatalf("Failed to index recipe %s: %v", doc.ID, err)
		}
	}

	// Тест 1: Поиск по запросу
	result, err := testRepo.Search(ctx, "паста", nil, 1, 10)
	if err != nil {
		t.Fatalf("Search failed: %v", err)
	}

	if len(result.Recipes) == 0 {
		t.Error("Expected at least one result for 'паста'")
	}

	// Тест 2: Поиск с фильтром по кухне
	filters := &meilisearch.SearchFilters{
		Cuisine: "итальянская",
	}
	result, err = testRepo.Search(ctx, "", filters, 1, 10)
	if err != nil {
		t.Fatalf("Search with filter failed: %v", err)
	}

	for _, recipe := range result.Recipes {
		if recipe.Cuisine != "итальянская" {
			t.Errorf("Expected cuisine 'итальянская', got %s", recipe.Cuisine)
		}
	}

	// Тест 3: Пагинация
	result, err = testRepo.Search(ctx, "", nil, 2, 1)
	if err != nil {
		t.Fatalf("Pagination search failed: %v", err)
	}

	if result.Page != 2 {
		t.Errorf("Expected page 2, got %d", result.Page)
	}
}

func TestSuggestions(t *testing.T) {
	ctx := context.Background()

	// Индексировать рецепт для тестов suggestions
	doc := &meilisearch.RecipeDocument{
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

	if err := testRepo.IndexRecipe(ctx, doc); err != nil {
		t.Fatalf("Failed to index recipe: %v", err)
	}

	// Тест: Автодополнение по названию
	suggestions, err := testRepo.GetSuggestions(ctx, "паст", "title", 10)
	if err != nil {
		t.Fatalf("Suggestions failed: %v", err)
	}

	if len(suggestions) == 0 {
		t.Error("Expected suggestions for 'паст'")
	}
}

func TestHealth(t *testing.T) {
	ctx := context.Background()

	health, err := testRepo.Health(ctx)
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
