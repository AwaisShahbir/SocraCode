import React, { useState, useCallback } from 'react';
import { Play, RotateCcw, AlertTriangle } from 'lucide-react';
import { useTheme } from './lib/theme';
import { Header } from './components/Header';
import { CodeEditor } from './features/editor/CodeEditor';
import { OutputConsole } from './features/output/OutputConsole';
import { HintLadderPreview } from './features/ladder/HintLadderPreview';
import { executeRun } from './lib/api';
import type { RunResult } from './types/runner';

const DEFAULT_PYTHON_CODE = `# Welcome to SocraCode - Step 1
# Try running this Python program or intentionally cause a bug!

def calculate_factorial(n: int) -> int:
    """Calculate factorial of n iteratively."""
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers.")
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result

# Test cases
numbers = [1, 3, 5, 7]
print("--- Calculating Factorials ---")
for num in numbers:
    fact = calculate_factorial(num)
    print(f"{num}! = {fact}")

print("\\nSuccess! Try changing code to introduce a bug and click Run.")
`;

export const App: React.FC = () => {
  const { mode, setMode, resolvedTheme } = useTheme();
  const [code, setCode] = useState<string>(DEFAULT_PYTHON_CODE);
  const [runResult, setRunResult] = useState<RunResult | null>(null);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [statusMessage, setStatusMessage] = useState<string>('Ready to run');

  const handleRun = useCallback(async () => {
    if (isRunning) return;

    setIsRunning(true);
    setStatusMessage('Running your code on sandboxed runner...');

    try {
      const result = await executeRun({
        language: 'python',
        code,
      });
      setRunResult(result);
      if (result.timed_out) {
        setStatusMessage('Execution timed out after limit');
      } else if (result.exit_code === 0) {
        setStatusMessage('Run completed successfully');
      } else {
        setStatusMessage(`Run completed with errors (Exit code ${result.exit_code})`);
      }
    } catch {
      setStatusMessage('Failed to execute code');
    } finally {
      setIsRunning(false);
    }
  }, [code, isRunning]);

  const handleReset = () => {
    setCode(DEFAULT_PYTHON_CODE);
    setRunResult(null);
    setStatusMessage('Code reset to default');
  };

  const hasFailingRun = Boolean(
    runResult && (runResult.exit_code !== 0 || runResult.timed_out || Boolean(runResult.stderr))
  );

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', width: '100vw', overflow: 'hidden' }}>
      {/* Top Navigation / Brand */}
      <Header themeMode={mode} onThemeChange={setMode} />

      {/* Main Workspace (60/40 Split) */}
      <main
        style={{
          display: 'grid',
          gridTemplateColumns: 'minmax(0, 1.4fr) minmax(360px, 1fr)',
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
              {hasFailingRun && <AlertTriangle size={14} />}
              <span>{statusMessage}</span>
            </div>
          </div>
        </section>

        {/* Right Column: Split between Output and Hint Ladder */}
        <section
          aria-label="Output and Guidance Panel"
          style={{
            display: 'grid',
            gridTemplateRows: '1fr 1fr',
            height: '100%',
            minHeight: 0,
            overflow: 'hidden',
          }}
        >
          {/* Top Half: Output Console */}
          <div style={{ minHeight: 0, height: '100%' }}>
            <OutputConsole
              result={runResult}
              isRunning={isRunning}
              onClear={() => setRunResult(null)}
            />
          </div>

          {/* Bottom Half: Five-Level Hint Ladder Preview */}
          <div style={{ minHeight: 0, height: '100%' }}>
            <HintLadderPreview
              hasError={hasFailingRun}
              onRequestHint={() => {
                alert('Level 1 hint will unlock when the full engine is wired in Step 2/3!');
              }}
            />
          </div>
        </section>
      </main>
    </div>
  );
};

export default App;
