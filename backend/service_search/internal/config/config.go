package config

import (
	"sync"

	"github.com/spf13/viper"
)

var (
	cfg  *Config
	once sync.Once
)

// Config — объединяет все конфигурационные структуры
type Config struct {
	Server      ServerConfig
	MeiliSearch MeiliSearchConfig
	RabbitMQ    RabbitMQConfig
	GRPC        GRPCConfig
	Logging     LoggingConfig
}

// Load загружает конфигурацию из переменных окружения
func Load() *Config {
	once.Do(func() {
		// === Настройка Viper ===
		// Добавляем префикс для всех переменных окружения
		viper.SetEnvPrefix("SEARCH_SERVICE")

		// Загружаем .env файл (для локальной разработки)
		viper.SetConfigFile(".env")
		viper.AutomaticEnv()

		// Если .env не найден — игнорируем ошибку, используем дефолты
		if err := viper.ReadInConfig(); err != nil {
			// Файл .env не найден или не читается — не прерываем работу
			// В Docker переменные будут переданы через ENV
		}

		setDefaults()
		cfg = &Config{
			Server:      loadServerConfig(),
			MeiliSearch: loadMeiliSearchConfig(),
			RabbitMQ:    loadRabbitMQConfig(),
			GRPC:        loadGRPCConfig(),
			Logging:     loadLoggingConfig(),
		}
	})
	return cfg
}

// Get возвращает загруженную конфигурацию
func Get() *Config {
	return cfg
}

func setDefaults() {
	// Server
	viper.SetDefault("HOST", "0.0.0.0")
	viper.SetDefault("PORT", 8002)

	// MeiliSearch
	viper.SetDefault("MEILISEARCH_HOST", "http://meilisearch:7700")
	viper.SetDefault("MEILISEARCH_API_KEY", "meili-master-key-secure-change-me")
	viper.SetDefault("MEILISEARCH_INDEX", "recipes")
	viper.SetDefault("MEILISEARCH_TIMEOUT", 30)
	viper.SetDefault("MEILISEARCH_RETRY_DELAY", 5)

	// RabbitMQ
	viper.SetDefault("RABBITMQ_USER", "admin")
	viper.SetDefault("RABBITMQ_PASSWORD", "rabbitmq-password")
	viper.SetDefault("RABBITMQ_VHOST", "/")
	viper.SetDefault("RABBITMQ_URL", "amqp://admin:rabbitmq-password@rabbitmq:5672/")
	viper.SetDefault("RABBITMQ_EXCHANGE", "recipe_events")
	viper.SetDefault("RABBITMQ_QUEUE", "search_service_queue")
	viper.SetDefault("RABBITMQ_RETRY_DELAY", 5)
	viper.SetDefault("RABBITMQ_RECONNECT", 5)

	// gRPC
	viper.SetDefault("GRPC_PORT", 50052)

	// Logging
	viper.SetDefault("LOG_LEVEL", "info")
	viper.SetDefault("LOG_FORMAT", "json")

	// Environment
	viper.SetDefault("ENVIRONMENT", "development")
}
