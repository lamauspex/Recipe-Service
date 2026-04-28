FROM golang:1.23-alpine AS builder

WORKDIR /build

# === Системные зависимости для сборки и protoc ===
RUN apk add --no-cache git ca-certificates protobuf curl

# === Копируем манифест зависимостей ===
COPY backend/service_search/go.mod ./

# === Копируем весь код сервиса (включая proto) ===
COPY backend/service_search/ ./

# === Устанавливаем Go плагины для protoc ===
RUN go install google.golang.org/protobuf/cmd/protoc-gen-go@v1.36.6 && \
    go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@v1.5.1

# === Добавляем bin в PATH (где лежат плагины) ===
ENV PATH="$PATH:/root/go/bin"

# === Скачиваем зависимости и создаём go.sum ===
RUN go mod tidy && \
    go mod download

# === Копируем стандартные proto файлы Google ===
RUN mkdir -p /tmp/protobuf/google/protobuf && \
    curl -sL https://raw.githubusercontent.com/protocolbuffers/protobuf/v29.4/src/google/protobuf/empty.proto -o /tmp/protobuf/google/protobuf/empty.proto && \
    curl -sL https://raw.githubusercontent.com/protocolbuffers/protobuf/v29.4/src/google/protobuf/duration.proto -o /tmp/protobuf/google/protobuf/duration.proto && \
    curl -sL https://raw.githubusercontent.com/protocolbuffers/protobuf/v29.4/src/google/protobuf/timestamp.proto -o /tmp/protobuf/google/protobuf/timestamp.proto && \
    curl -sL https://raw.githubusercontent.com/protocolbuffers/protobuf/v29.4/src/google/protobuf/any.proto -o /tmp/protobuf/google/protobuf/any.proto && \
    curl -sL https://raw.githubusercontent.com/protocolbuffers/protobuf/v29.4/src/google/protobuf/wrappers.proto -o /tmp/protobuf/google/protobuf/wrappers.proto && \
    curl -sL https://raw.githubusercontent.com/protocolbuffers/protobuf/v29.4/src/google/protobuf/struct.proto -o /tmp/protobuf/google/protobuf/struct.proto

# === Генерируем proto файлы ===
RUN protoc --proto_path=/tmp/protobuf \
    --proto_path=. \
    --go_out=. --go_opt=paths=source_relative \
    --go-grpc_out=. --go-grpc_opt=paths=source_relative \
    proto/search_service.proto

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

# === Порты ===
EXPOSE 50052

# === Точка входа ===
ENTRYPOINT ["./main"]