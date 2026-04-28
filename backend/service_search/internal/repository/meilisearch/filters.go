package meilisearch

import "strings"

func buildFilters(filters *SearchFilters) string {
	var filterStrings []string

	// TODO: Добавить поддержку фильтров при расширении модели Recipe

	return strings.Join(filterStrings, " AND ")
}
