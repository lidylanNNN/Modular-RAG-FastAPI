# Engineering RAG — DEV_SPEC

当前规格版本：**v1.4**；产品范围：**V1**；最后更新：**2026-09-09**。

## 版本变更目录

| 规格版本 | 日期 | 主要变更 | 对应章节 |
|---|---|---|---|
| v1.4（当前） | 2026-09-09 | 细化工程目录的目标文件清单；在开发计划中为各里程碑补充待完成文件/模块，明确真实知识库本地目录与评测目录隔离 | 2.6、7.3 |
| v1.3 | 2026-09-08 | 定义正式项目目录、模块落位和路径规则；拆分评测数据、维护脚本、单元测试、组件夹具和审查报告；旧开发集移入 archive；同步入口、协议及 CI，保持数据身份不变 | 2.6、7.3；README.md |
| v1.2 | 2026-09-08 | 统一单索引、N/M/K 检索预算、Source ID 引用、分层评测与 B3a/B3b 对照；前移快照及容器基础；审核补齐基线结果契约、排序评分口径和阶段能力限制；正式文件改为 DEV_SPEC.md | 3.5–3.8、4.2–4.6、4.9、5.3、6.3–6.7、7 |
| v1.1 | 2026-09-07；跨平台补充于 2026-09-08 | 补充 SourceSpan、Claims 验证、快照发布、原文锚点评测、资源预算、进度表和跨平台要求；加入合成开发集状态 | 3–8；[历史规格](docs/history/engineering-rag_DEV_SPEC_v1.md) |
| v1（初稿） | 未记录 | 建立四格式解析、统一 Chunk、混合检索、生成和评测的 V1 范围 | 1–9；初稿演变见 Git 历史 |

维护约定：正式规格始终使用 `DEV_SPEC.md`，文件名不携带版本号。修订时更新当前版本、日期及本表；详细差异由 Git 保存。历史文件仅供追溯，不作为开发依据。规格修订完成不代表功能验收完成。

> **Single Source of Truth**：本文件是 `engineering-rag` 项目的唯一开发规格。模块设计、数据契约、验证规则、验收标准均以本文件为准。
>
> **项目定位**：面向汽车研发文档与历史失效知识的、Evaluation-driven、Evidence-bound 的 Engineering Knowledge Service。
>
> **当前状态**：设计/实现规格。本文中的功能、接口和指标均为开发目标；量化指标只能在冻结测试集完成实测后写入简历或面试材料。

>
> **v1.2 修订摘要**：删除独立 `Evidence` 事实实体；统一 Elasticsearch 单索引文档；明确 `Retriever Top-N → RRF Top-M → Reranker Top-K`；将 RRF 定位为候选融合与预算控制；Citation 改为请求内 `Source ID` 映射；Evaluation 按 Retrieval / Reranking / Generation 分层；补充 `Union + Reranker` 与 `RRF + Reranker` 对照；同时前移最小 Snapshot、版本生命周期和 Linux 容器骨架，并将 `search_knowledge` 实现纳入 Reranker 闭环。

> **v1.3 修订摘要**：固定第 2.6 节目录规范并迁移现有文件。此次仅调整工程组织与路径，不改变 Chunk / EvalCase 契约、原始语料、题目事实、证据身份或发布门槛。

> **v1.4 修订摘要**：补齐 V1 工程目录目标文件清单，并把开发计划中的每个阶段映射到待完成文件/模块。此次仅细化实施落点，不代表对应文件已经实现。

---

# 1. Intent

## 1.1 Problem

项目源于动力域控制器软件开发场景。研发过程中存在大量需求、设计、接口、信号定义等工程文档，同时历史失效案例往往零散分布在不同资料中，难以在设计开发初期有效进入新人和新项目的信息流。

现有关键词搜索存在两个主要问题：

1. 对信号名、接口名、故障码等精确工程术语有效，但对自然语言、同义表达和跨文档问题能力有限；
2. 历史失效知识虽然存在，但难以在设计开发阶段按当前问题自动召回，容易重复踩坑。

因此本项目需要把工程文档和历史失效知识转化为可检索、可问答、可引用、可评测的知识服务。

## 1.2 Goals

系统最终必须具备：

1. 支持 PDF、DOCX、PPTX、XLSX 四类工程文档离线入库；
2. 保留不同文档格式的天然结构，不强行统一原始解析结果；
3. 根据文件类型使用对应的 Chunking Strategy；
4. Chunking 后统一为一个强类型 `Chunk` Contract；
5. 同时建立 BM25 全文索引与 BGE-M3 Dense 向量索引；
6. 在线检索采用 BM25 + Dense 并行 Top-N 召回、RRF 融合并截断 Top-M、BGE-Reranker 精排得到最终 Top-K；
7. LLM 回答必须绑定检索证据并返回 Citation；
8. 证据不足时拒答；
9. 建立冻结测试集、Ground Truth、Baseline、Ablation、Bad Case 与 Trace；
10. 通过 FastAPI 提供问答接口；
11. 将核心知识检索能力封装成 `search_knowledge` Tool，供 Code Review / Engineering Agent 复用；
12. 支持 Docker 化运行。

## 1.3 Non-Goals

V1 不做：

- GraphRAG；
- Multi-Agent；
- 自研 OCR / 文档版面模型；
- 自研向量数据库；
- 自研文档解析框架；
- 复杂 Query Router；
- 多模态图片理解作为核心能力；
- 用户/权限/组织管理平台；
- 大规模分布式架构；
- 前端产品化作为核心工作。

## 1.4 Success Criteria

项目成功不是“接口能返回答案”，而是同时满足：

- 四种文件均能完成 `Parse → Chunk → Index`；
- 同一 Query 可同时经过 BM25、Dense、RRF、Reranker；
- Answer 的 Source ID 可映射回具体 Chunk 和原始文档位置；
- Unanswerable Query 能拒答；
- 检索与生成均有冻结测试集；
- Baseline / Ablation 可复现；
- 每次请求具有 Trace；
- `search_knowledge` Tool 可被独立调用；
- pytest 与系统验收全部通过。

---

# 2. Architecture

## 2.1 System Context

系统分为两条主链路：

1. **Offline Ingestion Pipeline**：负责文档解析、分块、索引；
2. **Online Query Pipeline**：负责召回、融合、精排、证据绑定与生成。

外部消费者包括：

- Web / Frontend；
- Code Review Tool；
- Engineering Agent。

## 2.2 End-to-End Flow

### 2.2.1 Offline

```text
Raw Files
   │
   ├── DOCX
   ├── PDF
   ├── PPTX
   └── XLSX
   ↓
Format Dispatcher
   ↓
Format-specific Parser
   ↓
Format-specific Parsed Structure
   ↓
Format-specific Chunker
   ↓
Unified Chunk[]
   ↓
BGE-M3 Embedding
   ↓
Single Elasticsearch Snapshot Index
   └── one ES document per Chunk
       ├── content      → BM25 inverted index
       └── dense_vector → Dense vector index
```

### 2.2.2 Online

```text
User Query
   ↓
┌─────────────────────┐
│                     │
BM25 Top-N        Dense Top-N
│                     │
└──────── RRF ─────────┘
          ↓
   Candidate Top-M
          ↓
    BGE-Reranker
          ↓
      Final Top-K
          ↓
 Request-local Source Binding
          ↓
  Evidence-bound Prompt
          ↓
         LLM
          ↓
Structured Answer + Source IDs
          ↓
Citation Validation / Backend Source Mapping
          ↓
Frontend / API Consumer
```

### 2.2.3 Tool Exposure

```text
              Engineering RAG
                    │
             search_knowledge
                    │
        ┌───────────┴───────────┐
        ↓                       ↓
   Code Review           Engineering Agent
```

`search_knowledge` 返回结构化最终检索结果（`FinalCandidate[]`），不返回自由文本聊天结果作为唯一输出。

## 2.3 Module Boundaries

```text
Ingestion
├── Format Dispatcher
├── DOCX Parser
├── PDF Parser
├── PPTX Parser
├── XLSX Parser
├── DOCX Chunker
├── PDF Chunker
├── PPTX Chunker
└── XLSX Chunker

Indexing
├── BM25 Indexer
└── Dense Indexer

Retrieval
├── BM25 Retriever
├── Dense Retriever
├── RRF Fusion
└── Reranker

Generation
├── Context Builder
├── Prompt Builder
├── LLM Client
├── Source Binder
├── Citation Validator
├── Claim Verifier
└── Refusal Policy

Evaluation
├── Retrieval Eval
├── Generation Eval
├── Ablation Runner
└── Bad Case Analyzer

Runtime
├── FastAPI
├── search_knowledge Tool
└── Trace
```

## 2.4 Dependency Rules

- Parser 不能依赖 Retriever；
- Chunker 不能依赖 Elasticsearch；
- Retriever 只消费 `Chunk` / Index，不感知 DOCX/PDF/PPTX/XLSX 原始格式；
- Reranker 不修改原始 Chunk；
- Generation 只能引用本次请求由 FinalCandidate 绑定得到的 Source ID；
- Evaluation 必须通过公开接口调用系统，不允许复制一套隐藏逻辑；
- Tool 层只编排现有 Retrieval 能力，不复制 Retrieval 实现。

## 2.5 Key Design Decisions

### D1. 不建立统一原始 Block IR

不同文件天然结构差异较大。V1 参考 RAGFlow 的工程思路：

- 格式解析保持多态；
- Chunking Strategy 保持多态；
- **进入检索层时统一 Chunk Contract**。

### D2. 固定核心字段 + 开放 Metadata

最终 Chunk 使用强类型核心字段与必需的来源定位字段，格式特定展示/过滤信息进入 `metadata`。该设计参考 LlamaIndex / R2R 一类项目的“固定实体 + 开放 metadata”思路，避免完全自由 `dict[str, Any]` 造成边界失控。

### D3. 默认统一 Hybrid Retrieval

V1 不做 Query 类型 `switch-case` 路由。所有普通知识 Query 默认并行：

```text
BM25 + Dense → RRF → Reranker
```

只有 Evaluation / Bad Case 明确证明某类 Query 需要独立路径后，V2 才允许引入 Router。

---

## 2.6 Repository Layout

目录按职责组织。以下是 V1 的正式目标结构；带“规划”标记的目录/文件在对应里程碑实现时创建，未标记项为当前已有产物。不通过空目录、空模块或 `.gitkeep` 伪装功能已实现。

```text
Modular-RAG-FastAPI/
├── DEV_SPEC.md                     # 唯一正式开发规格，版本记录位于文首
├── README.md                       # 项目入口、当前能力和运行命令
├── .github/workflows/              # Windows / Linux CI
├── .gitattributes                  # 文本换行和二进制文件规则
├── .gitignore
├── pyproject.toml                  # 规划 M1：Python 包、工具和依赖声明
├── uv.lock                         # 已生成：锁定运行和开发依赖，和 pyproject.toml 配套
├── .env.example                    # 规划 M1：环境变量名称及无密钥示例
├── configs/                        # 规划 M1：可版本化的非敏感默认配置
│   ├── default.yaml
│   └── logging.yaml
├── src/engineering_rag/            # 规划 M1 起：唯一应用 Python 包
│   ├── bootstrap.py                # 配置、依赖组装与服务生命周期
│   ├── contracts/                  # Pydantic 数据契约与跨字段约束
│   ├── config/                     # 配置加载、路径解析和运行预检
│   ├── ingestion/
│   │   ├── dispatcher.py
│   │   ├── parsers/                # DOCX / XLSX / PDF / PPTX 适配器
│   │   └── chunkers/               # 四种格式分块策略及 SourceSpan 映射
│   ├── indexing/                   # ES 文档映射、向量写入、快照构建/验证
│   ├── retrieval/                  # BM25 / Dense / RRF / Reranker
│   ├── generation/                 # Context、Source Binding、Claims、Verifier、拒答
│   ├── services/                   # 入库/查询/版本生命周期的公开服务用例
│   ├── storage/                    # 原件/解析产物、SQLite job/manifest/lease 存储
│   ├── observability/              # 共享 Trace、日志和时延记录
│   ├── tools/                     # search_knowledge 薄适配层
│   ├── api/                       # FastAPI 路由、HTTP Schema 适配和错误映射
│   └── evaluation/                # 正式指标、锚点映射、实验执行与报告逻辑
├── scripts/
│   ├── experiments/              # 正式实验的薄 CLI 入口
│   └── validation_build/         # 验证集构建与资料校验命令
│       ├── validate_dataset.py
│       ├── validate_suite.py
│       └── build_expansion.py
├── tests/
│   ├── unit/validation_build/           # 当前资料校验器回归测试
│   ├── integration/              # 规划 M4 起：ES / Snapshot / HTTP 集成测试
│   ├── e2e/                      # 规划：锁定真实模型的端到端验收
│   └── fixtures/
│       └── answer_quality/        # 答案质量与证据覆盖组件夹具，不进入知识库
├── validation_build/             # 验证集构建资料，含 dev/validation/test 划分
│   ├── README.md
│   ├── datasets/
│   │   ├── dev/synthetic-v2/      # 当前 40 题开发集
│   │   ├── validation/synthetic-cooling-v1/  # 12 题验证草案
│   │   ├── test/                 # 规划 M11：独立冻结发布集
│   │   └── archive/synthetic-v1/ # 历史 20 题，仅供回归和追溯
│   ├── protocols/development.json # 当前未冻结协议；路径基准为 validation_build/
│   ├── schemas/                  # 评测附属文件的 JSON Schema
│   └── seeds/                    # 合成构建输入；不可作为摄入资料
├── docs/
│   ├── history/                  # 历史规格，不具备当前规格效力
│   ├── reviews/                  # 带日期的设计/数据审查记录
│   └── reports/                  # 规划：筛选归档的真实实验与发布报告
├── deploy/                       # 规划 M1/M12：容器骨架与最终部署配置
│   ├── Dockerfile
│   └── compose.yaml
├── artifacts/                    # 按需生成并忽略：运行结果、Trace、预览
└── .local/                       # 按需生成并忽略：本地数据库、原件和模型缓存
```

