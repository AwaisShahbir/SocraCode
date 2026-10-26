import type { Attempt, RunRequest, RunResult, UnlockedHint } from '../types/runner';

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

export async function createAttempt(params: {
  language: string;
  source: string;
  code: string;
  error_text: string;
  timed_out?: boolean;
}): Promise<Attempt | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/attempts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    });

    if (!response.ok) {
      return null;
    }
    return await response.json();
  } catch {
    return null;
  }
}

export async function requestNextHint(attemptId: string): Promise<UnlockedHint | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/attempts/${attemptId}/hint`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      return null;
    }
    return await response.json();
  } catch {
    return null;
  }
}

export async function resolveAttempt(attemptId: string, reflection?: string): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/attempts/${attemptId}/resolve`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ reflection: reflection || null }),
    });
    return response.ok;
  } catch {
    return false;
  }
}

export async function sendHintFeedback(hintId: string, helpful: boolean): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/hints/${hintId}/feedback`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ helpful }),
    });
    return response.ok;
  } catch {
    return false;
  }
}
