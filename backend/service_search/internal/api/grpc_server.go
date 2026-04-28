package api

import (
	"log"
	"log/slog"
	"os"

	"github.com/lamauspex/recipes/backend/service_search/internal/config"
	"github.com/lamauspex/recipes/backend/service_search/internal/consumer"
	"github.com/lamauspex/recipes/backend/service_search/internal/repository/meilisearch"
)

// parseLogLevel парсит строку уровня логирования
func parseLogLevel(level string) slog.Level {
	switch level {
	case "debug":
		return slog.LevelDebug
	case "warn":
		return slog.LevelWarn
	case "error":
		return slog.LevelError
	default:
		return slog.LevelInfo
	}
}

// Run — точка входа для сервиса поиска
func Run() {
	cfg := config.Load()
	if cfg == nil {
		log.Fatal("Failed to load configuration")
	}

	logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
		Level: parseLogLevel(cfg.Logging.Level),
	}))

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
