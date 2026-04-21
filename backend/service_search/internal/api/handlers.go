package api

import (
	"context"
	"fmt"
	"log/slog"

	"github.com/lamauspex/recipes/backend/service_search/internal/repository/meilisearch"
	"github.com/lamauspex/recipes/backend/service_search/proto"
)

// SearchRecipes — поиск рецептов
func (s *SearchServer) SearchRecipes(ctx context.Context, req *proto.SearchRequest) (*proto.SearchResponse, error) {
	filters := &meilisearch.SearchFilters{
		// TODO: Добавить поля при расширении модели Recipe
		// Cuisine:     req.GetCuisine(),
		// Difficulty:  req.GetDifficulty(),
		// MaxPrepTime: req.GetMaxPrepTime(),
		// Ingredients: req.GetIngredients(),
		// Tags:        req.GetTags(),
	}

	page, pageSize := validatePagination(int(req.Page), int(req.PageSize))

	result, err := s.repo.Search(ctx, req.Query, filters, page, pageSize)
	if err != nil {
		s.logger.Error("Search failed", slog.String("error", err.Error()))
		return nil, fmt.Errorf("search failed: %w", err)
	}

	return &proto.SearchResponse{
		Results:    result.Recipes,
		Total:      result.Total,
		Page:       result.Page,
		PageSize:   result.PageSize,
		TotalPages: result.TotalPages,
	}, nil
}

// GetRecipe — получить рецепт по ID
func (s *SearchServer) GetRecipe(ctx context.Context, req *proto.GetRecipeRequest) (*proto.RecipeResponse, error) {
	doc, err := s.repo.GetRecipeByID(ctx, req.Id)
	if err != nil {
		s.logger.Error("Get recipe failed", slog.String("error", err.Error()))
		return nil, fmt.Errorf("get recipe failed: %w", err)
	}

	return &proto.RecipeResponse{
		Id:          doc.ID,
		Title:       doc.Title,
		Description: doc.Description,
		// TODO: Добавить поля при расширении модели Recipe
		// Cuisine:      doc.Cuisine,
		// PrepTime:     int32(doc.PrepTime),
		// Difficulty:   doc.Difficulty,
		// Ingredients:  doc.Ingredients,
		// Tags:         doc.Tags,
		// Instructions: doc.Instructions,
		// Rating:       doc.Rating,
		// ReviewsCount: int32(doc.ReviewsCount),
		// AuthorId:     doc.AuthorID,
	}, nil
}

// GetSuggestions — автодополнение
func (s *SearchServer) GetSuggestions(ctx context.Context, req *proto.SuggestionsRequest) (*proto.SuggestionsResponse, error) {
	// TODO: Добавить поддержку типа при расширении модели Recipe
	// fieldType := "title"
	// if req.GetType() != "" {
	// 	fieldType = req.GetType()
	// }
	fieldType := "title"

	limit := int(req.Limit)
	if limit <= 0 {
		limit = DefaultPageSize
	}

	suggestions, err := s.repo.GetSuggestions(ctx, req.Query, fieldType, limit)
	if err != nil {
		s.logger.Error("Suggestions failed", slog.String("error", err.Error()))
		return nil, fmt.Errorf("get suggestions failed: %w", err)
	}

	return &proto.SuggestionsResponse{
		Suggestions: suggestions,
		// Type:        fieldType,
	}, nil
}
