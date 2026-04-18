package config

import (
	"time"

	"github.com/spf13/viper"
)

// MeiliSearchConfig — конфигурация MeiliSearch
type MeiliSearchConfig struct {
	Host       string
	APIKey     string
	IndexName  string
	Timeout    time.Duration
	RetryDelay time.Duration
}

func loadMeiliSearchConfig() MeiliSearchConfig {
	return MeiliSearchConfig{
		Host:       viper.GetString("MEILISEARCH_HOST"),
		APIKey:     viper.GetString("MEILISEARCH_API_KEY"),
		IndexName:  viper.GetString("MEILISEARCH_INDEX"),
		Timeout:    time.Duration(viper.GetInt("MEILISEARCH_TIMEOUT")) * time.Second,
		RetryDelay: time.Duration(viper.GetInt("MEILISEARCH_RETRY_DELAY")) * time.Second,
	}
}
