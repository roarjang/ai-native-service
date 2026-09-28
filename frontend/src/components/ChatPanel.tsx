// frontend/src/components/ChatPanel.tsx
import type { Conversation } from "../types/chat";
import { MessageForm } from "./MessageForm";
import { MessageList } from "./MessageList";

type ChatPanelProps = {
  conversation: Conversation | undefined;
  onsend: (message: string) => Promise<void>;
};

function EmptyState({ message }: { message: string }) {
  return <p className="empty-state">{message}</p>;
}

export function ChatPanel({ conversation, onsend }: ChatPanelProps) {
  if (!conversation) {
    return (
      <section className="chat-panel">
        <EmptyState message="대화를 선택하세요" />
      </section>
    );
  }

  return (
    <section className="chat-panel" aria-label={conversation.title}>
      <header className="chat-panel-header">
        <h2>{conversation.title}</h2>
      </header>
      {conversation.messages.length === 0 ? (
        <EmptyState message="첫 질문을 입력하세요" />
      ) : (
        <MessageList messages={conversation.messages} />
      )}
      <MessageForm onSend={onsend} />
    </section>
  );
}