### 2.6.1 工程文件目标清单

以下清单定义 V1 需要实现的主要文件落点。文件只在对应里程碑真正实现时创建；不得提交空模块来制造进度。相同职责只能有一个主实现，测试和 CLI 只能薄封装公共服务。

```text
configs/
├── default.yaml                   # M1：服务、路径、索引、模型和检索默认配置
├── logging.yaml                   # M1：日志格式、级别、Trace 字段
└── evaluation.yaml                # M4：实验参数、N/M/K、报告输出目录

src/engineering_rag/
├── __init__.py                    # M1：包版本与公共导出边界
├── bootstrap.py                   # M1：配置加载、依赖组装、生命周期入口
├── contracts/
│   ├── source.py                  # M1：SourceDocument、Revision、ParseArtifact
│   ├── chunk.py                   # M1/M3：Chunk、SourceSpan、ChunkFailure
│   ├── retrieval.py               # M1/M4-M7：Query、Candidate、FinalCandidate、Filter
│   ├── generation.py              # M8：SourceBinding、Claim、Answer、Citation、Refusal
│   ├── evaluation.py              # M1/M4-M11：EvalCase、GoldAnchor、Judgment、RunResult
│   └── errors.py                  # M1：统一错误类型、HTTP/Tool 错误映射输入
├── config/
│   ├── settings.py                # M1：强类型配置模型和环境变量覆盖
│   ├── paths.py                   # M1：跨平台路径解析、.local/artifacts 约束
│   ├── config_logging.py          # M1：结构化日志初始化
│   └── preflight.py               # M1/M5：依赖、模型、ES、GPU/CPU 兼容性检查
├── ingestion/
│   ├── dispatcher.py              # M1/M2：入库调度、文件类型分发、幂等入口
│   ├── jobs.py                    # M10：入库任务状态机、重试、取消
│   ├── parsers/
│   │   ├── parser_base.py         # M2：Parser 接口和错误约束
│   │   ├── parser_docx.py         # M2：DOCX 解析
│   │   ├── parser_xlsx.py         # M2：XLSX 解析
│   │   ├── parser_pdf.py          # M9：PDF 解析
│   │   └── parser_pptx.py         # M9：PPTX 解析
│   └── chunkers/
│       ├── chunker_base.py        # M3：Chunker 接口和 SourceSpan 校验入口
│       ├── chunker_docx.py        # M3：DOCX 分块
│       ├── chunker_xlsx.py        # M3：XLSX 分块
│       ├── chunker_pdf.py         # M9：PDF 分块
│       └── chunker_pptx.py        # M9：PPTX 分块
├── indexing/
│   ├── es_client.py               # M4：Elasticsearch 客户端封装
│   ├── mappings.py                # M4/M5：BM25、dense_vector、metadata 映射
│   ├── snapshots.py               # M4/M5：Snapshot 构建、校验、发布、lease
│   ├── embeddings.py              # M5：BGE-M3 向量生成和批处理
│   └── lifecycle.py               # M5：Update/Delete/Rollback/Recovery
├── retrieval/
│   ├── bm25.py                    # M4：BM25 召回
│   ├── dense.py                   # M5：Dense 召回
│   ├── fusion.py                  # M6：RRF、去重、Top-M 截断
│   ├── reranker.py                # M7：BGE-Reranker、降级和排序解释
│   └── service.py                 # M4-M7：统一检索服务入口
├── generation/
│   ├── context.py                 # M8：上下文预算和 Source 选择
│   ├── source_binding.py          # M8：请求内 Source ID 绑定
│   ├── claims.py                  # M8：声明抽取和证据对齐
│   ├── llm.py                     # M8：LLM 客户端适配
│   ├── verifier.py                # M8：语义/数值/版本验证
│   └── refusal.py                 # M8：拒答判定和错误区分
├── services/
│   ├── document_service.py        # M1/M2/M10：入库、删除、任务编排公开入口
│   ├── query_service.py           # M1/M4/M8：检索/生成统一查询入口
│   ├── snapshot_service.py        # M4/M5：索引发布、活动指针和恢复入口
│   └── evaluation_service.py      # M4-M11：评测运行入口
├── storage/
│   ├── local_files.py             # M1/M2：.local 原件、解析产物、缓存路径管理
│   ├── sqlite.py                  # M1/M10：SQLite 连接、迁移和事务
│   ├── repositories.py            # M1/M2/M5/M10：文档、任务、manifest、lease 仓储
│   └── manifests.py               # M2/M4/M5：corpus/snapshot manifest 持久化
├── observability/
│   ├── trace.py                   # M1：Trace 数据模型、span 记录和序列化
│   ├── trace_logging.py           # M1：日志字段绑定
│   └── trace_metrics.py           # M4/M10：latency、候选数量和错误率记录
├── tools/
│   └── search_knowledge.py        # M7：Tool 薄适配层
├── api/
│   ├── main.py                    # M10：FastAPI app 工厂
│   ├── dependencies.py            # M10：服务依赖注入
│   ├── schemas.py                 # M10：HTTP 请求/响应 Schema
│   └── routes/
│       ├── health.py              # M10：健康检查
│       ├── documents.py           # M10：入库/任务/删除
│       ├── tools.py               # M10：search_knowledge HTTP 包装
│       └── traces.py              # M10：Trace 查询
└── evaluation/
    ├── datasets.py                # M4：读取仓库级 validation_build 数据集
    ├── anchor_mapping.py          # M4/M5：GoldAnchor 到正式 Chunk 的映射
    ├── evaluation_metrics.py      # M4-M8：Recall、nDCG、Correctness、Citation 指标
    ├── judgments.py               # M4-M11：候选相关性标注读写
    ├── runner.py                  # M4-M11：实验执行
    └── reports.py                 # M4-M12：报告生成和哈希记录

scripts/
├── validation_build/
│   ├── validate_dataset.py        # 已有：评测资料校验
│   ├── validate_suite.py          # 已有：评测套件校验
│   └── build_expansion.py         # 已有：合成资料扩展构建
├── experiments/
│   └── run_experiment.py          # M4：薄封装 evaluation_service
└── dev/
    ├── dev_preflight.py           # M1：本地/容器预检入口
    └── ingest_local.py            # M2/M10：本地原件入库调试入口

tests/
├── unit/                          # M1 起：按 src/engineering_rag 职责镜像组织
├── integration/                   # M4 起：ES、Snapshot、HTTP、持久化测试
├── e2e/                           # M8/M11：真实模型和端到端验收
└── fixtures/                      # 测试夹具；不得作为知识库摄入

.local/
├── documents/                     # 本地真实知识库原件，不提交 Git
├── parsed/                        # 解析产物，不提交 Git
├── rag.sqlite                     # 本地任务/manifest/lease 数据库，不提交 Git
└── model-cache/                   # 模型缓存，不提交 Git

artifacts/
├── traces/                        # 运行 Trace
├── evaluation-runs/               # 实验输出
└── reports/                       # 临时报告；需归档的结论复制到 docs/reports/
```

### 2.6.2 模块归属与依赖

- 应用源码统一放在 `src/engineering_rag/`，不再平行引入承载同类业务的 `app/`、`backend/` 或根目录业务模块。
- `services/` 提供第 2.4 节要求的公开服务入口，协调 Ingestion、Indexing、Retrieval、Generation 和 Storage；HTTP、Tool、CLI 复用这些入口。它们不相互复制检索、发布或生成逻辑。
- `contracts/` 和 `config/` 不导入 API、Tool 或测试。业务包不能导入 `scripts/`、`tests/`，也不能把评测目录作为运行依赖。`storage/` 提供持久化适配，发布步骤由 services/indexing 编排，不在 API 路由中操作活动指针。
- 仅 `src/engineering_rag/evaluation/` 使用 `evaluation` 目录名，承载正式指标、实验执行与报告实现。仓库级 `validation_build/` 存放验证集构建资料，包括 dev、validation、test 划分的数据、协议、Schema 和构建输入。
- `scripts/validation_build/` 仅负责验证集构建和资料校验，使用 Python 标准库；正式实验 CLI 放入 `scripts/experiments/`，薄封装公开服务入口，不复制指标逻辑。测试允许导入这些维护脚本，但不反向依赖测试。
- 测试路径按被测职责镜像组织；当前 `tests/unit/validation_build/` 的回归测试属于资料校验器。`tests/fixtures/answer_quality/` 中未接入实现的用例不得计为测试通过。
- 本地真实知识库原件默认放入 `.local/documents/` 或由配置指向外部绝对路径；仓库级 `validation_build/**/corpus/` 只属于评测数据集，不是生产知识库目录。
- 新增骨架文件应避免重复 basename；除 Python 包约定的 `__init__.py`、Markdown 常规入口 `README.md`、评测数据集固定文件名（`cases.jsonl`、`annotations.jsonl`、`corpus_manifest.json`、`source_units.json`、`cases.md`）外，重名文件必须加模块前缀区分，例如 `parser_docx.py` 与 `chunker_docx.py`。

### 2.6.3 数据集内部结构与路径

每个有独立 manifest 的数据集保持自包含目录：

```text
<dataset>/
├── README.md
├── corpus/                        # 唯一允许摄入的原件所在目录
├── corpus_manifest.json           # 原件哈希、身份、修订、current
├── source_units.json              # 夹具原文及位置目录
├── cases.jsonl                    # EvalCase，每行一道题
├── annotations.jsonl              # 证据引文、复核、泄漏组与冲突依据
└── cases.md                       # 从标注生成的人读视图
```

- `sources.path` 始终相对于所在 manifest 的数据集根目录；迁移外层目录不重算原件哈希、revision_id、parse_artifact_id 或 corpus_manifest_id，不修改 GoldAnchor。
- `validation_build/protocols/development.json` 声明 `path_base=validation_build_root`；其中 datasets、historical_fixtures、Schema 和规格路径均相对于仓库 `validation_build/` 解析，不能相对于协议文件目录或当前工作目录猜测。数据集选择由协议显式列举，禁止递归扫描 archive 参与当前评测。
- 当前归档和修订集保留相同原件副本是有意的快照隔离：保留身份和可复现性，不改成跨目录软链接。二者属于相同泄漏组，不得当成独立开发/验证样本。后续大规模或真实私有语料采用外部制品存储时需另行定义获取及哈希校验协议。
- `seeds/` 是构建输入，原件是检索事实源；生成问题、答案、Source Map 模拟数据和审查报告均不可入库。仅按 manifest 的 sources.path 摄入原件。
- 脚本默认路径基于 `__file__` 定位仓库；显式 CLI 数据目录参数相对于调用方当前目录。应用运行数据目录通过配置传入，生产部署应解析为绝对路径；不硬编码盘符或用户主目录。

### 2.6.4 生成物与变更验收

- `artifacts/`、`.local/`、`.env`、解释器环境和缓存不提交 Git。需要保留的人工确认实验报告归档至 `docs/reports/`，并引用数据/配置哈希，不把临时输出复制进 corpus。
- 当前已有 `.artifact-work/` 属于本地制作缓存，继续忽略且不被任何正式运行命令依赖；后续预览和日志统一写入 `artifacts/`。
- 目录迁移必须同步修改导入、协议/种子路径、README、Markdown 链接和 CI，并验证原件/标注哈希保持不变、数据校验通过、测试发现可运行，以及从仓库外调用脚本仍正常。
- 不为保持旧路径而保留重复脚本或兼容目录；迁移后的命令以 README 为准。新增职责目录或改变现有归属时先更新本节及文首变更表。

---

# 3. Contracts

# 3.1 Source Document Identity

所有文件进入系统时必须先生成文档级身份信息。持久化核心模型使用 Pydantic v2；来源/身份模型不允许额外核心字段，扩展信息仅进入声明的 metadata/extra。以下省略统一导入，示例模型的跨字段约束必须在实现中用 validator 落实，不能仅靠 Field 限制。

