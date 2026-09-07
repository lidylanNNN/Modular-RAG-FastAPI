# Engineering RAG — DEV_SPEC v1

规格修订：v1.1（V1 范围不变；补齐证据、版本、评测和运行契约）。

> **Single Source of Truth**：本文件是 `engineering-rag` 项目的唯一开发规格。模块设计、数据契约、验证规则、验收标准均以本文件为准。
>
> **项目定位**：面向汽车研发文档与历史失效知识的、Evaluation-driven、Evidence-bound 的 Engineering Knowledge Service。
>
> **当前状态**：设计/实现规格。本文中的功能、接口和指标均为开发目标；量化指标只能在冻结测试集完成实测后写入简历或面试材料。

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
6. 在线检索采用 BM25 + Dense 并行召回、RRF 融合、BGE-Reranker 精排；
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
- Answer 可追溯到具体 Chunk 和原始文档位置；
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
   ├──→ BM25 Index
   └──→ BGE-M3 Embedding → Dense Index
```

### 2.2.2 Online

```text
User Query
   ↓
┌───────────────┐
│               │
BM25          Dense
│               │
└────── RRF ────┘
        ↓
   BGE-Reranker
        ↓
    Top Context
        ↓
Evidence-bound Prompt
        ↓
       LLM
        ↓
Structured Answer + Evidence IDs
        ↓
Citation Validation / Source Mapping
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

`search_knowledge` 返回结构化 Evidence，不返回自由文本聊天结果作为唯一输出。

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
├── Evidence Validator
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
- Generation 只能引用 Retriever 提供的 Evidence；
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

## 3.5.1 Retrieval Candidate

Retriever 输出统一候选结构：

```python
class RetrievalCandidate(BaseModel):
    chunk: Chunk
    source: Literal["bm25", "dense"]
    rank: int
    score: float | None = None
```

注意：BM25 score 与 Dense score 不直接比较。

## 3.5.2 RRF Result

```python
class FusedCandidate(BaseModel):
    chunk: Chunk
    rrf_score: float
    source_ranks: dict[str, int]
```

默认公式：

```text
RRF(d) = Σ 1 / (k + rank_i(d))
```

`k=60` 仅为默认基线参数，最终通过 Validation Set 验证。

## 3.5.3 Rerank Result

```python
class RerankedCandidate(BaseModel):
    chunk: Chunk
    rerank_score: float
    rank: int
```

Reranker 仅处理融合后的有限候选集，不允许全库 rerank。

---

# 3.6 Evidence / Generation Contracts

## 3.6.1 Evidence

```python
class Evidence(BaseModel):
    evidence_id: str
    chunk_id: str
    document_id: str
    revision_id: str
    parse_artifact_id: str
    content: str
    source_spans: list[SourceSpan] = Field(min_length=1)
    metadata: dict[str, Any]
```

`evidence_id` 由系统生成，不由 LLM 自由创造。

ID 在请求内唯一，并绑定本次 `snapshot_id` 中的具体 Chunk。Evidence.content 是实际送入 Prompt 的完整证据文本；V1 Context Builder 只选取完整 Chunk，不做隐式摘录或截断。未送入 Prompt 的候选保存在 Trace，不得被答案引用。

## 3.6.2 LLM Structured Output

```python
class CitedClaim(BaseModel):
    text: str = Field(min_length=1)
    evidence_ids: list[str] = Field(min_length=1)

class AnswerOutput(BaseModel):
    claims: list[CitedClaim]
    refused: bool
    refusal_reason: Literal[
        "insufficient_evidence", "version_conflict", "unsupported_claim"
    ] | None = None
```

规则：

- LLM 只能引用 Prompt 中给出的 `evidence_id`；
- 后处理必须校验 `evidence_id` 是否存在；
- 不存在的 Citation 直接判定输出无效；
- Evidence 不足必须支持拒答；
- Answer 不允许把模型自身知识伪装成工程文档事实。

