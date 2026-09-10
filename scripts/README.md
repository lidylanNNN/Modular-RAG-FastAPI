# 维护脚本

这里放仓库资料构建与检查命令。线上业务逻辑后续统一放入 `src/engineering_rag/`，不能复制到本目录。

`validation_build/` 负责验证集构建与资料校验；`experiments/run_experiment.py` 是正式实验入口骨架，调用应用服务层。

在仓库根目录运行：

```bash
python -X utf8 scripts/validation_build/validate_suite.py
python -X utf8 scripts/validation_build/validate_dataset.py
python -X utf8 scripts/validation_build/validate_dataset.py validation_build/datasets/archive/synthetic-v1
```

也支持模块调用：`python -X utf8 -m scripts.validation_build.validate_suite`。脚本直接调用可以从仓库外运行；模块调用要求当前目录为仓库根目录。Linux 可用已有的 python3。

`build_expansion.py` 从已有 XLSX 原件、归档基础集和 `validation_build/seeds/` 重建机器标注草案，不负责创建 XLSX。它会覆盖当前 pending 草案，不能作为日常校验命令；修改标注前保留 Git 记录，人工复核后脚本会拒绝覆盖。正常检查无需调用构建器，也不依赖本地制作缓存。

所有路径与职责以 [DEV_SPEC 第 2.6 节](../DEV_SPEC.md) 为准。
