
""" Назначение: В этом файле определяются маршруты (API endpoint). """


from fastapi import HTTPException, Depends, APIRouter
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(prefix="/api_fav", tags="Избранное")


# Добавление в избранное
@router.post("/favorites/my_list/append", summary="Добавить", tags=["Избранное"])
async def favorites_my(recipe_id: int, session: AsyncSession = Depends(get_session), user_id: int = Depends(get_current_active_user)):

    # Проверка на существования рецепта
    recipe_result = await session.execute(select(Recipe).where(Recipe.id == recipe_id))
    recipe = recipe_result.scalar_one_or_none()
    if recipe is None:
        raise HTTPException(status_code=404, detail="Рецепт не найден")

    # Проверка, не добавлен ли рецепт в избранное ранее
    existing_favorite = await session.execute(select(FavouriteRecipe).where(FavouriteRecipe.recipe_id == recipe_id, FavouriteRecipe.user_id == user_id))
    if existing_favorite.scalar_one_or_none():
        raise HTTPException(
            status_code=400, detail="Рецепт уже добавлен в избранное")

    # Добавление рецепта в избранное
    favorite = FavouriteRecipe(recipe_id=recipe_id, user_id=user_id)
    session.add(favorite)
    await session.commit()

    return {"message": "Рецепт добавлен в избранное"}

# Получение списка избранных рецептов


@router.get("/favorites/my_list", response_model=List[RecipeOut], summary="Посмотреть", tags=["Избранное"])
async def get_favorites(session: AsyncSession = Depends(get_session), user_id: int = Depends(get_current_active_user)):

    # Запрос для получения всех рецептов, добавленных в избранное пользователем
    result = await session.execute(
        select(Recipe).join(FavouriteRecipe).where(
            FavouriteRecipe.user_id == user_id)
    )
    favorite_recipes = result.scalars().all()

    # Возвращаем пустой список, если нет избранных рецептов
    if not favorite_recipes:
        return []
    return favorite_recipes