输出与拒答规则：

- 非拒答时 claims 非空、refusal_reason 为 null；每条 claim 表达一项可验证结论并引用本请求 Evidence。程序按顺序把 claims.text 渲染为 answer，不再接收无引用的第二份自由答案。
- 拒答时 claims 必须为空、refusal_reason 必须有值；answer 由程序生成固定解释。空检索结果直接拒答，不调用生成模型。
- 校验分两层：程序检查 Schema、ID、来源和跨字段约束；独立语义验证调用检查每条 claim 是否由引用证据支持，重点覆盖数值、单位、条件、否定和版本。验证结果仅为质量控制信号，不保证绝对正确，需通过 4.6 的人工标注评测验证。
- 语义验证返回每条 claim 的 `supported/unsupported/uncertain` 及理由；任一非 supported 时不得按成功答案返回。输入资料中的指令视为数据，不能改变系统规则或触发工具执行。
- Schema/虚构 ID/语义不支持最多触发一次纠正生成，使用同一 Evidence，仍须完整复验。仍为非法结构或 ID 时返回 `EvidenceValidationFailure`；结构有效但语义仍不支持时拒答 `unsupported_claim`。验证服务异常/超时返回系统错误，不伪装成证据不足。
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
    evidences: list[Evidence]
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
- 用户问答调用同一 Retrieval Core。

Tool 不直接绑定前端。

所有外部请求模型禁止额外字段，并做严格类型校验；query 去除首尾空白后仍须非空。过滤字段之间 AND，列表内 OR；空列表和超过 100 项的列表无效，null 表示不限制。sheet 使用精确匹配，无该字段的文档不命中；revision_ids 与 version_mode 的约束见 5.3。
不接受任意 Elasticsearch DSL。两路在召回前执行同一过滤语义，禁止先 top_n 再过滤导致候选不足。Tool 返回检索证据，不宣称证据足以回答；空结果返回空列表，检索异常返回错误。

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
    evidences: list[Evidence]
    trace_id: str
    snapshot_id: str
    degraded: bool = False
```

QueryResponse.evidences 返回本次实际送入 Prompt 的证据；claims.evidence_ids 明确标出实际引用。未引用证据不能展示为支持答案的引用。拒答可带本次检索证据供诊断，但 claims 为空。

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
EvidenceValidationFailure
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
| GenerationFailure / EvidenceValidationFailure | 上游响应不可用为 502；自身程序缺陷为 500 |
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
BM25 Index Entries
Dense Vector Index Entries
```

## Design

- Elasticsearch 负责 BM25；
- Dense 使用 BGE-M3 生成向量；
- V1 Dense 也存入 Elasticsearch；同一快照索引文档保存 Chunk、文本和 dense_vector，减少两套存储的发布协调。具体版本和向量查询兼容性在 M1 验证并锁定，不默认认为任意 Elasticsearch 版本均适用。
- Dense 索引与 Chunk 通过 `chunk_id` 关联；
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

高召回地获取相关证据。

## Flow

```text
Query
├── BM25 Retrieve(top_n)
└── Dense Retrieve(top_n)
        ↓
      RRF
        ↓
Candidate Set
```

## Design Decisions

- V1 所有普通 Query 默认 Hybrid；
- 不做 query_type switch-case；
- BM25 与 Dense 原始 score 不直接相加；
- RRF 是融合 baseline。

## Verification

- 单独 BM25 可运行；
- 单独 Dense 可运行；
- Hybrid 可运行；
- source rank 可追踪；
- duplicate chunk 可正确去重。

---

# 4.4 Reranking

## Responsibility

对 Hybrid 候选集进行高精度排序。

## Model

```text
BGE-Reranker
```

## Rules

- 输入：Query + Candidate Chunk；
- 输出：rerank_score + final rank；
- 不允许全库 rerank；
- Reranker 失败时可以降级到 RRF 排序，但必须记录 trace。