```python
class SourceDocument(BaseModel):
    document_id: str
    revision_id: str
    file_name: str
    file_type: Literal["docx", "pdf", "pptx", "xlsx"]
    version: str | None = None
    content_hash: str
```

约束：

- `document_id` 是系统内部稳定 ID；
- `content_hash` 用于判断内容是否变化；
- `version` 来自业务版本信息，若源文件无版本则允许为空；
- 文件更新不得默认为新文档，必须先执行版本/哈希策略。

身份与存储规则：

- 首次入库生成 UUID `document_id`；更新必须显式传入已有 ID，不按文件名猜测身份。更名不改变文档身份。
- `content_hash` 为原始文件字节的 SHA-256；`revision_id = SHA256(document_id + ':' + content_hash)`，标识不可变修订。业务 `version` 仅为展示标签，不用于排序或唯一性判断。
- 同一文档相同字节重复入库复用修订；同一字节对应的业务版本标签发生冲突时返回 `VersionConflict`，不得静默覆盖。不同文档允许具有相同内容哈希。
- 原文件及其修订记录持久化保存。生成 `parse_artifact_id` 时纳入 revision、Parser 版本和解析配置哈希；保存对应不可变解析产物，供定位和评测复用。
- `chunk_id` 使用 revision、解析产物 ID、分块配置哈希、源位置和块内序号的规范 JSON 计算 SHA-256。JSON 键排序、UTF-8、分隔符和文本规范化版本必须固定；不得使用进程内 `hash()`。
- 向量模型变化不改变 Chunk 身份，只改变索引构建版本。切块策略或解析产物变化允许生成新的 Chunk ID。

---

# 3.2 Format-specific Parsed Structures

解析阶段**不要求四种文件输出完全一致的数据模型**。每种 Parser 输出其格式天然结构；Chunker 负责消费对应结构。

## 3.2.1 DOCX Parsed Structure

DOCX 保留：

```text
DOCXDocument
├── Heading
│   ├── level
│   └── text
├── Paragraph
│   └── text
├── Table
│   └── rows / cells
└── List
```

最小解析契约：

```python
class DocxElement(BaseModel):
    element_type: Literal["heading", "paragraph", "table", "list"]
    content: str
    order: int
    heading_level: int | None = None
    page: int | None = None
    extra: dict[str, Any] = Field(default_factory=dict)

class DocxParseResult(BaseModel):
    document: SourceDocument
    elements: list[DocxElement]
```

解析实现优先使用 OOXML / python-docx 可获得的结构信息；不得先转纯文本后重新猜标题关系。

## 3.2.2 PDF Parsed Structure

PDF 保留 Page 与 Layout Block：

```text
PDFDocument
└── Page
     ├── Title Block
     ├── Text Block
     ├── Table Block
     ├── Image Block
     └── List Block
```

最小解析契约：

```python
class PdfBlock(BaseModel):
    block_type: Literal["title", "text", "table", "image", "list"]
    content: str
    page: int
    order: int
    bbox: list[float] | None = None
    heading_level: int | None = None
    extra: dict[str, Any] = Field(default_factory=dict)

class PdfParseResult(BaseModel):
    document: SourceDocument
    blocks: list[PdfBlock]
```

PDF Parser 可使用 MinerU 等成熟解析器；本项目不自研 Layout/OCR 模型。

## 3.2.3 PPTX Parsed Structure

PPTX 保留 Slide 原生结构：

```text
Presentation
└── Slide
     ├── Title
     ├── Text
     ├── Table
     ├── List
     └── Image
```

最小解析契约：

```python
class PptSlide(BaseModel):
    slide_number: int
    title: str | None = None
    texts: list[str] = Field(default_factory=list)
    tables: list[str] = Field(default_factory=list)
    images: list[str] = Field(default_factory=list)
    extra: dict[str, Any] = Field(default_factory=dict)

class PptxParseResult(BaseModel):
    document: SourceDocument
    slides: list[PptSlide]
```

V1 以 Slide 为主要语义边界，不强制恢复 Word 式章节树。

## 3.2.4 XLSX Parsed Structure

XLSX 保留 Workbook → Sheet → Table/Row：

```text
Workbook
└── Sheet
     └── Table
          ├── Header
          ├── Row
          ├── Row
          └── Row
```

最小解析契约：

```python
class ExcelRow(BaseModel):
    row_number: int
    values: dict[str, Any]

class ExcelTable(BaseModel):
    sheet_name: str
    columns: list[str]
    rows: list[ExcelRow]
    table_range: str | None = None

class XlsxParseResult(BaseModel):
    document: SourceDocument
    tables: list[ExcelTable]
```

失效案例类表格优先把“业务记录行”作为语义单位；不得把 Sheet 名硬解释为 Word 的 Chapter。

---

# 3.3 Unified Chunk Contract

**所有格式完成 Chunking 后必须统一成以下模型。**

```python
class SourceSpan(BaseModel):
    unit_id: str
    char_start: int = Field(ge=0)
    char_end: int = Field(gt=0)

class Chunk(BaseModel):
    chunk_id: str
    document_id: str
    revision_id: str
    parse_artifact_id: str
    content: str = Field(min_length=1)
    chunk_index: int = Field(ge=0)
    source_spans: list[SourceSpan] = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)
```

字段语义：

| Field | Meaning |
|---|---|
| `chunk_id` | Chunk 唯一 ID |
| `document_id` | 来源文档 ID |
| `revision_id` | 不可变源文件修订 ID |
| `parse_artifact_id` | 不可变解析产物 ID |
| `content` | BM25 / Embedding / Reranker 使用的标准文本 |
| `chunk_index` | Chunk 在源文档中的稳定顺序 |
| `metadata` | 格式特定定位、版本、结构、来源信息 |
| `source_spans` | 必需的原文位置列表；开放 metadata 不能替代它 |

本文代码块为契约片段，统一使用 Pydantic v2、`typing` 与共享模型导入，不视为独立可执行程序。

每个不可变解析产物维护只读定位目录：`unit_id → 原始位置 + canonical_text`。字符区间按 Python Unicode 字符索引、左闭右开计算，必须满足 `0 <= char_start < char_end <= len(canonical_text)`。
目录只负责来源定位，不取代各格式 Parsed Structure，不增加统一原始 Block IR。

| 格式 | 定位目录必须保存的位置 |
|---|---|
| DOCX | OOXML part + 元素顺序/路径；表格含行列。页码不可可靠获得时不填写，不能猜测 |
| PDF | 1-based 页码 + 页内 block 序号；bbox 可空，有值时使用左上原点的归一化 `[x0,y0,x1,y1]` 并验证范围和顺序 |
| PPTX | 1-based slide + shape/表格单元标识 |
| XLSX | sheet + table region + 单元格/行范围；有业务主键时保存 record_key，无主键时用修订内位置生成 |

跨页、跨元素和跨行 Chunk 使用多个 span，不能只保存第一页/第一行。表头和标题补入 content 时也保留来源映射；自动插入的分隔符不作为原文证据。Chunker 必须保存 content 到 span 的映射，禁止依靠生成后的模糊文本搜索恢复来源。

### Metadata Rules

共同必需字段（由 Chunk Validator 校验存在和类型；version 允许显式 null）：

```text
file_name
file_type
version
content_hash
```

DOCX 展示字段（heading_path 必需，允许空列表；page 可选）：

```text
heading_path
page
```

PDF 展示字段（具体定位以 source_spans 为准）：

```text
page
bbox
heading_path
```

PPTX 展示字段（slide 必需；slide_title 允许空）：

```text
slide
slide_title
```

XLSX 展示字段（sheet/row/record_key/columns 必需；多行定位以 source_spans 为准）：

```text
sheet
row
record_key
columns
```

约束：

- `metadata` 用于过滤、Citation、Trace；
- 不把 Embedding、BM25 score、Reranker score 永久写回核心 Chunk；
- Index 侧派生字段不得反向污染 Chunk Contract；
- 同一 Chunk 的 `chunk_id` 在未发生内容/切块策略变化时保持稳定。

共同 metadata 的 `file_type`、`version`、`content_hash` 必须与所属 SourceDocument 一致；所有 span 必须解析到该 `parse_artifact_id`。缺字段、空白 content、跨修订引用或不存在的位置一律 `ChunkFailure`，不得入索引。

---

# 3.4 Chunking Contracts

## 3.4.1 DOCX Chunking

策略：Structure-aware。

优先边界：

```text
Heading → Paragraph → Table/List
```

规则：

1. Heading 维护当前标题上下文；
2. 普通段落优先在同一标题上下文内聚合；
3. Table 不与无关段落任意拼接；
4. 超出 token budget 后在语义边界二次切分；
5. Chunk metadata 保留 `heading_path`；
6. 不允许把标题与其正文完全拆散而失去上下文。

## 3.4.2 PDF Chunking

策略：Layout / Structure-aware。

规则：

1. 使用 Parser 输出的 page、title、text、table 等 block；
2. 优先根据标题和块边界切分；
3. Page 仅作为定位信息，不默认强制“一页一个 Chunk”；
4. Table 独立保留结构化文本；
5. `page/bbox` 进入 metadata；
6. 复杂扫描件解析失败必须产生 Parse Failure，不得静默生成垃圾 Chunk。

## 3.4.3 PPTX Chunking

V1 参考 RAGFlow Presentation 模式：**Slide-based Chunking**。

规则：

1. 默认一页 Slide 为一个 Chunk；
2. Slide Title 拼入 `content`，以增强语义；
3. `slide` 与 `slide_title` 写入 metadata；
4. 超大 Slide 超过 token budget 时允许在页内二次切分；
5. 二次切分后的 Chunk 必须仍共享同一个 slide metadata。

## 3.4.4 XLSX Chunking

V1 对历史失效案例等结构化业务表参考 RAGFlow Table 模式：**Row-based Chunking**。

规则：

1. 一条完整业务记录优先生成一个 Chunk；
2. Column Name 必须与 Value 一起序列化到 `content`；
3. 不允许只存 Value 丢失列语义；
4. `sheet/row/record_key` 写入 metadata；
5. 空行不生成 Chunk；
6. 若一个 Sheet 存在多个独立 Table Region，应先识别 Table，再按业务记录切分；
7. 对非记录型 Excel，允许后续增加独立 chunk strategy，但不得污染默认失效案例策略。

8. 超长记录按字段/句子切分，重复携带业务键和相关列名，保存 `record_part_index/count`；不截掉尾部字段。多行合成记录须保留全部行范围。
9. 表头为空或重复时生成稳定列 ID 并保留原显示名，避免 dict 覆盖值。合并单元格只在其实际合并范围内展开；公式保存公式文本与可获得的缓存值，不计算外部链接，缓存缺失显式标记。

## 3.4.5 Shared Size Rules

分块预算包含重复标题和表头。所有格式均须按 4.9 的 tokenizer 和输入上限校验；禁止 Embedding/Reranker 客户端静默截断。
超限优先在原文语义边界继续分块，仍无法处理时返回 `ChunkFailure`。不修改冻结解析产物；分块结果必须覆盖所选可解析文本，排除的页眉页脚/图像等内容记录原因。

---

# 3.5 Retrieval Contracts

## 3.5.1 Retrieval Configuration

检索链路显式区分三层候选预算：

```python
class RetrievalConfig(BaseModel):
    bm25_top_n: int = Field(default=50, ge=1)
    dense_top_n: int = Field(default=50, ge=1)
    rrf_top_m: int = Field(default=50, ge=1)
    final_top_k: int = Field(default=5, ge=1, le=20)
    rrf_k: int = Field(default=60, ge=1)
```

约束：

- `Top-N`：BM25 / Dense 各自召回窗口；
- `Top-M`：RRF 对两路候选融合、去重后保留给 Cross-Encoder 的候选窗口；
- `Top-K`：Reranker 精排后最终返回给 Tool / Generation 的结果；
- 必须满足 `final_top_k <= rrf_top_m`；
- 请求级 `top_k` 可以覆盖 `final_top_k`，覆盖后仍须满足 `top_k <= rrf_top_m` 和系统范围；违反时返回请求 Schema 错误（422），不静默扩大 M；
- `N/M/K`、`rrf_k` 与实际候选数量必须进入 Trace 和实验 manifest。

## 3.5.2 Retrieval Candidate

Retriever 输出统一候选结构：

```python
class RetrievalCandidate(BaseModel):
    chunk: Chunk
    source: Literal["bm25", "dense"]
    rank: int = Field(ge=1)
    score: float | None = None
```

注意：BM25 score 与 Dense score 不直接比较。

## 3.5.3 RRF Result

```python
class FusedCandidate(BaseModel):
    chunk: Chunk
    rrf_score: float
    source_ranks: dict[str, int]
    rank: int = Field(ge=1)
```

默认公式：

```text
RRF(d) = Σ 1 / (k + rank_i(d))
```

规则：

