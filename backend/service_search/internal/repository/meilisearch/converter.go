package meilisearch

import (
	"encoding/json"

	"github.com/meilisearch/meilisearch-go"
)

func convertHitToDocument(hit map[string]any, doc *RecipeDocument) error {
	if id, ok := hit["id"].(string); ok {
		doc.ID = id
	}
	if title, ok := hit["title"].(string); ok {
		doc.Title = title
	}
	if desc, ok := hit["description"].(string); ok {
		doc.Description = desc
	}
	if cuisine, ok := hit["cuisine"].(string); ok {
		doc.Cuisine = cuisine
	}
	if prepTime, ok := hit["prep_time"].(float64); ok {
		doc.PrepTime = int(prepTime)
	}
	if difficulty, ok := hit["difficulty"].(string); ok {
		doc.Difficulty = difficulty
	}
	if tags, ok := hit["tags"].([]any); ok {
		doc.Tags = make([]string, 0, len(tags))
		for _, tag := range tags {
			if t, ok := tag.(string); ok {
				doc.Tags = append(doc.Tags, t)
			}
		}
	}
	if ingredients, ok := hit["ingredients"].([]any); ok {
		doc.Ingredients = make([]string, 0, len(ingredients))
		for _, ing := range ingredients {
			if i, ok := ing.(string); ok {
				doc.Ingredients = append(doc.Ingredients, i)
			}
		}
	}
	if instructions, ok := hit["instructions"].(string); ok {
		doc.Instructions = instructions
	}
	if authorID, ok := hit["author_id"].(string); ok {
		doc.AuthorID = authorID
	}
	if rating, ok := hit["rating"].(float64); ok {
		doc.Rating = rating
	}
	if reviewsCount, ok := hit["reviews_count"].(float64); ok {
		doc.ReviewsCount = int(reviewsCount)
	}
	if createdAt, ok := hit["created_at"].(string); ok {
		doc.CreatedAt = createdAt
	}
	if updatedAt, ok := hit["updated_at"].(string); ok {
		doc.UpdatedAt = updatedAt
	}
	return nil
}

// convertHitToDocumentFromJSON конвертирует hit из JSON в документ (для новых версий meilisearch-go)
func convertHitToDocumentFromJSON(hit meilisearch.Hit, doc *RecipeDocument) error {
	data, err := json.Marshal(hit)
	if err != nil {
		return err
	}
	return json.Unmarshal(data, doc)
}
