// frontend/src/components/ConversationSidebar.tsx
import { useEffect, useState } from "react";
import type { ConversationSummary } from "../types/chat";

type SidebarProps = {
  conversations: ConversationSummary[];
  selectedId: number | null;
  onSelect: (conversationId: number) => void;
  onCreate?: () => void;
  onDelete?: (conversationId: number) => void;
};

export function ConversationSidebar(props: SidebarProps) {
  return (
    <aside className="sidebar">
      <h1 className="sidebar-title">AI Native Chat</h1>
      {props.onCreate && <button onClick={props.onCreate}>+ 새 대화</button>}
      <ConversationList {...props} />
    </aside>
  );
}

type ContextMenuState = {
  conversationId: number;
  title: string;
  x: number;
  y: number;
};

function ConversationList({
  conversations,
  selectedId,
  onSelect,
  onDelete,
}: SidebarProps) {
  const [contextMenu, setContextMenu] = useState<ContextMenuState | null>(null);

  useEffect(() => {
    if (!contextMenu) return;
    const close = () => setContextMenu(null);
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") close();
    };
    window.addEventListener("click", close);
    window.addEventListener("scroll", close, true);
    window.addEventListener("keydown", closeOnEscape);
    return () => {
      window.removeEventListener("click", close);
      window.removeEventListener("scroll", close, true);
      window.removeEventListener("keydown", closeOnEscape);
    };
  }, [contextMenu]);

  return (
    <nav aria-label="대화 목록">
      {conversations.map((conversation) => (
        <div
          key={conversation.id}
          className="conversation-item"
          onContextMenu={(event) => {
            if (!onDelete) return;
            event.preventDefault();
            setContextMenu({
              conversationId: conversation.id,
              title: conversation.title,
              x: event.clientX,
              y: event.clientY,
            });
          }}
        >
          <button
            aria-current={conversation.id === selectedId}
            onClick={() => onSelect(conversation.id)}
          >
            {conversation.title}
          </button>
        </div>
      ))}

      {contextMenu && onDelete && (
        <div
          className="context-menu"
          style={{ left: contextMenu.x, top: contextMenu.y }}
          role="menu"
        >
          <button
            type="button"
            role="menuitem"
            className="context-menu-delete"
            onClick={() => {
              if (window.confirm(`"${contextMenu.title}" 대화를 삭제할까요?`)) {
                onDelete(contextMenu.conversationId);
              }
              setContextMenu(null);
            }}
          >
            대화 삭제
          </button>
        </div>
      )}
    </nav>
  );
}
