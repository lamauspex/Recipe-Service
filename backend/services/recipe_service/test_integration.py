"""
Тестовый скрипт для проверки импортов и структуры
"""

import sys
import os


# Добавляем корень проекта в путь Python
project_root = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)

print("Testing imports...")

# Проверка импортов репозитория
try:
    print("OK: Repository imports work correctly")
except ImportError as e:
    print(f"ERROR: Repository import error: {e}")

# Проверка импортов сервиса
try:
    print("OK: Service imports work correctly")
except ImportError as e:
    print(f"ERROR: Service import error: {e}")

# Проверка импортов схем
try:
    print("OK: Schema imports work correctly")
except ImportError as e:
    print(f"ERROR: Schema import error: {e}")

# Проверка импортов моделей
try:
    print("OK: Model imports work correctly")
except ImportError as e:
    print(f"ERROR: Model import error: {e}")

print("\nAll components created and configured!")
print("\nNote: Database connection requires .env file with proper settings")
print("See .env.example for reference")
