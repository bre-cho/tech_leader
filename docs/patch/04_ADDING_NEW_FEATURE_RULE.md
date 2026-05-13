# Rule khi bổ sung tính năng mới

Tính năng mới không được merge nếu chỉ là feature đơn lẻ.

Dev phải tạo đủ:

```text
/workflow
/agent
/skill
/runtime
/verification
/memory
/winner-dna
/docs
/tests
```

## Checklist PR

- [ ] Có workflow rõ ràng
- [ ] Có agent contract
- [ ] Có route qua Technical Lead Orchestrator
- [ ] Có verification checks
- [ ] Có promotion gate
- [ ] Policy promotion rõ ràng: `DRY_RUN -> NO PROMOTION` (status riêng, không promotable)
- [ ] Có memory update
- [ ] Có Winner DNA logic nếu output đạt threshold
- [ ] Có context graph entity/relation
- [ ] Có tests
