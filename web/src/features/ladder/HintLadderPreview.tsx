import React from 'react';
import { HelpCircle, Sparkles, MapPin, Code2, CheckSquare, Lock } from 'lucide-react';

interface HintLadderPreviewProps {
  hasError: boolean;
  onRequestHint?: () => void;
}

export const HintLadderPreview: React.FC<HintLadderPreviewProps> = ({
  hasError,
  onRequestHint,
}) => {
  const ladderSteps = [
    { level: 1, title: 'Nudge', desc: 'Guiding question to re-read your logic', icon: HelpCircle },
    { level: 2, title: 'Concept', desc: 'Identifies the underlying CS concept', icon: Sparkles },
    { level: 3, title: 'Location', desc: 'Pinpoints the problematic line or block', icon: MapPin },
    { level: 4, title: 'Similar Example', desc: 'A worked parallel example on other data', icon: Code2 },
    { level: 5, title: 'Full Solution', desc: 'Complete verified fix and explanation', icon: CheckSquare },
  ];

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        backgroundColor: 'var(--color-surface)',
        padding: 'var(--space-4)',
        overflowY: 'auto',
      }}
    >
      <div style={{ marginBottom: 'var(--space-3)' }}>
        <h2 style={{ fontSize: 'var(--font-size-sm)', fontWeight: 700, letterSpacing: '-0.2px' }}>
          Five-Level Hint Ladder
        </h2>
        <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-muted)', marginTop: '2px' }}>
          Socratic scaffolding unlocks sequentially upon failing test runs.
        </p>
      </div>

      {/* Stepper list */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)', flex: 1 }}>
        {ladderSteps.map((step) => {
          const Icon = step.icon;
          return (
            <div
              key={step.level}
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: 'var(--space-3)',
                padding: 'var(--space-2) var(--space-3)',
                backgroundColor: 'var(--color-surface-raised)',
                border: '1px solid var(--color-border)',
                borderRadius: 'var(--radius-container)',
                opacity: hasError && step.level === 1 ? 1 : 0.7,
              }}
            >
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  width: '26px',
                  height: '26px',
                  borderRadius: '50%',
                  backgroundColor: 'var(--color-code-bg)',
                  color: 'var(--color-text-muted)',
                  flexShrink: 0,
                  fontSize: 'var(--font-size-xs)',
                  fontWeight: 600,
                }}
              >
                {step.level}
              </div>

              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-1)' }}>
                    <Icon size={14} style={{ color: 'var(--color-text-muted)' }} />
                    <span style={{ fontSize: 'var(--font-size-xs)', fontWeight: 600 }}>
                      Level {step.level}: {step.title}
                    </span>
                  </div>
                  <Lock size={12} style={{ color: 'var(--color-text-muted)' }} />
                </div>
                <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', marginTop: '2px' }}>
                  {step.desc}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Action / Guidance Footer */}
      <div
        style={{
          marginTop: 'var(--space-4)',
          padding: 'var(--space-3)',
          backgroundColor: hasError ? 'rgba(43, 95, 217, 0.08)' : 'var(--color-code-bg)',
          borderRadius: 'var(--radius-control)',
          border: '1px solid var(--color-border)',
        }}
      >
        <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text)' }}>
          {hasError ? (
            <span>Your code encountered an error. Click <strong>Get Hint</strong> to unlock Level 1.</span>
          ) : (
            <span>Run your code. If it fails or raises an exception, the Socratic tutor will guide you step by step.</span>
          )}
        </div>

        <button
          type="button"
          disabled={!hasError}
          onClick={onRequestHint}
          style={{
            marginTop: 'var(--space-2)',
            width: '100%',
            padding: '8px 12px',
            backgroundColor: hasError ? 'var(--color-accent)' : 'var(--color-border)',
            color: hasError ? 'var(--color-on-accent)' : 'var(--color-text-muted)',
            border: 'none',
            borderRadius: 'var(--radius-control)',
            fontSize: 'var(--font-size-xs)',
            fontWeight: 600,
            cursor: hasError ? 'pointer' : 'not-allowed',
            transition: 'background-color var(--transition-fast)',
          }}
        >
          {hasError ? 'Get Hint (Level 1: Nudge)' : 'Hints Locked (Requires Failing Run)'}
        </button>
      </div>
    </div>
  );
};
