// frontend/src/components/MessageBubble.tsx
type MessageProps = {
  role: "user" | "assistant";
  content: string;
};

export function MessageBubble({ role, content }: MessageProps) {
  return (
    <article className={`message ${role}`}>
      <strong>{role === "user" ? "나" : "AI"}</strong>
      <p>{content}</p>
    </article>
  );
}
