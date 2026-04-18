package consumer

import (
	"context"
	"encoding/json"
	"fmt"
	"log/slog"
	"time"

	"github.com/lamauspex/recipes/backend/service_search/internal/repository/meilisearch"
	"github.com/rabbitmq/amqp091-go"
)

// handleMessage обрабатывает входящее сообщение
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

// handleRecipeUpsert обрабатывает создание или обновление рецепта
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

// handleRecipeDelete обрабатывает удаление рецепта
func (c *RabbitMQConsumer) handleRecipeDelete(event *RecipeEvent) error {
	return c.repo.DeleteRecipe(context.Background(), event.RecipeID)
}
