import React, { useEffect, useRef } from 'react'
import ChatBubble from './ChatBubble.tsx'
import { Message } from '../types/message.ts';

interface ChatWindowProps {
  messages: Message[];
  onRetry: (id: string) => void;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ messages, onRetry }) => {
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex flex-col gap-4 max-w-4xl mx-auto">
      {messages.map((m) => (
        <ChatBubble key={m.id} msg={m} onRetry={() => onRetry(m.id)} />
      ))}
      <div ref={bottomRef} />
    </div>
  );
};

export default ChatWindow;