- 默认 `k=60`，rank 从 1 开始；
- RRF 的职责是 **candidate fusion + candidate pruning / budget control**，不是最终相关性排序器；
- 按 `chunk_id` 合并 BM25 Top-N 与 Dense Top-N，保留各路原始 rank；每路对同一 Chunk 最多贡献一次，不能在去重时丢失任一路排名；
- RRF 只保留 Top-M 进入 Reranker；
- `k=60` 是成熟实现常用基线，最终配置必须记录验证集实验；不得把 60 描述为理论最优。

## 3.5.4 Final Candidate

```python
class FinalCandidate(BaseModel):
    chunk: Chunk
    rank: int = Field(ge=1)
    rrf_score: float | None = None
    source_ranks: dict[str, int]
    rerank_score: float | None = None
```

规则：

- 正常链路由 BGE-Reranker 对 RRF Top-M 重排并截断为 Top-K；
- `rerank_score` 只在 Reranker 成功时存在；
- Reranker 降级时允许保留 RRF 顺序，`rerank_score=None` 且响应必须标记 `degraded=true`；
- RRF 只决定 Reranker 可见的候选集合和候选优先级，不直接约束 Reranker 对 Top-M 内部的最终顺序；
- 不允许全库 rerank。
- B0/B1/B2/B3a 等评测路径复用同一结果投影；未执行 RRF 时 `rrf_score=None`，未执行 Reranker 时 `rerank_score=None`，不填伪造分数。`source_ranks` 保留各原始召回列表的排名。主动关闭模块的实验不标记 degraded；运行时失败才按降级规则处理。

---

# 3.6 Citation / Generation Contracts

V1 不建立独立 `Evidence` 事实实体。**检索得到的 `FinalCandidate.chunk` 是证据事实源**；Generation 仅在本次请求内为实际送入 Prompt 的 FinalCandidate 分配 Source ID。

## 3.6.1 Request-local Source Binding

请求内建立临时映射：

```text
S1 → FinalCandidate(chunk_A)
S2 → FinalCandidate(chunk_B)
S3 → FinalCandidate(chunk_C)
```

约束：

- `source_id` 仅在本次请求中唯一，不持久化为新的知识实体；
- Source ID 由后端生成，LLM 无权创建有效的新 ID；
- Prompt 中的 Source 文本直接来自对应 `FinalCandidate.chunk.content`；
- Citation 的文件名、版本、页码/Slide/Sheet、`source_spans` 等均由后端从 Chunk 回填，不能相信 LLM 自报来源；
- 未送入 Prompt 的候选只保存在 Trace，不得被答案引用；
- V1 Context Builder 只选择完整 Chunk，不做隐式摘录或静默截断。

API 输出使用响应投影视图，不建立第二份事实源：

```python
class CitationReference(BaseModel):
    source_id: str
    chunk: Chunk
```

`CitationReference` 仅用于将请求内 Source ID 与真实 Chunk 一起返回给调用方；事实源仍是 `Chunk`。

## 3.6.2 LLM Structured Output

```python
class CitedClaim(BaseModel):
    text: str = Field(min_length=1)
    source_ids: list[str] = Field(min_length=1)

class AnswerOutput(BaseModel):
    claims: list[CitedClaim]
    refused: bool
    refusal_reason: Literal[
        "insufficient_evidence", "version_conflict", "unsupported_claim"
    ] | None = None
```

规则：

- LLM 只能引用 Prompt 中实际提供的 `source_id`；
- 后处理必须用本次请求 Source Map 校验每个 `source_id`；
- 不存在的 Source ID 直接判定输出无效；
- 后端根据 `source_id → FinalCandidate → Chunk → source_spans/metadata` 生成真实 Citation；
- 证据不足必须支持拒答；
- Answer 不允许把模型自身知识伪装成工程文档事实。

输出与拒答规则：

- 非拒答时 claims 非空、refusal_reason 为 null；每条 claim 表达一项可验证结论并引用本请求 Source ID。程序按顺序把 claims.text 渲染为 answer，不再接收无引用的第二份自由答案。
- 拒答时 claims 必须为空、refusal_reason 必须有值；answer 由程序生成固定解释。空检索结果直接拒答，不调用生成模型。
- 校验分两层：程序检查 Schema、Source ID allowlist、来源和跨字段约束；独立语义验证调用检查每条 claim 是否由引用 Chunk 支持，重点覆盖数值、单位、条件、否定和版本。验证结果仅为质量控制信号，不保证绝对正确，需通过 4.6 的人工标注评测验证。
- 语义验证返回每条 claim 的 `supported/unsupported/uncertain` 及理由；任一非 supported 时不得按成功答案返回。输入资料中的指令视为数据，不能改变系统规则或触发工具执行。
- Schema/虚构 Source ID/语义不支持最多触发一次纠正生成，使用同一组 Source，仍须完整复验。仍为非法结构或 ID 时返回 `CitationValidationFailure`；结构有效但语义仍不支持时拒答 `unsupported_claim`。验证服务异常/超时返回系统错误，不伪装成证据不足。
- V1 采用整问拒答，不输出未经支持的部分结论；在评测中计入可回答问题误拒答率。
- 不把 rerank_score 当概率或统一拒答阈值；若以后加入分数阈值，必须在验证集校准并记录配置。版本选择按 5.3 执行。

---

# 3.7 Tool Contract

核心知识能力必须封装为：

```python
class KnowledgeFilter(BaseModel):
    document_ids: list[str] | None = None
    file_types: list[Literal["docx", "pdf", "pptx", "xlsx"]] | None = None
    revision_ids: list[str] | None = None
    sheet: str | None = None

class SearchKnowledgeRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)
    filters: KnowledgeFilter = Field(default_factory=KnowledgeFilter)
    version_mode: Literal["latest", "explicit", "compare"] = "latest"

class SearchKnowledgeResponse(BaseModel):
    query: str
    results: list[FinalCandidate]
    trace_id: str
    snapshot_id: str
    degraded: bool = False
```

Tool 名：

```text
search_knowledge
```

用途：

- Code Review 查询需求、设计、编码规范；
- Engineering Agent 查询工程知识；
- 用户问答复用同一 Retrieval Core。

Tool 不直接绑定前端，也不经过 LLM Generation；它返回最终 Top-K 结构化检索结果。Generation 需要 Citation 时，再对这些 FinalCandidate 建立 request-local Source Binding。

所有外部请求模型禁止额外字段，并做严格类型校验；query 去除首尾空白后仍须非空。过滤字段之间 AND，列表内 OR；空列表和超过 100 项的列表无效，null 表示不限制。sheet 使用精确匹配，无该字段的文档不命中；revision_ids 与 version_mode 的约束见 5.3。
不接受任意 Elasticsearch DSL。两路在召回前执行同一过滤语义，禁止先 top_n 再过滤导致候选不足。Tool 返回检索结果，不宣称结果足以回答；空结果返回空列表，检索异常返回错误。

---

# 3.8 API Contracts

最小 API：

```text
POST /documents/ingest
GET  /documents/ingest/{job_id}
DELETE /documents/{document_id}
POST /query
POST /tools/search_knowledge
GET  /trace/{trace_id}
GET  /health
```

查询请求/响应：

```python
class QueryRequest(SearchKnowledgeRequest):
    pass

class QueryResponse(AnswerOutput):
    answer: str
    references: list[CitationReference]
    trace_id: str
    snapshot_id: str
    degraded: bool = False
```

QueryResponse.references 返回本次实际送入 Prompt 的 Source Binding；claims.source_ids 明确标出实际引用。未被 claim 引用的 Reference 不能展示为“支持该 claim 的引用”。拒答可带本次检索到的 Reference 供诊断，但 claims 为空。

入库采用异步任务，单请求单文件：multipart `file`，可选 `document_id`、`version`，必需 `Idempotency-Key` 请求头。不接受客户端任意本机路径或远程 URL。V1 默认文件上限 50 MiB，解包后上限 500 MiB，超限拒绝，数值属于运行初始配置。

```python
class IngestJobResponse(BaseModel):
    job_id: str
    document_id: str
    revision_id: str | None = None
    status: Literal["queued", "running", "succeeded", "failed"]
    stage: Literal["queued", "parse", "chunk", "index", "publish", "done"]
    snapshot_id: str | None = None
    error_code: str | None = None
    trace_id: str
```

- POST 入库持久化接收任务后返回 202；GET job 返回 200 和任务状态。业务成功只在 snapshot 发布后标记；failed 必须包含 error_code。
- 同一 Idempotency-Key 和相同文件哈希/参数返回原 job；不同负载返回 409。任务记录持久化，进程重启可恢复；不得只依赖进程内 background task。
- DELETE 文档通过相同任务模型返回 202，发布不含该文档的新快照；不直接边删边对外查询。删除不存在文档返回 404。
- DELETE 也要求 Idempotency-Key，幂等负载包含操作类型和 document_id。首次操作成功后以相同键重试仍返回原任务，不因文档已删除改成 404。
- `/query` 与 Tool 成功/拒答返回 200；系统错误按 3.9 返回非 2xx。`GET /trace` 未找到返回 404。`/health` 为 readiness，依赖不可用返回 503，不触发真实 LLM 调用。
- V1 部署限可信本机/内网；用户权限平台仍不在范围内。Trace 和原文不面向公共互联网开放。

---

# 3.9 Error Semantics

统一错误类型至少包括：

```text
UnsupportedFileType
ParseFailure
ChunkFailure
IndexFailure
RetrievalFailure
RerankFailure
GenerationFailure
CitationValidationFailure
InvalidFilter
ContextBudgetExceeded
InputTooLong
VersionConflict
DocumentNotFound
JobNotFound
TraceNotFound
DeadlineExceeded
QueueFull
```

原则：

- Parser Failure 不允许静默吞掉；
- 单文档失败不得破坏其他文档入库；
- 在线 Retrieval/Rerank 失败必须被 Trace；
- LLM 返回非法 Schema 不得直接透传前端。

```python
class ErrorResponse(BaseModel):
    code: str
    message: str
    retryable: bool
    trace_id: str
```

| 错误 | HTTP / 任务语义 |
|---|---|
| InvalidFilter / 请求 Schema 错误 | 422；无模型调用 |
| ContextBudgetExceeded / InputTooLong | 422；不能伪装成知识库无答案 |
| UnsupportedFileType / 超文件大小 | 415 / 413 |
| DocumentNotFound / JobNotFound / TraceNotFound | 404 |
| VersionConflict / 幂等键负载冲突 | 接收前发现为 409；已接受任务内发现版本冲突则 job failed |
| ParseFailure / ChunkFailure / IndexFailure | 已接收的异步 job 标记 failed，查询 job 本身仍为 200 |
| RetrievalFailure / 模型依赖不可用 | 503 |
| GenerationFailure / CitationValidationFailure | 上游响应不可用为 502；自身程序缺陷为 500 |
| DeadlineExceeded / QueueFull | 504 / 503 |

错误 message 不暴露密钥或堆栈。非 2xx 也必须产生 trace_id。BM25 或 Dense 任一路失败时 V1 整次检索失败，不用单路冒充 Hybrid；Reranker 允许按 4.4 降级并设置 degraded=true，降级结果仍执行同一证据验证。

---

# 4. Modules

# 4.1 Ingestion

## Responsibility

将原始文件转换成 `Chunk[]`。

## Inputs

```text
SourceDocument + local file
```

## Outputs

```text
list[Chunk]
```

## Internal Flow

```text
File
→ Type Detection
→ Format Parser
→ Parsed Structure
→ Format Chunker
→ Chunk Validation
→ Chunk[]
```

## Failure Cases

- 文件损坏；
- 不支持格式；
- Parser 输出空；
- 表格结构损坏；
- 无法恢复文本；
- Chunk content 为空；
- Chunk ID 冲突。

## Verification

- 四种文件 fixture 均能生成 Chunk；
- 每个 Chunk 能追溯回 document_id；
- 格式特定 metadata 正确；
- 相同输入重复解析结果稳定。

---

# 4.2 Indexing

## Responsibility

把统一 Chunk 建立为 BM25 与 Dense 两路索引。

## Inputs

```text
list[Chunk]
```

## Outputs

```text
Elasticsearch Snapshot Index
└── one ES document per Chunk
    ├── content      → BM25 inverted index
    ├── dense_vector → Dense vector index
    └── metadata / source fields
```

## Design

- V1 使用**同一个 Elasticsearch 物理索引**承载全文与向量检索，不维护两套独立事实存储；
- 每个 Chunk 对应一条 ES Document，至少保存 `chunk_id / document_id / revision_id / parse_artifact_id / content / dense_vector / chunk_index / source_spans / metadata`；
- `content` 建立全文倒排索引用于 BM25；同一 `content` 通过 BGE-M3 生成 `dense_vector` 并建立向量索引用于 Dense Retrieval；
- Embedding 是索引派生产物，只存在于 ES Index Document，不写回核心 `Chunk` Contract；
- BM25 与 Dense 通过同一 `chunk_id` 和同一 snapshot 保证候选来源一致；
- 具体 Elasticsearch 版本、向量维度、距离函数与过滤查询兼容性在 M1 验证并锁定，不默认认为任意版本均适用；
- metadata 必须支持过滤；
- 索引必须保存 document/version/hash 信息。

