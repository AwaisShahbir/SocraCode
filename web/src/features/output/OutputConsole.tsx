import React, { useState } from 'react';
import { Terminal, AlertCircle, CheckCircle2, Zap, Trash2, Loader2, Copy, Check } from 'lucide-react';
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
  const [copied, setCopied] = useState<boolean>(false);

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

  const handleCopy = () => {
    const textToCopy = activeTab === 'output' ? result?.stdout : result?.stderr;
    if (textToCopy) {
      navigator.clipboard.writeText(textToCopy);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    }
  };

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
          height: '42px',
          flexShrink: 0,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-1)' }}>
          <button
            type="button"
            onClick={() => setActiveTab('output')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 12px',
              border: 'none',
              borderRadius: 'var(--radius-control)',
              background: activeTab === 'output' ? 'var(--color-surface)' : 'transparent',
              fontSize: '12px',
              fontWeight: 700,
              color: activeTab === 'output' ? 'var(--color-accent)' : 'var(--color-text-muted)',
              boxShadow: activeTab === 'output' ? 'var(--shadow-sm)' : 'none',
            }}
          >
            <Terminal size={14} />
            <span>Stdout</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('stderr')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 12px',
              border: 'none',
              borderRadius: 'var(--radius-control)',
              background: activeTab === 'stderr' ? 'var(--color-surface)' : 'transparent',
              fontSize: '12px',
              fontWeight: 700,
              color: activeTab === 'stderr' ? 'var(--color-danger)' : 'var(--color-text-muted)',
              boxShadow: activeTab === 'stderr' ? 'var(--shadow-sm)' : 'none',
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
                  boxShadow: '0 0 6px var(--color-danger)',
                }}
              />
            )}
          </button>
        </div>

        {/* Status Pill & Action */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          {isRunning && (
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                fontSize: '11px',
                fontWeight: 600,
                color: 'var(--color-accent)',
                padding: '3px 8px',
                background: 'rgba(99, 102, 241, 0.1)',
                borderRadius: 'var(--radius-pill)',
              }}
            >
              <Loader2 size={12} style={{ animation: 'spin 1s linear infinite' }} />
              <span>Executing in sandbox...</span>
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
                    fontSize: '11px',
                    fontWeight: 700,
                    color: 'var(--color-success)',
                    backgroundColor: 'rgba(16, 185, 129, 0.12)',
                    border: '1px solid rgba(16, 185, 129, 0.25)',
                    padding: '2px 8px',
                    borderRadius: 'var(--radius-pill)',
                  }}
                >
                  <CheckCircle2 size={12} />
                  <span>Exit 0</span>
                </span>
              ) : (
                <span
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '4px',
                    fontSize: '11px',
                    fontWeight: 700,
                    color: 'var(--color-danger)',
                    backgroundColor: 'rgba(239, 68, 68, 0.12)',
                    border: '1px solid rgba(239, 68, 68, 0.25)',
                    padding: '2px 8px',
                    borderRadius: 'var(--radius-pill)',
                  }}
                >
                  <AlertCircle size={12} />
                  <span>{result.timed_out ? 'Timed Out' : `Exit ${result.exit_code}`}</span>
                </span>
              )}

              <span
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '3px',
                  fontSize: '11px',
                  fontWeight: 600,
                  color: 'var(--color-text-muted)',
                  padding: '2px 6px',
                  background: 'var(--color-surface)',
                  borderRadius: 'var(--radius-control)',
                  border: '1px solid var(--color-border)',
                }}
              >
                <Zap size={11} color="var(--color-warning)" />
                <span>{result.duration_ms}ms</span>
              </span>

              <button
                type="button"
                onClick={handleCopy}
                title="Copy Terminal Output"
                style={{
                  background: 'transparent',
                  border: '1px solid var(--color-border)',
                  color: copied ? 'var(--color-success)' : 'var(--color-text-muted)',
                  padding: '4px 6px',
                  borderRadius: 'var(--radius-control)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  fontSize: '11px',
                }}
              >
                {copied ? <Check size={12} /> : <Copy size={12} />}
              </button>

              <button
                type="button"
                onClick={onClear}
                title="Clear Console Output"
                style={{
                  background: 'transparent',
                  border: '1px solid var(--color-border)',
                  color: 'var(--color-text-muted)',
                  padding: '4px 6px',
                  borderRadius: 'var(--radius-control)',
                  display: 'flex',
                  alignItems: 'center',
                }}
              >
                <Trash2 size={12} />
              </button>
            </div>
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
          fontSize: '13px',
          lineHeight: '1.6',
          overflowY: 'auto',
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-all',
        }}
      >
        {activeTab === 'output' ? (
          result?.stdout ? (
            <div style={{ color: 'var(--color-text)' }}>{result.stdout}</div>
          ) : (
            <div style={{ color: 'var(--color-text-muted)', fontStyle: 'italic', padding: '12px 0' }}>
              {result ? '(No stdout produced)' : 'Hit [Run Code] or press Ctrl+Enter to execute program in sandbox.'}
            </div>
          )
        ) : (
          result?.stderr ? (
            <div
              style={{
                color: 'var(--color-danger)',
                background: 'rgba(239, 68, 68, 0.05)',
                padding: '10px 12px',
                borderRadius: 'var(--radius-control)',
                border: '1px solid rgba(239, 68, 68, 0.15)',
              }}
            >
              {result.stderr}
            </div>
          ) : (
            <div style={{ color: 'var(--color-text-muted)', fontStyle: 'italic', padding: '12px 0' }}>
              {result ? 'No errors encountered! Execution was clean.' : 'Runtime errors and compiler diagnostics will appear here.'}
            </div>
          )
        )}
      </div>
    </div>
  );
};
