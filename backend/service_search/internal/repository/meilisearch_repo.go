package repository

import (
	"context"
	"fmt"
	"log/slog"
	"time"

	"github.com/lamauspex/recipes/backend/service_search/internal/config"
	"github.com/lamauspex/recipes/backend/service_search/pkg/proto"
	"github.com/meilisearch/meilisearch-go"
)

type RecipeDocument struct {
	ID          string   `json:"id"`
	Title       string   `json:"title"`
	Description string   `json:"description"`
	Cuisine     string   `json:"cuisine"`
	PrepTime    int      `json:"prep_time"`
	Difficulty  string   `json:"difficulty"`
	Ingredients []string `json:"ingredients"`
	Tags        []string `json:"tags"`
	Instructions string  `json:"instructions"`
	AuthorID    string   `json:"author_id"`
	Rating      float64  `json:"rating"`
	ReviewsCount int     `json:"reviews_count"`
	CreatedAt   string   `json:"created_at"`
	UpdatedAt   string   `json:"updated_at"`
}

type MeiliSearchRepository struct {
	client   *meilisearch.Client
	index    *meilisearch.Index
	indexName string
	logger   *slog.Logger
}

func NewMeiliSearchRepository(cfg *config.MeiliSearchConfig, logger *slog.Logger) (*MeiliSearchRepository, error) {
	client := meilisearch.New(meilisearch.Config{
		Host:   cfg.Host,
		APIKey: cfg.APIKey,
		Timeout: cfg.Timeout,
	})

	// Проверка подключения
	health, err := client.Health()
	if err != nil {
		return nil, fmt.Errorf("failed to connect to MeiliSearch: %w", err)
	}

	logger.Info("MeiliSearch connected", slog.String("status", health.Status))

	index := client.Index(cfg.IndexName)

	return &MeiliSearchRepository{
		client:    client,
		index:     index,
		indexName: cfg.IndexName,
		logger:    logger,
	}, nil
}

func (r *MeiliSearchRepository) IndexRecipe(ctx context.Context, doc *RecipeDocument) error {
	start := time.Now()

	task, err := r.index.AddDocuments([]RecipeDocument{*doc}, "id")
	if err != nil {
		return fmt.Errorf("failed to index recipe: %w", err)
	}

	// Ожидаем выполнения задачи
	ticker := time.NewTicker(100 * time.Millisecond)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return ctx.Err()
		case <-ticker.C:
			status, err := r.client.Task(task.TaskUID)
			if err != nil {
				continue
			}
			if status.Status == "succeeded" {
				r.logger.Debug("recipe indexed", slog.String("id", doc.ID), slog.Duration("duration", time.Since(start)))
				return nil
			}
			if status.Status == "failed" {
				return fmt.Errorf("indexing task failed: %s", status.Error)
			}
		}
	}
}

func (r *MeiliSearchRepository) DeleteRecipe(ctx context.Context, id string) error {
	start := time.Now()

	task, err := r.index.DeleteDocument(id)
	if err != nil {
		return fmt.Errorf("failed to delete recipe: %w", err)
	}

	// Ожидаем выполнения задачи
	ticker := time.NewTicker(100 * time.Millisecond)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return ctx.Err()
		case <-ticker.C:
			status, err := r.client.Task(task.TaskUID)
			if err != nil {
				continue
			}
			if status.Status == "succeeded" {
				r.logger.Debug("recipe deleted", slog.String("id", id), slog.Duration("duration", time.Since(start)))
				return nil
			}
			if status.Status == "failed" {
				return fmt.Errorf("deletion task failed: %s", status.Error)
			}
		}
	}
}

func (r *MeiliSearchRepository) Search(ctx context.Context, query string, filters *SearchFilters, page, pageSize int) (*SearchResult, error) {
	searchRequest := meilisearch.SearchRequest{
		Query:   query,
		Offset:  (page - 1) * pageSize,
		Limit:   pageSize,
		Filters: r.buildFilters(filters),
	}

	result, err := r.index.Search(query, &searchRequest)
	if err != nil {
		return nil, fmt.Errorf("search failed: %w", err)
	}

	recipes := make([]*proto.RecipeResult, 0, len(result.Hits))
	for _, hit := range result.Hits {
		var doc RecipeDocument
		if err := convertHitToDocument(hit, &doc); err != nil {
			continue
		}
		recipes = append(recipes, &proto.RecipeResult{
			Id:           doc.ID,
			Title:        doc.Title,
			Description:  doc.Description,
			Cuisine:      doc.Cuisine,
			PrepTime:     int32(doc.PrepTime),
			Difficulty:   doc.Difficulty,
			Tags:         doc.Tags,
			Rating:       doc.Rating,
			ReviewsCount: int32(doc.ReviewsCount),
		})
	}

	totalPages := int(result.HitsPerPage) / pageSize
	if int(result.HitsPerPage)%pageSize > 0 {
		totalPages++
	}

	return &SearchResult{
		Recipes:     recipes,
		Total:       int32(result.HitsPerPage),
		Page:        int32(page),
		PageSize:    int32(pageSize),
		TotalPages:  int32(totalPages),
	}, nil
}

