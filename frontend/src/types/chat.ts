export type Message = {
  id: number | string;
  role: "user" | "assistant";
  content: string;
  status?: "pending";
};

export type ConversationSummary = {
  id: number;
  title: string;
};

export type Conversation = ConversationSummary & {
  messages: Message[];
};
export type StreamEvent =
  | { type: "token"; content: string }
  | { type: "done"; message_id: number }
  | { type: "error"; code: string };
