package consumer

import (
	"fmt"
	"log/slog"

	"github.com/rabbitmq/amqp091-go"
)

// connect устанавливает подключение к RabbitMQ
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

	// Обменник типа Topic
	if err := c.ch.ExchangeDeclare(
		c.cfg.Exchange, "topic", true, false, false, false, nil,
	); err != nil {
		c.close()
		return fmt.Errorf("failed to declare exchange: %w", err)
	}

	// Очередь
	queue, err := c.ch.QueueDeclare(
		c.cfg.QueueName, true, false, false, false, nil,
	)
	if err != nil {
		c.close()
		return fmt.Errorf("failed to declare queue: %w", err)
	}

	// Привязка
	if err := c.ch.QueueBind(
		queue.Name, "recipe.#", c.cfg.Exchange, false, nil,
	); err != nil {
		c.close()
		return fmt.Errorf("failed to bind queue: %w", err)
	}

	c.logger.Info("Exchange and queue setup complete",
		slog.String("exchange", c.cfg.Exchange),
		slog.String("queue", c.cfg.QueueName))

	return nil
}

// consume запускает потребление сообщений — блокирующий вызов
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

	c.logger.Info("RabbitMQ consumer started, waiting for messages")

	for {
		select {
		case <-c.ctx.Done():
			return nil
		case msg, ok := <-msgs:
			if !ok {
				c.logger.Warn("Consumer channel closed")
				return fmt.Errorf("consumer channel closed")
			}
			c.handleMessage(msg)
		}
	}
}

// close закрывает текущее соединение и канал
func (c *RabbitMQConsumer) close() {
	if c.ch != nil {
		c.ch.Close()
		c.ch = nil
	}
	if c.conn != nil {
		c.conn.Close()
		c.conn = nil
	}
}
