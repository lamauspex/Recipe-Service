FROM golang:1.23-alpine AS builder

WORKDIR /build

# === Системные зависимости ===
RUN apk add --no-cache git ca-certificates curl

# === Копируем манифест зависимостей ===
COPY backend/service_search/go.mod ./

# === Копируем весь код сервиса (включая proto) ===
COPY backend/service_search/ ./

# === Скачиваем зависимости и создаём go.sum ===
RUN go mod tidy && \
    go mod download

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

# === Запуск от непривилегированного пользователя ===
USER appuser

# === Порты (gRPC + HTTP) ===
EXPOSE 50052 8002

# === Точка входа ===
ENTRYPOINT ["./main"]