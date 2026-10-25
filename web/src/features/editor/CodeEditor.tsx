import React, { useRef } from 'react';
import Editor from '@monaco-editor/react';
import type { OnMount } from '@monaco-editor/react';

interface CodeEditorProps {
  code: string;
  onChange: (value: string) => void;
  resolvedTheme: 'light' | 'dark';
  onRunShortcut?: () => void;
  isRunning?: boolean;
}

export const CodeEditor: React.FC<CodeEditorProps> = ({
  code,
  onChange,
  resolvedTheme,
  onRunShortcut,
  isRunning = false,
}) => {
  const editorRef = useRef<any>(null);

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
      {/* Editor toolbar */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: 'var(--space-2) var(--space-4)',
          backgroundColor: 'var(--color-surface-raised)',
          borderBottom: '1px solid var(--color-border)',
          fontSize: 'var(--font-size-xs)',
          color: 'var(--color-text-muted)',
        }}
      >
        <span style={{ fontWeight: 600 }}>main.py</span>
        <div style={{ display: 'flex', gap: 'var(--space-3)' }}>
          <span>{lineCount} lines</span>
          <span>Saved just now</span>
          <span title="Press Ctrl+Enter to execute code">
            <kbd style={{ backgroundColor: 'var(--color-code-bg)', padding: '1px 4px', borderRadius: '4px', border: '1px solid var(--color-border)' }}>Ctrl</kbd> + <kbd style={{ backgroundColor: 'var(--color-code-bg)', padding: '1px 4px', borderRadius: '4px', border: '1px solid var(--color-border)' }}>Enter</kbd> to run
          </span>
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
            lineHeight: 22,
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            smoothScrolling: true,
            tabSize: 4,
            wordWrap: 'on',
            automaticLayout: true,
            padding: { top: 12, bottom: 12 },
          }}
        />
      </div>
    </div>
  );
};