---

# 4.5 Generation & Evidence

## Responsibility

仅基于检索 Evidence 生成回答并绑定 Citation。

## Flow

```text
Reranked Candidates
→ Evidence Builder
→ Prompt Builder
→ LLM
→ Structured Output
→ Evidence Validator
→ Claim Verifier / Bounded Repair
→ Answer
```

## Rules

- Prompt 明确要求只基于 Evidence；
- Evidence 使用系统生成 ID；
- Citation 后处理校验；
- 无足够证据时拒答；
- 实际送入 Prompt 的 Evidence 必须随 QueryResponse 返回；引用子集由 claims 标明，未入选候选仅保存在 Trace。

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
- `eval_protocol.json` 固定样本划分、指标定义、模型/Prompt/配置版本、人工评分规程与 6.7 的门槛；测试解封前冻结并记录哈希。未填写或未冻结不能发布。
- 查看测试结果后若据此改配置或修标签，原测试集转为开发数据；新的发布结论需要新的未参与调参的冻结保留集。失败结果可以如实报告，不得通过事后降低门槛改判通过。

## Retrieval Metrics

核心：

```text
Recall@K
MRR
```

辅助：

```text
Precision@K
NDCG
Latency
```

## Generation Metrics

```text
Correctness
Faithfulness
Citation Correctness
Refusal Accuracy
```

LLM-as-Judge 可辅助，但必须进行人工抽样复核。

指标计算口径：

- 核心 `EvidenceGroupRecall@K`：每道可回答题命中的 group 数 / 所需 group 数，再对题目宏平均；报告中可简称 Recall@K，但必须声明此口径，不能与按 Chunk 计数的 Recall 混用。主 K=5，同时报告 K=10。
- `CompleteEvidence@K`：全部必需 group 均命中的可回答题比例；`MRR` 使用首次完整覆盖任一 group 的前缀排名倒数，无命中记 0。多证据题同时报告 CompleteEvidence，不能用 MRR 代替完整性。
- Precision@K/NDCG 作为可选辅助指标，只在针对该实验候选进行了独立相关性/分级标注时报告；不得从不完整 anchor 集合把所有未标注 Chunk 判成无关。无答案题不参与 Recall/MRR 分母。
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
evidence ids
llm structured output
final answer
refused
latency by stage
errors / fallback
snapshot_id / corpus_manifest_id
revision_ids / parse_artifact_ids
config_hash / model revisions / prompt hashes
候选及上下文 token 数 / 被预算排除的 Chunk 及原因
claim validation results / repair attempts
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
| BM25 / Dense top_n | 各 50；候选不足返回实际数量，不填充重复项 |
| RRF | k=60；rank 从 1 开始；按 chunk_id 去重，相同分数用 chunk_id 排序 |
| Rerank 候选 | RRF 前 50 条，batch_size 初值 8；吞吐和显存实测后调参 |
| 最终证据 | top_k 默认 5，范围 1–20；Tool 与 Query 使用同一 Evidence Builder 和预算 |
| 上下文预算 | LLM tokenizer 下证据总量最多 6000 tokens，输出预留 1500；连同系统 Prompt/Query 必须低于所选模型实际上限 |
| 输入上限处理 | 同时校验 Embedding 输入及 Reranker 的 Query+Chunk 输入。模型实际最大长度从锁定配置验证；超限不得静默截断 |
| 在线超时 | BM25/Dense 各 5 s，Reranker 10 s，单次生成/验证调用各 30 s，总 deadline 90 s，纠正调用也受总 deadline 约束 |
| 任务资源 | 每进程在线执行上限 2，等待队列上限 20，满载返回 503；入库 worker=1，单文件 deadline 初值 600 s |

模型兼容性预检属于 M1：验证本机硬件、模型加载、向量维度/归一化及距离函数、过滤查询、最大输入、中文/工程术语样例。检查失败必须调整并锁定配置后再形成基线，不把表中初值当作已验证兼容性。

