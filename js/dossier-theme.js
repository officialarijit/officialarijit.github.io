/**
 * Dossier dark mode — syncs with localStorage key "darkMode".
 */
(function () {
  const STORAGE_KEY = 'darkMode';

  function getPreference() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved === 'true') return true;
      if (saved === 'false') return false;
    } catch (e) {}
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  }

  function applyTheme(enabled) {
    document.documentElement.classList.toggle('dark-mode', enabled);
    document.body.classList.toggle('dark-mode', enabled);

    try {
      localStorage.setItem(STORAGE_KEY, enabled ? 'true' : 'false');
    } catch (e) {}

    document.querySelectorAll('.dossier-theme-toggle').forEach((button) => {
      const icon = button.querySelector('i');
      const label = button.querySelector('.dossier-theme-toggle__label');
      if (icon) {
        icon.classList.toggle('fa-sun', enabled);
        icon.classList.toggle('fa-moon', !enabled);
      }
      if (label) {
        label.textContent = enabled ? 'Light mode' : 'Dark mode';
      }
      button.setAttribute(
        'aria-label',
        enabled ? 'Switch to light mode' : 'Switch to dark mode'
      );
      button.setAttribute('title', enabled ? 'Light mode' : 'Dark mode');
    });
  }

  window.setDarkMode = applyTheme;

  document.addEventListener('DOMContentLoaded', () => {
    const enabled =
      document.documentElement.classList.contains('dark-mode') ||
      document.body.classList.contains('dark-mode') ||
      getPreference();

    applyTheme(enabled);

    document.querySelectorAll('.dossier-theme-toggle').forEach((button) => {
      button.addEventListener('click', () => {
        applyTheme(!document.documentElement.classList.contains('dark-mode'));
      });
    });

    if (window.matchMedia) {
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (event) => {
        try {
          if (localStorage.getItem(STORAGE_KEY) !== null) return;
        } catch (e) {}
        applyTheme(event.matches);
      });
    }
  });
})();
