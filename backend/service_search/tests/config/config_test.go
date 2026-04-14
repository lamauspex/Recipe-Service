package config

import (
	"os"
	"testing"
	"time"

	"github.com/lamauspex/recipes/backend/service_search/internal/config"
)

func TestLoadConfig_Defaults(t *testing.T) {
	// Очистить переменные окружения
	os.Clearenv()

	cfg := config.Load()

	if cfg.Server.Host != "0.0.0.0" {
		t.Errorf("Expected default host 0.0.0.0, got %s", cfg.Server.Host)
	}

	if cfg.Server.Port != 8002 {
		t.Errorf("Expected default port 8002, got %d", cfg.Server.Port)
	}

	if cfg.GRPC.Port != 50052 {
		t.Errorf("Expected default gRPC port 50052, got %d", cfg.GRPC.Port)
	}

	if cfg.MeiliSearch.Host != "http://meilisearch:7700" {
		t.Errorf("Expected default MeiliSearch host, got %s", cfg.MeiliSearch.Host)
	}

	if cfg.MeiliSearch.IndexName != "recipes" {
		t.Errorf("Expected default index name 'recipes', got %s", cfg.MeiliSearch.IndexName)
	}
}

func TestLoadConfig_CustomEnv(t *testing.T) {
	// Установить кастомные переменные
	os.Setenv("SERVER_HOST", "127.0.0.1")
	os.Setenv("SERVER_PORT", "9999")
	os.Setenv("GRPC_PORT", "55555")
	os.Setenv("MEILISEARCH_HOST", "http://localhost:7700")
	os.Setenv("MEILISEARCH_API_KEY", "test-key")
	os.Setenv("MEILISEARCH_INDEX", "test_recipes")
	os.Setenv("MEILISEARCH_TIMEOUT", "60")
	os.Setenv("RABBITMQ_URL", "amqp://test:test@localhost:5672/")
	os.Setenv("RABBITMQ_EXCHANGE", "test_events")
	os.Setenv("RABBITMQ_QUEUE", "test_queue")
	os.Setenv("LOG_LEVEL", "debug")

	defer func() {
		// Очистить переменные
		os.Clearenv()
	}()

	cfg := config.Load()

	if cfg.Server.Host != "127.0.0.1" {
		t.Errorf("Expected host 127.0.0.1, got %s", cfg.Server.Host)
	}

	if cfg.Server.Port != 9999 {
		t.Errorf("Expected port 9999, got %d", cfg.Server.Port)
	}

	if cfg.GRPC.Port != 55555 {
		t.Errorf("Expected gRPC port 55555, got %d", cfg.GRPC.Port)
	}

	if cfg.MeiliSearch.Host != "http://localhost:7700" {
		t.Errorf("Expected MeiliSearch host http://localhost:7700, got %s", cfg.MeiliSearch.Host)
	}

	if cfg.MeiliSearch.APIKey != "test-key" {
		t.Errorf("Expected API key 'test-key', got %s", cfg.MeiliSearch.APIKey)
	}

	if cfg.MeiliSearch.IndexName != "test_recipes" {
		t.Errorf("Expected index name 'test_recipes', got %s", cfg.MeiliSearch.IndexName)
	}

	if cfg.MeiliSearch.Timeout != 60*time.Second {
		t.Errorf("Expected timeout 60s, got %v", cfg.MeiliSearch.Timeout)
	}

	if cfg.RabbitMQ.URL != "amqp://test:test@localhost:5672/" {
		t.Errorf("Expected RabbitMQ URL, got %s", cfg.RabbitMQ.URL)
	}

	if cfg.RabbitMQ.Exchange != "test_events" {
		t.Errorf("Expected exchange 'test_events', got %s", cfg.RabbitMQ.Exchange)
	}

	if cfg.RabbitMQ.QueueName != "test_queue" {
		t.Errorf("Expected queue 'test_queue', got %s", cfg.RabbitMQ.QueueName)
	}

	if cfg.Logging.Level != "debug" {
		t.Errorf("Expected log level 'debug', got %s", cfg.Logging.Level)
	}
}

func TestGetConfig_Singleton(t *testing.T) {
	os.Clearenv()

	cfg1 := config.Load()
	cfg2 := config.Get()

	if cfg1 != cfg2 {
		t.Error("Expected singleton pattern, different instances returned")
	}
}
