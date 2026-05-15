# APPLY ADVANCED MODULES — Agent16 Upgrade Pack

## 1. Module mới được thêm

### Architecture Observer
- Blast Radius Detector: xác định vùng ảnh hưởng khi sửa file.
- Architecture Drift Detector: phát hiện lệch kiến trúc, dependency đi sai chiều.
- Dependency Evolution Graph: tạo bản đồ phụ thuộc và hotspot theo thời gian.

### Creative Intelligence Layer
- Creative Graph: nối người xem → hook → ưu đãi → hình ảnh → kênh phân phối.
- Visual Reasoning: chấm điểm chú ý, tin cậy, rõ ràng, chuyển đổi, khả năng lan truyền.
- Storyboard Memory: sinh bộ cảnh nền để tái sử dụng cho video/poster.
- Campaign Memory: lưu DNA mẫu thắng/thua.

### Economic OS Layer
- Revenue Intelligence: doanh thu, lợi nhuận, hiệu suất chi phí quảng cáo.
- Traffic Intelligence: tỷ lệ người xem → khách tiềm năng → khách mua.
- Funnel Intelligence: tìm điểm nghẽn trong hành trình mua hàng.
- Growth Optimization: đề xuất thử nghiệm tăng trưởng tiếp theo.

### Autonomous Runtime
- Agent Swarm: chia việc cho nhóm tác nhân nghiên cứu/kiến trúc/thực thi/kiểm thử.
- Distributed Execution: mô phỏng chia việc qua nhiều worker.
- GPU Orchestration: lập kế hoạch dùng GPU hoặc fallback CPU.
- Cloud-Native Runtime: healthcheck, autoscale, observability.

## 2. Cách chạy

```bash
python scripts/agent16_architecture_observer.py --changed ai_trading_brain/knowledge_os/runtime.py
python scripts/agent16_creative_runtime.py
python scripts/agent16_growth_runtime.py
python scripts/agent16_autonomous_runtime.py
pytest -q
```

## 3. File runtime sinh ra

- `docs/runtime/architecture-observer-report.json`
- `docs/runtime/creative-intelligence-report.json`
- `docs/runtime/economic-os-report.json`
- `docs/runtime/autonomous-runtime-report.json`

## 4. Luồng nâng cấp mới

```text
USER GOAL
↓
Architecture Observer kiểm tra vùng ảnh hưởng
↓
Creative Intelligence tạo góc nội dung / storyboard nếu là sản phẩm truyền thông
↓
Economic OS đánh giá tác động doanh thu / tăng trưởng
↓
Autonomous Runtime chia việc cho agent swarm
↓
Verification + Governance Gate
↓
Memory Update
```
