# Frontend `/design-studio`

## Màn hình
1. Form nhập ngành / sản phẩm / mục tiêu.
2. Generate Image Concepts.
3. Image Gallery.
4. AI Score Panel.
5. Upsell Video Recommendation.
6. Video Storyboard Preview.
7. Select Video Package.
8. Checkout / Create Video Project.

## State chính
- `input`
- `project`
- `imageVariants`
- `scores`
- `selectedImage`
- `upsellRecommendation`
- `videoConcept`
- `storyboard`
- `offer`
- `winnerDNAStatus`

## UX rule
- Hiển thị score ngay dưới từng ảnh.
- Ảnh có `VIDEO_UPSELL_READY` phải có badge “Có thể biến thành video”.
- Popup upsell chỉ xuất hiện sau khi khách chọn ảnh.
