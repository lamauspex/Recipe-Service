package meilisearch

import (
	"context"
	"fmt"
	"log/slog"

	"github.com/lamauspex/recipes/backend/service_search/internal/config"
	"github.com/meilisearch/meilisearch-go"
)

// MeiliSearchRepository - основной репозиторий для работы с MeiliSearch
type MeiliSearchRepository struct {
	client    meilisearch.ServiceManager
	indexName string
	logger    *slog.Logger
}

// NewMeiliSearchRepository создаёт новый экземпляр репозитория
func NewMeiliSearchRepository(cfg *config.MeiliSearchConfig, logger *slog.Logger) (*MeiliSearchRepository, error) {
	// New API: meilisearch.New(host, options...)
	client := meilisearch.New(cfg.Host, meilisearch.WithAPIKey(cfg.APIKey))

	// Проверка подключения
	health, err := client.Health()
	if err != nil {
		return nil, fmt.Errorf("failed to connect to MeiliSearch: %w", err)
	}

	logger.Info("MeiliSearch connected", "status", health.Status)

	return &MeiliSearchRepository{
		client:    client,
		indexName: cfg.IndexName,
		logger:    logger,
	}, nil
}

// Health проверяет здоровье подключения к MeiliSearch
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
