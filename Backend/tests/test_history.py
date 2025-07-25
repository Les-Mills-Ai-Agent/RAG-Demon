from langgraph.graph import MessagesState
from langchain_core.messages import HumanMessage, AIMessage
import json
import os
from io import StringIO
import sys

from ragdemon.history import save_chat, show_history


def test_save_chat():
    # Create a proper MessagesState with human and AI messages
    state = MessagesState(
        messages=[
            HumanMessage(content="What is the capital of France?"),
            AIMessage(content="The capital of France is Paris.")
        ]
    )

    CHAT_HISTORY_FILE = "test_chat_history.json"

    # Call the function to save chat
    save_chat(state, CHAT_HISTORY_FILE)

    # Verify that the chat history file was created and contains the expected data
    assert os.path.exists(CHAT_HISTORY_FILE)

    with open(CHAT_HISTORY_FILE, "r") as f:
        history = json.load(f)
        assert len(history) == 1
        assert history[0]["question"] == "What is the capital of France?"
        assert history[0]["response"] == "The capital of France is Paris."

    # Clean up test file
    os.remove(CHAT_HISTORY_FILE)


def test_show_history():
    CHAT_HISTORY_FILE = "test_chat_history.json"

    # Create a test chat history file
    with open(CHAT_HISTORY_FILE, "w") as f:
        json.dump([{
            "timestamp": "2023-10-01 12:00:00",
            "question": "What is the capital of France?",
            "response": "The capital of France is Paris."
        }], f, indent=2)

    # Capture the output of the show_history function
    captured_output = StringIO()
    sys.stdout = captured_output

    show_history(CHAT_HISTORY_FILE)

    # Reset stdout
    sys.stdout = sys.__stdout__

    # Verify the output
    output = captured_output.getvalue().strip()
    assert "#1 | 2023-10-01 12:00:00" in output
    assert "Q: What is the capital of France?" in output
    assert "A: The capital of France is Paris." in output

    # Clean up test file
    os.remove(CHAT_HISTORY_FILE)
