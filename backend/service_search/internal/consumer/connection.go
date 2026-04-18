package consumer

import (
	"fmt"
	"log/slog"
	"time"

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

// setupExchangeAndQueue настраивает exchange и queue
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

// consume запускает потребление сообщений
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
