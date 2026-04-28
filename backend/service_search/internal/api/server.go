package api

import (
	"fmt"
	"log/slog"
	"net"
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
	DefaultPage            = 1
	DefaultPageSize        = 10
	MaxPageSize            = 100
	ShutdownTimeout        = 30 * time.Second
	ServerVersion          = "1.0.0"
	ConsumerReconnect      = 5 * time.Second
	ConsumerStartupTimeout = 10 * time.Second
)

// SearchServer — gRPC сервер для поиска рецептов
type SearchServer struct {
	proto.UnimplementedSearchServiceServer
	cfg       *config.Config
	repo      *meilisearch.MeiliSearchRepository
	consumer  *consumer.RabbitMQConsumer
	logger    *slog.Logger
	startTime time.Time
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

// Start запускает gRPC сервер
func (s *SearchServer) Start() error {
	lis, err := net.Listen("tcp", fmt.Sprintf("%s:%d", s.cfg.Server.Host, s.cfg.GRPC.Port))
	if err != nil {
		return fmt.Errorf("failed to listen: %w", err)
	}

	grpcServer := s.createGRPCServer()

	s.logger.Info("Starting Search Service gRPC server",
		slog.String("address", lis.Addr().String()))

	// Запуск RabbitMQ consumer в фоне
	go func() {
		if err := s.consumer.Start(); err != nil {
			s.logger.Error("Consumer error", slog.String("error", err.Error()))
		}
	}()

	// Запуск gRPC сервера (блокирующий)
	if err := grpcServer.Serve(lis); err != nil {
		return fmt.Errorf("failed to serve: %w", err)
	}

	return nil
}

func (s *SearchServer) createGRPCServer() *grpc.Server {
	grpcServer := grpc.NewServer(
		grpc.UnaryInterceptor(s.loggingInterceptor),
	)
	proto.RegisterSearchServiceServer(grpcServer, s)
	grpc_health_v1.RegisterHealthServer(grpcServer, s)
	return grpcServer
}
