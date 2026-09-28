import { useEffect, useState } from "react";
import "./App.css";
import { ChatPanel } from "./components/ChatPanel";
import { ConversationSidebar } from "./components/ConversationSidebar";
import type { Conversation, Message } from "./types/chat";
import {
  createConversation,
  deleteConversation,
  listConversations,
} from "./api/conversations";
import { listMessages, streamMessage } from "./api/messages";

function App() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const selectedConversation = conversations.find((item) => item.id === selectedId);

  useEffect(() => {
    let active = true;
    listConversations()
      .then((summaries) => {
        if (!active) return;
        const loaded = summaries.map((summary) => ({ ...summary, messages: [] }));
        setConversations(loaded);
        setSelectedId(loaded[0]?.id ?? null);
      })
      .catch(() => {
        if (active) setError("대화 목록을 불러오지 못했습니다. 새로고침해 주세요.");
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    if (selectedId === null) return;
    const conversationId = selectedId;
    let active = true;
    listMessages(conversationId)
      .then((messages) => {
        if (!active) return;
        setConversations((current) =>
          current.map((item) =>
            item.id === conversationId ? { ...item, messages } : item,
          ),
        );
      })
      .catch(() => {
        if (active) setError("메시지를 불러오지 못했습니다. 다시 선택해 주세요.");
      });
    return () => {
      active = false;
    };
  }, [selectedId]);

  function updateMessages(conversationId: number, messages: Message[]) {
    setConversations((current) =>
      current.map((item) =>
        item.id === conversationId ? { ...item, messages } : item,
      ),
    );
  }

  function appendToken(conversationId: number, messageId: string, token: string) {
    setConversations((current) =>
      current.map((item) =>
        item.id === conversationId
          ? {
              ...item,
              messages: item.messages.map((message) =>
                message.id === messageId
                  ? { ...message, content: message.content + token }
                  : message,
              ),
            }
          : item,
      ),
    );
  }

  async function handleSend(content: string) {
    if (selectedId === null) return;
    const conversationId = selectedId;
    const pendingId = `pending-${crypto.randomUUID()}`;

    setConversations((current) =>
      current.map((item) =>
        item.id === conversationId
          ? {
              ...item,
              messages: [
                ...item.messages,
                { id: `user-${pendingId}`, role: "user", content, status: "pending" },
                { id: pendingId, role: "assistant", content: "", status: "pending" },
              ],
            }
          : item,
      ),
    );

    try {
      await streamMessage(conversationId, content, (event) => {
        if (event.type === "token") appendToken(conversationId, pendingId, event.content);
      });
    } catch (cause) {
      try {
        updateMessages(conversationId, await listMessages(conversationId));
      } catch {
        setConversations((current) =>
          current.map((item) =>
            item.id === conversationId
              ? { ...item, messages: item.messages.filter((message) => message.status !== "pending") }
              : item,
          ),
        );
        setError("대화 기록을 다시 불러오지 못했습니다. 새로고침해 주세요.");
      }
      throw cause;
    }

    try {
      updateMessages(conversationId, await listMessages(conversationId));
    } catch {
      setError("답변은 저장됐지만 대화 기록을 새로 고치지 못했습니다.");
    }
  }

  async function handleCreate() {
    const title = window.prompt("대화 제목", "FastAPI 질문")?.trim();
    if (!title) return;
    try {
      const created = await createConversation(title);
      setConversations((current) => [{ ...created, messages: [] }, ...current]);
      setSelectedId(created.id);
      setError(null);
    } catch {
      setError("대화를 만들지 못했습니다. 제목을 확인하고 다시 시도해 주세요.");
    }
  }

  async function handleDelete(conversationId: number) {
    try {
      await deleteConversation(conversationId);
      setConversations((current) => current.filter((item) => item.id !== conversationId));
      setSelectedId((current) =>
        current === conversationId
          ? (conversations.find((item) => item.id !== conversationId)?.id ?? null)
          : current,
      );
      setError(null);
    } catch {
      setError("대화를 삭제하지 못했습니다. 다시 시도해 주세요.");
    }
  }

  return (
    <main className="layout">
      <ConversationSidebar
        conversations={conversations}
        selectedId={selectedId}
        onSelect={setSelectedId}
        onCreate={handleCreate}
        onDelete={handleDelete}
      />
      <div className="content-area">
        {error && <p className="global-error" role="alert">{error}</p>}
        {loading ? (
          <p className="empty-state">대화 목록을 불러오는 중입니다.</p>
        ) : (
          <ChatPanel conversation={selectedConversation} onsend={handleSend} />
        )}
      </div>
    </main>
  );
}

export default App;
