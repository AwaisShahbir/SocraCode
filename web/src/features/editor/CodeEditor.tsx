import React, { useRef, useEffect, useState } from 'react';
import Editor from '@monaco-editor/react';
import type { OnMount } from '@monaco-editor/react';
import { FileCode2, Copy, Check, Navigation } from 'lucide-react';

interface CodeEditorProps {
  code: string;
  onChange: (value: string) => void;
  resolvedTheme: 'light' | 'dark';
  onRunShortcut?: () => void;
  isRunning?: boolean;
  highlightedLine?: number | null;
}

export const CodeEditor: React.FC<CodeEditorProps> = ({
  code,
  onChange,
  resolvedTheme,
  onRunShortcut,
  isRunning = false,
  highlightedLine = null,
}) => {
  const editorRef = useRef<any>(null);
  const [copied, setCopied] = useState<boolean>(false);

  const handleEditorDidMount: OnMount = (editor, monaco) => {
    editorRef.current = editor;

    // Add Ctrl/Cmd + Enter action to execute code
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
      if (onRunShortcut && !isRunning) {
        onRunShortcut();
      }
    });

    // Provide keyboard accessible escape route (Escape key exits focus trap)
    editor.addCommand(monaco.KeyCode.Escape, () => {
      const runBtn = document.getElementById('run-code-button');
      if (runBtn) {
        runBtn.focus();
      }
    });
  };

  useEffect(() => {
    if (editorRef.current && highlightedLine) {
      editorRef.current.revealLineInCenter(highlightedLine);
      editorRef.current.setPosition({ lineNumber: highlightedLine, column: 1 });
      editorRef.current.focus();
    }
  }, [highlightedLine]);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  const lineCount = code.split('\n').length;

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        backgroundColor: 'var(--color-surface)',
        borderRight: '1px solid var(--color-border)',
        overflow: 'hidden',
      }}
    >
      {/* Sleek Modern Tab Bar */}
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
        {/* Active Tab */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 12px',
              backgroundColor: 'var(--color-surface)',
              borderTop: '2px solid var(--color-accent)',
              borderLeft: '1px solid var(--color-border)',
              borderRight: '1px solid var(--color-border)',
              borderBottom: 'none',
              borderRadius: '6px 6px 0 0',
              fontSize: '13px',
              fontWeight: 600,
              color: 'var(--color-text)',
            }}
          >
            <FileCode2 size={15} color="var(--color-accent)" />
            <span>factorial.py</span>
          </div>

          {highlightedLine && (
            <div
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px',
                padding: '3px 8px',
                background: 'rgba(245, 158, 11, 0.15)',
                border: '1px solid rgba(245, 158, 11, 0.35)',
                borderRadius: 'var(--radius-pill)',
                color: 'var(--color-warning)',
                fontSize: '11px',
                fontWeight: 700,
              }}
            >
              <Navigation size={11} />
              <span>Inspecting Line {highlightedLine}</span>
            </div>
          )}
        </div>

        {/* Right Info & Actions */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
          <span style={{ fontSize: '12px', color: 'var(--color-text-muted)', fontFamily: 'var(--font-mono)' }}>
            {lineCount} lines
          </span>

          <button
            type="button"
            onClick={handleCopy}
            title="Copy Code"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              padding: '4px 8px',
              backgroundColor: 'transparent',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-control)',
              color: copied ? 'var(--color-success)' : 'var(--color-text-muted)',
              fontSize: '11px',
              fontWeight: 600,
            }}
          >
            {copied ? <Check size={12} /> : <Copy size={12} />}
            <span>{copied ? 'Copied!' : 'Copy'}</span>
          </button>

          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '3px',
              fontSize: '11px',
              color: 'var(--color-text-muted)',
            }}
          >
            <span className="kbd-key">Ctrl</span>
            <span>+</span>
            <span className="kbd-key">Enter</span>
            <span style={{ marginLeft: '2px' }}>to run</span>
          </div>
        </div>
      </div>

      {/* Monaco Container */}
      <div style={{ flex: 1, minHeight: 0 }}>
        <Editor
          height="100%"
          defaultLanguage="python"
          value={code}
          onChange={(val) => onChange(val || '')}
          theme={resolvedTheme === 'dark' ? 'vs-dark' : 'light'}
          onMount={handleEditorDidMount}
          options={{
            fontSize: 14,
            fontFamily: "'JetBrains Mono', 'Fira Code', Consolas, monospace",
            lineHeight: 23,
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            smoothScrolling: true,
            tabSize: 4,
            wordWrap: 'on',
            automaticLayout: true,
            padding: { top: 14, bottom: 14 },
            cursorBlinking: 'smooth',
            cursorSmoothCaretAnimation: 'on',
            renderLineHighlight: 'all',
          }}
        />
      </div>
    </div>
  );
};
