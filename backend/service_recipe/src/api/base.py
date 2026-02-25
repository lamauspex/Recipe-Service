""" База API"""

from fastapi import APIRouter

router = APIRouter(
    prefix="/recipes",
    tags=["Рецепты"]
)
