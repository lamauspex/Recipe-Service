package config

import (
	"time"

	"github.com/spf13/viper"
)

// RabbitMQConfig — конфигурация RabbitMQ
type RabbitMQConfig struct {
	URL        string
	Exchange   string
	QueueName  string
	RetryDelay time.Duration
	Reconnect  time.Duration
}

func loadRabbitMQConfig() RabbitMQConfig {
	return RabbitMQConfig{
		URL:        viper.GetString("RABBITMQ_URL"),
		Exchange:   viper.GetString("RABBITMQ_EXCHANGE"),
		QueueName:  viper.GetString("RABBITMQ_QUEUE"),
		RetryDelay: time.Duration(viper.GetInt("RABBITMQ_RETRY_DELAY")) * time.Second,
		Reconnect:  time.Duration(viper.GetInt("RABBITMQ_RECONNECT")) * time.Second,
	}
}
