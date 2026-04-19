# ========== Билд-этап ==========
FROM golang:1.23-alpine AS builder

WORKDIR /build

# === Системные зависимости для сборки ===
RUN apk add --no-cache git ca-certificates

# === Копируем манифест зависимостей ===
COPY backend/service_search/go.mod ./

# === Копируем код сервиса ===
COPY backend/service_search/ ./

# === Скачиваем зависимости ===
RUN go mod tidy
RUN go mod download


# === Сборка ===
RUN CGO_ENABLED=0 GOOS=linux go build \
    -ldflags="-w -s" \
    -o main \
    ./main.go

# ========== Runtime-этап ==========
FROM alpine:3.20

WORKDIR /app

# === Минимальные runtime-зависимости ===
RUN apk --no-cache add \
    ca-certificates \
    tzdata \
    wget \
    && addgroup -g 1000 appgroup \
    && adduser -u 1000 -G appgroup -D appuser

# === Копируем бинарник из билд-этапа ===
COPY --from=builder /build/main .

# === Переменные окружения ===
ENV GIN_MODE=release

# === Запуск от непривилегированного пользователя ===
USER appuser

# === Healthcheck ===
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8002/health || exit 1

# === Порты ===
EXPOSE 8002 50052

# === Точка входа ===
ENTRYPOINT ["./main"]