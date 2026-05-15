from __future__ import annotations

from .models import AnswerContext
from .search import HybridSearchEngine


class KnowledgeAssistant:
    def __init__(self, search: HybridSearchEngine) -> None:
        self.search_engine = search

    def answer(self, query: str, limit: int = 5) -> AnswerContext:
        hits = self.search_engine.search(query, limit=limit)
        if not hits:
            return AnswerContext(query=query, answer="Chưa tìm thấy dữ liệu liên quan trong kho tri thức nội bộ.", hits=[], citations=[], confidence=0.0)

        citations = [f"{hit.title}#{hit.position if hasattr(hit, 'position') else hit.chunk_id.split(':')[-1]}" for hit in hits]
        evidence_lines = []
        for i, hit in enumerate(hits, start=1):
            snippet = hit.text[:420].replace("\n", " ")
            evidence_lines.append(f"{i}. {snippet}")
        confidence = min(0.98, max(0.15, sum(hit.score for hit in hits[:3]) / 6.0))
        answer = (
            "Dựa trên kho tri thức nội bộ, các điểm liên quan nhất là:\n"
            + "\n".join(evidence_lines)
            + "\n\nKết luận vận hành: dùng các bằng chứng trên để cập nhật kế hoạch, tạo patch hoặc trả lời người dùng; nếu confidence thấp thì cần bổ sung tài liệu nguồn."
        )
        return AnswerContext(query=query, answer=answer, hits=hits, citations=citations, confidence=round(confidence, 3))
