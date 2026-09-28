// frontend/src/components/MessageForm.tsx
import { type FormEvent, type KeyboardEvent, useState } from "react";
import { ReplyFailedError } from "../api/messages";

type SubmitStatus = "idle" | "submitting" | "error";

type MessageFormProps = {
  onSend: (message: string) => Promise<void>;
};

export function MessageForm({ onSend }: MessageFormProps) {
  const [input, setInput] = useState("");
  const [status, setStatus] = useState<SubmitStatus>("idle");
  const [error, setError] = useState<string | null>(null);

  const isSubmitting = status === "submitting";
  const canSubmit = input.trim().length > 0 && !isSubmitting;

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const message = input.trim();
    if (!message || isSubmitting) return;

    try {
      setStatus("submitting");
      setError(null);
      await onSend(message);
      setInput("");
      setStatus("idle");
    } catch (cause) {
      if (cause instanceof ReplyFailedError) setInput("");
      setError(
        cause instanceof ReplyFailedError
          ? cause.message
          : "메시지를 전송하지 못했습니다. 대화 기록을 확인한 뒤 다시 시도해 주세요.",
      );
      setStatus("error");
    }
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      event.currentTarget.form?.requestSubmit();
    }
  }

  return (
    <form className="message-form" onSubmit={handleSubmit}>
      <textarea
        value={input}
        maxLength={2000}
        onChange={(event) => setInput(event.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="메시지를 입력하세요"
        aria-label="메시지 입력"
        disabled={isSubmitting}
      />
      <button type="submit" disabled={!canSubmit}>
        {status === "error" ? "다시 전송" : isSubmitting ? "응답 생성 중" : "전송"}
      </button>
      {status === "submitting" && (
        <p role="status" aria-live="polite">AI 응답 생성 중</p>
      )}
      {error && <p role="alert">{error}</p>}
    </form>
  );
}

