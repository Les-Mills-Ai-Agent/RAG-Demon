from langgraph.graph import MessagesState

import json
from datetime import datetime

def save_chat(state: MessagesState, CHAT_HISTORY_FILE: str = "chat_history.json"):
    """Save the latest user and AI message from LangGraph state to a JSON file."""
    try:
        with open(CHAT_HISTORY_FILE, "r") as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = []
    except FileNotFoundError:
        history = []

    # Extract latest human question and AI response from state["messages"]
    messages = state.get("messages", [])
    user_msg = next((m.content for m in reversed(messages) if m.type == "human"), None)
    ai_msg = next((m.content for m in reversed(messages) if m.type == "ai"), None)

    if user_msg and ai_msg:
        history.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "question": user_msg,
            "response": ai_msg
        })

        with open(CHAT_HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=2)

def show_history(CHAT_HISTORY_FILE: str = "chat_history.json"):
    """Display chat history from the JSON file in the terminal."""
    try:
        with open(CHAT_HISTORY_FILE, "r") as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = []
    except FileNotFoundError:
        print("No previous chats found.")
        return

    if not history:
        print("No previous chats found.")
        return

    print("\nChat History:")
    for idx, entry in enumerate(history, start=1):
        print(f"\n#{idx} | {entry['timestamp']}")
        print(f"Q: {entry['question']}")
        print(f"A: {entry['response']}")