Context Builder 按最终排序依次选择完整 Chunk；加入某块超预算时跳过并记录，继续考察后续候选，返回数量可少于 top_k。候选非空但无块可容纳时返回 `ContextBudgetExceeded`（422），不当作知识库无答案；候选原本为空按 3.6/3.7 的空检索规则处理。Embedding 或 Reranker Query 输入本身超限同样返回 `InputTooLong`（422）。
长 Chunk 在入库阶段按所有固定模型约束细分；线上遇到超限旧索引时标记索引不兼容并要求重建，不直接截断。Reranker 失败可降级，但配置不兼容不是正常降级路径。

离线与在线模型共享硬件时采用资源信号量，优先在线请求；阻塞推理不直接运行在异步 Web event loop 内。记录硬件、冷/热启动、并发、语料规模和 token 用量，分别报告检索与整体请求 p50/p95。

`eval_protocol.json` 还须填写目标硬件、规模、并发和检索/整体 p95 上限（毫秒）。性能门槛可在验证集预跑后确定，但必须在测试解封前冻结；缺值阻止发布，不能用 90 s 故障 deadline 代替性能目标。

---

# 5. System Invariants

## 5.1 Evidence Rules

1. 不存在的 Evidence ID 不能通过校验或进入成功响应；
2. 所有 Citation 必须可从 `evidence_id → chunk_id → revision_id / parse_artifact_id → source_spans → 原文件位置` 回溯；
3. Evidence 不足必须允许拒答；
4. Retriever 返回内容与 Citation 来源必须一致。
5. 引用 ID 合法与语义支持分别校验；关键事实只能由通过校验的 claims 渲染，不能附加未验证的自由答案。

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
- evidence ID validation；
- refusal policy；
- Pydantic schema validation。

还必须覆盖：SourceSpan 越界/不存在/跨修订、空 metadata、跨字段拒答约束、引用真实 ID 但错误数值/单位/否定条件、未知过滤字段/空列表/非法 top_k、上下文预算、长表格尾部信息、版本模式、GoldAnchor 跨块覆盖与重复区间计数。

# 6.2 Integration Verification

至少存在以下端到端测试：

```text
DOCX → Parse → Chunk → Index → Query → Evidence
PDF  → Parse → Chunk → Index → Query → Evidence
PPTX → Parse → Chunk → Index → Query → Evidence
XLSX → Parse → Chunk → Index → Query → Evidence
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
B2: Hybrid (BM25 + Dense + RRF)
B3: Hybrid + Reranker
```

Baseline 回答：

> 最终复杂方案是否比简单方案更好？

# 6.4 Ablation

至少进行：

```text
Full System
- Dense
- Reranker
- Structure-aware Chunking
```

或等价的逐步增量实验。

Ablation 回答：

> 最终效果提升究竟来自哪个模块？

所有实验必须固定：

- Test Set；
- Prompt；
- LLM；
- Top-K；
- 其他非目标变量。

分块消融固定原文件、解析产物、原文 GoldAnchor、模型和最终上下文 token 总预算；各策略分别生成 Chunk 与锚点映射。top_k 相同不等于文本量相同，因此必须同时报告实际 context tokens 和输入覆盖率。
Reranker 消融固定召回及融合候选集；Embedding 消融以 BM25-only + 相同后续模块对照。候选 top_n、RRF k、tokenizer、软件/模型 revision、Verifier、硬件和配置哈希写入实验 manifest。记录随机种子与生成参数，但不承诺外部模型服务逐字确定性。

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
- Citation 无伪造；
- Unanswerable Query 可拒答；
- Trace 可定位一次完整请求；
- Tool 可独立调用；
- README 可让另一台机器完成启动。

以上是功能门槛，发布还必须同时满足下表。数值均为 **V1 初始 Target，尚未实测**，可在验证阶段调整；最终值必须在解封测试集前写入冻结的 `eval_protocol.json`。不得以测试失败为由事后降低标准。

