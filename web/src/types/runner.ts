export type SupportedLanguage = 'python' | 'java' | 'cpp';

export interface RunRequest {
  language: SupportedLanguage;
  code: string;
  stdin?: string | null;
}

export interface RunResult {
  stdout: string;
  stderr: string;
  exit_code: number;
  duration_ms: number;
  timed_out: boolean;
}

export interface Attempt {
  id: string;
  language: string;
  source: string;
  category: string;
  concept: string;
  buggy_line: number;
  confidence: number;
  current_level: number;
  max_level_allowed: number;
  started_at: string;
}

export interface UnlockedHint {
  attempt_id: string;
  level: number;
  level_name: string;
  text: string;
  shown_at: string;
  is_last_available_level: boolean;
  hint_id: string;
  example_code?: string | null;
  solution_code?: string | null;
  explanation?: string | null;
  diff_summary?: string | null;
}

export type ThemeMode = 'light' | 'dark' | 'system';
