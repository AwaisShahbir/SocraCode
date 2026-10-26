import React from 'react';
import { Sun, Moon, Monitor, Sparkles, Terminal, Flame, ShieldCheck } from 'lucide-react';
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
        padding: '0 var(--space-5)',
        height: '60px',
        backgroundColor: 'var(--color-surface-glass)',
        backdropFilter: 'blur(16px)',
        WebkitBackdropFilter: 'blur(16px)',
        borderBottom: '1px solid var(--color-border)',
        position: 'relative',
        zIndex: 20,
        flexShrink: 0,
      }}
    >
      {/* Brand & Context Badges */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
        {/* Animated Gradient Logo Icon */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '36px',
            height: '36px',
            borderRadius: '10px',
            background: 'var(--color-accent-gradient)',
            color: '#FFFFFF',
            boxShadow: 'var(--shadow-accent-glow)',
          }}
          aria-hidden="true"
        >
          <Sparkles size={19} />
        </div>

        {/* Title & Tag */}
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 'var(--space-2)' }}>
          <span
            style={{
              fontWeight: 800,
              fontSize: '18px',
              letterSpacing: '-0.5px',
              background: 'linear-gradient(135deg, var(--color-text) 60%, var(--color-accent) 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            SocraCode
          </span>
          <span
            style={{
              fontSize: '11px',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.6px',
              color: 'var(--color-accent)',
              padding: '2px 8px',
              background: 'rgba(99, 102, 241, 0.12)',
              border: '1px solid rgba(99, 102, 241, 0.25)',
              borderRadius: 'var(--radius-pill)',
            }}
          >
            AI Socratic Tutor
          </span>
        </div>

        {/* Status Pill: Sandbox Isolation */}
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            marginLeft: 'var(--space-2)',
            padding: '3px 10px',
            fontSize: '12px',
            fontWeight: 600,
            color: 'var(--color-success)',
            background: 'rgba(16, 185, 129, 0.08)',
            border: '1px solid rgba(16, 185, 129, 0.2)',
            borderRadius: 'var(--radius-pill)',
          }}
        >
          <span className="pulsing-live-dot" aria-hidden="true" />
          <span>Sandbox Active</span>
        </div>

        {/* Gamified Streak Pill */}
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '5px',
            padding: '3px 10px',
            fontSize: '12px',
            fontWeight: 600,
            color: 'var(--color-warning)',
            background: 'rgba(245, 158, 11, 0.08)',
            border: '1px solid rgba(245, 158, 11, 0.2)',
            borderRadius: 'var(--radius-pill)',
          }}
        >
          <Flame size={13} fill="currentColor" />
          <span>Free Practice Mode</span>
        </div>
      </div>

      {/* Controls & Tools */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
        {/* Language Badge */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '4px 10px',
            background: 'var(--color-surface-raised)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-control)',
            fontSize: '13px',
            fontWeight: 600,
            color: 'var(--color-text)',
          }}
        >
          <Terminal size={14} color="var(--color-accent)" />
          <span>Python 3.13</span>
        </div>

        {/* Security / Privacy Badge */}
        <div
          title="Zero pre-trained leaks; local sandbox execution"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            padding: '4px 8px',
            fontSize: '11px',
            color: 'var(--color-text-muted)',
            cursor: 'default',
          }}
        >
          <ShieldCheck size={14} color="var(--color-success)" />
          <span>AST Verified</span>
        </div>

        {/* Theme Segmented Switcher */}
        <div
          role="group"
          aria-label="Theme selection"
          style={{
            display: 'flex',
            alignItems: 'center',
            background: 'var(--color-surface-raised)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-pill)',
            padding: '3px',
            gap: '2px',
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
              borderRadius: 'var(--radius-pill)',
              backgroundColor: themeMode === 'light' ? 'var(--color-surface)' : 'transparent',
              color: themeMode === 'light' ? 'var(--color-accent)' : 'var(--color-text-muted)',
              boxShadow: themeMode === 'light' ? 'var(--shadow-sm)' : 'none',
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
              borderRadius: 'var(--radius-pill)',
              backgroundColor: themeMode === 'dark' ? 'var(--color-surface)' : 'transparent',
              color: themeMode === 'dark' ? 'var(--color-accent)' : 'var(--color-text-muted)',
              boxShadow: themeMode === 'dark' ? 'var(--shadow-sm)' : 'none',
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
              borderRadius: 'var(--radius-pill)',
              backgroundColor: themeMode === 'system' ? 'var(--color-surface)' : 'transparent',
              color: themeMode === 'system' ? 'var(--color-accent)' : 'var(--color-text-muted)',
              boxShadow: themeMode === 'system' ? 'var(--shadow-sm)' : 'none',
            }}
          >
            <Monitor size={15} />
          </button>
        </div>
      </div>
    </header>
  );
};