## Verification

- 同一 chunk_id 可从两类索引定位；
- 删除/更新文档时两类索引一致；
- metadata filter 行为一致。

索引构建/发布遵循 5.3；BM25 与 Dense 不单独发布。BM25 分析器必须通过中文文本、信号名、下划线标识符、故障码的固定 fixture 验证，并记录 analyzer 配置；精确术语字段与自然语言字段的权重由验证集选择。

---

# 4.3 Retrieval

## Responsibility

高召回地获取相关证据，并在进入 Cross-Encoder 前完成低成本候选融合和预算控制。

## Flow

```text
Query
├── BM25 Retrieve(Top-N)
└── Dense Retrieve(Top-N)
        ↓
    Union + Dedup
        ↓
       RRF
        ↓
   Candidate Top-M
```

## Design Decisions

- V1 所有普通 Query 默认 Hybrid；
- 不做 query_type switch-case；
- BM25 与 Dense 原始 score 不直接相加；
- RRF 不承担最终排序职责，而承担 `candidate fusion + candidate pruning / budget control`；
- RRF Top-M 才进入 Reranker，避免把两路完整候选并集全部交给 Cross-Encoder；
- 默认 `rrf_k=60`，但参数与 N/M/K 必须进入验证集实验和 Trace。

## Verification

- 单独 BM25 可运行；
- 单独 Dense 可运行；
- Hybrid 可运行；
- source rank 可追踪；
- duplicate chunk 可正确去重；
- RRF Top-M 截断稳定、确定；
- 相同候选输入和配置得到稳定融合顺序。

---

# 4.4 Reranking

## Responsibility

对 RRF Top-M 候选集进行高精度排序，并输出最终 Top-K。

## Model

```text
BGE-Reranker
```

## Rules

- 输入：Query + RRF Top-M Candidate Chunk；
- 输出：`FinalCandidate[]`，正常情况下包含 rerank_score + final rank；
- RRF 原排名决定候选是否进入 Top-M，但进入 Reranker 后不直接约束其内部最终顺序；
- 不允许全库 rerank；
- Reranker 失败时可以降级到 RRF 排序，但必须记录 Trace 且 `degraded=true`；
- 评测必须单独比较 RRF 前后与 Reranker 前后排序质量，不能用同一个指标混淆召回与精排职责。

---

# 4.5 Generation & Citation

## Responsibility

仅基于 Final Top-K Chunk 生成回答，并通过请求内 Source ID 绑定 Citation。

## Flow

```text
FinalCandidate Top-K
→ Source Binder
→ Prompt Builder
→ LLM
→ Structured Output
→ Citation Validator
→ Claim Verifier / Bounded Repair
→ Backend Source Mapping
→ Answer + References
```

## Rules

- Prompt 明确要求只基于提供的 Source；
- Source ID 由后端按请求生成，LLM 只能选择；
- Citation 后处理先做 Source ID allowlist 校验，再做 claim-support 语义校验；
- 文件名、版本、页码/Slide/Sheet、SourceSpan 只从 Chunk 回填，不从 LLM 输出采信；
- 无足够证据时拒答；
- 实际送入 Prompt 的 Source Binding 必须随 QueryResponse 返回；引用子集由 claims.source_ids 标明，未入选候选仅保存在 Trace。

---

# 4.6 Evaluation

## Responsibility

证明修改真的改善系统，而不是凭主观判断。

## Dataset Schema

```python
class GoldAnchor(BaseModel):
    anchor_id: str
    document_id: str
    revision_id: str
    parse_artifact_id: str
    source_spans: list[SourceSpan] = Field(min_length=1)

class EvidenceGroup(BaseModel):
    group_id: str
    alternatives: list[GoldAnchor] = Field(min_length=1)

class EvalCase(BaseModel):
    case_id: str
    question: str
    reference_answer: str | None
    required_facts: list[str]
    evidence_groups: list[EvidenceGroup]
    answerable: bool
    expected_refusal_reason: Literal[
        "insufficient_evidence", "version_conflict", "unsupported_claim"
    ] | None = None
    question_type: str
    filters: KnowledgeFilter = Field(default_factory=KnowledgeFilter)
    version_mode: Literal["latest", "explicit", "compare"] = "latest"
    corpus_manifest_id: str
```

- GoldAnchor 标注在冻结修订的原文/解析产物位置，不绑定某个 Chunk ID。一个 group 内 alternatives 是等价证据（OR），多个 group 是回答所需的证据组合（AND）。
- answerable=true 时 reference_answer、required_facts 和 evidence_groups 非空、expected_refusal_reason=null；false 时 reference_answer=null、required_facts/evidence_groups 为空、expected_refusal_reason 必填，并人工确认在指定语料、过滤和版本范围内确实不可回答。版本冲突导致不可回答的题目需另附标注说明和矛盾原文，不能误标为“没有检索结果”。
- 测试集冻结 corpus_manifest（文件哈希、revision、parse artifact）、问题、原文锚点、评分事实和版本选择。仅 changing chunking 时复用同一解析产物，按 source_spans 重新映射，不能重写标签。
- 一个 anchor 被覆盖是指 Top-K 实际返回 content 的来源区间并集完整覆盖该 anchor 的全部 spans；仅命中文档或元数据不足以算命中。跨多个 Chunk 覆盖允许合并重叠区间，不能重复计数。一个 group 命中需覆盖至少一个 alternative。
- 映射结果可缓存 relevant_chunk_ids 作为实验派生数据，但不是 Ground Truth。更换 Parser 的实验需单独建立原文到新解析产物的人工核对映射；不能混入分块消融。

## Dataset Protocol

- 先建立开发 fixtures；验证集用于调参，冻结测试集只用于最终评测。按源文档族/业务案例分组切分，近重复问题、同一案例的不同表述不能跨验证/测试集合泄漏。
- V1 初始发布目标：测试集至少 120 题，其中至少 80 道可回答题、40 道不可回答题；四种格式各至少 15 道可回答题。版本冲突、精确术语、语义改写、历史失效、多证据各至少 10 题，类别可重叠。数量是目标，非现有数据规模。
- 每道测试题核对原文证据与 required_facts；歧义标签先裁决再冻结。无可用真实语料时可用脱敏/合成 fixtures 开发，但不能据此宣称真实汽车研发业务效果。
- `validation_build/protocols/development.json` 固定样本划分、指标定义、模型/Prompt/配置版本、人工评分规程与 6.7 的门槛；测试解封前冻结并记录哈希。未填写或未冻结不能发布。
- 查看测试结果后若据此改配置或修标签，原测试集转为开发数据；新的发布结论需要新的未参与调参的冻结保留集。失败结果可以如实报告，不得通过事后降低门槛改判通过。

## Retrieval Metrics

Retrieval / Fusion 主指标：

```text
EvidenceGroupRecall@K
CompleteEvidence@K
```

其中：

- BM25 / Dense 单路主要看 Recall@N；
- RRF 主要看 Top-M 候选是否保持/提升证据覆盖，不能只看最终 Top-K；
- Latency、候选数量与去重率作为诊断指标。

## Reranking Metrics

Reranker 主指标：

```text
nDCG@K
```

诊断指标：

```text
MRR
Precision@K
Recall@K
Reranker Latency
```

nDCG 使用冻结 relevance judgment；若只有二元相关性标签，则使用 binary gain 并在报告中明确，不把它包装成分级相关性。

排序评分协议（与原文 GoldAnchor 分开保存为实验派生标注）：

- 同一分块配置下，先固定所有待比较路径及参数，取各路径召回候选的并集作为每题共同 judgment pool；B0/B1/B2 的待评分结果也必须包含在内。标注人员依据原文判断相关性，隐藏路径名称、分数及排序；不得为每条路径分别选择 IDCG 候选池。
- 原文 GoldAnchor 始终是跨分块事实依据；judgment 文件以 case_id、chunk_id、chunk_config_hash、relevance、reviewer 记录该实验的派生评分。更换分块配置须重新映射并复核，不能复用旧 Chunk 标签；跨分块结论以原文证据覆盖和生成质量为主，nDCG 需同时声明候选粒度变化。
- 默认 binary relevance 为 0/1：Chunk 实际文本是否提供至少一项 required_fact 的有效支持片段（可为联合证据的一部分）。若采用分级评分，须事先冻结等级定义。`gain = 2**relevance - 1`，`DCG@K = Σ gain_i / log2(i+1)`；IDCG 为共同已标注池按 relevance 降序的前 K 项 DCG。
- 每题 `nDCG@K = DCG@K / IDCG@K`；可回答题中 IDCG=0 记 0，并另报零相关候选池题数，不能剔除这类召回失败。结果不足 K 按缺失位置 gain=0 处理；Precision@K 为前 K 中 relevance>0 的数量除以 K。两者对可回答题宏平均，无答案题单独统计。
- 所有被评分候选必须完成标注；存在未标注项则评分不完整，禁止据此发布。协议、路径配置先冻结；保留集标注由评测方在不反馈调参的条件下完成，再锁定 judgment 哈希并评分。查看评分后调整系统仍适用测试集转为开发数据的规则。


## Generation Metrics

```text
Correctness
Faithfulness
Citation Correctness
FalseAnswerRate / FalseRefusalRate
```

`Refusal Accuracy` 可作为汇总辅助指标，但不替代 FalseAnswerRate 与 FalseRefusalRate。

LLM-as-Judge 可辅助，但必须进行人工抽样复核。

指标计算口径：

- 核心 `EvidenceGroupRecall@K`：每道可回答题命中的 group 数 / 所需 group 数，再对题目宏平均；报告中可简称 Recall@K，但必须声明此口径，不能与按 Chunk 计数的 Recall 混用。Retriever/Fusion 重点报告各自候选预算 N/M；最终 Top-K 另行报告。
- `CompleteEvidence@K`：全部必需 group 均命中的可回答题比例。`MRR` 作为排序诊断指标，使用首次完整覆盖任一 group 的前缀排名倒数，无命中记 0；多证据题同时报告 CompleteEvidence，不能用 MRR 代替完整性。
- `nDCG@K` 是 Reranker 的主排序指标。冻结评测集必须为进入 Reranker 的候选建立 relevance judgment；有分级标签时使用 graded gain，仅有二元标签时使用 binary gain 并明确口径。Precision@K、MRR、Recall@K 作为诊断；不得把未标注 Chunk 默认判成无关。无答案题不参与 Recall/MRR/nDCG 分母。
- `Correctness`：可回答题中完整覆盖 required_facts 且无错误事实的比例；误拒答记错。`Faithfulness`：非拒答输出中受到引用原文支持的原子事实数 / 全部原子事实数；无非拒答输出记 N/A，不可记满分。
- `Citation Correctness`：引用 claim 与对应来源存在、版本正确且语义支持的有效配对数 / 全部 claim-citation 配对数。多证据共同支持的 claim 先判断引用集合是否联合支持，再检查各引用是否提供相应支持片段，不要求每条引用独立证明完整结论。另报引用覆盖率（有有效引用的原子事实比例）；未知 ID 单独计数，不与语义支持混为一谈。
- `FalseAnswerRate`：无答案题中非拒答的比例；`FalseRefusalRate`：可回答题中拒答的比例。Refusal Accuracy 仅辅助报告，不能掩盖两类错误。
- 系统错误、超时、降级独立报告；系统错误不可按正确拒答计分，端到端 Correctness 分母不剔除错误请求。另报非 2xx 比例和各类比例的样本数/95% 区间。
- 发布评测对完整测试集输出进行人工评分并保存记录；第二人复核至少 20%，覆盖各类别及所有分歧/高风险数值结论并裁决。开发阶段可使用 LLM Judge，记录模型、Prompt、温度、重复次数及与人工评分的差异。
- 报告逐题配对差值及各类别结果；优势不明确时写“尚未证实提升”，不把总体平均小幅变化等同于所有场景改善。

---

# 4.7 Trace / Observability

每次 Query 至少记录：

```text
trace_id
query
filters
bm25 candidates + ranks
dense candidates + ranks
rrf result
reranker result
top context
source map (source_id → chunk_id)
llm structured output
final answer
refused
latency by stage
errors / fallback
snapshot_id / corpus_manifest_id
revision_ids / parse_artifact_ids
config_hash / model revisions / prompt hashes
候选及上下文 token 数 / 被预算排除的 Chunk 及原因
claim / citation validation results / repair attempts
degraded / timeout / usage tokens
```

Trace 是 Bad Case 分析和面试可解释性的必要条件。

Trace 从最小服务层开始实现，CLI、Tool 和 HTTP 共享同一埋点。持久化采用 SQLite（WAL，单机 V1），同库保存入库 job、发布 manifest 和活动快照指针。原文件/解析产物使用 Docker 持久卷。默认 Trace 保留 30 天，评测 Trace 随实验归档；不记录密钥，原文内容按可信本机/内网边界访问。

---

# 4.8 Runtime Interface

## FastAPI

负责：

- 文档入库；
- Query；
- Tool；
- Trace 查询；
- Health Check。

