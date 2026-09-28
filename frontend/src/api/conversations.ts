// frontend/src/api/conversations.ts
import type { ConversationSummary } from "../types/chat";
import { requestJson, requestVoid } from "./client";

export function listConversations() {
  return requestJson<ConversationSummary[]>("/api/conversations");
}

export function createConversation(title: string) {
  return requestJson<ConversationSummary>("/api/conversations", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  });
}

export function deleteConversation(conversationId: number) {
  return requestVoid(`/api/conversations/${conversationId}`, {
    method: "DELETE",
  });
}
