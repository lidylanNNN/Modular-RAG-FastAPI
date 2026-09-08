# 组件验收输入

这些是给后续实现使用的确定性输入与预期结果，目前尚未接入评测器或 Generation。不能把文件存在计为测试通过。

- `span_coverage_cases.json`：groups 的三层结构是 group → alternative → spans；检查跨块覆盖、重叠去重、OR、AND 与多 span。所有区间基于同一模拟不可变解析单元，不属于入库语料。
- `generation_cases.json`：检查 Source ID allowlist、错误数值、一次纠正、Verifier 超时和未入 Prompt 的来源。Verifier stub 的状态是注入行为，不是模型实际判断。

解析边界的实体资料（长表格、合并单元格、损坏文件、PDF/PPTX）随 M2/M3/M9 添加。不可将本目录递归摄入知识库。