## Docker

至少包含：

- application；
- Elasticsearch；
- SQLite 数据库文件、原文/解析产物持久卷；
- 必要配置；
- README 启动说明。

# 4.9 Runtime Configuration & Budgets

以下为待验证的初始配置，不是硬件性能承诺。配置进入版本控制，模型/运行环境 manifest 必须在首次基线前锁定。

| 配置 | V1 初始值 / 约束 |
|---|---|
| Embedding 模型 | `BAAI/bge-m3`；仅使用 dense 输出 |
| Reranker 模型 | `BAAI/bge-reranker-v2-m3`，锁定模型 revision |
| 模型/软件锁定 | Parser、Embedding、Reranker、LLM、Verifier、tokenizer、Python、依赖锁文件和 Elasticsearch 镜像版本/摘要写入 manifest；LLM/Verifier 必须显式配置，不用浮动别名宣称可复现 |
| Chunk budget | 512 tokens；使用锁定 Embedding tokenizer；字符数不能代替 token 数 |
| BM25 / Dense Top-N | 各 50；候选不足返回实际数量，不填充重复项 |
| RRF | `k=60`；rank 从 1 开始；按 chunk_id 去重，相同分数用 chunk_id 排序 |
| RRF Top-M | 默认 50；用于候选融合后的 pruning / reranker budget control |
| Reranker | 输入 RRF Top-M，batch_size 初值 8；输出 Final Top-K；吞吐和显存实测后调参 |
| Final Top-K | 默认 5，范围 1–20；Tool 与 Query 共用 Retrieval Core 的 N/M/K 预算；LLM Context Builder 预算仅适用于 Query |
| 上下文预算 | LLM tokenizer 下证据总量最多 6000 tokens，输出预留 1500；连同系统 Prompt/Query 必须低于所选模型实际上限 |
| 输入上限处理 | 同时校验 Embedding 输入及 Reranker 的 Query+Chunk 输入。模型实际最大长度从锁定配置验证；超限不得静默截断 |
| 在线超时 | BM25/Dense 各 5 s，Reranker 10 s，单次生成/验证调用各 30 s，总 deadline 90 s，纠正调用也受总 deadline 约束 |
| 任务资源 | 每进程在线执行上限 2，等待队列上限 20，满载返回 503；入库 worker=1，单文件 deadline 初值 600 s |

模型兼容性预检属于 M1：验证本机硬件、模型加载、向量维度/归一化及距离函数、过滤查询、最大输入、中文/工程术语样例。检查失败必须调整并锁定配置后再形成基线，不把表中初值当作已验证兼容性。

Tool 返回完整 Final Top-K，不加载 LLM tokenizer，也不执行 LLM 上下文裁剪。Query 的 Context Builder 按 Final Top-K 排序依次选择完整 Chunk；加入某块超预算时跳过并记录，继续考察后续候选，实际送入 Prompt 的 Source 数量可少于请求 top_k。候选非空但无块可容纳时返回 `ContextBudgetExceeded`（422），不当作知识库无答案；候选原本为空按 3.6/3.7 的空检索规则处理。Embedding 或 Reranker Query 输入本身超限同样返回 `InputTooLong`（422）。
长 Chunk 在入库阶段按所有固定模型约束细分；线上遇到超限旧索引时标记索引不兼容并要求重建，不直接截断。Reranker 失败可降级，但配置不兼容不是正常降级路径。

离线与在线模型共享硬件时采用资源信号量，优先在线请求；阻塞推理不直接运行在异步 Web event loop 内。记录硬件、冷/热启动、并发、语料规模和 token 用量，分别报告检索与整体请求 p50/p95。

`validation_build/protocols/development.json` 还须填写目标硬件、规模、并发和检索/整体 p95 上限（毫秒）。性能门槛可在验证集预跑后确定，但必须在测试解封前冻结；缺值阻止发布，不能用 90 s 故障 deadline 代替性能目标。

---

# 5. System Invariants

## 5.1 Citation / Source Rules

1. 不存在于本次请求 Source Map 的 Source ID 不能通过校验或进入成功响应；
2. 所有 Citation 必须可从 `source_id → FinalCandidate → chunk_id → revision_id / parse_artifact_id → source_spans → 原文件位置` 回溯；
3. 检索证据不足必须允许拒答；
4. Prompt 中的 Source 内容与 Citation 回填来源必须来自同一个 Chunk；
5. Source ID 合法与语义支持分别校验；关键事实只能由通过校验的 claims 渲染，不能附加未验证的自由答案；
6. Source ID 是请求内引用标识，不得持久化为第二套知识事实实体。

## 5.2 Determinism Rules

1. 同一版本文件 + 同一 Parser/Chunk Config，应生成稳定 Chunk 顺序；
2. Chunk ID 生成策略必须确定；
3. Eval Test Set 冻结后不得边调参边修改标签；
4. Baseline / Ablation 需要固定 Dataset、Prompt、LLM 与随机性设置。

## 5.3 Version Consistency

1. 文档必须具有 `content_hash`；
2. 内容更新仅对变化文档重新解析/分块/Embedding；查询发布按完整快照切换，不原地增量覆盖活动索引；
3. Chunk 策略变化可触发全量重建；
4. 查询结果必须能识别来源版本；
5. 旧版本保留/删除策略必须显式配置。

### 5.3.1 Snapshot Publish Protocol

V1 采用单入库 worker + 不可变完整快照，优先正确性，不实现跨服务分布式事务。

阶段能力约束：M4 允许仅供开发/评测的 `retrieval_profile=bm25_only` 快照，manifest 显式记录 profile；该阶段不要求 dense_vector，只验证 BM25、来源和过滤字段。M5 起完整服务使用 `retrieval_profile=hybrid`，必须验证以下全部双路规则。BM25-only 快照不能作为 Hybrid 服务的活动快照，尝试 Hybrid 查询返回 RetrievalFailure；切换到 M5 时补全向量、验证并发布新的 Hybrid 快照。B0 是显式单路实验，可在 Hybrid 快照上运行，不构成线上单路降级。


1. 基于当前快照构建新 `snapshot_id`，manifest 保存全部保留的文档修订/Chunk 和每个文档的 current revision。新文件修订只有发布成功后才成为 current；不按业务 version 字符串比较大小。
2. 在新的 Elasticsearch 物理索引写入完整快照。未变化 Chunk 可从旧快照复制并复用相同模型 revision 的向量；新/变化 Chunk 必须同时具备 BM25 文本、向量、过滤字段、来源定位和 current 标记。
3. 构建后 refresh 并检查文档数量、Chunk ID 集合哈希、向量维度、缺字段和两路过滤 fixture；全部通过才标记 ready。任何失败使 job failed，新索引不发布，旧快照继续服务。
4. SQLite 事务内以预期旧指针做 compare-and-swap，更新活动快照指针并将 job 标记 succeeded。CAS 冲突则重新基于最新快照构建，禁止覆盖另一已发布结果。
5. 查询开始只读取一次活动物理索引名并持有快照 lease；BM25、Dense、来源读取都使用这一名字，不能在请求中途重新读取活动指针。Trace 保存 snapshot_id。
6. 进程重启扫描 queued/running 任务：根据幂等键、构建状态和持久化指针恢复/重试。尚未发布的物理索引可回收；不得删除指针仍引用的索引。
7. 默认在活动快照中保留历史修订，但普通知识查询只检索 current；DELETE 发布的新快照不含该文档任何修订。原文件在没有活动/保留快照和评测档案引用前不物理清除。
8. 旧快照至少保留 24 小时供回滚，且有在途 lease 或评测引用时不可回收；24 小时是运维默认值，可调整。GC 和获取 lease 使用协调锁；回滚同样以事务切换指针，不能修改不可变旧索引。

### 5.3.2 Query Version Policy

- `latest`：默认；revision_ids 必须省略或为 null（空列表仍是非法过滤），只查询快照中每个文档标记的 current 修订。
- `explicit`：必须提供非空 revision_ids，只检索指定修订；指定修订在当前快照中不存在返回 404，不退回最新版本。
- `compare`：必须提供至少两个 revision_ids，允许版本对照；输出 claim 必须明确各自修订/业务标签及差异，不能把互相矛盾的值合成一个值。
- 所有模式均与其他 filters 取交集。对普通问答，在选定范围内出现无法消解的直接冲突时拒答 `version_conflict`；不能让 LLM 自行选“看起来最新”的证据。
- 历史评测通过公开服务层的 `evaluate(request, snapshot_id)` 固定保留快照，不依赖在线 current 指针。该入口不暴露为面向普通调用方的任意索引访问接口。

## 5.4 Failure / Refusal Rules

- Parse Failure ≠ 空文档；
- Retrieval Failure ≠ 无答案；
- “没有检索到充分证据”与“系统异常”必须区分；
- LLM Schema Invalid 必须重试或失败，不可伪装成功。

## 5.5 Dependency Constraints

- Ingestion 不导入 Web/UI 代码；
- Core Retrieval 不依赖 Agent；
- Agent/Code Review 只能通过 Tool Contract 复用知识能力；
- Evaluation 不写死具体实现内部状态。

---

# 6. Verification

# 6.1 Unit Verification

必须覆盖：

- document identity/hash；
- DOCX parser；
- PDF parser adapter；
- PPTX parser；
- XLSX parser；
- 四类 chunker；
- chunk validation；
- RRF；
- metadata filter；
- source ID allowlist / citation mapping validation；
- refusal policy；
- Pydantic schema validation。

还必须覆盖：SourceSpan 越界/不存在/跨修订、空 metadata、跨字段拒答约束、引用真实 ID 但错误数值/单位/否定条件、未知过滤字段/空列表/非法 top_k、上下文预算、长表格尾部信息、版本模式、GoldAnchor 跨块覆盖与重复区间计数。

# 6.2 Integration Verification

至少存在以下端到端测试：

```text
DOCX → Parse → Chunk → Index → Query → FinalCandidate
PDF  → Parse → Chunk → Index → Query → FinalCandidate
PPTX → Parse → Chunk → Index → Query → FinalCandidate
XLSX → Parse → Chunk → Index → Query → FinalCandidate
```

以及：

```text
Query → BM25 + Dense → RRF → Reranker → LLM → Citation
```

故障注入必须覆盖：

- 新索引部分写入失败后，旧快照的两路查询仍一致；
- 发布前后进程重启、相同幂等键重试、发布指针冲突；
- 请求进行中发布新快照，当前请求仍只读旧快照；旧快照有 lease 时 GC 不删除；
- 文档更新/删除/回滚后，两路召回及来源定位与 manifest 一致；
- Reranker 降级仍保留 degraded/Trace，检索失败不返回成功拒答；
- Schema 错误、伪造引用、正确 ID 错误结论、Verifier 超时、纠正次数耗尽；
- 输入资料含诱导修改系统规则的文本时，不执行其指令；
- 过大文件、并发队列满、超时、空上下文均返回约定结果。

确定性 fixture 可使用模型替身；发布前至少运行一次锁定真实模型和 Elasticsearch 的端到端验收，替身测试不作为模型效果证据。

# 6.3 Retrieval Evaluation

## Baseline

至少比较：

```text
B0: BM25
B1: Dense
B2: Hybrid (BM25 + Dense + RRF Top-M)
B3a: BM25 + Dense → Union + Dedup → Reranker → Top-K
B3b: BM25 + Dense → RRF Top-M → Reranker → Top-K   # V1 默认链路
```

Baseline 回答：

> 最终复杂方案是否比简单方案更好？RRF 在 Reranker 前是否通过更小候选预算获得可接受或更好的排序质量与延迟？

必须同时保存：

- Retrieval/Fusion：EvidenceGroupRecall@N/M、CompleteEvidence@N/M；
- Reranker：nDCG@K、MRR、Precision@K；
- 两条 Reranker 路径的实际候选数量与 Reranker latency；
- Final Top-K 的来源覆盖与最终 Generation 输入 token 数。

---

# 6.4 Ablation

至少进行：

```text
A0: Full System (RRF + Reranker)
A1: - Dense
A2: - Reranker
A3: - Structure-aware Chunking
A4: RRF + Reranker → Union + Dedup + Reranker
```

其中 A4 是 RRF 专项消融：

```text
BM25 Top-N + Dense Top-N
├── Union + Dedup → Reranker → Top-K
└── RRF Top-M    → Reranker → Top-K
```

必须比较：

```text
nDCG@K
MRR
Precision@K
候选数量
Reranker latency
E2E latency
```

Ablation 回答：

> 最终效果提升究竟来自哪个模块？RRF 的候选融合与预算控制是否在质量/成本之间提供了实际价值？

所有实验必须固定：

- Test Set / Validation Set 按用途区分；
- Prompt；
- LLM；
- Final Top-K；
- BM25 / Dense Top-N；
- 除目标变量外的其他配置。

