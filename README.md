# Engineering RAG

面向工程文档和历史失效知识的 RAG 服务，目标为四格式解析、混合检索、证据绑定回答及 FastAPI / Tool 接口。

当前处于开发准备阶段：已有 40 题合成开发集、12 题独立文档族验证草案和资料校验工具。人工复核、应用服务及真实模型评测尚未完成。

## 目录

| 路径 | 当前用途 |
|---|---|
| [DEV_SPEC.md](DEV_SPEC.md) | 唯一正式规格；第 2.6 节定义完整目录规划和模块依赖 |
| [evaluation/](evaluation/README.md) | 数据集、协议、Schema、合成构建输入；历史数据位于 datasets/archive |
| [scripts/](scripts/README.md) | 资料构建与校验命令 |
| [tests/](tests/README.md) | 单元测试及组件夹具 |
| docs/ | 历史规格、审查记录；后续归档实验报告 |
| .github/workflows/ | Windows / Linux CI |

`src/engineering_rag/`、`configs/`、`deploy/` 和依赖锁文件按 DEV_SPEC 在 M1 起创建，目前尚未实现。运行输出写入被忽略的 `artifacts/` 或 `.local/`。

## 当前可运行的检查

使用已有 Python 3.11 / 3.12；校验器和测试只依赖标准库，无需安装项目依赖。在仓库根目录运行：

```bash
python -X utf8 scripts/evaluation/validate_suite.py
python -X utf8 -m unittest discover -s tests -t . -p "test_*.py"
```

Linux 可将命令中的 `python` 换成已有的 `python3`。校验脚本也支持通过绝对路径从仓库外调用；这些命令不是启动 RAG 服务。

只将数据集 manifest 明确列出的原件入库，不能递归摄入题目、答案、协议或测试夹具。使用方法见 [评测说明](evaluation/README.md)。