func (r *MeiliSearchRepository) GetRecipeByID(ctx context.Context, id string) (*RecipeDocument, error) {
	var doc RecipeDocument
	err := r.index.GetDocument(id, &doc)
	if err != nil {
		return nil, fmt.Errorf("failed to get recipe: %w", err)
	}
	return &doc, nil
}

func (r *MeiliSearchRepository) GetSuggestions(ctx context.Context, query string, fieldType string, limit int) ([]string, error) {
	if limit <= 0 || limit > 100 {
		limit = 10
	}

	searchRequest := meilisearch.SearchRequest{
		Query:  query,
		Limit:  int64(limit),
		AttributesToRetrieve: []string{fieldType},
	}

	result, err := r.index.Search(query, &searchRequest)
	if err != nil {
		return nil, fmt.Errorf("suggestions failed: %w", err)
	}

	suggestions := make([]string, 0, len(result.Hits))
	for _, hit := range result.Hits {
		if field, ok := hit[fieldType]; ok {
			if str, ok := field.(string); ok && str != "" {
				suggestions = append(suggestions, str)
			}
		}
	}

	return suggestions, nil
}

func (r *MeiliSearchRepository) Health(ctx context.Context) (*HealthStatus, error) {
	health, err := r.client.Health()
	if err != nil {
		return &HealthStatus{
			Healthy: false,
			Message: fmt.Sprintf("MeiliSearch unreachable: %v", err),
		}, nil
	}

	return &HealthStatus{
		Healthy: health.Status == "available",
		Message: fmt.Sprintf("MeiliSearch status: %s", health.Status),
	}, nil
}

func (r *MeiliSearchRepository) buildFilters(filters *SearchFilters) []string {
	var filterStrings []string

	if filters != nil {
		if filters.Cuisine != "" {
			filterStrings = append(filterStrings, fmt.Sprintf("cuisine = \"%s\"", filters.Cuisine))
		}
		if filters.Difficulty != "" {
			filterStrings = append(filterStrings, fmt.Sprintf("difficulty = \"%s\"", filters.Difficulty))
		}
		if filters.MaxPrepTime > 0 {
			filterStrings = append(filterStrings, fmt.Sprintf("prep_time <= %d", filters.MaxPrepTime))
		}
		if len(filters.Ingredients) > 0 {
			for _, ing := range filters.Ingredients {
				filterStrings = append(filterStrings, fmt.Sprintf("ingredients CONTAINS \"%s\"", ing))
			}
		}
		if len(filters.Tags) > 0 {
			for _, tag := range filters.Tags {
				filterStrings = append(filterStrings, fmt.Sprintf("tags CONTAINS \"%s\"", tag))
			}
		}
	}

	return filterStrings
}

func convertHitToDocument(hit map[string]any, doc *RecipeDocument) error {
	if id, ok := hit["id"].(string); ok {
		doc.ID = id
	}
	if title, ok := hit["title"].(string); ok {
		doc.Title = title
	}
	if desc, ok := hit["description"].(string); ok {
		doc.Description = desc
	}
	if cuisine, ok := hit["cuisine"].(string); ok {
		doc.Cuisine = cuisine
	}
	if prepTime, ok := hit["prep_time"].(float64); ok {
		doc.PrepTime = int(prepTime)
	}
	if difficulty, ok := hit["difficulty"].(string); ok {
		doc.Difficulty = difficulty
	}
	if tags, ok := hit["tags"].([]any); ok {
		doc.Tags = make([]string, 0, len(tags))
		for _, tag := range tags {
			if t, ok := tag.(string); ok {
				doc.Tags = append(doc.Tags, t)
			}
		}
	}
	if ingredients, ok := hit["ingredients"].([]any); ok {
		doc.Ingredients = make([]string, 0, len(ingredients))
		for _, ing := range ingredients {
			if i, ok := ing.(string); ok {
				doc.Ingredients = append(doc.Ingredients, i)
			}
		}
	}
	if instructions, ok := hit["instructions"].(string); ok {
		doc.Instructions = instructions
	}
	if authorID, ok := hit["author_id"].(string); ok {
		doc.AuthorID = authorID
	}
	if rating, ok := hit["rating"].(float64); ok {
		doc.Rating = rating
	}
	if reviewsCount, ok := hit["reviews_count"].(float64); ok {
		doc.ReviewsCount = int(reviewsCount)
	}
	if createdAt, ok := hit["created_at"].(string); ok {
		doc.CreatedAt = createdAt
	}
	if updatedAt, ok := hit["updated_at"].(string); ok {
		doc.UpdatedAt = updatedAt
	}
	return nil
}

// SearchFilters - фильтры для поиска
type SearchFilters struct {
	Cuisine     string
	Difficulty  string
	MaxPrepTime int32
	Ingredients []string
	Tags        []string
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
