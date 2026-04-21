package consumer

import "time"

// EventType — тип события рецепта
type EventType string

const (
	RecipeCreated EventType = "recipe.created"
	RecipeUpdated EventType = "recipe.updated"
	RecipeDeleted EventType = "recipe.deleted"
)

// RecipeEvent — событие рецепта
type RecipeEvent struct {
	Type      EventType     `json:"type"`
	RecipeID  string        `json:"recipe_id"`
	Payload   RecipePayload `json:"payload,omitempty"`
	Timestamp time.Time     `json:"timestamp"`
}

// RecipePayload — данные рецепта в событии
type RecipePayload struct {
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
}
