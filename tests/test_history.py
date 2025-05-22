from langgraph.graph import MessagesState

import json

from ragdemon.history import save_chat, show_history

def test_save_chat():
    # Test data
    state = MessagesState(
        question="What is the capital of France?",
        response="The capital of France is Paris."
    )

    CHAT_HISTORY_FILE = "test_chat_history.json"

    # Call the function to save chat
    save_chat(state, CHAT_HISTORY_FILE)

    # Verify that the chat history file was created and contains the expected data
    with open(CHAT_HISTORY_FILE, "r") as f:
        history = json.load(f)
        assert len(history) == 1
        assert history[0]["question"] == state["question"]
        assert history[0]["response"] == state["response"]

    # Clean up test file
    import os
    os.remove(CHAT_HISTORY_FILE)

def test_show_history():
    # Test data
    CHAT_HISTORY_FILE = "test_chat_history.json"

    # Create a test chat history file
    with open(CHAT_HISTORY_FILE, "w") as f:
        json.dump([{
            "timestamp": "2023-10-01 12:00:00",
            "question": "What is the capital of France?",
            "response": "The capital of France is Paris."
        }], f, indent=2)

    # Capture the output of the show_history function
    from io import StringIO
    import sys

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
    import os
    os.remove(CHAT_HISTORY_FILE)