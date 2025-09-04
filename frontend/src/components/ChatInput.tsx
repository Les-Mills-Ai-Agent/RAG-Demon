import React, { useState } from "react";
import { Message, newUserMessage, UserMessage } from "../models/models";

interface ChatInputProps {
  onSubmit: (query: Message) => void;
  disabled: boolean;
}

const ChatInput: React.FC<ChatInputProps> = ({ onSubmit, disabled }) => {
  const [input, setInput] = useState<string>("");
  const [error, setError] = useState<boolean>(false);

  const submit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    const trimmed = input.trim();
    if (!trimmed) {
      setError(true);
      return;
    }

    const message: UserMessage = newUserMessage(trimmed);

    onSubmit(message);
    setInput("");
    setError(false);
  };

  return (
    <>
      <form
        onSubmit={submit}
        className={`w-full max-w-3xl mx-auto flex items-center gap-3 bg-white border ${
          error ? "border-red-500" : "border-gray-300"
        } rounded-full px-4 py-2 shadow transition-all duration-200`}
      >
        <input
          type="text"
          className="flex-1 text-sm text-gray-800 placeholder-gray-400 bg-transparent focus:outline-none"
          placeholder="Ask anything..."
          value={input}
          onChange={(e) => {
            setInput(e.target.value);
            if (error) setError(false);
          }}
        />
        <button
          type="submit"
          className={`text-sm font-semibold px-4 py-2 rounded-full transition
    ${
      disabled
        ? "text-gray-500 bg-gray-300 cursor-not-allowed"
        : "text-white bg-blue-500 hover:bg-blue-600 cursor-pointer"
    }`}
          disabled={disabled}
        >
          ➤
        </button>
      </form>
      {error && (
        <p className="text-sm text-red-500 text-center mt-1">
          Please enter a valid message.
        </p>
      )}
    </>
  );
};

export default ChatInput;
