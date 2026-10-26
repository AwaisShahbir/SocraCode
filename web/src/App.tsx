import React, { useState, useCallback, useEffect } from 'react';
import { Play, RotateCcw, AlertTriangle, CheckCircle2, Send } from 'lucide-react';
import { useTheme } from './lib/theme';
import { Header } from './components/Header';
import { CodeEditor } from './features/editor/CodeEditor';
import { OutputConsole } from './features/output/OutputConsole';
import { HintLadderPanel } from './features/ladder/HintLadderPanel';
import { executeRun, createAttempt, requestNextHint, resolveAttempt, sendHintFeedback } from './lib/api';
import type { Attempt, RunResult, UnlockedHint } from './types/runner';

const DEFAULT_PYTHON_CODE = `# Welcome to SocraCode - Socratic AI Debugging Tutor
# Below is a buggy factorial implementation: line 7 has a missing colon!
# Run the code, observe the error, and climb the Hint Ladder.

def calculate_factorial(n: int) -> int:
    """Calculate factorial of n iteratively."""
    if n < 0
        raise ValueError("Factorial is not defined for negative numbers.")
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result

# Test cases
numbers = [1, 3, 5]
print("--- Calculating Factorials ---")
for num in numbers:
    fact = calculate_factorial(num)
    print(f"{num}! = {fact}")
`;

