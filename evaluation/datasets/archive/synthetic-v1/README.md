# 合成开发评测集

此目录保留为历史基础夹具。当前开发采用 [synthetic-v2](../../dev/synthetic-v2/README.md)，其中修正了旧题证据范围并增加复杂场景；不要把两套题视为互相独立的数据集合。

这套资料用于 Engineering RAG 的 M0 开发准备，共 20 题：16 道可回答、4 道不可回答。全部工程参数、标识符和失效案例均为虚构，不可用于真实车辆设计，也不能作为真实业务检索效果的证据。

当前为机器生成的标注草案，人工复核尚未完成；不是冻结发布测试集。没有运行 BM25、Dense、RRF、Reranker 或 LLM 评测，不能从结构校验结果推导模型质量。

## 文件

| 文件 | 用途 |
|---|---|
| [cases.md](cases.md) | 人工阅读题目、答案、必需事实、证据原文和拒答依据 |
| [cases.jsonl](cases.jsonl) | 每行一个 DEV_SPEC EvalCase，共 20 行 |
| [annotations.jsonl](annotations.jsonl) | 合成来源、待复核状态、证据引文、泄漏分组和无答案说明 |
| [corpus_manifest.json](corpus_manifest.json) | 原文件哈希、稳定文档身份、修订和 current 标记 |
| [source_units.json](source_units.json) | 从原文件提取的夹具定位目录，支持原文位置校验 |
| [corpus/synthetic_control_v1.docx](corpus/synthetic_control_v1.docx) | 同一规范的 1.0 修订，100 ms 超时和 300 ms 启动屏蔽 |
| [corpus/synthetic_control_v2.docx](corpus/synthetic_control_v2.docx) | 2.0 修订，150 ms 超时和 500 ms 启动屏蔽，标记为 current |
| [corpus/synthetic_failures.xlsx](corpus/synthetic_failures.xlsx) | 6 条合成失效记录，Sheet 为“失效案例”，表头第 4 行，数据第 5–10 行 |

## 使用顺序

1. 阅读 cases.md，对照 DOCX 条款与 XLSX 单元格复核答案和原文锚点。确认无答案题在指定范围内确实没有答案，不依据模型是否答出进行标注。
2. 运行 `python scripts/evaluation/validate_dataset.py evaluation/datasets/archive/synthetic-v1`。使用已有 Python 解释器即可，校验器只依赖标准库；这一步检查结构与原文一致性，不评价语义答案是否正确。
3. 仅将 corpus_manifest.json 的 sources.path 列出的三份原文件入库。不要递归摄入整个 evaluation 目录，否则题目、标准答案和定位目录会泄漏到检索语料。
4. 两版 DOCX 使用相同 document_id，先入 1.0 再入 2.0；若 API 生成自己的 ID，建立显式的 fixture-ID 到 runtime-ID 映射，不能将它们当成两个不同逻辑文档。默认查询仅使用 current；DEV-015 指定旧版，DEV-016 显式比较两版。
5. 建立检索结果后，按原文 spans 映射到候选 Chunk，记录每题来源和错误类型；不能用文件名相同代替证据命中。

## 夹具定位与正式解析器

`fixture-locator-v1` 是这次生成资料使用的可核对定位约定，不是已实现的生产 Parser。DOCX 定位采用 `word/document.xml` 的 1-based body 子元素序号；XLSX 按列顺序将“列名: 值”用换行连接为一条记录。char_start/char_end 为 Unicode 字符区间，左闭右开。

原文件、实际哈希和位置是真实可校验的；parse_artifact_id 属于夹具约定。接入正式 Parser 时须生成 fixture anchor 到实际解析产物的映射并核对原文覆盖，不能直接假定解析器会生成相同 unit_id。不要修改原文标签去迎合某次 Chunk 边界。

当前锚点采用整条条款/整行记录，便于初始链路验证；评估精细分块时，先在开发集人工细化必要证据区间并记录标注版本，再做公平对比。本套题的 evidence groups 表达 AND 关系；尚未覆盖复杂的替代证据 OR 标注。

## 题型分布

| 类型 | 数量 |
|---|---:|
| precise_term 精确术语 | 4 |
| semantic_paraphrase 自然语言改写 | 4 |
| history_failure 历史失效 | 4 |
| multi_evidence 多证据 | 2 |
| version_query 版本指定与对照 | 2 |
| unanswerable 不可回答 | 4 |

## 复核与扩展

- 全部题目同属 `synthetic-control-family` 泄漏组，只用于 dev，不拆成验证集和最终测试集。新增独立文档族后再分组划分。
- 人工复核后，在 annotations.jsonl 记录实际 reviewer、reviewed_at、review_notes 并将 human_review_status 改为 reviewed；不可填写未发生的复核。
- 发布集按 DEV_SPEC 另行准备，至少 120 题，并补 PDF/PPTX、扫描解析、长表格、实际版本冲突拒答、复杂多证据和真实业务资料。当前小语料不能代表这些场景。
- corpus 中不得加入 QA 预览或工具日志；截图/PDF 是内部格式检查产物，不属于摄入文件。
