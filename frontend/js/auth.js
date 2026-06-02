// ── AUTH MODAL ─────────────────────────────────────────────
import { Modal }    from './modal.js';
import { showToast } from './toast.js';
import { API, STORAGE_KEYS } from './constants.js';

class AuthModal extends Modal {
  constructor() {
    super('auth-overlay');

    this._emailInput    = document.getElementById('auth-email');
    this._passwordInput = document.getElementById('auth-password');
    this._loginBtn      = document.getElementById('auth-login-btn');
    this._registerBtn   = document.getElementById('auth-register-btn');

    this._loginBtn.addEventListener('click', () => this._handleLogin());
    this._registerBtn.addEventListener('click', () => this._handleRegister());

    // Submit on Enter inside password field
    this._passwordInput.addEventListener('keydown', e => {
      if (e.key === 'Enter') this._handleLogin();
    });
  }

  onClose() {
    // Reset form on close
    this._emailInput.value    = '';
    this._passwordInput.value = '';
    this._setLoading(false);
  }

  // ── Login ─────────────────────────────────────────────────
  async _handleLogin() {
    const email    = this._emailInput.value.trim();
    const password = this._passwordInput.value;

    if (!email || !password) { showToast('Заполните оба поля'); return; }

    this._setLoading(true);
    try {
      const res  = await fetch(API.LOGIN, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json();

      if (res.ok) {
        localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN,  data.access_token);
        localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, data.refresh_token);
        const name = data.name || email.split('@')[0];
        this.close();
        setUserPill(name);
        showToast('Добро пожаловать');
      } else {
        showToast(data.detail || 'Неверные данные');
      }
    } catch {
      showToast('Нет соединения с сервером');
    } finally {
      this._setLoading(false);
    }
  }

  // ── Register (stub) ───────────────────────────────────────
  _handleRegister() {
    showToast('Регистрация будет добавлена в следующем этапе');
  }

  // ── Helpers ───────────────────────────────────────────────
  _setLoading(on) {
    this._loginBtn.disabled    = on;
    this._registerBtn.disabled = on;
    this._loginBtn.textContent = on ? '...' : 'Войти';
  }
}

// ── Header pill ────────────────────────────────────────────
function setUserPill(name) {
  const btn = document.getElementById('header-auth-btn');
  btn.textContent = name;
  btn.className   = 'user-pill';
  btn.onclick     = null;
}

// ── Init ───────────────────────────────────────────────────
export function initAuth() {
  const modal = new AuthModal();
  document.getElementById('header-auth-btn')
    .addEventListener('click', () => modal.open());
}