分块消融固定原文件、解析产物、原文 GoldAnchor、模型和最终上下文 token 总预算；各策略分别生成 Chunk 与锚点映射。top_k 相同不等于文本量相同，因此必须同时报告实际 context tokens 和输入覆盖率。
Reranker 消融固定召回及融合候选集；Embedding 消融以 BM25-only + 相同后续模块对照。RRF 专项消融固定两路 Top-N、Reranker 模型、Final Top-K 与硬件，并同时报告 Union 候选数和 RRF Top-M 候选数，不能只比较质量而忽略计算预算。
候选 Top-N/Top-M/Top-K、RRF k、tokenizer、软件/模型 revision、Verifier、硬件和配置哈希写入实验 manifest。记录随机种子与生成参数，但不承诺外部模型服务逐字确定性。

---

# 6.5 Generation Evaluation

至少包含：

- answerable query；
- unanswerable query；
- conflicting version query；
- precise engineering term query；
- semantic paraphrase query；
- history failure case query。

# 6.6 Bad Case Taxonomy

统一分类：

```text
Parse Failure
Chunk Boundary
Metadata Error
Recall Miss
Fusion / Rank Error
Rerank Error
Context Noise
Generation Hallucination
Citation Error
Should-refuse-but-answered
Should-answer-but-refused
```

# 6.7 Acceptance Gates

发布 V1 前必须满足：

- 所有核心 pytest 通过；
- 四种格式端到端通过；
- Baseline 可复现；
- Ablation 可运行；
- Test Set 冻结；
- Citation Source ID 无伪造且来源可回溯；
- Unanswerable Query 可拒答；
- Trace 可定位一次完整请求；
- Tool 可独立调用；
- README 可让另一台机器完成启动。

以上是功能门槛，发布还必须同时满足下表。数值均为 **V1 初始 Target，尚未实测**，可在验证阶段调整；最终值必须在解封测试集前写入冻结的 `validation_build/protocols/development.json`。不得以测试失败为由事后降低标准。

| 质量项 | 初始发布目标 | 计分口径 |
|---|---|---|
| EvidenceGroupRecall@5 | ≥ 0.85 | 可回答题宏平均，见 4.6 |
| CompleteEvidence@5 | ≥ 0.75 | 全部必需证据组均覆盖 |
| Reranker nDCG@5 | ≥ B2，且与 B3a 的允许差值写入冻结协议 | Reranker 主排序指标；binary/graded gain 口径必须固定 |
| Correctness | ≥ 0.80 | 可回答题，拒答/系统错误不剔除 |
| Faithfulness | ≥ 0.95 | 人工事实支持标注；N/A 不通过 |
| Citation Correctness / 覆盖率 | 均 ≥ 0.95 | 人工语义与来源核对 |
| FalseAnswerRate | ≤ 0.05 | 无答案题错误作答比例 |
| FalseRefusalRate | ≤ 0.15 | 可回答题误拒答比例 |
| 无效引用/源位置 | 0 个进入成功输出 | 在本次验收集上的观测值，不代表所有未来输入绝对为零 |
| 系统错误率 | ≤ 0.01 | 本次测试全部请求的非 2xx 比例 |
| 性能 | 满足冻结协议的两个 p95 上限 | 指定硬件、规模和并发；缺值不通过 |

四种格式及关键问题类型分别报告样本量与结果；任一类别 Correctness < 0.60 阻止发布，不能用总体平均掩盖明显失效。报告 95% 区间和小样本限制；门槛针对本次点估计，不宣称统计保证。

复杂度决策：V1 默认链路 B3b（RRF + Reranker）至少不得低于 B0/B1 中较优者的 EvidenceGroupRecall@5，并满足 Reranker nDCG@5 与性能门槛。B3b 还必须与 B3a（Union + Reranker）同时报告质量、候选数量和延迟；若 RRF 导致实质质量退化，则阻止发布并调整 N/M/k 或实现，不能仅因“链路更完整”判定通过。只有配对实验支持时才宣称提升，未证实的提升不写成成果。

---

# 7. Execution Plan

# 7.1 Development Order

按依赖关系开发，不按 UI 开发；Evaluation 与 Trace 从 M0/M1 贯穿后续里程碑。

```text
M0  开发 fixtures / 验证集草案 / 原文锚点 / 评测协议草案

M1  Core Models / Config / 模型兼容性预检 / 最小 Trace
    依赖锁定 / Linux Container Skeleton / 公共服务层骨架

M2  DOCX + XLSX Parser / 定位目录 / 原文与 Parse Artifact 存储

M3  DOCX + XLSX Chunker / SourceSpan Validation

M4  BM25 Index / Retrieve
    最小 Snapshot Build + Validate + Publish
    第一份 B0 Retrieval Evaluation

M5  Dense Index / Retrieve / B1 Evaluation
    完整 Snapshot 发布
    Update / Delete / Rollback / Failure Recovery

M6  RRF / Candidate Fusion + Top-M Budget
    B0-B2 对照与 RRF 参数/候选窗口验证

M7  Reranker / Final Top-K
    B3a Union+Reranker vs B3b RRF+Reranker
    search_knowledge Tool 实现
    第一里程碑验收

M8  Source Binding / Claims / Generation
    Citation Validation / Verifier / Refusal
    Generation Evaluation

M9  PDF + PPTX Parser/Chunker
    四格式端到端 / 四格式 Version + Citation 验收

M10 FastAPI / 持久化入库任务 / Trace 查询
    资源限额 / Queue / Timeout

M11 冻结测试协议与测试集
    Final Baseline + Ablation / 人工评测 / Bad Case / Performance

M12 最终 Docker Compose / 持久卷
    第二台机器启动 / 发布门槛 / README / 最终实测报告
```

执行原则：

- M4 第一次真实写入 Elasticsearch 时就建立最小不可变 Snapshot 发布链路，避免 M5 再返工 Indexing；
- M5 在 Dense 接入时把双路一致性、更新、删除、回滚和故障恢复一起闭环；M9 只验证这套版本机制对新增 PDF/PPTX 同样成立；
- `search_knowledge` Contract 已在第 3.7 节冻结，M7 在 Reranker/FinalCandidate 稳定后实现 Tool，避免 M6 提前绑定未完成的 Retrieval Core；
- Docker/容器分两层：M1 解决依赖锁定和 Linux Container Skeleton，M12 才做最终 Compose、持久化卷与 clean-machine 交付；
- M11 是最终发布评测，不是首次实现 Evaluation；每增加一个模块，都在验证集比较前后结果；
- M1 公共服务层可被 CLI/pytest 调用，M10 HTTP 仅包装同一逻辑，遵守“Evaluation 通过公开接口”的依赖规则。

# 7.2 Current Milestone

第一里程碑只要求打通：

```text
DOCX + XLSX
→ Unified Chunk
→ Single Elasticsearch Snapshot
→ BM25 Top-N + Dense Top-N
→ RRF Top-M
→ Reranker Final Top-K
→ search_knowledge Tool
```

Generation / Citation 在 M8 进入第二闭环，再补 PDF / PPTX，避免四种解析器同时展开导致项目无法闭环。

第一里程碑还必须交付：

- 至少 20 道带原文锚点的开发/验证问题（不充当冻结发布测试集）；
- B0 / B1 / B2 / B3a / B3b 检索结果；
- 逐阶段 Trace，包含 N/M/K、RRF k、候选数量、rank/score 与 latency；
- 稳定来源定位；
- 最小 Snapshot 构建/发布；
- 重复入库幂等、更新/删除、失败不发布、回滚基础测试；
- `search_knowledge` 可通过公共服务层独立调用。

此时只能说明**检索与 Tool 链路已打通**，不能声明 Generation/Citation 质量或 V1 发布完成。

# 7.3 Development Progress

最后更新：2026-09-09。

当前阶段：开发准备。DEV_SPEC v1.4 的规格修订已完成；已有 40 题修订合成开发集、12 题独立文档族验证草案、评测协议草案及原文/分组校验器。旧 20 题作为历史夹具保留，不能重复计为独立数据。人工复核待完成，尚无应用实现、冻结测试集或模型实测报告。以下状态以本仓库可核查产物为准，规格中的模型示例不计为功能实现。

状态：**未开始 → 进行中 → 待验收 → 已完成**；遇到无法继续的问题标记 **阻塞**，同时写明原因和解除条件。只有满足第 8 章 DoD 且提供验收依据，才能标记已完成。

| 阶段 | 主要交付物 | 待完成文件/模块 | 完成所需验收依据 | 当前状态 | 实际产物 / 验证记录 |
|---|---|---|---|---|---|
| M0 评测准备 | 开发 fixtures、原文锚点、验证集及评测协议草案 | `validation_build/**`、`scripts/validation_build/validate_dataset.py`、`scripts/validation_build/validate_suite.py`、`tests/unit/validation_build/**`、`tests/fixtures/answer_quality/**`、`docs/reviews/**` | 锚点可定位；可回答/不可回答标签经核对；数据划分明确 | 进行中 | validation_build/README.md：40 题 dev + 12 题 validation 草案；原文/分组校验及校验器回归测试通过；人工复核、真实候选标注待完成 |
| M1 工程基础 | 核心模型、配置、模型预检、最小 Trace、依赖锁定、Linux Container Skeleton、公共服务层 | `pyproject.toml`、`uv.lock`、`.env.example`、`configs/default.yaml`、`configs/logging.yaml`、`src/engineering_rag/bootstrap.py`、`src/engineering_rag/contracts/{source,chunk,retrieval,evaluation,errors}.py`、`src/engineering_rag/config/{settings,paths,config_logging,preflight}.py`、`src/engineering_rag/observability/{trace,trace_logging}.py`、`src/engineering_rag/services/{document_service,query_service}.py`、`src/engineering_rag/storage/{local_files,sqlite,repositories}.py`、`deploy/{Dockerfile,compose.yaml}`、`scripts/dev/dev_preflight.py`、`tests/unit/{contracts,config,observability,services,storage}/**` | Schema 验证、配置加载、模型兼容性预检、容器骨架启动和 Trace 测试记录 | 进行中 | 工程骨架、配置样例、Docker/Compose 骨架和开发脚本已创建；所有函数具备三单引号 docstring；uv 已配置 dev 依赖组并生成 `uv.lock`；Python 3.12 `.venv` 已安装项目及开发依赖，14 项资料校验器 pytest 回归测试通过；模型/ES 预检和 M1 业务单元测试待完成 |
| M2 DOCX/XLSX 解析 | 两类 Parser、定位目录、原文与解析产物存储 | `src/engineering_rag/ingestion/dispatcher.py`、`src/engineering_rag/ingestion/parsers/{parser_base,parser_docx,parser_xlsx}.py`、`src/engineering_rag/storage/{local_files,repositories,manifests}.py`、`src/engineering_rag/services/document_service.py`、`scripts/dev/ingest_local.py`、`tests/unit/ingestion/parsers/**`、`tests/fixtures/documents/{docx,xlsx}/**` | 两类正常/异常 fixture 通过；原文位置可回溯 | 未开始 | — |
| M3 DOCX/XLSX 分块 | 两类 Chunker、SourceSpan 校验、超长记录处理 | `src/engineering_rag/contracts/chunk.py`、`src/engineering_rag/ingestion/chunkers/{chunker_base,chunker_docx,chunker_xlsx}.py`、`src/engineering_rag/ingestion/dispatcher.py`、`tests/unit/ingestion/chunkers/**`、`tests/fixtures/chunking/**` | 分块稳定性、边界、来源映射和长记录尾部测试通过 | 未开始 | — |
| M4 BM25 | 全文索引、检索、最小 Snapshot Build/Publish、B0 评测报告 | `configs/evaluation.yaml`、`src/engineering_rag/indexing/{es_client,mappings,snapshots}.py`、`src/engineering_rag/retrieval/{bm25,service}.py`、`src/engineering_rag/services/{snapshot_service,evaluation_service}.py`、`src/engineering_rag/evaluation/{datasets,anchor_mapping,metrics,runner,reports}.py`、`scripts/experiments/run_experiment.py`、`tests/integration/{indexing,retrieval}/**` | 中文/精确术语/过滤测试通过；首份验证集检索结果可复现；最小快照可验证后发布 | 未开始 | — |
| M5 Dense 与生命周期 | 向量索引、检索、完整快照、Update/Delete/Rollback/Recovery | `src/engineering_rag/indexing/{embeddings,mappings,snapshots,lifecycle}.py`、`src/engineering_rag/retrieval/dense.py`、`src/engineering_rag/config/preflight.py`、`src/engineering_rag/services/{document_service,snapshot_service}.py`、`src/engineering_rag/storage/{repositories,manifests}.py`、`tests/integration/{dense,lifecycle,snapshot}/**` | B1 结果；双路一致性、幂等、更新删除、失败不发布、回滚及重启恢复测试 | 未开始 | — |
| M6 RRF | 融合、去重、Top-M Candidate Budget、B0–B2 对照 | `src/engineering_rag/retrieval/{fusion,service}.py`、`src/engineering_rag/contracts/retrieval.py`、`src/engineering_rag/observability/trace_metrics.py`、`src/engineering_rag/evaluation/{evaluation_metrics,runner,reports}.py`、`tests/unit/retrieval/test_fusion.py`、`tests/integration/retrieval/test_hybrid_budget.py` | RRF/过滤测试；N/M/k 配置可追踪；B0–B2 对照可复现 | 未开始 | — |
| M7 Reranker 与 Tool | 精排、降级、B3a/B3b、search_knowledge、第一里程碑报告 | `src/engineering_rag/retrieval/{reranker,service}.py`、`src/engineering_rag/tools/search_knowledge.py`、`src/engineering_rag/services/query_service.py`、`src/engineering_rag/contracts/retrieval.py`、`src/engineering_rag/evaluation/{evaluation_metrics,runner,reports}.py`、`tests/unit/{retrieval,tools}/**`、`tests/integration/tools/test_search_knowledge.py`、`docs/reports/milestone-1.md` | Union+Reranker vs RRF+Reranker 对照；Tool 可独立调用；降级 Trace；第 7.2 节全部交付物齐备 | 未开始 | — |
| M8 生成与 Citation | Source Binding、Claims、生成、Citation/语义验证、有限纠正、拒答 | `src/engineering_rag/contracts/generation.py`、`src/engineering_rag/generation/{context,source_binding,claims,llm,verifier,refusal}.py`、`src/engineering_rag/services/query_service.py`、`src/engineering_rag/evaluation/{evaluation_metrics,runner,reports}.py`、`tests/unit/generation/**`、`tests/e2e/test_generation_eval.py` | Source ID/引用/数值/版本/拒答及模型异常测试；验证集生成结果 | 未开始 | — |
| M9 PDF/PPTX 扩展 | 两类 Parser/Chunker、四格式端到端与版本/Citation场景 | `src/engineering_rag/ingestion/parsers/{parser_pdf,parser_pptx}.py`、`src/engineering_rag/ingestion/chunkers/{chunker_pdf,chunker_pptx}.py`、`src/engineering_rag/contracts/chunk.py`、`validation_build/datasets/dev/*/corpus/*.{pdf,pptx}`、`tests/unit/ingestion/{parsers,chunkers}/**`、`tests/e2e/test_four_format_flow.py` | 四格式端到端通过；既有 Update/Delete/Version/Citation 机制在新增格式上验收 | 未开始 | — |
| M10 HTTP 与任务运行 | FastAPI、持久化入库任务、Trace API、资源限额 | `src/engineering_rag/api/{main,dependencies,schemas}.py`、`src/engineering_rag/api/routes/{health,documents,tools,traces}.py`、`src/engineering_rag/ingestion/jobs.py`、`src/engineering_rag/services/{document_service,query_service}.py`、`src/engineering_rag/storage/{sqlite,repositories}.py`、`tests/integration/api/**`、`deploy/compose.yaml` | 请求/响应、错误码、任务重启、队列与超时验收记录 | 未开始 | — |
| M11 发布评测 | 冻结协议/测试集、Baseline、Ablation、人工评分、Bad Case | `validation_build/datasets/test/**`、`validation_build/protocols/release.json`、`validation_build/schemas/**`、`src/engineering_rag/evaluation/{judgments,runner,reports}.py`、`docs/reports/release-baseline.md`、`docs/reports/bad-cases.md`、`tests/e2e/test_release_protocol.py` | 配置与数据哈希、逐题结果、复核记录及第 6.7 节质量结论 | 未开始 | — |
| M12 交付与发布 | 最终 Docker Compose、持久卷、启动文档、真实实验报告 | `deploy/{Dockerfile,compose.yaml}`、`README.md`、`.env.example`、`configs/default.yaml`、`docs/reports/final-system-report.md`、`docs/reports/clean-machine-run.md`、`tests/e2e/test_clean_machine_smoke.py` | 第二台机器 clean-machine 启动记录；全部发布门槛与 System DoD 核对通过 | 未开始 | — |

