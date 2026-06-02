// ── TOAST ──────────────────────────────────────────────────
import { TOAST_DURATION_MS } from './constants.js';

const el = document.getElementById('toast');
let timer = null;

export function showToast(message) {
  el.textContent = message;
  el.classList.add('toast--visible');
  clearTimeout(timer);
  timer = setTimeout(() => el.classList.remove('toast--visible'), TOAST_DURATION_MS);
}
