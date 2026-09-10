# 冷却监控验证草案

12 题：9 可回答、3 不可回答；1 份 XLSX、8 个原文单元。文档族为 synthetic-cooling-family，与当前开发集没有相同文档 ID、文件内容哈希或泄漏组。

这是独立文档族的合成验证草案，不是独立真人编写的业务测试，也不是盲测保留集；可用于开发期选择配置。人工标签和近重复审查均待完成，不能据此宣称真实业务效果。

阅读 [cases.md](cases.md)，执行 [cases.jsonl](cases.jsonl)。仅摄入 corpus_manifest.json 指定文件，并使用本集独立快照，不能混入开发语料。正式模型运行前必须建立 fixture ID / span 到实际解析产物的映射。

```text
python -X utf8 scripts/validation_build/validate_dataset.py validation_build/datasets/validation/synthetic-cooling-v1
```

记录真实 reviewer、带时区的 reviewed_at、review_notes 后才能将 annotations.jsonl 状态改为 reviewed。模型相关性 judgment 应在实际候选产生后填写；本目录不预造 Chunk 或 Source ID。