export const App: React.FC = () => {
  const { mode, setMode, resolvedTheme } = useTheme();
  const [code, setCode] = useState<string>(DEFAULT_PYTHON_CODE);
  const [runResult, setRunResult] = useState<RunResult | null>(null);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [statusMessage, setStatusMessage] = useState<string>('Ready to run');

  // Attempt & Hint State
  const [activeAttempt, setActiveAttempt] = useState<Attempt | null>(null);
  const [unlockedHints, setUnlockedHints] = useState<UnlockedHint[]>([]);
  const [isLoadingHint, setIsLoadingHint] = useState<boolean>(false);
  const [highlightedLine, setHighlightedLine] = useState<number | null>(null);

  // Reflection Dialog State
  const [showReflectionBox, setShowReflectionBox] = useState<boolean>(false);
  const [reflectionText, setReflectionText] = useState<string>('');
  const [isResolved, setIsResolved] = useState<boolean>(false);

  const handleRun = useCallback(async () => {
    if (isRunning) return;

    setIsRunning(true);
    setStatusMessage('Running your code in sandbox...');
    setHighlightedLine(null);

    try {
      const result = await executeRun({
        language: 'python',
        code,
      });
      setRunResult(result);

      const hasError = result.exit_code !== 0 || result.timed_out || Boolean(result.stderr);

      if (hasError) {
        setStatusMessage('Error encountered. Initializing diagnostic attempt...');
        const attempt = await createAttempt({
          language: 'python',
          source: 'web',
          code,
          error_text: result.stderr || 'Execution failed',
          timed_out: result.timed_out,
        });

        if (attempt) {
          setActiveAttempt(attempt);
          setUnlockedHints([]);
          setStatusMessage('Diagnostic complete. Hint Ladder unlocked (Click "Get Hint")');
        } else {
          setStatusMessage('Run completed with error.');
        }
      } else {
        // Success!
        setStatusMessage('Run completed successfully! (Exit 0)');
        if (activeAttempt && !isResolved) {
          setShowReflectionBox(true);
        }
      }
    } catch {
      setStatusMessage('Failed to execute code');
    } finally {
      setIsRunning(false);
    }
  }, [code, isRunning, activeAttempt, isResolved]);

  const handleGetNextHint = useCallback(async () => {
    if (!activeAttempt || isLoadingHint) return;

    setIsLoadingHint(true);
    try {
      const hint = await requestNextHint(activeAttempt.id);
      if (hint) {
        setUnlockedHints((prev) => [...prev, hint]);
        setActiveAttempt((prev) => (prev ? { ...prev, current_level: hint.level } : null));

        // If Level 3 Location, extract line number
        if (hint.level === 3) {
          const match = hint.text.match(/line\s+(\d+)/i);
          if (match) {
            setHighlightedLine(parseInt(match[1], 10));
          }
        }
      }
    } catch {
      alert('Unable to fetch next hint from server.');
    } finally {
      setIsLoadingHint(false);
    }
  }, [activeAttempt, isLoadingHint]);

  const handleFeedback = async (hintId: string, helpful: boolean) => {
    await sendHintFeedback(hintId, helpful);
  };

  const handleResolveSubmit = async () => {
    if (activeAttempt) {
      await resolveAttempt(activeAttempt.id, reflectionText);
    }
    setIsResolved(true);
    setShowReflectionBox(false);
    setActiveAttempt(null);
    setUnlockedHints([]);
    setStatusMessage('Bug fixed! Attempt logged to your learning history.');
  };

  const handleReset = () => {
    setCode(DEFAULT_PYTHON_CODE);
    setRunResult(null);
    setActiveAttempt(null);
    setUnlockedHints([]);
    setHighlightedLine(null);
    setShowReflectionBox(false);
    setStatusMessage('Code reset to sample');
  };

  // Keyboard shortcut Ctrl/Cmd + Shift + H to request next hint
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && (e.key === 'H' || e.key === 'h')) {
        e.preventDefault();
        handleGetNextHint();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleGetNextHint]);

  const hasFailingRun = Boolean(
    runResult && (runResult.exit_code !== 0 || runResult.timed_out || Boolean(runResult.stderr))
  );

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', width: '100vw', overflow: 'hidden' }}>
      {/* Top Navigation */}
      <Header themeMode={mode} onThemeChange={setMode} />

      {/* Main Workspace (60/40 Split) */}
      <main
        style={{
          display: 'grid',
          gridTemplateColumns: 'minmax(0, 1.4fr) minmax(380px, 1fr)',
          flex: 1,
          minHeight: 0,
          backgroundColor: 'var(--color-bg)',
        }}
      >
        {/* Left Column: Code Editor & Action Bar */}
        <section
          aria-label="Code Editor Area"
          style={{
            display: 'flex',
            flexDirection: 'column',
            height: '100%',
            minHeight: 0,
            overflow: 'hidden',
          }}
        >
          {/* Editor Container */}
          <div style={{ flex: 1, minHeight: 0 }}>
            <CodeEditor
              code={code}
              onChange={setCode}
              resolvedTheme={resolvedTheme}
              onRunShortcut={handleRun}
              isRunning={isRunning}
              highlightedLine={highlightedLine}
            />
          </div>

          {/* Action Bar */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: 'var(--space-3) var(--space-4)',
              backgroundColor: 'var(--color-surface)',
              borderTop: '1px solid var(--color-border)',
              borderRight: '1px solid var(--color-border)',
              height: '56px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
              <button
                id="run-code-button"
                type="button"
                onClick={handleRun}
                disabled={isRunning}
                title="Execute program (Ctrl+Enter)"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 'var(--space-2)',
                  minHeight: '44px',
                  padding: '0 var(--space-4)',
                  backgroundColor: 'var(--color-accent)',
                  color: 'var(--color-on-accent)',
                  border: 'none',
                  borderRadius: 'var(--radius-control)',
                  fontWeight: 600,
                  fontSize: 'var(--font-size-sm)',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                  opacity: isRunning ? 0.7 : 1,
                  cursor: isRunning ? 'wait' : 'pointer',
                  transition: 'opacity var(--transition-fast)',
                }}
              >
                <Play size={16} fill="currentColor" />
                <span>{isRunning ? 'Running...' : 'Run Code'}</span>
              </button>

              <button
                type="button"
                onClick={handleReset}
                title="Reset code to default"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  minHeight: '44px',
                  minWidth: '44px',
                  backgroundColor: 'var(--color-surface-raised)',
                  color: 'var(--color-text-muted)',
                  border: '1px solid var(--color-border)',
                  borderRadius: 'var(--radius-control)',
                  cursor: 'pointer',
                }}
              >
                <RotateCcw size={16} />
              </button>
            </div>

            {/* Status Live Region */}
            <div
              aria-live="polite"
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 'var(--space-2)',
                fontSize: 'var(--font-size-xs)',
                color: hasFailingRun ? 'var(--color-danger)' : 'var(--color-text-muted)',
              }}
            >
              {hasFailingRun ? <AlertTriangle size={14} /> : <CheckCircle2 size={14} style={{ color: 'var(--color-success)' }} />}
              <span>{statusMessage}</span>
            </div>
          </div>
        </section>

        {/* Right Column: Split between Output and Hint Ladder */}
        <section
          aria-label="Output and Guidance Panel"
          style={{
            display: 'grid',
            gridTemplateRows: '1fr 1.2fr',
            height: '100%',
            minHeight: 0,
            overflow: 'hidden',
          }}
        >
          {/* Top: Output Console */}
          <div style={{ minHeight: 0, height: '100%' }}>
            <OutputConsole
              result={runResult}
              isRunning={isRunning}
              onClear={() => setRunResult(null)}
            />
          </div>

          {/* Bottom: Five-Level Hint Ladder */}
          <div style={{ minHeight: 0, height: '100%' }}>
            <HintLadderPanel
              unlockedHints={unlockedHints}
              currentLevel={activeAttempt ? activeAttempt.current_level : 0}
              maxLevelAllowed={3}
              hasActiveAttempt={Boolean(activeAttempt)}
              isLoadingHint={isLoadingHint}
              onGetNextHint={handleGetNextHint}
              onSelectLine={(line) => setHighlightedLine(line)}
              onFeedback={handleFeedback}
            />
          </div>
        </section>
      </main>

      {/* Reflection Modal on Fix */}
      {showReflectionBox && (
        <div
          role="dialog"
          aria-labelledby="reflection-title"
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 100,
            padding: 'var(--space-4)',
          }}
        >
          <div
            style={{
              backgroundColor: 'var(--color-surface)',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-container)',
              padding: 'var(--space-6)',
              maxWidth: '480px',
              width: '100%',
              boxShadow: 'var(--shadow-floating)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', color: 'var(--color-success)' }}>
              <CheckCircle2 size={24} />
              <h3 id="reflection-title" style={{ fontSize: 'var(--font-size-md)', fontWeight: 700 }}>
                Bug Fixed Successfully!
              </h3>
            </div>

            <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-muted)', marginTop: 'var(--space-2)' }}>
              Reflecting on what went wrong solidifies debugging memory. What was the bug and what helped you fix it?
            </p>

            <textarea
              value={reflectionText}
              onChange={(e) => setReflectionText(e.target.value)}
              placeholder="e.g. I missed the colon at the end of the if statement on line 7..."
              rows={3}
              style={{
                width: '100%',
                marginTop: 'var(--space-3)',
                padding: 'var(--space-2)',
                backgroundColor: 'var(--color-code-bg)',
                color: 'var(--color-text)',
                border: '1px solid var(--color-border)',
                borderRadius: 'var(--radius-control)',
                fontFamily: 'inherit',
                fontSize: 'var(--font-size-sm)',
                resize: 'none',
              }}
            />

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--space-2)', marginTop: 'var(--space-4)' }}>
              <button
                type="button"
                onClick={() => setShowReflectionBox(false)}
                style={{
                  padding: '8px 14px',
                  backgroundColor: 'transparent',
                  border: '1px solid var(--color-border)',
                  borderRadius: 'var(--radius-control)',
                  color: 'var(--color-text-muted)',
                  fontSize: 'var(--font-size-xs)',
                  fontWeight: 600,
                  cursor: 'pointer',
                }}
              >
                Skip
              </button>

              <button
                type="button"
                onClick={handleResolveSubmit}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 'var(--space-1)',
                  padding: '8px 16px',
                  backgroundColor: 'var(--color-accent)',
                  color: 'var(--color-on-accent)',
                  border: 'none',
                  borderRadius: 'var(--radius-control)',
                  fontSize: 'var(--font-size-xs)',
                  fontWeight: 600,
                  cursor: 'pointer',
                }}
              >
                <Send size={13} />
                <span>Save Reflection</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
