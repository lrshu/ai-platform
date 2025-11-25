from __future__ import annotations

from src import orchestration
from src.models import GenerationResult, RetrievalResult


def test_orchestration_smoke(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "src.orchestration.index",
        lambda name, path: type("Idx", (), {"name": name, "chunk_count": 1})(),
    )

    fake_result = RetrievalResult(content="answer", score=1.0, metadata={})
    monkeypatch.setattr("src.orchestration.search", lambda name, question, options=None: [fake_result])
    monkeypatch.setattr(
        "src.orchestration.chat",
        lambda name, question, options=None: GenerationResult(answer="response", citations=[fake_result]),
    )

    idx = orchestration.index("demo", str(tmp_path / "file.pdf"))
    assert idx.name == "demo"

    results = orchestration.search("demo", "question")
    assert results[0].content == "answer"

    answer = orchestration.chat("demo", "question")
    assert answer.answer == "response"
