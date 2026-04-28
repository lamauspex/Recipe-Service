package meilisearch

import (
	"context"
	"fmt"
	"time"

	"github.com/meilisearch/meilisearch-go"
)

const taskWaitTimeout = 30 * time.Second

// waitForTask ожидает завершения задачи с таймаутом
func (r *MeiliSearchRepository) waitForTask(ctx context.Context, taskUID int64) error {
	deadline := time.Now().Add(taskWaitTimeout)
	ticker := time.NewTicker(100 * time.Millisecond)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return ctx.Err()
		case <-ticker.C:
			if time.Now().After(deadline) {
				return fmt.Errorf("task %d timed out after %v", taskUID, taskWaitTimeout)
			}
			status, err := r.client.GetTask(taskUID)
			if err != nil {
				continue
			}
			if status.Status == "succeeded" {
				return nil
			}
			if status.Status == "failed" {
				return fmt.Errorf("task %d failed: %v", taskUID, status.Error)
			}
		}
	}
}

// IndexRecipe добавляет или обновляет рецепт в индексе
func (r *MeiliSearchRepository) IndexRecipe(ctx context.Context, doc *RecipeDocument) error {
	start := time.Now()

	task, err := r.client.Index(r.indexName).AddDocuments([]RecipeDocument{*doc}, nil)
	if err != nil {
		return fmt.Errorf("failed to index recipe: %w", err)
	}

	if err := r.waitForTask(ctx, task.TaskUID); err != nil {
		return err
	}

	r.logger.Debug("recipe indexed", "id", doc.ID, "duration", time.Since(start))
	return nil
}

// DeleteRecipe удаляет рецепт из индекса
func (r *MeiliSearchRepository) DeleteRecipe(ctx context.Context, id string) error {
	start := time.Now()

	task, err := r.client.Index(r.indexName).DeleteDocument(id)
	if err != nil {
		return fmt.Errorf("failed to delete recipe: %w", err)
	}

	if err := r.waitForTask(ctx, task.TaskUID); err != nil {
		return err
	}

	r.logger.Debug("recipe deleted", "id", id, "duration", time.Since(start))
	return nil
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
	task, err := r.client.DeleteIndex(r.indexName)
	if err != nil {
		return nil // индекс может не существовать
	}
	return r.waitForTask(ctx, task.TaskUID)
}
