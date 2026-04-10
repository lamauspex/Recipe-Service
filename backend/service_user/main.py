"""
Точка входа для User Service
"""

from backend.service_user.src.runner import ServiceRunner

if __name__ == "__main__":
    runner = ServiceRunner()
    runner.run()
