export type SupportedLanguage = 'python';

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

export type ThemeMode = 'light' | 'dark' | 'system';
