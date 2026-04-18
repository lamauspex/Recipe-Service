package meilisearch

import (
	"encoding/json"

	"github.com/meilisearch/meilisearch-go"
)

// convertHitToDocumentFromJSON конвертирует hit из JSON в документ (для новых версий meilisearch-go)
func convertHitToDocumentFromJSON(hit meilisearch.Hit, doc *RecipeDocument) error {
	data, err := json.Marshal(hit)
	if err != nil {
		return err
	}
	return json.Unmarshal(data, doc)
}
