package config

import (
	"github.com/spf13/viper"
)

// ServerConfig — конфигурация HTTP сервера
type ServerConfig struct {
	Host string
	Port int
}

func loadServerConfig() ServerConfig {
	return ServerConfig{
		Host: viper.GetString("SERVER_HOST"),
		Port: viper.GetInt("SERVER_PORT"),
	}
}
