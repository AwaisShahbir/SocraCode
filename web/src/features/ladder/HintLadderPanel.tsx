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
  onFeedback,
}) => {
  const [expandedLevels, setExpandedLevels] = useState<Record<number, boolean>>({});
  const [feedbackSent, setFeedbackSent] = useState<Record<string, boolean>>({});

  const ladderDefinitions = [
    { level: 1, title: 'Nudge', subtitle: 'Guiding question', icon: HelpCircle },
    { level: 2, title: 'Concept', subtitle: 'Underlying CS concept', icon: Sparkles },
    { level: 3, title: 'Location', subtitle: 'Problem line & area', icon: MapPin },
    { level: 4, title: 'Similar Example', subtitle: 'Worked parallel code', icon: Code2 },
    { level: 5, title: 'Full Solution', subtitle: 'Complete verified fix', icon: CheckSquare },
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
      {/* Header */}
      <div
        style={{
          padding: 'var(--space-3) var(--space-4)',
          backgroundColor: 'var(--color-surface-raised)',
          borderBottom: '1px solid var(--color-border)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <h2 style={{ fontSize: 'var(--font-size-sm)', fontWeight: 700, letterSpacing: '-0.2px' }}>
            Five-Level Hint Ladder
          </h2>
          <span
            style={{
              fontSize: 'var(--font-size-xs)',
              color: 'var(--color-text-muted)',
              backgroundColor: 'var(--color-code-bg)',
              padding: '2px 8px',
              borderRadius: 'var(--radius-control)',
            }}
          >
            Level {currentLevel} of {maxLevelAllowed}
          </span>
        </div>
        <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-muted)', marginTop: '2px' }}>
          Socratic guidance that helps you debug step by step.
        </p>
      </div>

      {/* Screen Reader Live Announcement */}
      <div
        aria-live="polite"
        style={{
          position: 'absolute',
          width: '1px',
          height: '1px',
          margin: '-1px',
          overflow: 'hidden',
          clip: 'rect(0,0,0,0)',
        }}
      >
        {unlockedHints.length > 0
          ? `Hint Level ${unlockedHints[unlockedHints.length - 1].level} unlocked: ${
              unlockedHints[unlockedHints.length - 1].text
            }`
          : ''}
      </div>

      {/* Stepper Items */}
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
                  ? 'var(--color-surface)'
                  : isUnlocked
                  ? 'var(--color-surface-raised)'
                  : 'var(--color-code-bg)',
                opacity: isUnlocked ? 1 : 0.65,
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
                  padding: 'var(--space-2) var(--space-3)',
                  background: 'transparent',
                  border: 'none',
                  textAlign: 'left',
                  cursor: isUnlocked ? 'pointer' : 'default',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      width: '24px',
                      height: '24px',
                      borderRadius: '50%',
                      backgroundColor: isCurrent
                        ? 'var(--color-accent)'
                        : isUnlocked
                        ? 'var(--color-success)'
                        : 'var(--color-border)',
                      color: isUnlocked ? 'var(--color-on-accent)' : 'var(--color-text-muted)',
                      fontSize: 'var(--font-size-xs)',
                      fontWeight: 700,
                    }}
                  >
                    {isUnlocked && !isCurrent ? <Check size={14} /> : step.level}
                  </div>

                  <div>
                    <span
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '4px',
                        fontSize: 'var(--font-size-xs)',
                        fontWeight: 600,
                        color: isCurrent ? 'var(--color-accent)' : 'var(--color-text)',
                      }}
                    >
                      <Icon size={13} />
                      <span>Level {step.level}: {step.title}</span>
                    </span>
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
                      <span>{step.level <= 3 ? `Unlocks after L${step.level - 1}` : 'Unlocks in Step 3'}</span>
                    </div>
                  )}
                </div>
              </button>

              {/* Expanded Hint Content Body */}
              {isUnlocked && isExpanded && hint && (
                <div
                  style={{
                    padding: 'var(--space-3)',
                    borderTop: '1px solid var(--color-border)',
                    backgroundColor: 'var(--color-surface)',
                  }}
                >
                  <p
                    style={{
                      fontSize: 'var(--font-size-sm)',
                      lineHeight: '1.5',
                      color: 'var(--color-text)',
                    }}
                  >
                    {hint.text}
                  </p>

                  {/* Location Action Helper for Level 3 */}
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
                        marginTop: 'var(--space-2)',
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '4px',
                        padding: '4px 8px',
                        fontSize: 'var(--font-size-xs)',
                        fontWeight: 600,
                        color: 'var(--color-accent)',
                        backgroundColor: 'var(--color-code-bg)',
                        border: '1px solid var(--color-border)',
                        borderRadius: 'var(--radius-control)',
                        cursor: 'pointer',
                      }}
                    >
                      <MapPin size={12} />
                      <span>Highlight line in editor</span>
                    </button>
                  )}

                  {/* Feedback Bar */}
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      marginTop: 'var(--space-3)',
                      paddingTop: 'var(--space-2)',
                      borderTop: '1px dashed var(--color-border)',
                      fontSize: '11px',
                      color: 'var(--color-text-muted)',
                    }}
                  >
                    <span>Was this hint helpful?</span>
                    {feedbackSent[hint.hint_id] ? (
                      <span style={{ color: 'var(--color-success)', fontWeight: 600 }}>
                        Thank you for your feedback!
                      </span>
                    ) : (
                      <div style={{ display: 'flex', gap: 'var(--space-1)' }}>
                        <button
                          type="button"
                          onClick={() => handleFeedbackClick(hint.hint_id, true)}
                          title="Helpful"
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '2px',
                            padding: '2px 6px',
                            border: '1px solid var(--color-border)',
                            borderRadius: '4px',
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
                          title="Not helpful"
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '2px',
                            padding: '2px 6px',
                            border: '1px solid var(--color-border)',
                            borderRadius: '4px',
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
        }}
      >
        <button
          type="button"
          onClick={onGetNextHint}
          disabled={!canRequestNext}
          title="Unlock next pedagogical hint (Ctrl+Shift+H)"
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 'var(--space-2)',
            width: '100%',
            minHeight: '44px',
            padding: '0 var(--space-3)',
            backgroundColor: canRequestNext ? 'var(--color-accent)' : 'var(--color-border)',
            color: canRequestNext ? 'var(--color-on-accent)' : 'var(--color-text-muted)',
            border: 'none',
            borderRadius: 'var(--radius-control)',
            fontSize: 'var(--font-size-sm)',
            fontWeight: 600,
            cursor: canRequestNext ? 'pointer' : 'not-allowed',
            transition: 'background-color var(--transition-fast)',
          }}
        >
          {isLoadingHint ? (
            <>
              <Loader2 size={16} className="spin-animation" style={{ animation: 'spin 1s linear infinite' }} />
              <span>Analyzing & unlocking hint...</span>
            </>
          ) : !hasActiveAttempt ? (
            <span>Run code to unlock hints on error</span>
          ) : currentLevel >= maxLevelAllowed ? (
            <span>All Step 2 hints unlocked (Level 3 reached)</span>
          ) : currentLevel === 0 ? (
            <span>Get Hint (Level 1: Nudge)</span>
          ) : (
            <span>Get Next Hint (Level {currentLevel + 1})</span>
          )}
        </button>
      </div>
    </div>
  );
};
