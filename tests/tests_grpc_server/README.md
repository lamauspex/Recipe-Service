# Тестирование gRPC сервера

## Запуск и тестирование

Запустите сервер:

bash
python server.py

В консоли должно появиться: gRPC Server started on port 50051.

## В другом терминале запустите клиент:

bash
python client.py

Ожидаемый вывод клиента:

Testing ValidateToken...
ValidateToken response: valid: true
user_id: "123"
email: "user@example.com"
error: ""

Testing GetUserById...
GetUserById response: id: "123"
email: "user@example.com"
user_name: "John Doe"
is_active: true
exists: true