package meilisearch

import "github.com/lamauspex/recipes/backend/service_search/proto"

// RecipeDocument представляет документ рецепта в MeiliSearch
type RecipeDocument struct {
	ID          string `json:"id"`
	Title       string `json:"title"`
	Description string `json:"description"`
	// TODO: Добавить поля при расширении модели Recipe
	// Cuisine      string   `json:"cuisine"`
	// PrepTime     int      `json:"prep_time"`
	// Difficulty   string   `json:"difficulty"`
	// Ingredients  []string `json:"ingredients"`
	// Tags         []string `json:"tags"`
	// Instructions string   `json:"instructions"`
	// AuthorID     string   `json:"author_id"`
	// Rating       float64  `json:"rating"`
	// ReviewsCount int      `json:"reviews_count"`
	CreatedAt string `json:"created_at"`
	UpdatedAt string `json:"updated_at"`
}

// SearchFilters - фильтры для поиска
type SearchFilters struct {
	// TODO: Добавить поля при расширении модели Recipe
	// Cuisine     string
	// Difficulty  string
	// MaxPrepTime int32
	// Ingredients []string
	// Tags        []string
}

// SearchResult - результат поиска
type SearchResult struct {
	Recipes    []*proto.RecipeResult
	Total      int32
	Page       int32
	PageSize   int32
	TotalPages int32
}

// HealthStatus - статус здоровья
type HealthStatus struct {
	Healthy bool
	Message string
}
