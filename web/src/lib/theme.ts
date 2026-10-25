import { useState, useEffect } from 'react';
import type { ThemeMode } from '../types/runner';

export function useTheme() {
  const [mode, setMode] = useState<ThemeMode>(() => {
    const saved = localStorage.getItem('socracode-theme') as ThemeMode | null;
    if (saved === 'light' || saved === 'dark' || saved === 'system') {
      return saved;
    }
    return 'system';
  });

  const [resolvedTheme, setResolvedTheme] = useState<'light' | 'dark'>(() => {
    if (mode === 'system') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    return mode;
  });

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    const updateResolvedTheme = () => {
      let active: 'light' | 'dark';
      if (mode === 'system') {
        active = mediaQuery.matches ? 'dark' : 'light';
      } else {
        active = mode;
      }
      setResolvedTheme(active);
      document.documentElement.setAttribute('data-theme', active);
    };

    updateResolvedTheme();
    localStorage.setItem('socracode-theme', mode);

    const handler = () => {
      if (mode === 'system') {
        updateResolvedTheme();
      }
    };

    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, [mode]);

  return { mode, setMode, resolvedTheme };
}
