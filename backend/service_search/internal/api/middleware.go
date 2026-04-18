package api

import (
	"context"
	"log/slog"
	"time"

	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
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

// recoveryInterceptor — middleware для recovery от panic
func recoveryInterceptor(
	ctx context.Context,
	req interface{},
	info *grpc.UnaryServerInfo,
	handler grpc.UnaryHandler,
) (interface{}, error) {
	defer func() {
		if r := recover(); r != nil {
			// Можно логировать и возвращать ошибку
			_ = r
		}
	}()

	return handler(ctx, req)
}

// statusFromError — конвертация ошибки в gRPC статус
func statusFromError(err error) error {
	if err == nil {
		return nil
	}

	// Пример: если ошибка содержит "not found", возвращаем NotFound
	// Можно расширить для других случаев
	return status.Error(codes.Internal, err.Error())
}
