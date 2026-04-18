package api

import (
	"context"
	"fmt"
	"time"

	"github.com/lamauspex/recipes/backend/service_search/proto"
	"google.golang.org/grpc/health/grpc_health_v1"
	emptypb "google.golang.org/protobuf/types/known/emptypb"
)

// Health — health check для протокола приложения
func (s *SearchServer) Health(ctx context.Context, _ *emptypb.Empty) (*proto.HealthResponse, error) {
	healthStatus, err := s.repo.Health(ctx)
	if err != nil {
		return &proto.HealthResponse{
			Status:            "error",
			Version:           ServerVersion,
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
		Version:           ServerVersion,
		UptimeSeconds:     int64(time.Since(s.startTime).Seconds()),
		MeilisearchStatus: healthStatus.Message,
	}, nil
}

// Check — grpc health check (согласовано с grpc_health_v1)
func (s *SearchServer) Check(ctx context.Context, req *grpc_health_v1.HealthCheckRequest) (*grpc_health_v1.HealthCheckResponse, error) {
	healthStatus, err := s.repo.Health(ctx)
	if err != nil || !healthStatus.Healthy {
		return &grpc_health_v1.HealthCheckResponse{
			Status: grpc_health_v1.HealthCheckResponse_NOT_SERVING,
		}, nil
	}
	return &grpc_health_v1.HealthCheckResponse{
		Status: grpc_health_v1.HealthCheckResponse_SERVING,
	}, nil
}

// Watch — grpc health watch
func (s *SearchServer) Watch(req *grpc_health_v1.HealthCheckRequest, server grpc_health_v1.Health_WatchServer) error {
	// Отправляем начальное состояние
	resp, err := s.Check(server.Context(), req)
	if err != nil {
		return err
	}
	if err := server.Send(resp); err != nil {
		return err
	}

	// Подписываемся на изменения
	ticker := time.NewTicker(10 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-server.Context().Done():
			return server.Context().Err()
		case <-ticker.C:
			resp, err := s.Check(server.Context(), req)
			if err != nil {
				return err
			}
			if err := server.Send(resp); err != nil {
				return err
			}
		}
	}
}
