import re
import pytest
from langchain_core.messages import SystemMessage
from langchain_impl.app import generate

from langgraph.graph import MessagesState
from langchain_core.messages import ToolMessage, SystemMessage, AIMessage, HumanMessage


class AIMsg:
    def __init__(self, content):
        self.type = "ai"
        self.content = content
        self.tool_calls = None


class RecordingLLM:
    def __init__(self):
        self.last_prompt = None

    def invoke(self, prompt):
        self.last_prompt = prompt
        # Return something that looks like an AI message
        return AIMsg("ok")  # content doesn't matter here


def _state_with_messages():
    # Two tool messages (appear most-recent-first in real run; generate reverses)

    tool1 = ToolMessage("SNIPPET-1")
    tool2 = ToolMessage("SNIPPET-2")
    # Mixed conversation
    sys1 = SystemMessage("prior system")
    ai_with_tool = AIMessage("ai toolcall", tool_calls=[{"id": "x"}])
    ai_no_tool = AIMessage("plain ai")
    human = HumanMessage("human asks something")

    # generate() walks messages reversed to gather tool messages, then filters the rest.
    return MessagesState({"messages": [tool1, tool2, sys1, ai_with_tool, ai_no_tool, human]})


def test_generate_builds_policy_system_message_and_filters(mod):
    state = _state_with_messages()
    result = generate(state)

    # LLM got a prompt
    prompt = mod.llm.last_prompt
    assert prompt is not None and len(prompt) >= 2

    # First item is SystemMessage with our guardrails
    assert isinstance(prompt[0], SystemMessage)
    text = prompt[0].content
    assert "You are the Les Mills B2B Assistant." in text
    assert "SCOPE" in text and "GUARDRAILS" in text and "REFUSALS" in text

    # Accept either "CONTEXT (verbatim, may be long):" or "CONTEXT (verbatim):"
    assert re.search(r"CONTEXT \(verbatim(?:, may be long)?\):", text)

    # After the SystemMessage, only system, ai(no tool_calls), human should remain in order
    body = prompt[1:]
    types = [getattr(m, "type", None) for m in body]
    assert types == ["system", "ai", "human"]

    # generate returns a dict with an AI message
    assert isinstance(result, dict) and "messages" in result
    assert result["messages"] and result["messages"][-1].type == "ai"
