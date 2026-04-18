package api

import (
	"context"
	"log/slog"
	"time"

	"google.golang.org/grpc"
)

// loggingInterceptor — middleware для логирования gRPC запросов
func (s *SearchServer) loggingInterceptor(
	ctx context.Context,
	req interface{},
	info *grpc.UnaryServerInfo,
	handler grpc.UnaryHandler,
) (interface{}, error) {
	start := time.Now()

	resp, err := handler(ctx, req)

	duration := time.Since(start)

	if err != nil {
		s.logger.Error("gRPC request failed",
			slog.String("method", info.FullMethod),
			slog.String("error", err.Error()),
			slog.Duration("duration", duration),
		)
	} else {
		s.logger.Debug("gRPC request completed",
			slog.String("method", info.FullMethod),
			slog.Duration("duration", duration),
		)
	}

	return resp, err
}