| 质量项 | 初始发布目标 | 计分口径 |
|---|---|---|
| EvidenceGroupRecall@5 | ≥ 0.85 | 可回答题宏平均，见 4.6 |
| CompleteEvidence@5 | ≥ 0.75 | 全部必需证据组均覆盖 |
| Correctness | ≥ 0.80 | 可回答题，拒答/系统错误不剔除 |
| Faithfulness | ≥ 0.95 | 人工事实支持标注；N/A 不通过 |
| Citation Correctness / 覆盖率 | 均 ≥ 0.95 | 人工语义与来源核对 |
| FalseAnswerRate | ≤ 0.05 | 无答案题错误作答比例 |
| FalseRefusalRate | ≤ 0.15 | 可回答题误拒答比例 |
| 无效引用/源位置 | 0 个进入成功输出 | 在本次验收集上的观测值，不代表所有未来输入绝对为零 |
| 系统错误率 | ≤ 0.01 | 本次测试全部请求的非 2xx 比例 |
| 性能 | 满足冻结协议的两个 p95 上限 | 指定硬件、规模和并发；缺值不通过 |

四种格式及关键问题类型分别报告样本量与结果；任一类别 Correctness < 0.60 阻止发布，不能用总体平均掩盖明显失效。报告 95% 区间和小样本限制；门槛针对本次点估计，不宣称统计保证。

复杂度决策：B3 至少不得低于 B0/B1 中较优者的 Recall@5 和 MRR 点估计，并满足性能门槛。未达到时保留实验结果、继续验证或重新修订默认检索方案，不能仅因“链路更完整”判定通过。只有配对实验支持时才宣称提升，未证实的提升不写成成果。

---

# 7. Execution Plan

# 7.1 Development Order

按依赖关系开发，不按 UI 开发：

```text
M0  开发 fixtures / 验证集草案 / 原文锚点 / 评测协议草案
M1  Core Models / Config / 模型兼容性预检 / 最小 Trace / 公共服务层
M2  DOCX + XLSX Parser / 定位目录 / 原文存储
M3  DOCX + XLSX Chunker / SourceSpan Validation
M4  BM25 Index / Retrieve / 第一份检索评测报告
M5  Dense Index / Retrieve / Snapshot 发布与故障恢复
M6  RRF / B0-B2 对照 / search_knowledge 服务契约
M7  Reranker / B3 对照 / 第一里程碑验收
M8  Evidence / Claims / Generation / Verifier / Refusal
M9  PDF + PPTX Parser/Chunker / 四格式与版本验收
M10 FastAPI / 持久化入库任务 / Trace 查询 / 资源限额
M11 冻结测试协议 / Baseline + Ablation / 人工评测 / Bad Case
M12 Docker / 第二台机器启动 / 发布门槛 / README 实测报告
```

Evaluation 和 Trace 从 M0/M1 贯穿后续里程碑；M11 是最终发布评测，不是首次实现评测。每增加一个模块，都在验证集比较前后结果。M1 公共服务层可被 CLI/pytest 调用，M10 HTTP 仅包装同一逻辑，遵守“Evaluation 通过公开接口”的依赖规则。

# 7.2 Current Milestone

第一里程碑只要求打通：

```text
DOCX + XLSX
→ Chunk
→ BM25 + Dense
→ RRF
→ Reranker
→ Evidence
```

再补 PDF / PPTX，避免四种解析器同时展开导致项目无法闭环。

第一里程碑还必须交付：至少 20 道带原文锚点的开发/验证问题（不充当冻结发布测试集）、B0-B3 检索结果、逐阶段 Trace、稳定来源定位、重复入库幂等与失败不发布测试。此时只能说明检索链路已打通，不能声明生成质量或 V1 发布完成。

# 7.3 Development Progress

最后更新：2026-09-07。

