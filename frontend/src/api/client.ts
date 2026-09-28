export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export const CLIENT_ID = "student-web";

export async function readError(response: Response): Promise<ApiError> {
  const body = await response.json().catch(() => null);
  const detail = typeof body?.detail === "string" ? body.detail : "API 요청 실패";
  return new ApiError(response.status, detail);
}

export async function requestJson<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: { "X-Client-Id": CLIENT_ID, ...init?.headers },
  });
  if (!response.ok) {
    throw await readError(response);
  }
  return response.json() as Promise<T>;
}

export async function requestVoid(path: string, init?: RequestInit): Promise<void> {
  const response = await fetch(path, {
    ...init,
    headers: { "X-Client-Id": CLIENT_ID, ...init?.headers },
  });
  if (!response.ok) {
    throw await readError(response);
  }
}
