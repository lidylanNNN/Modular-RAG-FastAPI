# 自动化测试与组件夹具

- `unit/evaluation/`：资料校验器的真实可运行回归测试，使用临时副本构造异常，不修改仓库数据。
- [fixtures/evaluation/](fixtures/evaluation/README.md)：后续指标/Generation 的确定性输入和预期行为，目前未接入对应实现，不计为通过的测试。
- `integration/`、`e2e/` 在对应模块实现时创建，当前不放空占位测试。

在仓库根目录运行：

```bash
python -X utf8 -m unittest discover -s tests -t . -p "test_*.py"
```

`-t .` 将仓库根目录作为导入根，测试使用 `scripts.evaluation` 包导入被测维护工具。`__init__.py` 用于标准库 unittest 递归发现；后续切换测试工具时同步更新命令与 CI。

目录调整还须核对原件和标注身份不变、从仓库外运行 CLI，以及构建器重建结果。测试通过只证明检查工具行为，不代表模型检索或生成质量。
