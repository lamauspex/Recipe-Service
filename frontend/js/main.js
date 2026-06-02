// ── MAIN ───────────────────────────────────────────────────
// Entry point. Imports and boots each module.
// Nothing lives here except wiring.

import { initAuth }   from './auth.js';
import { initSearch } from './search.js';

document.addEventListener('DOMContentLoaded', () => {
  initAuth();
  initSearch();
});
