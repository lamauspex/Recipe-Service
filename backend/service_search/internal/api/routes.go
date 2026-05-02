package api

import (
	"log/slog"
	"net/http"
	"time"
)

// SetupHTTPRoutes настраивает HTTP маршруты для сервисов
// Возвращает configured http.Handler
func (s *SearchServer) SetupHTTPRoutes() http.Handler {
	mux := http.NewServeMux()

	// === REST API endpoints ===
	// Поиск рецептов
	mux.HandleFunc("GET /api/v1/search", s.SearchHandler)
	mux.HandleFunc("GET /api/v1/search/", s.SearchHandler)

	// Health check
	mux.HandleFunc("GET /health", s.HealthHandler)

	// === Middleware chain ===
	// Обертка с логированием и CORS
	wrappedMux := s.withLogging(s.withCORSMiddleware(mux))

	s.logger.Info("HTTP routes configured",
		slog.String("endpoints", "/api/v1/search, /health"))

	return wrappedMux
}

// withCORSMiddleware добавляет CORS заголовки к обработчику
func (s *SearchServer) withCORSMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// CORS заголовки
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")
		w.Header().Set("Access-Control-Max-Age", "86400")

		// Обработка preflight запросов
		if r.Method == "OPTIONS" {
			w.WriteHeader(http.StatusNoContent)
			return
		}

		next.ServeHTTP(w, r)
	})
}

// withLogging добавляет логирование HTTP запросов
func (s *SearchServer) withLogging(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := s.now()

		// Обертка для записи статуса
		wrapped := &responseWriter{
			ResponseWriter: w,
			status:         http.StatusOK,
		}

		next.ServeHTTP(wrapped, r)

		duration := s.now().Sub(start)
		s.logger.Debug("HTTP request completed",
			slog.String("method", r.Method),
			slog.String("path", r.URL.Path),
			slog.Int("status", wrapped.status),
			slog.Duration("duration", duration),
		)
	})
}

// responseWriter — обертка для записи HTTP статуса
type responseWriter struct {
	http.ResponseWriter
	status int
}

func (rw *responseWriter) WriteHeader(code int) {
	rw.status = code
	rw.ResponseWriter.WriteHeader(code)
}

// now возвращает текущее время (для тестирования можно мокать)
func (s *SearchServer) now() time.Time {
	return time.Now()
}
