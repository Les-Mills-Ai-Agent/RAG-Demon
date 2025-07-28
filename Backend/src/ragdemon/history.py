from langgraph.graph import MessagesState

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
