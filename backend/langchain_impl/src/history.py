# backend/langchain_impl/src/history.py

from langgraph.graph import MessagesState
from pathlib import Path
from datetime import datetime
from typing import List
import json
import os

# =========================
# Local JSON history (dev)
# =========================
# These helpers are **dev-only** so you can peek at Q/A pairs locally.
# Production persistence + replay is handled by LangGraph's checkpointer.

def _ensure_parent(path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)

def save_chat(state: MessagesState, CHAT_HISTORY_FILE: str = "chat_data/chat_history.json") -> None:
    """Append the latest human+AI pair into a pretty JSON file (dev only)."""
    _ensure_parent(CHAT_HISTORY_FILE)

    try:
        with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = []
    except FileNotFoundError:
        history = []

    messages = state.get("messages", []) if isinstance(state, dict) else getattr(state, "messages", [])
    user_msg = next((getattr(m, "content", None) for m in reversed(messages) if getattr(m, "type", "") == "human"), None)
    ai_msg   = next((getattr(m, "content", None) for m in reversed(messages) if getattr(m, "type", "") == "ai"), None)

    if user_msg and ai_msg:
        history.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "question": user_msg,
            "response": ai_msg,
        })
        tmp = CHAT_HISTORY_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        os.replace(tmp, CHAT_HISTORY_FILE)

def show_history(CHAT_HISTORY_FILE: str = "chat_data/chat_history.json") -> None:
    """Print the dev chat history file."""
    try:
        with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = []
    except FileNotFoundError:
        history = []

    if not history:
        print("No previous chats found.")
        return

    print("\nChat History:")
    for idx, entry in enumerate(history, start=1):
        print(f"\n#{idx} | {entry['timestamp']}")
        print(f"Q: {entry['question']}")
        print(f"A: {entry['response']}")

def list_chat_summaries(CHAT_HISTORY_FILE: str = "chat_data/chat_history.json") -> None:
    """List entry timestamps only (quick scan)."""
    try:
        with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = []
    except FileNotFoundError:
        history = []

    if not history:
        print("No previous chats found.")
        return

    print("\nChat Summaries:")
    for idx, entry in enumerate(history, start=1):
        print(f"#{idx} | {entry['timestamp']}")

def view_chat_entry(index: int, CHAT_HISTORY_FILE: str = "chat_data/chat_history.json") -> None:
    """View one entry by index (1-based)."""
    try:
        with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = []
    except FileNotFoundError:
        print("No chat history available.")
        return

    if 0 < index <= len(history):
        entry = history[index - 1]
        print(f"\n#{index} | {entry['timestamp']}")
        print(f"Q: {entry['question']}")
        print(f"A: {entry['response']}")
    else:
        print("Invalid index. Please choose a valid chat number.")

def show_history_menu() -> None:
    """Tiny CLI menu for the dev history file."""
    while True:
        print("\n--- Chat History Menu ---")
        print("1. List chat timestamps")
        print("2. View a specific chat")
        print("3. Back")

        choice = input("Choose an option: ").strip()
        if choice == "1":
            list_chat_summaries()
        elif choice == "2":
            idx = input("Enter chat number: ").strip()
            if idx.isdigit():
                view_chat_entry(int(idx))
            else:
                print("Invalid input. Please enter a number.")
        elif choice == "3":
            break
        else:
            print("Invalid option. Try again.")
