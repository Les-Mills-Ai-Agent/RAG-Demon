from langgraph.graph import MessagesState

import json
from datetime import datetime

def save_chat(state: MessagesState, CHAT_HISTORY_FILE: str = "chat_history.json"):
    # Attempt to open the existing chat history file in read mode
    try:
        with open(CHAT_HISTORY_FILE, "r") as f:
            #load the existing chat history from the JSON file
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                # If the file is empty or not valid JSON, initialize an empty history list
                history = []
    except FileNotFoundError:
        #if the file doenst exist yet, initalise and empty history list as shown.
        history = []

    # Append the new chat entry to the history with questions timestamps and responses from the Ai model.
    history.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "question": state["question"],
        "response": state["response"]
    })

    #Write the updated History back to the file in JSON Format, with indentations to make sure it is neat.
    with open(CHAT_HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def show_history(CHAT_HISTORY_FILE: str = "chat_history.json"):
    try:
        with open(CHAT_HISTORY_FILE, "r") as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                # If the file is empty or not valid JSON, initialize an empty history list
                history = []
    except FileNotFoundError:
        print("No previous chats found.")
        return

    if not history:
        print("No previous chats found.")
        return

    for idx, entry in enumerate(history, start=1):
        print(f"\n#{idx} | {entry['timestamp']}")
        print(f"Q: {entry['question']}")
        print(f"A: {entry['response']}")