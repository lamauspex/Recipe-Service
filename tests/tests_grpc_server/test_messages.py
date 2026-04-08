

from backend.shared.proto import user_service_pb2


request = user_service_pb2.ValidateTokenRequest(token="test_token")
print("Request:", request)

# Сериализуем
serialized = request.SerializeToString()
print("Serialized:", serialized)

# Десериализуем обратно
new_request = user_service_pb2.ValidateTokenRequest()
new_request.ParseFromString(serialized)
print("Deserialized:", new_request)
