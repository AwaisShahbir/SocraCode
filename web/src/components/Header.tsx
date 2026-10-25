import React from 'react';
import { Sun, Moon, Monitor, Code2, BookOpen } from 'lucide-react';
import type { ThemeMode } from '../types/runner';

interface HeaderProps {
  themeMode: ThemeMode;
  onThemeChange: (mode: ThemeMode) => void;
}

export const Header: React.FC<HeaderProps> = ({ themeMode, onThemeChange }) => {
  return (
    <header
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 var(--space-4)',
        height: '56px',
        backgroundColor: 'var(--color-surface)',
        borderBottom: '1px solid var(--color-border)',
        flexShrink: 0,
      }}
    >
      {/* Brand & Context */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '32px',
            height: '32px',
            borderRadius: 'var(--radius-control)',
            backgroundColor: 'var(--color-accent)',
            color: 'var(--color-on-accent)',
          }}
          aria-hidden="true"
        >
          <Code2 size={20} />
        </div>
        <div>
          <span style={{ fontWeight: 700, fontSize: 'var(--font-size-md)', letterSpacing: '-0.3px' }}>
            SocraCode
          </span>
          <span
            style={{
              marginLeft: 'var(--space-2)',
              fontSize: 'var(--font-size-xs)',
              color: 'var(--color-text-muted)',
              padding: '2px 6px',
              backgroundColor: 'var(--color-code-bg)',
              borderRadius: 'var(--radius-control)',
            }}
          >
            Step 1 · Prototype
          </span>
        </div>

        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 'var(--space-1)',
            marginLeft: 'var(--space-4)',
            padding: '2px var(--space-2)',
            fontSize: 'var(--font-size-xs)',
            color: 'var(--color-accent)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-control)',
          }}
        >
          <BookOpen size={14} />
          <span>Free Practice</span>
        </div>
      </div>

      {/* Language & Theme Controls */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
        {/* Language selector */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <label htmlFor="language-select" style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-muted)' }}>
            Language:
          </label>
          <select
            id="language-select"
            value="python"
            disabled
            style={{
              backgroundColor: 'var(--color-surface-raised)',
              color: 'var(--color-text)',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-control)',
              padding: '4px var(--space-2)',
              fontSize: 'var(--font-size-sm)',
            }}
          >
            <option value="python">Python 3.13</option>
          </select>
        </div>

        {/* Theme Segmented Switcher */}
        <div
          role="group"
          aria-label="Theme selection"
          style={{
            display: 'flex',
            alignItems: 'center',
            backgroundColor: 'var(--color-code-bg)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-control)',
            padding: '2px',
          }}
        >
          <button
            type="button"
            onClick={() => onThemeChange('light')}
            aria-pressed={themeMode === 'light'}
            title="Light Theme"
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: '28px',
              height: '28px',
              border: 'none',
              borderRadius: 'var(--radius-control)',
              backgroundColor: themeMode === 'light' ? 'var(--color-surface)' : 'transparent',
              color: themeMode === 'light' ? 'var(--color-accent)' : 'var(--color-text-muted)',
              transition: 'all var(--transition-fast)',
            }}
          >
            <Sun size={15} />
          </button>
          <button
            type="button"
            onClick={() => onThemeChange('dark')}
            aria-pressed={themeMode === 'dark'}
            title="Dark Theme"
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: '28px',
              height: '28px',
              border: 'none',
              borderRadius: 'var(--radius-control)',
              backgroundColor: themeMode === 'dark' ? 'var(--color-surface)' : 'transparent',
              color: themeMode === 'dark' ? 'var(--color-accent)' : 'var(--color-text-muted)',
              transition: 'all var(--transition-fast)',
            }}
          >
            <Moon size={15} />
          </button>
          <button
            type="button"
            onClick={() => onThemeChange('system')}
            aria-pressed={themeMode === 'system'}
            title="System Preference"
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: '28px',
              height: '28px',
              border: 'none',
              borderRadius: 'var(--radius-control)',
              backgroundColor: themeMode === 'system' ? 'var(--color-surface)' : 'transparent',
              color: themeMode === 'system' ? 'var(--color-accent)' : 'var(--color-text-muted)',
              transition: 'all var(--transition-fast)',
            }}
          >
            <Monitor size={15} />
          </button>
        </div>
      </div>
    </header>
  );
};
