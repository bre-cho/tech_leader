# Hardcode Operating Law

Không cho phép agent chạy trực tiếp. Không cho phép feature mới bỏ qua verify/memory.

## Required lifecycle

- target_define
- research
- plan
- execute
- verify
- distill_to_skill
- memory_update
- winner_dna_update

Nếu thiếu bất kỳ bước nào: `PROMOTION_GATE = BLOCKED`.

## Required module contract cho feature mới

Mỗi feature mới phải có:

- workflow definition
- agent contract
- runtime execution path
- verification checks
- memory hooks
- winner DNA compatibility
- docs
- tests
