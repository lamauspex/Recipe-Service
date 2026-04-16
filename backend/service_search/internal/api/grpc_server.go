package api

import (
	"context"
	"fmt"
	"log"
	"log/slog"
	"net"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/lamauspex/recipes/backend/service_search/internal/config"
	"github.com/lamauspex/recipes/backend/service_search/internal/consumer"
	"github.com/lamauspex/recipes/backend/service_search/internal/repository"
	"github.com/lamauspex/recipes/backend/service_search/proto"
	"google.golang.org/grpc"
	"google.golang.org/grpc/health/grpc_health_v1"
	emptypb "google.golang.org/protobuf/types/known/emptypb"
)

type SearchServer struct {
	proto.UnimplementedSearchServiceServer
	cfg       *config.Config
	repo      *repository.MeiliSearchRepository
	consumer  *consumer.RabbitMQConsumer
	logger    *slog.Logger
	startTime time.Time
}

func NewSearchServer(cfg *config.Config, repo *repository.MeiliSearchRepository, consumer *consumer.RabbitMQConsumer, logger *slog.Logger) *SearchServer {
	return &SearchServer{
		cfg:       cfg,
		repo:      repo,
		consumer:  consumer,
		logger:    logger,
		startTime: time.Now(),
	}
}

func (s *SearchServer) Start() error {
	lis, err := net.Listen("tcp", fmt.Sprintf("%s:%d", s.cfg.Server.Host, s.cfg.Server.Port))
	if err != nil {
		return fmt.Errorf("failed to listen: %w", err)
	}

	grpcServer := grpc.NewServer()
	proto.RegisterSearchServiceServer(grpcServer, s)
	grpc_health_v1.RegisterHealthServer(grpcServer, s)

	s.logger.Info("Starting Search Service gRPC server",
		slog.String("address", lis.Addr().String()))

	go func() {
		if err := grpcServer.Serve(lis); err != nil {
			s.logger.Error("Failed to serve", slog.String("error", err.Error()))
		}
	}()

	// Запуск RabbitMQ consumer
	go func() {
		if err := s.consumer.Start(); err != nil {
			s.logger.Error("Consumer failed", slog.String("error", err.Error()))
		}
	}()

	// Ожидание сигнала остановки
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	s.logger.Info("Shutting down Search Service")

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	grpcServer.GracefulStop()

	if err := s.consumer.Stop(); err != nil {
		s.logger.Error("Failed to stop consumer", slog.String("error", err.Error()))
	}

	s.logger.Info("Search Service stopped")
	return nil
}

// SearchRecipes - поиск рецептов
func (s *SearchServer) SearchRecipes(ctx context.Context, req *proto.SearchRequest) (*proto.SearchResponse, error) {
	filters := &repository.SearchFilters{
		Cuisine:     req.GetCuisine(),
		Difficulty:  req.GetDifficulty(),
		MaxPrepTime: req.GetMaxPrepTime(),
		Ingredients: req.GetIngredients(),
		Tags:        req.GetTags(),
	}

	page := int(req.Page)
	if page < 1 {
		page = 1
	}
	pageSize := int(req.PageSize)
	if pageSize < 1 {
		pageSize = 10
	}
	if pageSize > 100 {
		pageSize = 100
	}

	result, err := s.repo.Search(ctx, req.Query, filters, page, pageSize)
	if err != nil {
		s.logger.Error("Search failed", slog.String("error", err.Error()))
		return nil, err
	}

	return &proto.SearchResponse{
		Results:    result.Recipes,
		Total:      result.Total,
		Page:       result.Page,
		PageSize:   result.PageSize,
		TotalPages: result.TotalPages,
	}, nil
}

// GetRecipe - получить рецепт по ID
func (s *SearchServer) GetRecipe(ctx context.Context, req *proto.GetRecipeRequest) (*proto.RecipeResponse, error) {
	doc, err := s.repo.GetRecipeByID(ctx, req.Id)
	if err != nil {
		s.logger.Error("Get recipe failed", slog.String("error", err.Error()))
		return nil, err
	}

	return &proto.RecipeResponse{
		Id:           doc.ID,
		Title:        doc.Title,
		Description:  doc.Description,
		Cuisine:      doc.Cuisine,
		PrepTime:     int32(doc.PrepTime),
		Difficulty:   doc.Difficulty,
		Ingredients:  doc.Ingredients,
		Tags:         doc.Tags,
		Instructions: doc.Instructions,
		Rating:       doc.Rating,
		ReviewsCount: int32(doc.ReviewsCount),
		AuthorId:     doc.AuthorID,
	}, nil
}

// GetSuggestions - автодополнение
func (s *SearchServer) GetSuggestions(ctx context.Context, req *proto.SuggestionsRequest) (*proto.SuggestionsResponse, error) {
	fieldType := "title"
	if req.GetType() != "" {
		fieldType = req.GetType()
	}

	limit := int(req.Limit)
	if limit <= 0 {
		limit = 10
	}

	suggestions, err := s.repo.GetSuggestions(ctx, req.Query, fieldType, limit)
	if err != nil {
		s.logger.Error("Suggestions failed", slog.String("error", err.Error()))
		return nil, err
	}

	return &proto.SuggestionsResponse{
		Suggestions: suggestions,
		Type:        fieldType,
	}, nil
}

// Health - health check
func (s *SearchServer) Health(ctx context.Context, _ *emptypb.Empty) (*proto.HealthResponse, error) {
	healthStatus, err := s.repo.Health(ctx)
	if err != nil {
		return &proto.HealthResponse{
			Status:            "error",
			Version:           "1.0.0",
			UptimeSeconds:     int64(time.Since(s.startTime).Seconds()),
			MeilisearchStatus: fmt.Sprintf("error: %v", err),
		}, nil
	}

	status := "ok"
	if !healthStatus.Healthy {
		status = "degraded"
	}

	return &proto.HealthResponse{
		Status:            status,
		Version:           "1.0.0",
		UptimeSeconds:     int64(time.Since(s.startTime).Seconds()),
		MeilisearchStatus: healthStatus.Message,
	}, nil
}

// Check - grpc health check
func (s *SearchServer) Check(ctx context.Context, req *grpc_health_v1.HealthCheckRequest) (*grpc_health_v1.HealthCheckResponse, error) {
	healthStatus, err := s.repo.Health(ctx)
	if err != nil || !healthStatus.Healthy {
		return &grpc_health_v1.HealthCheckResponse{
			Status: grpc_health_v1.HealthCheckResponse_SERVING,
		}, nil
	}
	return &grpc_health_v1.HealthCheckResponse{
		Status: grpc_health_v1.HealthCheckResponse_NOT_SERVING,
	}, nil
}

// Watch - grpc health watch (не реализован)
func (s *SearchServer) Watch(req *grpc_health_v1.HealthCheckRequest, server grpc_health_v1.Health_WatchServer) error {
	return nil
}

func Run() {
	logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
		Level: slog.LevelInfo,
	}))

	cfg := config.Load()

	repo, err := repository.NewMeiliSearchRepository(&cfg.MeiliSearch, logger)
	if err != nil {
		log.Fatalf("Failed to create MeiliSearch repository: %v", err)
	}

	consumer, err := consumer.NewRabbitMQConsumer(&cfg.RabbitMQ, repo, logger)
	if err != nil {
		log.Fatalf("Failed to create RabbitMQ consumer: %v", err)
	}

	server := NewSearchServer(cfg, repo, consumer, logger)

	if err := server.Start(); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}
