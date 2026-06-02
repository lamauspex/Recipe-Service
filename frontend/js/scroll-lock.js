// ── SCROLL LOCK ────────────────────────────────────────────
// Centralised body scroll locking — avoids duplicating
// document.body.style.overflow = 'hidden' across modules.

let lockCount = 0;

export function lockScroll() {
  lockCount++;
  document.body.classList.add('scroll-locked');
}

export function unlockScroll() {
  lockCount = Math.max(0, lockCount - 1);
  if (lockCount === 0) document.body.classList.remove('scroll-locked');
}
