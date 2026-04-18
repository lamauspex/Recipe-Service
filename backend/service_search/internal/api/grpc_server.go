package api

import (
	"log"
	"log/slog"
	"os"

	"github.com/lamauspex/recipes/backend/service_search/internal/config"
	"github.com/lamauspex/recipes/backend/service_search/internal/consumer"
	"github.com/lamauspex/recipes/backend/service_search/internal/repository/meilisearch"
)

// Run — точка входа для сервиса поиска
func Run() {
	logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
		Level: slog.LevelInfo,
	}))

	cfg := config.Load()
	if cfg == nil {
		log.Fatal("Failed to load configuration")
	}

	repo, err := meilisearch.NewMeiliSearchRepository(&cfg.MeiliSearch, logger)
	if err != nil {
		log.Fatalf("Failed to create MeiliSearch repository: %v", err)
	}

	consumer, err := consumer.NewRabbitMQConsumer(&cfg.RabbitMQ, repo, logger)
	if err != nil {
		log.Fatalf("Failed to create RabbitMQ consumer: %v", err)
	}

	server, err := NewSearchServer(cfg, repo, consumer, logger)
	if err != nil {
		log.Fatalf("Failed to create server: %v", err)
	}

	if err := server.Start(); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}
