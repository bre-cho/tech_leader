# Agent Operating Model

## Technical Lead Agent
Vai trò điều phối trung tâm. Không tự làm hết. Nhiệm vụ là chia việc, kiểm tra output, chặn lỗi schema, chặn flow rời rạc, kích hoạt audit và release gate.

## Agent Contracts
Mỗi agent phải tuân thủ contract:
- `agent_name`
- `input_schema`
- `output_schema`
- `decision_reason`
- `confidence_score`
- `trace_id`
- `project_id`
- `lineage.parent_step_id`
- `lineage.output_artifact_id`

## 16 Agent trong hệ
1. Planning Agent: dựng luồng tổng thể trước code.
2. Business Diagnosis Agent: hiểu ngành, sản phẩm, mục tiêu.
3. Image Design Agent: tạo concept/prompt/headline/CTA.
4. Image QA Agent: chấm Attention/Trust/Conversion/Brand Fit/Upsell Potential.
5. Industry Adaptation Agent: chỉnh logic theo ngành.
6. Upsell Opportunity Agent: tìm lý do bán thêm video.
7. Video Concept Agent: biến ảnh thành concept video.
8. Storyboard Agent: tách cảnh cho Veo/Runway/Kling/Seedance.
9. Offer Agent: tạo gói dễ mua.
10. CRM Follow-up Agent: tạo chuỗi follow-up.
11. Analytics Agent: đo conversion và insight ngành.
12. Workflow Agent: đóng gói workflow MVP hoàn chỉnh.
13. Frontend Agent: build `/design-studio`.
14. Backend API Agent: build endpoint.
15. Database/Memory Agent: schema + winner DNA.
16. Tech Lead Audit Agent: scan, validate, release gate.
