import type { Message, StreamEvent } from "../types/chat";
import { ApiError, CLIENT_ID, readError, requestJson } from "./client";

export function listMessages(conversationId: number) {
  return requestJson<Message[]>(`/api/conversations/${conversationId}/messages`);
}

export class ReplyFailedError extends Error {
  constructor() {
    super("질문은 저장됐지만 AI 답변을 받지 못했습니다. 대화 기록을 확인해 주세요.");
    this.name = "ReplyFailedError";
  }
}

export async function streamMessage(
  conversationId: number,
  content: string,
  onEvent: (event: StreamEvent) => void,
): Promise<void> {
  const response = await fetch(
    `/api/conversations/${conversationId}/messages/stream`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Client-Id": CLIENT_ID },
      body: JSON.stringify({ content }),
    },
  );
  if (!response.ok) {
    throw await readError(response);
  }
  if (!response.body) {
    throw new ApiError(0, "스트림을 읽을 수 없습니다.");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let completed = false;

  function handleLine(line: string) {
    if (!line.trim()) return;
    const event = JSON.parse(line) as StreamEvent;
    if (event.type === "error") throw new ReplyFailedError();
    if (event.type === "done") completed = true;
    onEvent(event);
  }

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";
    for (const line of lines) handleLine(line);
  }
  buffer += decoder.decode();
  handleLine(buffer);
  if (!completed) throw new ApiError(0, "응답이 완료되기 전에 연결이 끊겼습니다.");
}
