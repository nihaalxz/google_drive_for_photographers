import { writable } from 'svelte/store';

export type Theme = 'light' | 'dark' | 'system';

function createThemeStore() {
  const isBrowser = typeof window !== 'undefined';
  const saved = isBrowser ? (localStorage.getItem('lensvault_theme') as Theme | null) : null;
  const initial: Theme = saved || 'system';

  const { subscribe, set } = writable<Theme>(initial);

  function applyTheme(t: Theme) {
    if (!isBrowser) return;

    let isDark = false;
    if (t === 'system') {
      isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    } else {
      isDark = t === 'dark';
    }

    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }

    localStorage.setItem('lensvault_theme', t);
  }

  if (isBrowser) {
    applyTheme(initial);

    // Watch for system color scheme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      const current = localStorage.getItem('lensvault_theme') as Theme;
      if (current === 'system' || !current) {
        if (e.matches) {
          document.documentElement.classList.add('dark');
        } else {
          document.documentElement.classList.remove('dark');
        }
      }
    });
  }

  return {
    subscribe,
    set: (t: Theme) => {
      set(t);
      applyTheme(t);
    },
    toggle: () => {
      if (!isBrowser) return;
      const isCurrentlyDark = document.documentElement.classList.contains('dark');
      const next: Theme = isCurrentlyDark ? 'light' : 'dark';
      set(next);
      applyTheme(next);
    }
  };
}

export const theme = createThemeStore();
