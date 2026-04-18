package meilisearch

import (
	"context"
	"fmt"
	"time"

	"github.com/meilisearch/meilisearch-go"
)

// IndexRecipe добавляет или обновляет рецепт в индексе
func (r *MeiliSearchRepository) IndexRecipe(ctx context.Context, doc *RecipeDocument) error {
	start := time.Now()

	task, err := r.client.Index(r.indexName).AddDocuments([]RecipeDocument{*doc}, nil)
	if err != nil {
		return fmt.Errorf("failed to index recipe: %w", err)
	}

	// Ожидаем выполнения задачи
	ticker := time.NewTicker(100 * time.Millisecond)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return ctx.Err()
		case <-ticker.C:
			status, err := r.client.GetTask(task.TaskUID)
			if err != nil {
				continue
			}
			if status.Status == "succeeded" {
				r.logger.Debug("recipe indexed", "id", doc.ID, "duration", time.Since(start))
				return nil
			}
			if status.Status == "failed" {
				return fmt.Errorf("indexing task failed: %v", status.Error)
			}
		}
	}
}

// DeleteRecipe удаляет рецепт из индекса
func (r *MeiliSearchRepository) DeleteRecipe(ctx context.Context, id string) error {
	start := time.Now()

	task, err := r.client.Index(r.indexName).DeleteDocument(id)
	if err != nil {
		return fmt.Errorf("failed to delete recipe: %w", err)
	}

	// Ожидаем выполнения задачи
	ticker := time.NewTicker(100 * time.Millisecond)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return ctx.Err()
		case <-ticker.C:
			status, err := r.client.GetTask(task.TaskUID)
			if err != nil {
				continue
			}
			if status.Status == "succeeded" {
				r.logger.Debug("recipe deleted", "id", id, "duration", time.Since(start))
				return nil
			}
			if status.Status == "failed" {
				return fmt.Errorf("deletion task failed: %v", status.Error)
			}
		}
	}
}

// GetRecipeByID получает рецепт по ID
func (r *MeiliSearchRepository) GetRecipeByID(ctx context.Context, id string) (*RecipeDocument, error) {
	var doc RecipeDocument
	query := &meilisearch.DocumentQuery{}
	err := r.client.Index(r.indexName).GetDocument(id, query, &doc)
	if err != nil {
		return nil, fmt.Errorf("failed to get recipe: %w", err)
	}
	return &doc, nil
}

// DeleteIndex удаляет весь индекс (для тестов)
func (r *MeiliSearchRepository) DeleteIndex(ctx context.Context) error {
	// Удаляем конкретный документ по ID или весь индекс
	// Используем DeleteIndex с именем индекса
	task, err := r.client.DeleteIndex(r.indexName)
	if err != nil {
		// Индекс может не существовать - это нормально
		return nil
	}

	// Ожидаем выполнения задачи
	ticker := time.NewTicker(100 * time.Millisecond)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return ctx.Err()
		case <-ticker.C:
			status, err := r.client.GetTask(task.TaskUID)
			if err != nil {
				continue
			}
			if status.Status == "succeeded" || status.Status == "failed" {
				return nil
			}
		}
	}
}
