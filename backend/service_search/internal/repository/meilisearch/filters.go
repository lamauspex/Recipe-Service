package meilisearch

func buildFilters(filters *SearchFilters) string {
	var filterStrings []string

	// TODO: Добавить поддержку фильтров при расширении модели Recipe
	// if filters != nil {
	// 	if filters.Cuisine != "" {
	// 		filterStrings = append(filterStrings, fmt.Sprintf("cuisine = \"%s\"", filters.Cuisine))
	// 	}
	// 	if filters.Difficulty != "" {
	// 		filterStrings = append(filterStrings, fmt.Sprintf("difficulty = \"%s\"", filters.Difficulty))
	// 	}
	// 	if filters.MaxPrepTime > 0 {
	// 		filterStrings = append(filterStrings, fmt.Sprintf("prep_time <= %d", filters.MaxPrepTime))
	// 	}
	// 	if len(filters.Ingredients) > 0 {
	// 		for _, ing := range filters.Ingredients {
	// 			filterStrings = append(filterStrings, fmt.Sprintf("ingredients CONTAINS \"%s\"", ing))
	// 		}
	// 	}
	// 	if len(filters.Tags) > 0 {
	// 		for _, tag := range filters.Tags {
	// 			filterStrings = append(filterStrings, fmt.Sprintf("tags CONTAINS \"%s\"", tag))
	// 		}
	// 	}
	// }

	return join(filterStrings, " AND ")
}

// join соединяет строки разделителем (замена strings.Join)
func join(elems []string, sep string) string {
	switch len(elems) {
	case 0:
		return ""
	case 1:
		return elems[0]
	}

	n := len(sep) * (len(elems) - 1)
	for i := 0; i < len(elems); i++ {
		n += len(elems[i])
	}

	b := make([]byte, n)
	bp := copy(b, elems[0])
	for _, s := range elems[1:] {
		bp += copy(b[bp:], sep)
		bp += copy(b[bp:], s)
	}
	return string(b)
}
