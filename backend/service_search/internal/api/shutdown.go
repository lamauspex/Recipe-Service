package api

import (
	"context"
	"log/slog"
	"os"
	"os/signal"
	"syscall"

	"google.golang.org/grpc"
)

// waitForShutdown ожидает сигнал остановки и выполняет graceful shutdown
func (s *SearchServer) waitForShutdown(grpcServer *grpc.Server) {
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	s.logger.Info("Shutting down Search Service")

	ctx, cancel := context.WithTimeout(context.Background(), ShutdownTimeout)
	defer cancel()

	// Graceful shutdown gRPC
	done := make(chan struct{})
	go func() {
		grpcServer.GracefulStop()
		close(done)
	}()

	select {
	case <-done:
		s.logger.Info("gRPC server stopped gracefully")
	case <-ctx.Done():
		grpcServer.Stop()
		s.logger.Info("gRPC server stopped forcefully")
	}

	// Stop consumer
	if err := s.consumer.Stop(); err != nil {
		s.logger.Error("Failed to stop consumer", slog.String("error", err.Error()))
	} else {
		s.logger.Info("Consumer stopped gracefully")
	}

	s.logger.Info("Search Service stopped")
}
