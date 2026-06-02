// ── CONSTANTS ──────────────────────────────────────────────
// Single source of truth for all magic numbers and strings.

export const API = {
  LOGIN: '/api/v1/auth/login',
  REGISTER: '/api/v1/register',
  REFRESH: '/api/v1/auth/refresh',
  SEARCH: '/api/v1/search',
  RECIPES: '/api/v1/recipes',
};

export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
};

export const TOAST_DURATION_MS = 3000;
