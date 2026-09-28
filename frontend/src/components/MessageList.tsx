// frontend/src/components/MessageList.tsx
import { useEffect, useRef } from "react";
import type { Message } from "../types/chat";
import { MessageBubble } from "./MessageBubble";

type MessageListProps = { messages: Message[] };

export function MessageList({ messages }: MessageListProps) {
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ block: "end" });
  }, [messages]);

  return (
    <section aria-label="대화 메시지" className="message-list">
      {messages.map((message) => (
        <MessageBubble
          key={message.id}
          role={message.role}
          content={message.content}
        />
      ))}
      <div ref={endRef} aria-hidden="true" />
    </section>
  );
}
