from __future__ import annotations

class GrowthOptimization:
    def recommend(self, revenue: dict, traffic: dict, funnel: dict) -> dict:
        actions = []
        if revenue.get("roas", 0) < 1.5:
            actions.append("Giảm ngân sách kênh quảng cáo yếu, ưu tiên mẫu quảng cáo có tỷ lệ chuyển đổi tốt hơn.")
        if funnel.get("primary_bottleneck") == "traffic_to_lead":
            actions.append("Tối ưu trang đầu vào: hook rõ hơn, bằng chứng mạnh hơn, lời kêu gọi hành động dễ hiểu hơn.")
        else:
            actions.append("Tối ưu chăm sóc khách hàng tiềm năng: ưu đãi, tin nhắn tư vấn, bằng chứng tin cậy.")
        return {"priority_actions": actions, "next_experiment": "Chạy 3 biến thể hook × 2 biến thể ưu đãi trong 7 ngày."}
