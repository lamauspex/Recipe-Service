package main

import (
	"context"
	"log"
	"log/slog"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/lamauspex/recipes/backend/service_search/internal/api"
	"github.com/lamauspex/recipes/backend/service_search/internal/config"
	"github.com/lamauspex/recipes/backend/service_search/internal/consumer"
	"github.com/lamauspex/recipes/backend/service_search/internal/repository/meilisearch"
)

// ShutdownTimeout — время на graceful shutdown
const ShutdownTimeout = 30 * time.Second

func main() {
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

	server, err := api.NewSearchServer(cfg, repo, consumer, logger)
	if err != nil {
		log.Fatalf("Failed to create server: %v", err)
	}

	// Запуск сервера в отдельной goroutine
	go func() {
		if err := server.Start(); err != nil {
			log.Fatalf("Failed to start server: %v", err)
		}
	}()

	logger.Info("Search Service started, waiting for shutdown signal...")

	// Ожидание сигнала остановки
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	logger.Info("Shutting down Search Service...")

	ctx, cancel := context.WithTimeout(context.Background(), ShutdownTimeout)
	defer cancel()

	// Graceful shutdown
	if err := server.Shutdown(ctx); err != nil {
		logger.Error("Shutdown error", slog.String("error", err.Error()))
	}

	logger.Info("Search Service stopped")
}

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
