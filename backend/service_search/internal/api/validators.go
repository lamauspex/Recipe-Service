package api

// validatePagination проверяет и нормализует параметры пагинации
func validatePagination(page, pageSize int) (int, int) {
	if page < 1 {
		page = DefaultPage
	}
	if pageSize < 1 {
		pageSize = DefaultPageSize
	}
	if pageSize > MaxPageSize {
		pageSize = MaxPageSize
	}
	return page, pageSize
}

// validateSearchRequest проверяет валидность запроса на поиск
func validateSearchRequest(req interface{}) error {
	// Можно расширить для более сложной валидации
	return nil
}
