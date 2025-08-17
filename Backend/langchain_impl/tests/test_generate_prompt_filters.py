import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[4]))

import importlib
import pytest
from langchain_core.messages import SystemMessage

MODULE_PATH = "langchain_impl.src.app"


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


@pytest.fixture
def mod(monkeypatch):
    appmod = importlib.import_module(MODULE_PATH)
    monkeypatch.setattr(appmod, "llm", RecordingLLM(), raising=True)
    return appmod


def _state_with_messages():
    # Two tool messages (appear most-recent-first in real run; generate reverses)
    tool1 = type("T", (), {"type": "tool", "content": "SNIPPET-1"})
    tool2 = type("T", (), {"type": "tool", "content": "SNIPPET-2"})
    # Mixed conversation
    sysm = type("M", (), {"type": "system", "content": "prior system"})
    ai_with_tool = type("M", (), {"type": "ai", "content": "ai toolcall", "tool_calls": [{"id": "x"}]})
    ai_no_tool = type("M", (), {"type": "ai", "content": "plain ai", "tool_calls": None})
    human = type("M", (), {"type": "human", "content": "user asks something"})

    # generate() walks messages reversed to gather tool messages, then filters the rest.
    return {"messages": [tool1, tool2, sysm, ai_with_tool, ai_no_tool, human]}


def test_generate_builds_policy_system_message_and_filters(mod):
    state = _state_with_messages()
    result = mod.generate(state)

    # LLM got a prompt
    prompt = mod.llm.last_prompt
    assert prompt is not None and len(prompt) >= 2

    # First item is SystemMessage with our guardrails
    assert isinstance(prompt[0], SystemMessage)
    text = prompt[0].content
    assert "You are the Les Mills B2B Assistant." in text
    assert "SCOPE" in text and "GUARDRAILS" in text and "REFUSALS" in text
    assert "CONTEXT (verbatim, may be long)" in text  # don’t assert doc injection to keep this robust

    # After the SystemMessage, only system, ai(no tool_calls), human should remain in order
    body = prompt[1:]
    types = [getattr(m, "type", None) for m in body]
    assert types == ["system", "ai", "human"]

    # generate returns a dict with an AI message
    assert isinstance(result, dict) and "messages" in result
    assert result["messages"] and result["messages"][-1].type == "ai"
