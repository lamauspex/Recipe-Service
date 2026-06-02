// ── MODAL (base class) ─────────────────────────────────────
// Handles: open/close, Esc key, overlay-click, focus trap, scroll lock.
// Extend this for each concrete modal — no duplication.

import { lockScroll, unlockScroll } from './scroll-lock.js';

const FOCUSABLE = [
  'a[href]',
  'button:not(:disabled)',
  'input:not(:disabled)',
  'select:not(:disabled)',
  'textarea:not(:disabled)',
  '[tabindex]:not([tabindex="-1"])',
].join(', ');

export class Modal {
  /** @param {string} overlayId - ID of the .modal-overlay element */
  constructor(overlayId) {
    this.overlay = document.getElementById(overlayId);
    this.dialog  = this.overlay.querySelector('.modal-dialog');

    this._onKeydown     = this._onKeydown.bind(this);
    this._onOverlayClick = this._onOverlayClick.bind(this);

    this.overlay
      .querySelector('.modal-close')
      ?.addEventListener('click', () => this.close());

    this.overlay.addEventListener('click', this._onOverlayClick);
  }

  open() {
    this.overlay.classList.add('modal-overlay--open');
    this.overlay.setAttribute('aria-hidden', 'false');
    lockScroll();
    document.addEventListener('keydown', this._onKeydown);
    // Focus first focusable element
    requestAnimationFrame(() => {
      const first = this.dialog.querySelectorAll(FOCUSABLE)[0];
      first?.focus();
    });
  }

  close() {
    this.overlay.classList.remove('modal-overlay--open');
    this.overlay.setAttribute('aria-hidden', 'true');
    unlockScroll();
    document.removeEventListener('keydown', this._onKeydown);
    this.onClose?.();
  }

  // ── Private ──────────────────────────────────────────────

  _onKeydown(e) {
    if (e.key === 'Escape') { this.close(); return; }
    if (e.key === 'Tab')    { this._trapFocus(e); }
  }

  _onOverlayClick(e) {
    if (e.target === this.overlay) this.close();
  }

  _trapFocus(e) {
    const nodes    = [...this.dialog.querySelectorAll(FOCUSABLE)];
    const first    = nodes[0];
    const last     = nodes[nodes.length - 1];
    const active   = document.activeElement;

    if (e.shiftKey) {
      if (active === first) { e.preventDefault(); last?.focus(); }
    } else {
      if (active === last)  { e.preventDefault(); first?.focus(); }
    }
  }
}
