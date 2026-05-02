package api

import (
	"context"
	"fmt"
	"log/slog"
	"net"
	"net/http"
	"time"

	"github.com/lamauspex/recipes/backend/service_search/internal/config"
	"github.com/lamauspex/recipes/backend/service_search/internal/consumer"
	"github.com/lamauspex/recipes/backend/service_search/internal/repository/meilisearch"
	"github.com/lamauspex/recipes/backend/service_search/proto"
	"google.golang.org/grpc"
	"google.golang.org/grpc/health/grpc_health_v1"
)

// Константы для сервера
const (
	DefaultPage     = 1
	DefaultPageSize = 10
	MaxPageSize     = 100
	ServerVersion   = "1.0.0"

	ConsumerReconnect      = 5 * time.Second
	ConsumerStartupTimeout = 10 * time.Second
)

// SearchServer — gRPC + HTTP сервер для поиска рецептов
type SearchServer struct {
	proto.UnimplementedSearchServiceServer
	cfg        *config.Config
	repo       *meilisearch.MeiliSearchRepository
	consumer   *consumer.RabbitMQConsumer
	logger     *slog.Logger
	startTime  time.Time
	httpServer *http.Server // HTTP сервер для REST API
}

// NewSearchServer создаёт новый экземпляр сервера
func NewSearchServer(cfg *config.Config, repo *meilisearch.MeiliSearchRepository, consumer *consumer.RabbitMQConsumer, logger *slog.Logger) (*SearchServer, error) {
	if cfg == nil {
		return nil, fmt.Errorf("config cannot be nil")
	}
	if repo == nil {
		return nil, fmt.Errorf("repository cannot be nil")
	}
	if consumer == nil {
		return nil, fmt.Errorf("consumer cannot be nil")
	}
	if logger == nil {
		return nil, fmt.Errorf("logger cannot be nil")
	}

	return &SearchServer{
		cfg:       cfg,
		repo:      repo,
		consumer:  consumer,
		logger:    logger,
		startTime: time.Now(),
	}, nil
}

// Start запускает gRPC и HTTP серверы параллельно
func (s *SearchServer) Start() error {
	// Запуск RabbitMQ consumer в фоне
	go func() {
		if err := s.consumer.Start(); err != nil {
			s.logger.Error("Consumer error", slog.String("error", err.Error()))
		}
	}()

	// === Запуск gRPC сервера ===
	grpcLis, err := net.Listen("tcp", fmt.Sprintf("%s:%d", s.cfg.Server.Host, s.cfg.GRPC.Port))
	if err != nil {
		return fmt.Errorf("failed to listen for gRPC: %w", err)
	}

	grpcServer := s.createGRPCServer()
	s.logger.Info("Starting Search Service gRPC server",
		slog.String("address", grpcLis.Addr().String()))

	// gRPC сервер запускается в отдельной goroutine
	go func() {
		if err := grpcServer.Serve(grpcLis); err != nil {
			s.logger.Error("gRPC server error", slog.String("error", err.Error()))
		}
	}()

	// === Запуск HTTP сервера ===
	httpRouter := s.SetupHTTPRoutes()

	httpAddr := fmt.Sprintf("%s:%d", s.cfg.Server.Host, s.cfg.Server.Port)
	s.httpServer = &http.Server{
		Addr:         httpAddr,
		Handler:      httpRouter.(http.Handler),
		ReadTimeout:  15 * time.Second,
		WriteTimeout: 15 * time.Second,
		IdleTimeout:  60 * time.Second,
	}

	s.logger.Info("Starting Search Service HTTP server",
		slog.String("address", httpAddr))

	// HTTP сервер запускается в отдельной goroutine
	go func() {
		if err := s.httpServer.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			s.logger.Error("HTTP server error", slog.String("error", err.Error()))
		}
	}()

	s.logger.Info("Search Service started successfully",
		slog.String("grpc_address", grpcLis.Addr().String()),
		slog.String("http_address", httpAddr))

	// Блокируем главную goroutine (ожидаем сигнал остановки из main.go)
	select {}
}

func (s *SearchServer) createGRPCServer() *grpc.Server {
	grpcServer := grpc.NewServer(
		grpc.UnaryInterceptor(s.loggingInterceptor),
	)
	proto.RegisterSearchServiceServer(grpcServer, s)
	grpc_health_v1.RegisterHealthServer(grpcServer, s)
	return grpcServer
}

// Shutdown выполняет graceful shutdown всех компонентов
func (s *SearchServer) Shutdown(ctx context.Context) error {
	s.logger.Info("Shutting down server...")

	// 1. Остановка HTTP сервера
	if s.httpServer != nil {
		if err := s.httpServer.Shutdown(ctx); err != nil {
			s.logger.Error("HTTP server shutdown error", slog.String("error", err.Error()))
			return err
		}
		s.logger.Info("HTTP server stopped gracefully")
	}

	// 2. Остановка consumer
	if err := s.consumer.Stop(); err != nil {
		s.logger.Error("Failed to stop consumer", slog.String("error", err.Error()))
		return err
	}
	s.logger.Info("Consumer stopped gracefully")

	return nil
}
