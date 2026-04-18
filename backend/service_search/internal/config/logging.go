package config

import (
	"github.com/spf13/viper"
)

// LoggingConfig — конфигурация логгера
type LoggingConfig struct {
	Level  string
	Format string
}

func loadLoggingConfig() LoggingConfig {
	return LoggingConfig{
		Level:  viper.GetString("LOG_LEVEL"),
		Format: viper.GetString("LOG_FORMAT"),
	}
}
