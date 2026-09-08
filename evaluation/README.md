# 评测资料与跨平台运行

开发和验收口径以仓库根目录的 [DEV_SPEC.md](../DEV_SPEC.md) 为准。

当前交付是 [40 题修订开发集](datasets/dev/synthetic-v2/README.md)、[12 题独立文档族验证草案](datasets/validation/synthetic-cooling-v1/README.md)和标准库校验器。[旧 20 题](datasets/archive/synthetic-v1/README.md)作为历史夹具保留，不计为另一份独立数据。全部为合成内容，人工复核待完成，尚未实现 RAG 服务。

评测口径草案见 [development.json](protocols/development.json)，组件输入见 [fixtures](../tests/fixtures/evaluation/README.md)，候选相关性格式见 [relevance_judgment.schema.json](schemas/relevance_judgment.schema.json)。实际候选未产生，未填写或伪造 judgment。

## 运行

校验器支持目标为 Python 3.11 / 3.12，Windows 与 Linux 使用同一份代码，无需 pip 安装依赖，也不需要 Microsoft Office、PowerShell、Node.js 或模型服务。

Linux，在仓库根目录使用已有解释器：

```bash
python3 -X utf8 scripts/evaluation/validate_suite.py
```

Windows，在仓库根目录使用已有解释器：

```powershell
python -X utf8 scripts/evaluation/validate_suite.py
```

也可从任何目录通过脚本的绝对路径运行，默认数据路径相对于脚本定位。单集检查用 `python -X utf8 scripts/evaluation/validate_dataset.py`，默认选择 synthetic-v2；第一个参数可选择其他目录，参数相对于当前工作目录解析。

成功返回退出码 0，开发集应为 40 题（29/11）、5 份源文件、97 个原文单元；验证集为 12 题（9/3）、1 份源文件、8 个原文单元。套件还检查跨 split 的文档族、文档身份、文件哈希和规范化问题重复。失败返回非零退出码；近重复和语义标签仍需人工审查。

回归测试命令：`python -X utf8 -m unittest discover -s tests -t . -p "test_*.py"`。测试只验证资料校验器，不证明 RAG 的检索或生成效果。

## 当前仍需完成

1. 人工复核所有题目、证据组和拒答依据，登记真实复核信息。
2. 正式 Parser/Chunker 实现后核对锚点映射，建立真实候选池及相关性标注。
3. 按 M2/M3/M9 补解析边界和 PDF/PPTX 实体资料；M11 另建未参与调参的冻结发布集。
4. 锁定模型、Prompt、硬件和性能上限后运行完整评测；协议中的 null 表示待填，不能当作已验收。

## 兼容性边界

- `.github/workflows/evaluation.yml` 配置 Ubuntu 24.04 / Windows Server 2022 与 Python 3.11 / 3.12 的四组校验，并检查从仓库外运行。首次推送并得到成功记录后，才可认定对应环境验证通过。
- 文件名大小写必须严格匹配；代码用 `pathlib` 组装路径，文本显式采用 UTF-8。Git 将脚本文本规范为 LF，DOCX/XLSX 保持二进制，避免检出过程改变源文件哈希。
- DOCX/XLSX 是已生成的输入资料，校验器直接读取其 ZIP/XML，不调用 Office。制作时的临时渲染脚本不属于项目运行依赖；中文显示依赖阅读端字体，校验不依赖字体。
- 后续 FastAPI、Elasticsearch、模型推理及文档解析依赖尚未实现或验证；其 Linux 部署和 GPU 兼容性仍属于 M1 及后续验收，不能由本校验器通过推导。
