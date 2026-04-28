package consumer

import (
	"context"
	"log/slog"
	"time"

	"github.com/lamauspex/recipes/backend/service_search/internal/config"
	"github.com/lamauspex/recipes/backend/service_search/internal/repository/meilisearch"
	"github.com/rabbitmq/amqp091-go"
)

// RabbitMQConsumer — потребитель событий RabbitMQ
type RabbitMQConsumer struct {
	conn   *amqp091.Connection
	ch     *amqp091.Channel
	cfg    *config.RabbitMQConfig
	repo   *meilisearch.MeiliSearchRepository
	logger *slog.Logger
	ctx    context.Context
	cancel context.CancelFunc
}

// NewRabbitMQConsumer создаёт новый экземпляр потребителя
func NewRabbitMQConsumer(cfg *config.RabbitMQConfig, repo *meilisearch.MeiliSearchRepository, logger *slog.Logger) (*RabbitMQConsumer, error) {
	ctx, cancel := context.WithCancel(context.Background())

	return &RabbitMQConsumer{
		cfg:    cfg,
		repo:   repo,
		logger: logger,
		ctx:    ctx,
		cancel: cancel,
	}, nil
}

// Start запускает потребителя — блокирует до остановки
func (c *RabbitMQConsumer) Start() error {
	c.logger.Info("Starting RabbitMQ consumer")

	for {
		select {
		case <-c.ctx.Done():
			return nil
		default:
		}

		if err := c.connect(); err != nil {
			c.logger.Error("Failed to connect to RabbitMQ", slog.String("error", err.Error()))
			select {
			case <-c.ctx.Done():
				return nil
			case <-time.After(c.cfg.Reconnect):
				continue
			}
		}

		if err := c.consume(); err != nil {
			c.logger.Error("Consumer error", slog.String("error", err.Error()))
			c.close()
			select {
			case <-c.ctx.Done():
				return nil
			case <-time.After(c.cfg.Reconnect):
				continue
			}
		}
	}
}

// Stop останавливает потребителя
func (c *RabbitMQConsumer) Stop() error {
	c.logger.Info("Stopping RabbitMQ consumer")
	c.cancel()
	c.close()
	return nil
}
