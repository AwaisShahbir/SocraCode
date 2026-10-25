import type { RunRequest, RunResult } from '../types/runner';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

export async function executeRun(request: RunRequest): Promise<RunResult> {
  try {
    const response = await fetch(`${API_BASE_URL}/runs`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const detail = errorData.detail || `Server returned error (${response.status})`;
      return {
        stdout: '',
        stderr: `Server Error: ${detail}`,
        exit_code: -1,
        duration_ms: 0,
        timed_out: false,
      };
    }

    return await response.json();
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'Unknown network failure';
    return {
      stdout: '',
      stderr: `The backend server did not respond at ${API_BASE_URL}. Ensure the FastAPI server is running with 'uvicorn app.main:app --port 8000'. (${message})`,
      exit_code: -1,
      duration_ms: 0,
      timed_out: false,
    };
  }
}