进度汇总：**已验收 0 / 13 个阶段**。阶段工作量不同，该计数不代表总工时完成百分比。

下一步：人工复核 M0 合成题与锚点及独立文档族划分，补充真实资料；正式分块后建立候选相关性 judgment。M1 锁定运行依赖并验证 Linux 部署。当前没有记录已确认的阻塞项；真实数据可用性和模型硬件兼容性尚待检查。

## 跨平台开发与验收约束

- Linux 为服务部署目标，Windows 为受支持开发环境；共享 Python 业务代码，不维护两套业务实现。当前标准库评测校验器以 Python 3.11 / 3.12 为验证矩阵，完整服务版本在 M1 根据模型和解析依赖兼容结果锁定。
- 路径使用 pathlib，禁止硬编码盘符、用户目录和反斜杠分隔符；文本显式 UTF-8，文件名大小写一致。数据、模型缓存和临时目录通过配置传入，不能依赖当前工作目录。
- 生产解析与服务启动不得依赖 Windows COM、Microsoft Office 或 PowerShell。额外系统工具须列入 Linux 镜像依赖，并在启动预检中报告缺失项。
- M1 完成依赖锁定与 Linux Container Skeleton；数据库、索引及模型缓存使用可配置持久化目录。M12 再完成最终 Compose、持久卷和 clean-machine 交付。GPU 为单独验证项，记录驱动/CUDA/模型框架组合；未验证前不得承诺不同平台性能一致。
- 当前 CI 已配置在 Ubuntu 与 Windows 校验开发集和原文件证据；配置存在不代表已运行通过，验收需附实际 CI 记录。实现服务后扩展到公共逻辑测试、四种文档解析、服务启动及健康检查；Linux 容器的入库→检索→引用回溯冒烟测试通过后，才可声明完整服务支持 Linux。

维护规则：

- 开始阶段、完成验收或出现阻塞时更新本表及日期；开发期间发生有意义的进展时补充实际产物路径、测试命令/结果、报告或提交号，不仅填写“已完成”。
- “待验收”表示实现已有产物，但测试、效果评测或人工复核尚未满足要求；不得提前计入已验收阶段数。
- 阻塞时在记录列写明具体缺项及解除条件；尚未开始的下游阶段不因依赖未完成统一标成阻塞。
- 每次状态变更同步检查第 8.2 节勾选项；表格摘要与验收依据不一致时，以实际证据为准并修正状态。
- 阶段范围以第 7.1 节为准，验收细则以第 6/8 章为准；本表用于跟踪，不另设一套质量标准。

# 7.4 Deferred Work

V1 完成后再评估：

- Query Router；
- MCP 暴露；
- Query Rewrite；
- Parent-child retrieval；
- multimodal image understanding；
- GraphRAG；
- advanced table retrieval；
- online evaluation；
- permissions / ACL。

只有 Evaluation / Bad Case 能证明价值的能力才进入主链路。

# 7.5 Decision Log

## Decision 001

**Parser 层多态，Chunk 层统一。**

原因：Word/PDF/PPT/Excel 天然结构差异明显；强行统一原始结构会增加无价值抽象。

## Decision 002

**Chunk 核心字段强类型，格式差异放 metadata。**

原因：避免 RAGFlow 式 free-form dict 在项目扩大后产生字段边界污染，同时保留扩展能力。

补充：revision/parse artifact/source_spans 属于必需强类型来源字段；metadata 保留可扩展的展示/过滤信息，不能承担唯一定位责任。

## Decision 003

**V1 默认所有 Query 走 Hybrid Retrieval。**

原因：BM25 与 Dense 错误模式互补；在没有 Evaluation 证据前不引入 Query Router。

## Decision 004

**PPT 默认 Slide-based；失效案例 Excel 默认 Row-based。**

原因：遵循各自天然语义结构，并参考成熟 RAG 平台的格式特定 Chunking 思路。

## Decision 005

**Embedding 不属于 Chunk 核心实体。**

原因：Embedding 是索引派生产物，同一 Chunk 可能对应不同模型/版本的向量。

## Decision 006

**Evaluation 是主模块，不是项目收尾脚本。**

原因：Chunk、Retrieval、Rerank、Refusal 等所有技术决策必须通过冻结数据集证明。

调参使用验证集，最终结论使用未参与调参的冻结测试集。

## Decision 007

**原文锚点作为 Ground Truth，Chunk 标签是实验派生物。**

原因：改变分块策略时保持可比较的证据目标，并支持多块联合覆盖与等价证据。

## Decision 008

**V1 同一 Elasticsearch 快照承载文本与 Dense，构建成功后原子切换活动指针。**

原因：允许复用未变化向量，同时避免半更新状态进入查询；完整快照的额外存储与构建成本需在目标规模验证。

## Decision 009

**逐条事实引用并独立验证，校验失败不输出自由答案。**

原因：Source ID 存在只能证明本次请求中的真实 Chunk 存在，不能证明工程结论正确；语义验证仍需人工评测约束。

## Decision 010

**不建立独立 Evidence 事实实体，Citation 使用 request-local Source ID。**

原因：检索 Chunk 是唯一证据事实源；Source ID 只负责让 LLM 选择已提供来源，后端再映射真实 Chunk 与原文位置，避免 RetrievalResult/Evidence 两份内容产生漂移。

## Decision 011

**RRF 保留为候选融合与预算控制层，最终排序由 Reranker 完成。**

原因：BM25/Dense 两路 Top-N 并集可能显著大于 Cross-Encoder 预算；RRF Top-M 先低成本融合和截断，再由 Reranker 对有限候选做联合语义排序。必须通过 Union+Reranker 对照验证质量/延迟价值。

## Decision 012

**同一 Elasticsearch Snapshot 同时承载 content 与 dense_vector。**

原因：同一 Chunk 只保留一个索引事实文档，BM25 与 Dense 分别使用倒排字段和向量字段，避免双存储发布协调；Embedding 仍是索引派生数据，不进入 Chunk 核心 Contract。

---

# 8. Definition of Done

# 8.1 Module DoD

任何模块只有同时满足以下条件才算完成：

```text
Requirement clear
+ Contract defined
+ Implementation complete
+ pytest pass
+ Failure cases covered
+ User can explain design
+ User can locate/debug failure
```

代码“能跑”不等于完成。

Python 实现约定：新建或修改的同步/异步函数、方法、辅助函数及测试函数均须在函数体首行写 `'''...'''` 中文 docstring；复杂函数按需说明参数、返回值/产出和异常。函数签名带类型注解，依赖通过锁文件管理。以上约定不要求重写未修改的第三方代码。

# 8.2 System DoD

V1 完成必须同时具备：

- [ ] PDF / DOCX / PPTX / XLSX 四种文档可入库；
- [ ] 四种 Parser 输出对应格式结构；
- [ ] 四种 Chunker 正常工作；
- [ ] 全部最终统一为 `Chunk`；
- [ ] Elasticsearch BM25 可检索；
- [ ] BGE-M3 Dense 可检索；
- [ ] RRF 可融合；
- [ ] BGE-Reranker 可精排；
- [ ] Source-bound / Evidence-bound Generation 可运行；
- [ ] Citation 可回溯源文档；
- [ ] 无答案问题可拒答；
- [ ] Frozen Eval Set 存在；
- [ ] Recall@K / MRR 可计算；
- [ ] Correctness / Faithfulness / Citation 可评；
- [ ] Baseline 可复现；
- [ ] Ablation 可复现；
- [ ] Bad Case 分类存在；
- [ ] Query Trace 完整；
- [ ] FastAPI 可运行；
- [ ] `search_knowledge` Tool 可独立调用；
- [ ] Docker 可启动；
- [ ] README 包含架构、运行、Evaluation、真实实验结果。
- [ ] 原文锚点可跨分块实验重新映射，标签不绑定某次 Chunk ID；
- [ ] Claims Source ID / Citation / 语义校验及拒答跨字段约束通过；
- [ ] 快照发布、并发查询、更新/删除、重启恢复和回滚测试通过；
- [ ] 4.9 模型/运行配置 manifest 与性能目标已锁定；
- [ ] 6.7 功能和质量门槛均有冻结测试结果证明。

# 8.3 Release Criteria

只有在冻结测试集得到真实结果后，才允许：

1. 把实测指标写入 README；
2. 把实测指标写入简历；
3. 在面试中使用“提升 X%”等完成态表述。

在此之前，任何数字均只能标记为 Target / Expected，不得描述为已完成结果。

---

# 9. Interview Architecture Summary

项目完整技术主线：

```text
工程文档 / 历史失效知识
        ↓
格式特定解析
        ↓
格式特定 Chunking
        ↓
统一 Chunk Contract
        ↓
BM25 Top-N + BGE-M3 Dense Top-N
        ↓
RRF Top-M
        ↓
BGE-Reranker Final Top-K
        ↓
Request-local Source Binding
        ↓
Evidence-bound Generation
        ↓
Answer + Citation / Refusal
        ↓
Evaluation + Trace + Bad Case
        ↓
FastAPI + search_knowledge Tool
```

一句话架构原则：

> **解析层保留格式特性，Chunking 层允许策略多态，检索层统一数据 Contract；RRF 负责候选融合与预算控制，Reranker 负责最终精排；模型负责语义生成，程序负责 Source ID、证据边界、验证与可追溯性。**
