import React, { useState } from 'react';
import { Terminal, AlertCircle, CheckCircle2, Clock, Trash2, Loader2 } from 'lucide-react';
import type { RunResult } from '../../types/runner';

interface OutputConsoleProps {
  result: RunResult | null;
  isRunning: boolean;
  onClear: () => void;
}

export const OutputConsole: React.FC<OutputConsoleProps> = ({
  result,
  isRunning,
  onClear,
}) => {
  const [activeTab, setActiveTab] = useState<'output' | 'stderr'>('output');

  // Automatically switch tab if there are errors and no stdout
  React.useEffect(() => {
    if (result) {
      if (result.stderr && !result.stdout) {
        setActiveTab('stderr');
      } else {
        setActiveTab('output');
      }
    }
  }, [result]);

  const hasStderr = Boolean(result && result.stderr);

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        backgroundColor: 'var(--color-surface)',
        borderBottom: '1px solid var(--color-border)',
        overflow: 'hidden',
      }}
    >
      {/* Console Tab Header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 var(--space-3)',
          backgroundColor: 'var(--color-surface-raised)',
          borderBottom: '1px solid var(--color-border)',
          height: '40px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-1)' }}>
          <button
            type="button"
            onClick={() => setActiveTab('output')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 'var(--space-1)',
              padding: '6px var(--space-3)',
              border: 'none',
              background: 'transparent',
              fontSize: 'var(--font-size-xs)',
              fontWeight: 600,
              color: activeTab === 'output' ? 'var(--color-accent)' : 'var(--color-text-muted)',
              borderBottom: activeTab === 'output' ? '2px solid var(--color-accent)' : '2px solid transparent',
            }}
          >
            <Terminal size={14} />
            <span>Standard Output</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('stderr')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 'var(--space-1)',
              padding: '6px var(--space-3)',
              border: 'none',
              background: 'transparent',
              fontSize: 'var(--font-size-xs)',
              fontWeight: 600,
              color: activeTab === 'stderr' ? 'var(--color-danger)' : 'var(--color-text-muted)',
              borderBottom: activeTab === 'stderr' ? '2px solid var(--color-danger)' : '2px solid transparent',
            }}
          >
            <AlertCircle size={14} />
            <span>Errors & Diagnostics</span>
            {hasStderr && (
              <span
                style={{
                  display: 'inline-block',
                  width: '6px',
                  height: '6px',
                  borderRadius: '50%',
                  backgroundColor: 'var(--color-danger)',
                }}
              />
            )}
          </button>
        </div>

        {/* Status Pill & Action */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
          {isRunning && (
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 'var(--space-1)',
                fontSize: 'var(--font-size-xs)',
                color: 'var(--color-accent)',
              }}
            >
              <Loader2 size={13} className="spin-animation" style={{ animation: 'spin 1s linear infinite' }} />
              <span>Running code...</span>
            </span>
          )}

          {!isRunning && result && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
              {result.exit_code === 0 && !result.timed_out ? (
                <span
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '4px',
                    fontSize: 'var(--font-size-xs)',
                    color: 'var(--color-success)',
                    backgroundColor: 'rgba(31, 122, 77, 0.1)',
                    padding: '2px 8px',
                    borderRadius: 'var(--radius-control)',
                  }}
                >
                  <CheckCircle2 size={13} />
                  <span>Exit 0</span>
                </span>
              ) : (
                <span
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '4px',
                    fontSize: 'var(--font-size-xs)',
                    color: 'var(--color-danger)',
                    backgroundColor: 'rgba(179, 38, 30, 0.1)',
                    padding: '2px 8px',
                    borderRadius: 'var(--radius-control)',
                  }}
                >
                  <AlertCircle size={13} />
                  <span>{result.timed_out ? 'Timed Out' : `Exit ${result.exit_code}`}</span>
                </span>
              )}

              <span
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '2px',
                  fontSize: 'var(--font-size-xs)',
                  color: 'var(--color-text-muted)',
                }}
              >
                <Clock size={12} />
                <span>{result.duration_ms} ms</span>
              </span>
            </div>
          )}

          {result && (
            <button
              type="button"
              onClick={onClear}
              title="Clear Console Output"
              style={{
                background: 'transparent',
                border: 'none',
                color: 'var(--color-text-muted)',
                padding: '4px',
                borderRadius: 'var(--radius-control)',
                display: 'flex',
                alignItems: 'center',
              }}
            >
              <Trash2 size={14} />
            </button>
          )}
        </div>
      </div>

      {/* Terminal Content Body */}
      <div
        tabIndex={0}
        aria-label="Console output area"
        style={{
          flex: 1,
          padding: 'var(--space-3) var(--space-4)',
          backgroundColor: 'var(--color-code-bg)',
          color: 'var(--color-text)',
          fontFamily: 'var(--font-mono)',
          fontSize: 'var(--font-size-sm)',
          lineHeight: '1.5',
          overflowY: 'auto',
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-all',
        }}
      >
        {activeTab === 'output' ? (
          result?.stdout ? (
            result.stdout
          ) : (
            <span style={{ color: 'var(--color-text-muted)', fontStyle: 'italic' }}>
              {result ? '(No standard output generated)' : 'Click [Run] or press Ctrl+Enter to execute program.'}
            </span>
          )
        ) : (
          result?.stderr ? (
            <span style={{ color: 'var(--color-danger)' }}>{result.stderr}</span>
          ) : (
            <span style={{ color: 'var(--color-text-muted)', fontStyle: 'italic' }}>
              {result ? '(No errors or exceptions encountered)' : 'Error tracebacks and compiler diagnostics will appear here.'}
            </span>
          )
        )}
      </div>
    </div>
  );
};
