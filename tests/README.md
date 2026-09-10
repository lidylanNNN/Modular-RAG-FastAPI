# 自动化测试与组件夹具

- `unit/validation_build/`：资料校验器的真实可运行回归测试，使用临时副本构造异常，不修改仓库数据。
- [fixtures/answer_quality/](fixtures/answer_quality/README.md)：后续指标/Generation 的确定性输入和预期行为，目前未接入对应实现，不计为通过的测试。
- `integration/`、`e2e/` 在对应模块实现时创建，当前不放空占位测试。

在仓库根目录运行：

```bash
uv sync --locked
uv run --locked pytest tests
```

pytest 在仓库根目录运行时会把根目录放入导入路径，测试使用 `scripts.validation_build` 包导入被测维护工具。测试依赖 pytest；资料校验脚本自身仍只使用 Python 标准库。

目录调整还须核对原件和标注身份不变、从仓库外运行 CLI，以及构建器重建结果。测试通过只证明检查工具行为，不代表模型检索或生成质量。
