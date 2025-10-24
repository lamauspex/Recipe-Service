#!/usr/bin/env python3
"""
Скрипт для запуска user-service в режиме разработки
"""
import uvicorn
import os
import sys

# Добавляем src в путь для импорта
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="debug"
    )