package config

import (
	"sync"
	"time"

	"github.com/spf13/viper"
)

var (
	cfg  *Config
	once sync.Once
)

type Config struct {
	Server       ServerConfig
	MeiliSearch  MeiliSearchConfig
	RabbitMQ     RabbitMQConfig
	GRPC         GRPCConfig
	Logging      LoggingConfig
}

type ServerConfig struct {
	Host string
	Port int
}

type MeiliSearchConfig struct {
	Host       string
	APIKey     string
	IndexName  string
	Timeout    time.Duration
	RetryDelay time.Duration
}

type RabbitMQConfig struct {
	URL         string
	Exchange    string
	QueueName   string
	RetryDelay  time.Duration
	Reconnect   time.Duration
}

type GRPCConfig struct {
	Port int
}

type LoggingConfig struct {
	Level  string
	Format string
}

func Load() *Config {
	once.Do(func() {
		viper.AutomaticEnv()
		viper.SetDefault("SERVER_HOST", "0.0.0.0")
		viper.SetDefault("SERVER_PORT", 8002)
		viper.SetDefault("GRPC_PORT", 50052)
		viper.SetDefault("MEILISEARCH_HOST", "http://meilisearch:7700")
		viper.SetDefault("MEILISEARCH_API_KEY", "meili-master-key-secure-change-me")
		viper.SetDefault("MEILISEARCH_INDEX", "recipes")
		viper.SetDefault("MEILISEARCH_TIMEOUT", 30)
		viper.SetDefault("RABBITMQ_URL", "amqp://admin:rabbitmq-password@rabbitmq:5672/")
		viper.SetDefault("RABBITMQ_EXCHANGE", "recipe_events")
		viper.SetDefault("RABBITMQ_QUEUE", "search_service_queue")
		viper.SetDefault("LOG_LEVEL", "info")
		viper.SetDefault("LOG_FORMAT", "json")

		cfg = &Config{
			Server: ServerConfig{
				Host: viper.GetString("SERVER_HOST"),
				Port: viper.GetInt("SERVER_PORT"),
			},
			MeiliSearch: MeiliSearchConfig{
				Host:      viper.GetString("MEILISEARCH_HOST"),
				APIKey:    viper.GetString("MEILISEARCH_API_KEY"),
				IndexName: viper.GetString("MEILISEARCH_INDEX"),
				Timeout:   time.Duration(viper.GetInt("MEILISEARCH_TIMEOUT")) * time.Second,
			},
			RabbitMQ: RabbitMQConfig{
				URL:       viper.GetString("RABBITMQ_URL"),
				Exchange:  viper.GetString("RABBITMQ_EXCHANGE"),
				QueueName: viper.GetString("RABBITMQ_QUEUE"),
			},
			GRPC: GRPCConfig{
				Port: viper.GetInt("GRPC_PORT"),
			},
			Logging: LoggingConfig{
				Level:  viper.GetString("LOG_LEVEL"),
				Format: viper.GetString("LOG_FORMAT"),
			},
		}
	})
	return cfg
}

func Get() *Config {
	return cfg
}
