from langgraph.graph import MessagesState
import os, time, json  # you already import json; keeping here for clarity
from typing import List, Dict

import json
from datetime import datetime

def save_chat(state: MessagesState, CHAT_HISTORY_FILE: str = "chat_data/chat_history.json"):
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

def show_history(CHAT_HISTORY_FILE: str = "chat_data/chat_history.json"):
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


def list_chat_summaries(CHAT_HISTORY_FILE: str = "chat_data/chat_history.json"):
    """List all past chat entries with timestamps and index only (for CLI selection)."""
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

    print("\nChat Summaries:")
    for idx, entry in enumerate(history, start=1):
        print(f"#{idx} | {entry['timestamp']}")

def view_chat_entry(index: int, CHAT_HISTORY_FILE: str = "chat_data/chat_history.json"):
    """View full details of a selected chat entry by index."""
    try:
        with open(CHAT_HISTORY_FILE, "r") as f:
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

def show_history_menu():
    """Simple CLI menu to interact with chat history."""
    while True:
        print("\n--- Chat History Menu ---")
        print("1. List chat timestamps")
        print("2. View a specific chat")
        print("3. Back")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            list_chat_summaries()
        elif choice == "2":
            index = input("Enter chat number: ").strip()
            if index.isdigit():
                view_chat_entry(int(index))
            else:
                print("Invalid input. Please enter a number.")
        elif choice == "3":
            break
        else:
            print("Invalid option. Try again.")

# ----- Stateless session helpers (DynamoDB with local fallback) -----

SESSIONS_TABLE = os.getenv("SESSIONS_TABLE")  # e.g., "lmai-sessions"

def _sessions_tbl():
    import boto3
    return boto3.resource("dynamodb").Table(SESSIONS_TABLE)

def append_message(session_id: str, role: str, content: str) -> None:
    """
    Persist a single turn.
    - If SESSIONS_TABLE is set: write to DynamoDB (PK=session_id, SK=ts).
    - Else (local dev): append to a JSONL file namespaced by session_id.
    """
    if SESSIONS_TABLE:
        _sessions_tbl().put_item(Item={
            "session_id": session_id,
            "ts": int(time.time() * 1000),
            "role": role,           # "user" | "assistant" | "system"
            "content": content
        })
        return

    # Local fallback (per-session)
    os.makedirs("chat_data", exist_ok=True)
    sidecar = "chat_data/dev_messages.jsonl"
    with open(sidecar, "a", encoding="utf-8") as f:
        f.write(json.dumps({"session_id": session_id, "role": role, "content": content}) + "\n")

def load_history(session_id: str, limit: int = 14) -> List[Dict]:
    """
    Return oldest→newest list of {role, content} for a session.
    Uses DynamoDB if configured; otherwise reads local JSONL fallback.
    """
    if SESSIONS_TABLE:
        from boto3.dynamodb.conditions import Key
        resp = _sessions_tbl().query(
            KeyConditionExpression=Key("session_id").eq(session_id),
            ScanIndexForward=True,
            Limit=limit,
        )
        items = resp.get("Items", [])
        return [{"role": it["role"], "content": it["content"]} for it in items]

    # Local fallback
    try:
        with open("chat_data/dev_messages.jsonl", "r", encoding="utf-8") as f:
            lines = [json.loads(x) for x in f]
    except FileNotFoundError:
        return []

    msgs = [m for m in lines if m.get("session_id") == session_id]
    return [{"role": m["role"], "content": m["content"]} for m in msgs][-limit:]

