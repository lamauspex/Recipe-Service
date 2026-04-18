package config

import (
	"github.com/spf13/viper"
)

// GRPCConfig — конфигурация gRPC сервера
type GRPCConfig struct {
	Port int
}

func loadGRPCConfig() GRPCConfig {
	return GRPCConfig{
		Port: viper.GetInt("GRPC_PORT"),
	}
}
