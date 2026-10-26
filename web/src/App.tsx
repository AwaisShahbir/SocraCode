import React, { useState, useCallback, useEffect } from 'react';
import { Play, RotateCcw, AlertTriangle, CheckCircle2, Send, Sparkles, BookOpen, Trophy } from 'lucide-react';
import { useTheme } from './lib/theme';
import { Header } from './components/Header';
import { CodeEditor } from './features/editor/CodeEditor';
import { OutputConsole } from './features/output/OutputConsole';
import { HintLadderPanel } from './features/ladder/HintLadderPanel';
import { executeRun, createAttempt, requestNextHint, resolveAttempt, sendHintFeedback } from './lib/api';
import type { Attempt, RunResult, UnlockedHint } from './types/runner';

interface BugPreset {
  id: string;
  name: string;
  category: string;
  code: string;
}

const BUG_PRESETS: BugPreset[] = [
  {
    id: 'syntax_colon',
    name: 'Factorial (SyntaxError: Missing Colon)',
    category: 'Syntax Error',
    code: `# Welcome to SocraCode - Socratic AI Debugging Tutor
# Challenge: Factorial implementation with syntax bug on line 7
# Run the code, observe the error, and climb the Hint Ladder!

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
`,
  },
  {
    id: 'undefined_typo',
    name: 'Counter (NameError: Undefined Typo)',
    category: 'Undefined Name',
    code: `# Challenge: Tracking user visits with counter
# Run the code to diagnose the undefined variable bug!

def record_visits():
    total_visits = 10
    new_visitors = 5
    # Typo on variable name
    updated_total = totl_visits + new_visitors
    return updated_total

print("Total site visits:", record_visits())
`,
  },
  {
    id: 'index_bounds',
    name: 'Scores Average (IndexError: Off-by-one)',
    category: 'Index Error',
    code: `# Challenge: Compute high score average
# Watch out for list index bounds!

def get_top_score(scores):
    # Attempting to read index equal to length
    highest_index = len(scores)
    return scores[highest_index]

student_scores = [88, 92, 79, 95]
print("Top score is:", get_top_score(student_scores))
`,
  },
  {
    id: 'infinite_loop',
    name: 'Countdown Timer (Timeout Loop)',
    category: 'Loop Boundary',
    code: `# Challenge: Countdown timer
# Beware of missing iteration state!

def countdown(start):
    count = start
    while count > 0:
        print(f"T-minus {count}...")
        # Forgot to decrement count!

print("Initiating launch sequence:")
countdown(3)
print("Blast off!")
`,
  },
];

