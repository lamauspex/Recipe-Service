package consumer

import (
	"context"
	"fmt"
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

// Start запускает потребителя
func (c *RabbitMQConsumer) Start() error {
	c.logger.Info("Starting RabbitMQ consumer")

	var err error
	for {
		select {
		case <-c.ctx.Done():
			return nil
		default:
			err = c.connect()
			if err == nil {
				break
			}
			c.logger.Error("Failed to connect to RabbitMQ", slog.String("error", err.Error()))
			select {
			case <-c.ctx.Done():
				return nil
			case <-time.After(c.cfg.Reconnect):
				continue
			}
		}
		break
	}

	err = c.setupExchangeAndQueue()
	if err != nil {
		return fmt.Errorf("failed to setup exchange and queue: %w", err)
	}

	err = c.consume()
	if err != nil {
		return fmt.Errorf("failed to start consuming: %w", err)
	}

	c.logger.Info("RabbitMQ consumer started successfully")
	return nil
}

// Stop останавливает потребителя
func (c *RabbitMQConsumer) Stop() error {
	c.logger.Info("Stopping RabbitMQ consumer")
	c.cancel()

	if c.ch != nil {
		if err := c.ch.Close(); err != nil {
			return fmt.Errorf("failed to close channel: %w", err)
		}
	}

	if c.conn != nil {
		if err := c.conn.Close(); err != nil {
			return fmt.Errorf("failed to close connection: %w", err)
		}
	}

	return nil
}
