# 修订开发集

本集包含 40 题：29 可回答、11 不可回答；5 份原文件、97 个原文单元。全部是合成资料，人工复核待完成，不是冻结测试集。

## 主要变化

- 继承原 20 题，在新目录中收紧评分锚点。DEV-001 只要求周期原文；DEV-013 增加历史误报现象及根因，使历史表与规范各提供必要事实。
- 新增 DEV-021–040，包含相近对象/通道/模式、等价证据 OR、跨来源 AND、多 span、过滤后无答案、部分证据与冲突拒答。
- 辅助接口资料新增 64 条相近编号对象规则。它们是有条件差异的合成记录，不能仅凭条数宣称 RRF/Reranker 有提升。实际分块和召回后需确认候选并集是否超过 M。
- DEV-032 的两份同范围现行资料无优先级，期望 version_conflict；DEV-033 明确要求对照，期望分别列出差异。不同文档的 current 不能解释成其中一个覆盖另一个。

## 使用

先阅读 [cases.md](cases.md)；运行输入为 [cases.jsonl](cases.jsonl)。[annotations.jsonl](annotations.jsonl) 保存复核状态、精确证据引文和拒答理由。组内 alternatives 为 OR，不同 evidence_groups 为 AND。

只摄入 corpus_manifest.json 中 sources.path 指定的 5 份文件。源文件的页码/行号不可取代 GoldAnchor；fixture-locator-v1 需映射到正式 Parser 的实际解析产物与 span。不要把题目、标注、定位目录、协议、生成种子或预览加入检索语料。

在仓库根目录运行：

```text
python -X utf8 scripts/evaluation/validate_dataset.py
python -X utf8 scripts/evaluation/validate_suite.py
```

第一条默认验证本集，第二条还验证独立冷却文档族及分组隔离。参数为 Python 命令示例，Linux 可使用已有 python3。

## 人工复核

逐条对照原件检查 question、required_facts 和每个证据组是否必要、是否充分，特别检查等价证据与拒答范围。记录实际 reviewer、带时区的 reviewed_at、review_notes，再将 human_review_status 改为 reviewed。程序通过不代替人工复核。

Source ID 在请求内生成，不能把 S1 等写死为 Gold。冲突原文放在 annotation.conflict_anchors，拒答题自身仍保留空 required_facts/evidence_groups，以符合 DEV_SPEC。

同属 synthetic-control-family 的历史题与新增题均只用于开发。独立验证草案见 [冷却资料](../../validation/synthetic-cooling-v1/README.md)；整个项目尚无冻结发布测试集。
