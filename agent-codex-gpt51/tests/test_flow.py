import pytest

from src import OnboardingApp


def test_default_flow_completes_all_checklist():
    app = OnboardingApp()
    state = app.run()

    assert all(item.status == "done" for item in state.checklist)
    assert state.pending_action is None
    assert any(
        "入职主管总结" in message.content for message in state.messages if hasattr(message, "content")
    )


def test_role_specific_access():
    app = OnboardingApp()
    state = app.run(employee_profile={"education": {"position": "IT"}})

    assert "git" in state.tool_outputs
    assert state.tool_outputs["git"]["account"].startswith("git_it")
    assert state.tool_outputs["git"]["status"] == "enabled"


def test_question_answered():
    app = OnboardingApp()
    question = "请再提醒后续任务有哪些？"
    state = app.run(question=question)

    assert any("后续任务" in msg.content for msg in state.messages)