当前阶段：开发准备。DEV_SPEC v1.1 的规格修订已完成；当前仓库尚无应用实现、测试集或实测报告。以下状态以本仓库可核查产物为准，规格中的模型示例不计为功能实现。

状态：**未开始 → 进行中 → 待验收 → 已完成**；遇到无法继续的问题标记 **阻塞**，同时写明原因和解除条件。只有满足第 8 章 DoD 且提供验收依据，才能标记已完成。

| 阶段 | 主要交付物 | 完成所需验收依据 | 当前状态 | 实际产物 / 验证记录 |
|---|---|---|---|---|
| M0 评测准备 | 开发 fixtures、原文锚点、验证集及评测协议草案 | 锚点可定位；可回答/不可回答标签经核对；数据划分明确 | 未开始 | — |
| M1 工程基础 | 核心模型、配置、模型预检、最小 Trace、公共服务层 | Schema 验证、配置加载、模型兼容性预检和 Trace 测试记录 | 未开始 | — |
| M2 DOCX/XLSX 解析 | 两类 Parser、定位目录、原文与解析产物存储 | 两类正常/异常 fixture 通过；原文位置可回溯 | 未开始 | — |
| M3 DOCX/XLSX 分块 | 两类 Chunker、SourceSpan 校验、超长记录处理 | 分块稳定性、边界、来源映射和长记录尾部测试通过 | 未开始 | — |
| M4 BM25 | 全文索引、检索、B0 评测报告 | 中文/精确术语/过滤测试通过；首份验证集检索结果可复现 | 未开始 | — |
| M5 Dense 与快照 | 向量索引、检索、快照发布和恢复 | B1 结果；双路一致性、幂等、失败不发布及重启恢复测试 | 未开始 | — |
| M6 RRF 与 Tool Core | 融合、去重、search_knowledge 服务实现 | RRF/过滤测试；B0–B2 对照；Tool 服务可独立调用 | 未开始 | — |
| M7 Reranker | 精排、降级、第一里程碑报告 | B3 对照；降级 Trace；第 7.2 节全部交付物齐备 | 未开始 | — |
| M8 生成与证据 | Claims、生成、语义验证、有限纠正、拒答 | 引用/数值/版本/拒答及模型异常测试；验证集生成结果 | 未开始 | — |
| M9 PDF/PPTX 扩展 | 两类 Parser/Chunker、四格式和版本场景 | 四格式端到端通过；来源定位、版本选择和冲突测试 | 未开始 | — |
| M10 HTTP 与任务运行 | FastAPI、持久化入库任务、Trace API、资源限额 | 请求/响应、错误码、任务重启、队列与超时验收记录 | 未开始 | — |
| M11 发布评测 | 冻结协议/测试集、Baseline、Ablation、人工评分、Bad Case | 配置与数据哈希、逐题结果、复核记录及第 6.7 节质量结论 | 未开始 | — |
| M12 交付与发布 | Docker、持久卷、启动文档、真实实验报告 | 第二台机器启动记录；全部发布门槛与 System DoD 核对通过 | 未开始 | — |

进度汇总：**已验收 0 / 13 个阶段**。阶段工作量不同，该计数不代表总工时完成百分比。

下一步：从 M0 开始整理 DOCX/XLSX 开发样本和带原文锚点的问题，同时明确 M1 的运行环境配置。当前没有记录已确认的阻塞项；数据可用性和硬件兼容性尚待检查。

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

原因：ID 存在只能证明引用对象存在，不能证明工程结论正确；语义验证仍需人工评测约束。

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
- [ ] Evidence-bound Generation 可运行；
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
- [ ] Claims 引用/语义校验及拒答跨字段约束通过；
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
BM25 + BGE-M3 Dense
        ↓
RRF
        ↓
BGE-Reranker
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

> **解析层保留格式特性，Chunking 层允许策略多态，检索层统一数据 Contract；模型负责语义生成，程序负责证据边界、验证与可追溯性。**
