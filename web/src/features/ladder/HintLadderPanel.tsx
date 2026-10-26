import React, { useState } from 'react';
import {
  HelpCircle,
  Sparkles,
  MapPin,
  Code2,
  CheckSquare,
  Lock,
  ChevronDown,
  ChevronRight,
  ThumbsUp,
  ThumbsDown,
  Check,
  Loader2,
  Copy,
  ArrowRight,
  AlertCircle,
  Zap,
  ShieldAlert,
} from 'lucide-react';
import type { UnlockedHint } from '../../types/runner';

interface HintLadderPanelProps {
  unlockedHints: UnlockedHint[];
  currentLevel: number;
  maxLevelAllowed: number;
  hasActiveAttempt: boolean;
  isLoadingHint: boolean;
  onGetNextHint: () => void;
  onSelectLine?: (line: number) => void;
  onApplySolution?: (code: string) => void;
  onFeedback: (hintId: string, helpful: boolean) => void;
}

export const HintLadderPanel: React.FC<HintLadderPanelProps> = ({
  unlockedHints,
  currentLevel,
  maxLevelAllowed,
  hasActiveAttempt,
  isLoadingHint,
  onGetNextHint,
  onSelectLine,
  onApplySolution,
  onFeedback,
}) => {
  const [expandedLevels, setExpandedLevels] = useState<Record<number, boolean>>({});
  const [feedbackSent, setFeedbackSent] = useState<Record<string, boolean>>({});
  const [showConfirmLevel5, setShowConfirmLevel5] = useState<boolean>(false);
  const [copiedLevel5, setCopiedLevel5] = useState<boolean>(false);
  const [copiedExample, setCopiedExample] = useState<boolean>(false);

  const ladderDefinitions = [
    { level: 1, title: 'Nudge', subtitle: 'Socratic inquiry', icon: HelpCircle, color: '#38BDF8' },
    { level: 2, title: 'Concept', subtitle: 'Underlying CS theory', icon: Sparkles, color: '#818CF8' },
    { level: 3, title: 'Location', subtitle: 'Target problem line', icon: MapPin, color: '#FBBF24' },
    { level: 4, title: 'Parallel Example', subtitle: 'Worked problem', icon: Code2, color: '#C084FC' },
    { level: 5, title: 'Full Solution', subtitle: 'Rule-verified fix', icon: CheckSquare, color: '#34D399' },
  ];

  const toggleExpand = (level: number) => {
    setExpandedLevels((prev) => ({
      ...prev,
      [level]: prev[level] !== undefined ? !prev[level] : false,
    }));
  };

  const handleFeedbackClick = (hintId: string, helpful: boolean) => {
    onFeedback(hintId, helpful);
    setFeedbackSent((prev) => ({ ...prev, [hintId]: true }));
  };

  const handlePrimaryAction = () => {
    if (currentLevel === 4) {
      setShowConfirmLevel5(true);
    } else {
      onGetNextHint();
    }
  };

  const confirmShowSolution = () => {
    setShowConfirmLevel5(false);
    onGetNextHint();
  };

  const canRequestNext = hasActiveAttempt && currentLevel < maxLevelAllowed && !isLoadingHint;

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        backgroundColor: 'var(--color-surface)',
        borderLeft: '1px solid var(--color-border)',
        overflowY: 'auto',
      }}
    >
      {/* Header & Stepper Progress Tracker */}
      <div
        style={{
          padding: 'var(--space-3) var(--space-4)',
          backgroundColor: 'var(--color-surface-raised)',
          borderBottom: '1px solid var(--color-border)',
          flexShrink: 0,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Zap size={16} color="var(--color-accent)" />
            <h2 style={{ fontSize: '14px', fontWeight: 800, letterSpacing: '-0.3px', margin: 0 }}>
              Socratic Hint Ladder
            </h2>
          </div>
          <span
            style={{
              fontSize: '11px',
              fontWeight: 700,
              color: 'var(--color-accent)',
              backgroundColor: 'rgba(99, 102, 241, 0.12)',
              border: '1px solid rgba(99, 102, 241, 0.25)',
              padding: '2px 8px',
              borderRadius: 'var(--radius-pill)',
            }}
          >
            Level {currentLevel} of {maxLevelAllowed}
          </span>
        </div>

        {/* Stepper Timeline Pills */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '4px', marginTop: '6px' }}>
          {ladderDefinitions.map((step) => {
            const isUnlocked = step.level <= currentLevel;
            const isCurrent = step.level === currentLevel;
            return (
              <div
                key={step.level}
                title={`Level ${step.level}: ${step.title}`}
                style={{
                  flex: 1,
                  height: '4px',
                  borderRadius: '2px',
                  backgroundColor: isCurrent
                    ? 'var(--color-accent)'
                    : isUnlocked
                    ? 'var(--color-success)'
                    : 'var(--color-border)',
                  boxShadow: isCurrent ? '0 0 8px var(--color-accent)' : 'none',
                  transition: 'all 0.3s ease',
                }}
              />
            );
          })}
        </div>
      </div>

      {/* Screen Reader Live Announcement */}
      <div aria-live="polite" style={{ position: 'absolute', width: '1px', height: '1px', overflow: 'hidden', clip: 'rect(0,0,0,0)' }}>
        {unlockedHints.length > 0 ? `Hint Level ${unlockedHints[unlockedHints.length - 1].level} unlocked` : ''}
      </div>

      {/* Stepper Cards */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: 'var(--space-2)',
          padding: 'var(--space-3)',
          flex: 1,
        }}
      >
        {ladderDefinitions.map((step) => {
          const Icon = step.icon;
          const hint = unlockedHints.find((h) => h.level === step.level);
          const isUnlocked = Boolean(hint);
          const isCurrent = step.level === currentLevel;
          const isExpanded = expandedLevels[step.level] ?? isCurrent;

          return (
            <div
              key={step.level}
              style={{
                borderRadius: 'var(--radius-container)',
                border: isCurrent
                  ? '1.5px solid var(--color-accent)'
                  : isUnlocked
                  ? '1px solid var(--color-border)'
                  : '1px dashed var(--color-border)',
                backgroundColor: isCurrent
                  ? 'var(--color-surface-card)'
                  : isUnlocked
                  ? 'var(--color-surface-raised)'
                  : 'rgba(0, 0, 0, 0.02)',
                boxShadow: isCurrent ? '0 4px 16px rgba(99, 102, 241, 0.12)' : 'none',
                opacity: isUnlocked ? 1 : 0.6,
                transition: 'all var(--transition-fast)',
                overflow: 'hidden',
              }}
            >
              {/* Stepper Card Header */}
              <button
                type="button"
                onClick={() => isUnlocked && toggleExpand(step.level)}
                disabled={!isUnlocked}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  width: '100%',
                  padding: '10px 12px',
                  background: 'transparent',
                  border: 'none',
                  textAlign: 'left',
                  cursor: isUnlocked ? 'pointer' : 'default',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      width: '26px',
                      height: '26px',
                      borderRadius: '8px',
                      backgroundColor: isCurrent
                        ? 'var(--color-accent)'
                        : isUnlocked
                        ? 'rgba(16, 185, 129, 0.15)'
                        : 'var(--color-surface-raised)',
                      color: isCurrent
                        ? '#FFFFFF'
                        : isUnlocked
                        ? 'var(--color-success)'
                        : 'var(--color-text-muted)',
                      border: isUnlocked ? 'none' : '1px solid var(--color-border)',
                      fontSize: '12px',
                      fontWeight: 700,
                    }}
                  >
                    {isUnlocked && !isCurrent ? <Check size={14} /> : step.level}
                  </div>

                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <Icon size={14} color={isCurrent ? 'var(--color-accent)' : step.color} />
                      <span
                        style={{
                          fontSize: '13px',
                          fontWeight: 700,
                          color: isCurrent ? 'var(--color-accent)' : 'var(--color-text)',
                        }}
                      >
                        L{step.level}: {step.title}
                      </span>
                    </div>
                    <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
                      {step.subtitle}
                    </div>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                  {isUnlocked ? (
                    isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />
                  ) : (
                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px',
                        fontSize: '11px',
                        color: 'var(--color-text-muted)',
                      }}
                    >
                      <Lock size={12} />
                      <span>Locked</span>
                    </div>
                  )}
                </div>
              </button>

              {/* Expanded Hint Content Body */}
              {isUnlocked && isExpanded && hint && (
                <div
                  style={{
                    padding: '12px 14px',
                    borderTop: '1px solid var(--color-border)',
                    backgroundColor: 'var(--color-surface)',
                  }}
                >
                  {/* General / Level 1-3 Text */}
                  {step.level <= 3 && (
                    <p
                      style={{
                        fontSize: '13.5px',
                        lineHeight: '1.6',
                        color: 'var(--color-text)',
                        margin: 0,
                      }}
                    >
                      {hint.text}
                    </p>
                  )}

                  {/* Level 3: Location line highlight trigger */}
                  {step.level === 3 && onSelectLine && (
                    <button
                      type="button"
                      onClick={() => {
                        const lineMatch = hint.text.match(/line\s+(\d+)/i);
                        if (lineMatch) {
                          onSelectLine(parseInt(lineMatch[1], 10));
                        }
                      }}
                      style={{
                        marginTop: '10px',
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '5px',
                        padding: '5px 10px',
                        fontSize: '12px',
                        fontWeight: 700,
                        color: 'var(--color-warning)',
                        backgroundColor: 'rgba(245, 158, 11, 0.1)',
                        border: '1px solid rgba(245, 158, 11, 0.3)',
                        borderRadius: 'var(--radius-control)',
                        cursor: 'pointer',
                      }}
                    >
                      <MapPin size={13} />
                      <span>Inspect line in Monaco Editor</span>
                    </button>
                  )}

                  {/* Level 4: Worked Example Code Block */}
                  {step.level === 4 && (
                    <div>
                      <p style={{ fontSize: '12px', color: 'var(--color-text)', marginBottom: '8px' }}>
                        Here is a parallel worked example demonstrating the correct pattern on different data:
                      </p>
                      {hint.example_code && (
                        <div style={{ position: 'relative' }}>
                          <pre
                            style={{
                              padding: '12px',
                              backgroundColor: 'var(--color-code-bg)',
                              color: 'var(--color-text)',
                              fontFamily: 'var(--font-mono)',
                              fontSize: '12px',
                              borderRadius: 'var(--radius-control)',
                              border: '1px solid var(--color-border)',
                              overflowX: 'auto',
                              lineHeight: '1.5',
                            }}
                          >
                            <code>{hint.example_code}</code>
                          </pre>
                          <button
                            type="button"
                            onClick={() => {
                              navigator.clipboard.writeText(hint.example_code!);
                              setCopiedExample(true);
                              setTimeout(() => setCopiedExample(false), 1500);
                            }}
                            style={{
                              position: 'absolute',
                              top: '6px',
                              right: '6px',
                              padding: '3px 8px',
                              background: 'var(--color-surface)',
                              border: '1px solid var(--color-border)',
                              borderRadius: '4px',
                              fontSize: '11px',
                              color: copiedExample ? 'var(--color-success)' : 'var(--color-text-muted)',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '4px',
                            }}
                          >
                            {copiedExample ? <Check size={11} /> : <Copy size={11} />}
                            <span>{copiedExample ? 'Copied' : 'Copy'}</span>
                          </button>
                        </div>
                      )}
                      {hint.explanation && (
                        <p style={{ fontSize: '12px', color: 'var(--color-text-muted)', marginTop: '8px' }}>
                          <strong>Pattern Note:</strong> {hint.explanation}
                        </p>
                      )}
                    </div>
                  )}

                  {/* Level 5: Full Solution */}
                  {step.level === 5 && (
                    <div>
                      {hint.solution_code ? (
                        <div>
                          {hint.diff_summary && (
                            <div
                              style={{
                                display: 'inline-flex',
                                alignItems: 'center',
                                gap: '5px',
                                padding: '3px 10px',
                                backgroundColor: 'rgba(16, 185, 129, 0.12)',
                                border: '1px solid rgba(16, 185, 129, 0.25)',
                                color: 'var(--color-success)',
                                borderRadius: 'var(--radius-pill)',
                                fontSize: '11px',
                                fontWeight: 700,
                                marginBottom: '10px',
                              }}
                            >
                              <Check size={12} />
                              <span>{hint.diff_summary}</span>
                            </div>
                          )}

                          <pre
                            style={{
                              padding: '12px',
                              backgroundColor: 'var(--color-code-bg)',
                              color: 'var(--color-text)',
                              fontFamily: 'var(--font-mono)',
                              fontSize: '12px',
                              borderRadius: 'var(--radius-control)',
                              border: '1px solid var(--color-border)',
                              overflowX: 'auto',
                              lineHeight: '1.5',
                              maxHeight: '220px',
                            }}
                          >
                            <code>{hint.solution_code}</code>
                          </pre>

                          <div style={{ display: 'flex', gap: 'var(--space-2)', marginTop: '10px' }}>
                            {onApplySolution && (
                              <button
                                type="button"
                                onClick={() => onApplySolution(hint.solution_code!)}
                                style={{
                                  display: 'inline-flex',
                                  alignItems: 'center',
                                  gap: '6px',
                                  padding: '7px 14px',
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
                                <ArrowRight size={13} />
                                <span>Apply Fix to Editor</span>
                              </button>
                            )}
                            <button
                              type="button"
                              onClick={() => {
                                navigator.clipboard.writeText(hint.solution_code!);
                                setCopiedLevel5(true);
                                setTimeout(() => setCopiedLevel5(false), 2000);
                              }}
                              style={{
                                display: 'inline-flex',
                                alignItems: 'center',
                                gap: '5px',
                                padding: '7px 12px',
                                backgroundColor: 'var(--color-surface-raised)',
                                color: 'var(--color-text)',
                                border: '1px solid var(--color-border)',
                                borderRadius: 'var(--radius-control)',
                                fontSize: '12px',
                                fontWeight: 600,
                                cursor: 'pointer',
                              }}
                            >
                              {copiedLevel5 ? <Check size={13} color="var(--color-success)" /> : <Copy size={13} />}
                              <span>{copiedLevel5 ? 'Copied!' : 'Copy Code'}</span>
                            </button>
                          </div>

                          {hint.explanation && (
                            <p style={{ fontSize: '12px', color: 'var(--color-text-muted)', marginTop: '10px', lineHeight: '1.5' }}>
                              <strong>Why this fix works:</strong> {hint.explanation}
                            </p>
                          )}
                        </div>
                      ) : (
                        <div style={{ display: 'flex', alignItems: 'flex-start', gap: 'var(--space-2)', padding: '10px', backgroundColor: 'var(--color-code-bg)', borderRadius: 'var(--radius-control)' }}>
                          <AlertCircle size={16} style={{ color: 'var(--color-warning)', flexShrink: 0, marginTop: '2px' }} />
                          <p style={{ fontSize: '12px', color: 'var(--color-text-muted)' }}>
                            SocraCode can't verify a full fix for this bug with certainty. Review the worked example in Level 4 or consult your course instructor.
                          </p>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Feedback Bar */}
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      marginTop: '12px',
                      paddingTop: '8px',
                      borderTop: '1px dashed var(--color-border)',
                      fontSize: '11px',
                      color: 'var(--color-text-muted)',
                    }}
                  >
                    <span>Was this hint helpful?</span>
                    {feedbackSent[hint.hint_id] ? (
                      <span style={{ color: 'var(--color-success)', fontWeight: 600 }}>Thank you for feedback!</span>
                    ) : (
                      <div style={{ display: 'flex', gap: '6px' }}>
                        <button
                          type="button"
                          onClick={() => handleFeedbackClick(hint.hint_id, true)}
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '3px',
                            padding: '2px 8px',
                            border: '1px solid var(--color-border)',
                            borderRadius: 'var(--radius-control)',
                            background: 'transparent',
                            color: 'var(--color-text-muted)',
                            cursor: 'pointer',
                          }}
                        >
                          <ThumbsUp size={11} />
                          <span>Yes</span>
                        </button>
                        <button
                          type="button"
                          onClick={() => handleFeedbackClick(hint.hint_id, false)}
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '3px',
                            padding: '2px 8px',
                            border: '1px solid var(--color-border)',
                            borderRadius: 'var(--radius-control)',
                            background: 'transparent',
                            color: 'var(--color-text-muted)',
                            cursor: 'pointer',
                          }}
                        >
                          <ThumbsDown size={11} />
                          <span>No</span>
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Footer Primary Action */}
      <div
        style={{
          padding: 'var(--space-3) var(--space-4)',
          backgroundColor: 'var(--color-surface-raised)',
          borderTop: '1px solid var(--color-border)',
          flexShrink: 0,
        }}
      >
        <button
          type="button"
          onClick={handlePrimaryAction}
          disabled={!canRequestNext}
          title="Unlock next pedagogical hint (Ctrl+Shift+H)"
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            width: '100%',
            minHeight: '44px',
            padding: '0 var(--space-3)',
            background: canRequestNext
              ? 'var(--color-accent-gradient)'
              : 'var(--color-border)',
            color: canRequestNext ? '#FFFFFF' : 'var(--color-text-muted)',
            border: 'none',
            borderRadius: 'var(--radius-control)',
            fontSize: '13px',
            fontWeight: 700,
            cursor: canRequestNext ? 'pointer' : 'not-allowed',
            boxShadow: canRequestNext ? 'var(--shadow-accent-glow)' : 'none',
            transition: 'all var(--transition-fast)',
          }}
        >
          {isLoadingHint ? (
            <>
              <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} />
              <span>Analyzing & unlocking hint...</span>
            </>
          ) : !hasActiveAttempt ? (
            <span>Run code to unlock hints on error</span>
          ) : currentLevel >= maxLevelAllowed ? (
            <span>Full Solution Reached</span>
          ) : currentLevel === 0 ? (
            <>
              <Sparkles size={15} />
              <span>Get Hint (Level 1: Nudge)</span>
            </>
          ) : currentLevel === 4 ? (
            <>
              <CheckSquare size={15} />
              <span>Show Full Solution (Level 5)</span>
            </>
          ) : (
            <>
              <Sparkles size={15} />
              <span>Get Next Hint (Level {currentLevel + 1})</span>
            </>
          )}
        </button>
      </div>

      {/* Level 5 Confirmation Modal */}
      {showConfirmLevel5 && (
        <div
          role="dialog"
          aria-labelledby="confirm-solution-title"
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.7)',
            backdropFilter: 'blur(12px)',
            WebkitBackdropFilter: 'blur(12px)',
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
              padding: '24px',
              maxWidth: '460px',
              width: '100%',
              boxShadow: 'var(--shadow-floating)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--color-warning)', marginBottom: '8px' }}>
              <ShieldAlert size={22} />
              <h3 id="confirm-solution-title" style={{ fontSize: '16px', fontWeight: 800, margin: 0 }}>
                Show Full Solution?
              </h3>
            </div>
            <p style={{ fontSize: '13px', color: 'var(--color-text-muted)', lineHeight: '1.6' }}>
              Trying to fix the code yourself first reinforces deeper understanding and long-term problem-solving stamina.
              Are you sure you want to reveal the full code solution?
            </p>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '20px' }}>
              <button
                type="button"
                autoFocus
                onClick={() => setShowConfirmLevel5(false)}
                style={{
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
                Keep Trying 💪
              </button>
              <button
                type="button"
                onClick={confirmShowSolution}
                style={{
                  padding: '8px 14px',
                  backgroundColor: 'transparent',
                  color: 'var(--color-danger)',
                  border: '1px solid rgba(239, 68, 68, 0.4)',
                  borderRadius: 'var(--radius-control)',
                  fontSize: '12px',
                  fontWeight: 600,
                  cursor: 'pointer',
                }}
              >
                Show Solution
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
