from pathlib import Path

from ai_trading_brain.knowledge_os import KnowledgeOSRuntime


def test_knowledge_os_index_and_query(tmp_path: Path):
    root = tmp_path / "project"
    root.mkdir()
    (root / "brief.md").write_text("Agent 16 tối ưu marketing, tài chính và quy trình viết code an toàn.", encoding="utf-8")
    (root / "release.md").write_text("Release gate cần chạy kiểm thử, báo cáo xác minh và kế hoạch rollback.", encoding="utf-8")

    runtime = KnowledgeOSRuntime(tmp_path / "knowledge.sqlite")
    index = runtime.build_index(root)

    assert index["files"] == 2
    assert index["chunks"] >= 2
    assert index["edges"] > 0

    answer = runtime.query("release gate cần gì", limit=3)
    assert answer["hits"]
    assert "Release gate" in answer["answer"] or "release" in answer["answer"].lower()
    assert answer["confidence"] > 0


def test_knowledge_os_memory(tmp_path: Path):
    runtime = KnowledgeOSRuntime(tmp_path / "knowledge.sqlite")
    memory = runtime.remember_winner("Mẫu hook về tiết kiệm chi phí quảng cáo thắng", score=90)
    assert memory["memory_id"] >= 1

    recalled = runtime.recall(kind="winner_pattern")
    assert recalled
    assert "hook" in recalled[0]["content"]
