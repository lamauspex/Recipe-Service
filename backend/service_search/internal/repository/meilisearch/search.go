package meilisearch

import (
	"context"
	"encoding/json"
	"fmt"

	"github.com/lamauspex/recipes/backend/service_search/proto"
	"github.com/meilisearch/meilisearch-go"
)

// Search выполняет поиск рецептов
func (r *MeiliSearchRepository) Search(ctx context.Context, query string, filters *SearchFilters, page, pageSize int) (*SearchResult, error) {
	// Фильтры в виде строки
	filterStr := buildFilters(filters)

	searchRequest := &meilisearch.SearchRequest{
		Query:  query,
		Offset: int64((page - 1) * pageSize),
		Limit:  int64(pageSize),
		Filter: filterStr,
	}

	result, err := r.client.Index(r.indexName).Search(query, searchRequest)
	if err != nil {
		return nil, fmt.Errorf("search failed: %w", err)
	}

	recipes := make([]*proto.RecipeResult, 0, len(result.Hits))
	for _, hit := range result.Hits {
		var doc RecipeDocument
		// Преобразуем map[string]any в структуру
		data, _ := json.Marshal(hit)
		if err := json.Unmarshal(data, &doc); err != nil {
			continue
		}
		recipes = append(recipes, &proto.RecipeResult{
			Id:          doc.ID,
			Title:       doc.Title,
			Description: doc.Description,
			// TODO: Добавить поля при расширении модели Recipe
			// Cuisine:      doc.Cuisine,
			// PrepTime:     int32(doc.PrepTime),
			// Difficulty:   doc.Difficulty,
			// Tags:         doc.Tags,
			// Rating:       doc.Rating,
			// ReviewsCount: int32(doc.ReviewsCount),
		})
	}

	var totalPages int32
	if pageSize > 0 {
		totalPages = int32((int(result.EstimatedTotalHits) + pageSize - 1) / pageSize)
	}

	return &SearchResult{
		Recipes:    recipes,
		Total:      int32(result.EstimatedTotalHits),
		Page:       int32(page),
		PageSize:   int32(pageSize),
		TotalPages: int32(totalPages),
	}, nil
}

// GetSuggestions получает подсказки для автодополнения
func (r *MeiliSearchRepository) GetSuggestions(ctx context.Context, query string, fieldType string, limit int) ([]string, error) {
	if limit <= 0 || limit > 100 {
		limit = 10
	}

	searchRequest := &meilisearch.SearchRequest{
		Query:                query,
		Limit:                int64(limit),
		AttributesToRetrieve: []string{fieldType},
	}

	result, err := r.client.Index(r.indexName).Search(query, searchRequest)
	if err != nil {
		return nil, fmt.Errorf("suggestions failed: %w", err)
	}

	suggestions := make([]string, 0, len(result.Hits))
	for _, hit := range result.Hits {
		hitMap, ok := hit.(map[string]interface{})
		if !ok {
			continue
		}
		if rawValue, ok := hitMap[fieldType]; ok {
			value, _ := rawValue.(string)
			if value != "" {
				suggestions = append(suggestions, value)
			}
		}
	}

	return suggestions, nil
}
