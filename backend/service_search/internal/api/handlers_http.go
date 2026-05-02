package api

import (
	"encoding/json"
	"log/slog"
	"net/http"
	"strconv"

	"github.com/lamauspex/recipes/backend/service_search/internal/repository/meilisearch"
	"github.com/lamauspex/recipes/backend/service_search/proto"
)

// SearchHandler — REST endpoint для поиска рецептов
// GET /api/v1/search?q=...&page=...&limit=...
func (s *SearchServer) SearchHandler(w http.ResponseWriter, r *http.Request) {
	// Только GET запросы
	if r.Method != http.MethodGet {
		http.Error(w, `{"error": "Method not allowed"}`, http.StatusMethodNotAllowed)
		return
	}

	// Парсинг query параметров
	query := r.URL.Query().Get("q")
	if query == "" {
		http.Error(w, `{"error": "Query parameter 'q' is required"}`, http.StatusBadRequest)
		return
	}

	// Парсинг page
	page := DefaultPage
	if pageStr := r.URL.Query().Get("page"); pageStr != "" {
		if parsed, err := strconv.Atoi(pageStr); err == nil && parsed >= 1 {
			page = parsed
		}
	}

	// Парсинг limit
	pageSize := DefaultPageSize
	if limitStr := r.URL.Query().Get("limit"); limitStr != "" {
		if parsed, err := strconv.Atoi(limitStr); err == nil {
			if parsed >= 1 && parsed <= MaxPageSize {
				pageSize = parsed
			}
		}
	}

	// Создание gRPC запроса
	grpcReq := &proto.SearchRequest{
		Query:    query,
		Page:     int32(page),
		PageSize: int32(pageSize),
	}

	// Вызов gRPC метода
	ctx := r.Context()
	grpcRes, err := s.SearchRecipes(ctx, grpcReq)
	if err != nil {
		s.logger.Error("Search failed", slog.String("error", err.Error()))
		http.Error(w, `{"error": "Search failed"}`, http.StatusInternalServerError)
		return
	}

	// Формирование REST ответа
	res := map[string]interface{}{
		"results":     grpcRes.Results,
		"total":       grpcRes.Total,
		"page":        grpcRes.Page,
		"page_size":   grpcRes.PageSize,
		"total_pages": grpcRes.TotalPages,
	}

	w.Header().Set("Content-Type", "application/json")
	if err := json.NewEncoder(w).Encode(res); err != nil {
		s.logger.Error("Failed to encode response", slog.String("error", err.Error()))
	}
}

// HealthHandler — HTTP health check
// GET /health
func (s *SearchServer) HealthHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, `{"error": "Method not allowed"}`, http.StatusMethodNotAllowed)
		return
	}

	res := map[string]string{
		"status": "ok",
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	if err := json.NewEncoder(w).Encode(res); err != nil {
		s.logger.Error("Failed to encode response", slog.String("error", err.Error()))
	}
}

// SearchFiltersFromRequest создаёт фильтры из HTTP запроса
// TODO: Добавить поддержку фильтров при расширении модели Recipe
func SearchFiltersFromRequest(r *http.Request) *meilisearch.SearchFilters {
	return &meilisearch.SearchFilters{}
}
