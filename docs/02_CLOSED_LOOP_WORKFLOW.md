# Closed-loop MVP Workflow

## Workflow người dùng
1. Khách nhập ngành + sản phẩm + mục tiêu.
2. AI tạo 3 concept ảnh.
3. AI chấm điểm từng ảnh.
4. Khách chọn ảnh ưng ý.
5. AI phân tích ảnh có thể dựng video gì.
6. Popup upsell: “Bạn có muốn biến thiết kế này thành video quảng cáo 15 giây không?”
7. AI tạo video concept + storyboard preview.
8. Khách chọn gói video.
9. Hệ thống tạo project video.
10. AI lưu winner DNA vào memory.

## Workflow hệ thống
`design_project.created` → `business.diagnosed` → `industry.adapted` → `image.concepts.generated` → `image.scored` → `image.selected` → `upsell.analyzed` → `video.concept.generated` → `storyboard.generated` → `offer.recommended` → `crm.followup.scheduled` → `analytics.updated` → `winner_dna.saved`.

## Rule bắt buộc
- Không có `project_id` → không chạy agent.
- Không có `trace_id` → output bị reject.
- Score < 70 → không upsell mạnh, chỉ gợi ý cải thiện ảnh.
- `upsell_video_potential_score >= 80` → `VIDEO_UPSELL_READY = true`.
- Có purchase/conversion → lưu Winner DNA.
