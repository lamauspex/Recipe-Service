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
		Host: viper.GetString("HOST"),
		Port: viper.GetInt("PORT"),
	}
}
