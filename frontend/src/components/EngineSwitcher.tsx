import React from "react";

type Props = {
  value: "openai" | "bedrock";
  onChange: (v: "openai" | "bedrock") => void;
  className?: string;
};

export default function EngineSwitcher({ value, onChange, className }: Props) {
  return (
    <div className={`flex items-center gap-2 ${className ?? ""}`}>
      <label className="text-sm text-gray-600 dark:text-gray-300">Engine</label>
      <select
        className="border rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 dark:border-gray-600 outline-none focus:ring w-44"
        value={value}
        onChange={(e) => onChange(e.target.value as "openai" | "bedrock")}
      >
        <option value="openai">OpenAI</option>
        <option value="bedrock">AWS Bedrock</option>
      </select>
    </div>
  );
}
