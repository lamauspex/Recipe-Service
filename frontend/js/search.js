// ── SEARCH ─────────────────────────────────────────────────
import { API }       from './constants.js';
import { showToast } from './toast.js';

function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

function buildResultRow(recipe) {
  const row = document.createElement('div');
  row.className = 'result-row';
  row.innerHTML = `
    <span class="result-row__name">${escHtml(recipe.title)}</span>
    <span class="result-row__tag">${escHtml(recipe.cuisine || '')}</span>
  `;
  return row;
}

async function runSearch(query, resultsEl) {
  if (!query) return;

  resultsEl.innerHTML = `<p class="search-results__label">Поиск…</p>`;

  try {
    const res  = await fetch(`${API.SEARCH}?q=${encodeURIComponent(query)}`);
    const data = await res.json();

    if (!res.ok || !data.results?.length) {
      resultsEl.innerHTML = `
        <p class="search-results__label">По запросу «${escHtml(query)}» ничего не найдено</p>
      `;
      return;
    }

    const label = document.createElement('p');
    label.className   = 'search-results__label';
    label.textContent = `${data.results.length} результат(а)`;

    resultsEl.replaceChildren(label, ...data.results.map(buildResultRow));
  } catch {
    resultsEl.innerHTML = `<p class="search-results__label">Ошибка соединения</p>`;
  }
}

export function initSearch() {
  const input     = document.getElementById('search-input');
  const btn       = document.getElementById('search-btn');
  const resultsEl = document.getElementById('search-results');

  const submit = () => runSearch(input.value.trim(), resultsEl);

  btn.addEventListener('click', submit);
  input.addEventListener('keydown', e => { if (e.key === 'Enter') submit(); });
}
