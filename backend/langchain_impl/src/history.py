from langgraph.graph import MessagesState
from typing import List, Dict, Optional, Tuple
from functools import lru_cache
from pathlib import Path
from datetime import datetime
import os
import time
import json

# =========================
# Local JSON history (dev)
# =========================

def _ensure_parent(path: str) -> None:
    """Ensure the parent directory for a file path exists."""
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

    # state may be a dict-like or an object; handle both
    messages = state.get("messages", []) if isinstance(state, dict) else getattr(state, "messages", [])
    user_msg = next((getattr(m, "content", None) for m in reversed(messages) if getattr(m, "type", "") == "human"), None)
    ai_msg   = next((getattr(m, "content", None) for m in reversed(messages) if getattr(m, "type", "") == "ai"), None)

    if user_msg and ai_msg:
        history.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "question": user_msg,
            "response": ai_msg,
        })
        # Atomic write to prevent corruption
        tmp = CHAT_HISTORY_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        os.replace(tmp, CHAT_HISTORY_FILE)

def show_history(CHAT_HISTORY_FILE: str = "chat_data/chat_history.json") -> None:
    """Display chat history from the JSON file in the terminal (dev only)."""
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
    """List chat entries with timestamps and index only (for CLI selection)."""
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
    """View full details of a selected chat entry by index (1-based)."""
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
    """Simple CLI menu to interact with dev chat history."""
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

# ======================================
# DynamoDB-backed stateless session log
# ======================================

SESSIONS_TABLE = os.getenv("SESSIONS_TABLE")  # e.g., "lmai-sessions"
AWS_REGION     = os.getenv("AWS_REGION")      # optional; default chain if unset

@lru_cache(maxsize=1)
def _sessions_tbl():
    """Cache the DynamoDB Table handle across warm Lambda invocations."""
    if not SESSIONS_TABLE:
        return None
    import boto3
    res = boto3.resource("dynamodb", region_name=AWS_REGION)
    return res.Table(SESSIONS_TABLE)

def append_message(session_id: str, role: str, content: str) -> None:
    """
    Persist a single message.
    - If SESSIONS_TABLE is set: write to DynamoDB (PK=session_id, SK=ts).
    - Else (local dev): append to a JSONL file in ./chat_data.
    """
    tbl = _sessions_tbl()
    if tbl is not None:
        tbl.put_item(Item={
            "session_id": session_id,       # PK (S)
            "ts": int(time.time() * 1000),  # SK (N) - ms precision
            "role": role,                   # "user" | "assistant" | "system"
            "content": content,
        })
        return

    # Local fallback
    Path("chat_data").mkdir(parents=True, exist_ok=True)
    sidecar = "chat_data/dev_messages.jsonl"
    with open(sidecar, "a", encoding="utf-8") as f:
        f.write(json.dumps(
            {"session_id": session_id, "role": role, "content": content},
            ensure_ascii=False
        ) + "\n")

def load_history(session_id: str, limit: int = 14, last_evaluated_key: Optional[Dict] = None
                 ) -> Tuple[List[Dict], Optional[Dict]]:
    """
    Return oldest→newest list of {role, content} for a session.

    Returns:
        (messages, last_evaluated_key)
        - messages: List[{"role": str, "content": str}]
        - last_evaluated_key: Dict or None (for DynamoDB pagination)
    """
    tbl = _sessions_tbl()
    if tbl is not None:
        from boto3.dynamodb.conditions import Key
        kwargs = {
            "KeyConditionExpression": Key("session_id").eq(session_id),
            "ScanIndexForward": True,  # oldest → newest
            "Limit": limit,
        }
        if last_evaluated_key:
            kwargs["ExclusiveStartKey"] = last_evaluated_key

        resp = tbl.query(**kwargs)
        items = resp.get("Items", [])
        msgs = [{"role": it["role"], "content": it["content"]} for it in items]
        return msgs, resp.get("LastEvaluatedKey")

    # Local fallback
    try:
        with open("chat_data/dev_messages.jsonl", "r", encoding="utf-8") as f:
            lines = [json.loads(x) for x in f]
    except FileNotFoundError:
        return [], None

    msgs = [m for m in lines if m.get("session_id") == session_id]
    msgs = msgs[-limit:]
    return [{"role": m["role"], "content": m["content"]} for m in msgs], None