export const App: React.FC = () => {
  const { mode, setMode, resolvedTheme } = useTheme();
  const [selectedPresetId, setSelectedPresetId] = useState<string>('syntax_colon');
  const [code, setCode] = useState<string>(BUG_PRESETS[0].code);
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

  const handleSelectPreset = (presetId: string) => {
    const preset = BUG_PRESETS.find((p) => p.id === presetId);
    if (preset) {
      setSelectedPresetId(presetId);
      setCode(preset.code);
      setRunResult(null);
      setActiveAttempt(null);
      setUnlockedHints([]);
      setHighlightedLine(null);
      setShowReflectionBox(false);
      setIsResolved(false);
      setStatusMessage(`Loaded challenge: ${preset.name}`);
    }
  };

  const handleRun = useCallback(async () => {
    if (isRunning) return;

    setIsRunning(true);
    setStatusMessage('Running in isolated sandbox...');
    setHighlightedLine(null);

    try {
      const result = await executeRun({
        language: 'python',
        code,
      });
      setRunResult(result);

      const hasError = result.exit_code !== 0 || result.timed_out || Boolean(result.stderr);

      if (hasError) {
        setStatusMessage('Bug encountered. Diagnostic model active.');
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
        setStatusMessage('Execution finished cleanly! (Exit 0)');
        if (activeAttempt && !isResolved) {
          setShowReflectionBox(true);
        }
      }
    } catch {
      setStatusMessage('Network error: failed to communicate with sandbox');
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
    setStatusMessage('Bug fixed! Learning history recorded.');
  };

  const handleReset = () => {
    const current = BUG_PRESETS.find((p) => p.id === selectedPresetId) || BUG_PRESETS[0];
    setCode(current.code);
    setRunResult(null);
    setActiveAttempt(null);
    setUnlockedHints([]);
    setHighlightedLine(null);
    setShowReflectionBox(false);
    setIsResolved(false);
    setStatusMessage('Code reset to default');
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
      {/* Top Modern Header */}
      <Header themeMode={mode} onThemeChange={setMode} />

      {/* Main Workspace (60/40 Split) */}
      <main
        style={{
          display: 'grid',
          gridTemplateColumns: 'minmax(0, 1.4fr) minmax(390px, 1fr)',
          flex: 1,
          minHeight: 0,
          backgroundColor: 'var(--color-bg)',
        }}
      >
        {/* Left Column: Code Editor & Action Dock */}
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

          {/* Action Dock */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '0 var(--space-4)',
              backgroundColor: 'var(--color-surface-glass)',
              backdropFilter: 'blur(16px)',
              WebkitBackdropFilter: 'blur(16px)',
              borderTop: '1px solid var(--color-border)',
              borderRight: '1px solid var(--color-border)',
              height: '58px',
              flexShrink: 0,
            }}
          >
            {/* Run & Presets Controls */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
              <button
                id="run-code-button"
                type="button"
                onClick={handleRun}
                disabled={isRunning}
                title="Execute program in sandbox (Ctrl+Enter)"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '8px',
                  minHeight: '40px',
                  padding: '0 18px',
                  background: 'var(--color-accent-gradient)',
                  color: '#FFFFFF',
                  border: 'none',
                  borderRadius: 'var(--radius-control)',
                  fontWeight: 700,
                  fontSize: '13px',
                  boxShadow: 'var(--shadow-accent-glow)',
                  opacity: isRunning ? 0.75 : 1,
                  cursor: isRunning ? 'wait' : 'pointer',
                  transition: 'all var(--transition-fast)',
                }}
              >
                <Play size={15} fill="currentColor" />
                <span>{isRunning ? 'Running...' : 'Run Code'}</span>
                <span
                  style={{
                    fontSize: '10px',
                    padding: '2px 5px',
                    background: 'rgba(255, 255, 255, 0.25)',
                    borderRadius: '4px',
                    fontWeight: 800,
                    marginLeft: '2px',
                  }}
                >
                  Ctrl ↵
                </span>
              </button>

              <button
                type="button"
                onClick={handleReset}
                title="Reset code to default"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  width: '40px',
                  height: '40px',
                  backgroundColor: 'var(--color-surface-raised)',
                  color: 'var(--color-text-muted)',
                  border: '1px solid var(--color-border)',
                  borderRadius: 'var(--radius-control)',
                  cursor: 'pointer',
                }}
              >
                <RotateCcw size={15} />
              </button>

              {/* Practice Challenge Quick-Loader */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginLeft: 'var(--space-2)' }}>
                <BookOpen size={14} color="var(--color-accent)" />
                <select
                  value={selectedPresetId}
                  onChange={(e) => handleSelectPreset(e.target.value)}
                  title="Select sample bug challenge"
                  style={{
                    backgroundColor: 'var(--color-surface-raised)',
                    color: 'var(--color-text)',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-control)',
                    padding: '6px 10px',
                    fontSize: '12px',
                    fontWeight: 600,
                    cursor: 'pointer',
                  }}
                >
                  {BUG_PRESETS.map((preset) => (
                    <option key={preset.id} value={preset.id}>
                      {preset.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Status Live Chip */}
            <div
              aria-live="polite"
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                fontSize: '12px',
                fontWeight: 600,
                padding: '4px 10px',
                borderRadius: 'var(--radius-pill)',
                backgroundColor: hasFailingRun
                  ? 'rgba(239, 68, 68, 0.1)'
                  : 'var(--color-surface-raised)',
                border: hasFailingRun
                  ? '1px solid rgba(239, 68, 68, 0.3)'
                  : '1px solid var(--color-border)',
                color: hasFailingRun ? 'var(--color-danger)' : 'var(--color-text-muted)',
              }}
            >
              {hasFailingRun ? (
                <AlertTriangle size={13} color="var(--color-danger)" />
              ) : (
                <CheckCircle2 size={13} color="var(--color-success)" />
              )}
              <span>{statusMessage}</span>
            </div>
          </div>
        </section>

        {/* Right Column: Console & Hint Ladder */}
        <section
          aria-label="Output and Guidance Panel"
          style={{
            display: 'grid',
            gridTemplateRows: '1fr 1.3fr',
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
              maxLevelAllowed={activeAttempt ? activeAttempt.max_level_allowed : 5}
              hasActiveAttempt={Boolean(activeAttempt)}
              isLoadingHint={isLoadingHint}
              onGetNextHint={handleGetNextHint}
              onSelectLine={(line) => setHighlightedLine(line)}
              onApplySolution={(fixedCode) => setCode(fixedCode)}
              onFeedback={handleFeedback}
            />
          </div>
        </section>
      </main>

      {/* Gamified Celebration Reflection Modal on Fix */}
      {showReflectionBox && (
        <div
          role="dialog"
          aria-labelledby="reflection-title"
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.75)',
            backdropFilter: 'blur(16px)',
            WebkitBackdropFilter: 'blur(16px)',
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
              padding: '28px',
              maxWidth: '500px',
              width: '100%',
              boxShadow: 'var(--shadow-floating)',
            }}
          >
            {/* Header with Trophy & XP */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    width: '38px',
                    height: '38px',
                    borderRadius: '10px',
                    background: 'rgba(16, 185, 129, 0.15)',
                    color: 'var(--color-success)',
                  }}
                >
                  <Trophy size={20} />
                </div>
                <div>
                  <h3 id="reflection-title" style={{ fontSize: '17px', fontWeight: 800, margin: 0 }}>
                    Bug Crushed! 🎉
                  </h3>
                  <div style={{ fontSize: '12px', color: 'var(--color-text-muted)' }}>
                    Program passed with Exit 0
                  </div>
                </div>
              </div>

              <span
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px',
                  padding: '3px 10px',
                  background: 'rgba(245, 158, 11, 0.15)',
                  border: '1px solid rgba(245, 158, 11, 0.3)',
                  color: 'var(--color-warning)',
                  borderRadius: 'var(--radius-pill)',
                  fontSize: '11px',
                  fontWeight: 800,
                }}
              >
                <Sparkles size={12} />
                <span>+50 XP</span>
              </span>
            </div>

            <p style={{ fontSize: '13px', color: 'var(--color-text-muted)', lineHeight: '1.6', marginTop: '10px' }}>
              Reflecting on what went wrong solidifies debugging memory and prevents repeat mistakes. What was the underlying root cause?
            </p>

            <textarea
              value={reflectionText}
              onChange={(e) => setReflectionText(e.target.value)}
              placeholder="e.g., I missed the colon at the end of the if statement line..."
              rows={3}
              style={{
                width: '100%',
                marginTop: '12px',
                padding: '12px',
                backgroundColor: 'var(--color-code-bg)',
                color: 'var(--color-text)',
                border: '1px solid var(--color-border)',
                borderRadius: 'var(--radius-control)',
                fontFamily: 'inherit',
                fontSize: '13px',
                resize: 'none',
              }}
            />

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '20px' }}>
              <button
                type="button"
                onClick={() => setShowReflectionBox(false)}
                style={{
                  padding: '8px 16px',
                  backgroundColor: 'transparent',
                  border: '1px solid var(--color-border)',
                  borderRadius: 'var(--radius-control)',
                  color: 'var(--color-text-muted)',
                  fontSize: '12px',
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
                  gap: '6px',
                  padding: '8px 18px',
                  background: 'var(--color-accent-gradient)',
                  color: '#FFFFFF',
                  border: 'none',
                  borderRadius: 'var(--radius-control)',
                  fontSize: '12px',
                  fontWeight: 700,
                  boxShadow: 'var(--shadow-accent-glow)',
                  cursor: 'pointer',
                }}
              >
                <Send size={13} />
                <span>Save to Learning Log</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
