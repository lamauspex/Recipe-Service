package consumer

import (
	"context"
	"encoding/json"
	"fmt"
	"log/slog"
	"time"

	"github.com/lamauspex/recipes/backend/service_search/internal/config"
	"github.com/lamauspex/recipes/backend/service_search/internal/repository/meilisearch"
	"github.com/rabbitmq/amqp091-go"
)

type EventType string

const (
	RecipeCreated EventType = "recipe.created"
	RecipeUpdated EventType = "recipe.updated"
	RecipeDeleted EventType = "recipe.deleted"
)

type RecipeEvent struct {
	Type      EventType     `json:"type"`
	RecipeID  string        `json:"recipe_id"`
	Payload   RecipePayload `json:"payload,omitempty"`
	Timestamp time.Time     `json:"timestamp"`
}

type RecipePayload struct {
	ID           string   `json:"id"`
	Title        string   `json:"title"`
	Description  string   `json:"description"`
	Cuisine      string   `json:"cuisine"`
	PrepTime     int      `json:"prep_time"`
	Difficulty   string   `json:"difficulty"`
	Ingredients  []string `json:"ingredients"`
	Tags         []string `json:"tags"`
	Instructions string   `json:"instructions"`
	AuthorID     string   `json:"author_id"`
	Rating       float64  `json:"rating"`
	ReviewsCount int      `json:"reviews_count"`
}

type RabbitMQConsumer struct {
	conn   *amqp091.Connection
	ch     *amqp091.Channel
	cfg    *config.RabbitMQConfig
	repo   *meilisearch.MeiliSearchRepository
	logger *slog.Logger
	ctx    context.Context
	cancel context.CancelFunc
}

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

func (c *RabbitMQConsumer) connect() error {
	conn, err := amqp091.Dial(c.cfg.URL)
	if err != nil {
		return fmt.Errorf("failed to dial RabbitMQ: %w", err)
	}

	ch, err := conn.Channel()
	if err != nil {
		conn.Close()
		return fmt.Errorf("failed to open channel: %w", err)
	}

	c.conn = conn
	c.ch = ch

	// Настройка уведомления о закрытии соединения
	go func() {
		notify := conn.NotifyClose(make(chan *amqp091.Error, 1))
		if err := <-notify; err != nil {
			c.logger.Error("RabbitMQ connection closed", slog.String("error", err.Error()))
			time.Sleep(c.cfg.Reconnect)
			c.connect()
		}
	}()

	return nil
}

func (c *RabbitMQConsumer) setupExchangeAndQueue() error {
	// Обменник типа Topic для маршрутизации событий
	err := c.ch.ExchangeDeclare(
		c.cfg.Exchange,
		"topic",
		true,
		false,
		false,
		false,
		nil,
	)
	if err != nil {
		return fmt.Errorf("failed to declare exchange: %w", err)
	}

	// Очередь для сервиса поиска
	queue, err := c.ch.QueueDeclare(
		c.cfg.QueueName,
		true,
		false,
		false,
		false,
		nil,
	)
	if err != nil {
		return fmt.Errorf("failed to declare queue: %w", err)
	}

	// Привязка очереди к обменнику с routing key для всех событий рецептов
	err = c.ch.QueueBind(
		queue.Name,
		"recipe.#",
		c.cfg.Exchange,
		false,
		nil,
	)
	if err != nil {
		return fmt.Errorf("failed to bind queue: %w", err)
	}

	c.logger.Info("Exchange and queue setup complete",
		slog.String("exchange", c.cfg.Exchange),
		slog.String("queue", c.cfg.QueueName))

	return nil
}

func (c *RabbitMQConsumer) consume() error {
	msgs, err := c.ch.Consume(
		c.cfg.QueueName,
		"",
		false,
		false,
		false,
		false,
		nil,
	)
	if err != nil {
		return fmt.Errorf("failed to register consumer: %w", err)
	}

	go func() {
		for {
			select {
			case <-c.ctx.Done():
				return
			case msg, ok := <-msgs:
				if !ok {
					c.logger.Warn("Consumer channel closed, reconnecting...")
					return
				}
				c.handleMessage(msg)
			}
		}
	}()

	return nil
}

func (c *RabbitMQConsumer) handleMessage(msg amqp091.Delivery) {
	var event RecipeEvent
	if err := json.Unmarshal(msg.Body, &event); err != nil {
		c.logger.Error("Failed to unmarshal event",
			slog.String("error", err.Error()),
			slog.String("body", string(msg.Body)))
		msg.Nack(false, true)
		return
	}

	c.logger.Info("Processing recipe event",
		slog.String("type", string(event.Type)),
		slog.String("recipe_id", event.RecipeID))

	var err error
	switch event.Type {
	case RecipeCreated, RecipeUpdated:
		err = c.handleRecipeUpsert(&event)
	case RecipeDeleted:
		err = c.handleRecipeDelete(&event)
	default:
		c.logger.Warn("Unknown event type", slog.String("type", string(event.Type)))
		msg.Ack(false)
		return
	}

	if err != nil {
		c.logger.Error("Failed to process event",
			slog.String("error", err.Error()),
			slog.String("type", string(event.Type)))
		msg.Nack(false, true) // requeue
	} else {
		msg.Ack(false)
	}
}

func (c *RabbitMQConsumer) handleRecipeUpsert(event *RecipeEvent) error {
	if event.Payload.ID == "" {
		return fmt.Errorf("payload is empty for upsert event")
	}

	doc := &meilisearch.RecipeDocument{
		ID:           event.Payload.ID,
		Title:        event.Payload.Title,
		Description:  event.Payload.Description,
		Cuisine:      event.Payload.Cuisine,
		PrepTime:     event.Payload.PrepTime,
		Difficulty:   event.Payload.Difficulty,
		Ingredients:  event.Payload.Ingredients,
		Tags:         event.Payload.Tags,
		Instructions: event.Payload.Instructions,
		AuthorID:     event.Payload.AuthorID,
		Rating:       event.Payload.Rating,
		ReviewsCount: event.Payload.ReviewsCount,
		CreatedAt:    event.Timestamp.Format(time.RFC3339),
		UpdatedAt:    time.Now().Format(time.RFC3339),
	}

	return c.repo.IndexRecipe(context.Background(), doc)
}

func (c *RabbitMQConsumer) handleRecipeDelete(event *RecipeEvent) error {
	return c.repo.DeleteRecipe(context.Background(), event.RecipeID)
}

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
