# 合成评测题

所有参数和记录均为虚构；人工复核待完成，不是冻结发布测试集。

## VAL-001 precise_term

问题：泵运行且传感器有效时，SYN_CoolFlow 的低流量置位条件是什么？

答案：流量严格低于 2.5 L/min 并连续 4 s。

模式：latest；过滤：`{}`

必需事实：严格低于 2.5 L/min；连续 4 s

证据组 VAL-001-G1（组内 OR）：VAL-001-G1-A1

锚点 VAL-001-G1-A1，位置 `{"sheet": "冷却规则", "sheet_part": "xl/worksheets/sheet1.xml", "row": 5, "header_row": 4, "columns": "ABCDE", "record_key": "C01"}`

> 对象: SYN_CoolFlow
> 条件: 泵运行且传感器有效
> 规则: 流量严格低于 2.5 L/min 并连续 4 s，置位低流量故障。

## VAL-002 semantic_paraphrase

问题：正常泵运行时，流量恰好 2.5 L/min 会开始低流量计时吗？

答案：不会，必须严格低于该边界。

模式：latest；过滤：`{}`

必需事实：边界不启动计时；严格小于

证据组 VAL-002-G1（组内 OR）：VAL-002-G1-A1

锚点 VAL-002-G1-A1，位置 `{"sheet": "冷却规则", "sheet_part": "xl/worksheets/sheet1.xml", "row": 5, "header_row": 4, "columns": "ABCDE", "record_key": "C01"}`

> 对象: SYN_CoolFlow
> 条件: 泵运行且传感器有效
> 规则: 流量严格低于 2.5 L/min 并连续 4 s，置位低流量故障。

## VAL-003 semantic_paraphrase

问题：已有低流量故障后，流量恢复到 3.0 L/min 只保持 6 s 能清除吗？

答案：不能，要求连续 7 s。

模式：latest；过滤：`{}`

必需事实：6 s 不足；连续 7 s

证据组 VAL-003-G1（组内 OR）：VAL-003-G1-A1

锚点 VAL-003-G1-A1，位置 `{"sheet": "冷却规则", "sheet_part": "xl/worksheets/sheet1.xml", "row": 6, "header_row": 4, "columns": "ABCDE", "record_key": "C02"}`

> 对象: SYN_CoolFlow
> 条件: 泵运行且传感器有效
> 规则: 流量恢复到 3.0 L/min 或以上并连续 7 s，清除当前低流量故障。

## VAL-004 precise_term

问题：SYN_CoolTemp 的高温进入和退出条件分别是什么？

答案：达到 65 ℃进入；降至 60 ℃或以下连续 8 s 退出。

模式：latest；过滤：`{}`

必需事实：65 ℃进入；不高于 60 ℃；连续 8 s 退出

证据组 VAL-004-G1（组内 OR）：VAL-004-G1-A1

锚点 VAL-004-G1-A1，位置 `{"sheet": "冷却规则", "sheet_part": "xl/worksheets/sheet1.xml", "row": 7, "header_row": 4, "columns": "ABCDE", "record_key": "C03"}`

> 对象: SYN_CoolTemp
> 条件: 温度传感器有效
> 规则: 温度达到 65 ℃进入高温状态；降到 60 ℃或以下连续 8 s 才退出。

## VAL-005 semantic_paraphrase

问题：流量传感器无效时，可把读数当正常流量继续判定吗？

答案：不可以，禁止使用读数计算流量故障，应输出传感器不可用。

模式：latest；过滤：`{}`

必需事实：禁止使用读数判定；输出不可用；不能视为正常

证据组 VAL-005-G1（组内 OR）：VAL-005-G1-A1

锚点 VAL-005-G1-A1，位置 `{"sheet": "冷却规则", "sheet_part": "xl/worksheets/sheet1.xml", "row": 8, "header_row": 4, "columns": "ABCDE", "record_key": "C04"}`

> 对象: SYN_CoolSensor
> 条件: 传感器标志为无效
> 规则: 禁止使用读数计算流量故障；输出传感器不可用状态。
> 备注: 传感器不可用不能记为正常流量。

## VAL-006 history_failure

问题：SYN-COOL-F01 为什么在泵停止后误报，修正后怎样处理？

答案：未判断泵运行条件；修正后泵停止时不启动低流量计时。

模式：latest；过滤：`{}`

必需事实：缺少泵运行条件；停止时不启动计时

证据组 VAL-006-G1（组内 OR）：VAL-006-G1-A1

锚点 VAL-006-G1-A1，位置 `{"sheet": "冷却规则", "sheet_part": "xl/worksheets/sheet1.xml", "row": 9, "header_row": 4, "columns": "ABCDE", "record_key": "C05"}`

> 对象: SYN-COOL-F01
> 条件: 泵停止后的故障误报
> 规则: 根因是没有判断泵运行条件。
> 备注: 修正后泵停止时不启动低流量故障计时。

## VAL-007 multi_evidence

问题：冷却状态发布周期和压力采样周期分别是多少？

答案：状态发布 80 ms，压力采样 40 ms。

模式：latest；过滤：`{}`

必需事实：发布 80 ms；采样 40 ms

证据组 VAL-007-G1（组内 OR）：VAL-007-G1-A1

证据组 VAL-007-G2（组内 OR）：VAL-007-G2-A1

锚点 VAL-007-G1-A1，位置 `{"sheet": "冷却规则", "sheet_part": "xl/worksheets/sheet1.xml", "row": 10, "header_row": 4, "columns": "ABCDE", "record_key": "C06"}`

> 对象: SYN_CoolStatus
> 条件: 监控任务
> 规则: 状态发布周期为 80 ms。

锚点 VAL-007-G2-A1，位置 `{"sheet": "冷却规则", "sheet_part": "xl/worksheets/sheet1.xml", "row": 12, "header_row": 4, "columns": "ABCDE", "record_key": "C08"}`

> 对象: SYN_CoolPressure
> 条件: 压力监控
> 规则: 压力采样周期为 40 ms。

## VAL-008 hard_negative

问题：保养模式低流量记录能套用正常运行的 2.5 L/min 和 4 s 吗？

答案：不能；保养模式采用 1.5 L/min 和连续 12 s。

模式：latest；过滤：`{}`

必需事实：不能套用；1.5 L/min；12 s

证据组 VAL-008-G1（组内 OR）：VAL-008-G1-A1

锚点 VAL-008-G1-A1，位置 `{"sheet": "冷却规则", "sheet_part": "xl/worksheets/sheet1.xml", "row": 11, "header_row": 4, "columns": "ABCDE", "record_key": "C07"}`

> 对象: SYN_CoolFlow
> 条件: 仅保养模式
> 规则: 低流量记录阈值为 1.5 L/min，并连续 12 s。
> 备注: 保养记录规则不适用于正常泵运行诊断。

## VAL-009 multi_evidence

问题：有效传感器下，正常泵运行的低流量置位阈值与恢复阈值分别是多少？

答案：低于 2.5 L/min 连续 4 s 置位；恢复至 3.0 L/min 或以上连续 7 s 清除。

模式：latest；过滤：`{}`

必需事实：置位低于 2.5 L/min 连续 4 s；恢复不低于 3.0 L/min 连续 7 s

证据组 VAL-009-G1（组内 OR）：VAL-009-G1-A1

证据组 VAL-009-G2（组内 OR）：VAL-009-G2-A1

锚点 VAL-009-G1-A1，位置 `{"sheet": "冷却规则", "sheet_part": "xl/worksheets/sheet1.xml", "row": 5, "header_row": 4, "columns": "ABCDE", "record_key": "C01"}`

> 对象: SYN_CoolFlow
> 条件: 泵运行且传感器有效
> 规则: 流量严格低于 2.5 L/min 并连续 4 s，置位低流量故障。

锚点 VAL-009-G2-A1，位置 `{"sheet": "冷却规则", "sheet_part": "xl/worksheets/sheet1.xml", "row": 6, "header_row": 4, "columns": "ABCDE", "record_key": "C02"}`

> 对象: SYN_CoolFlow
> 条件: 泵运行且传感器有效
> 规则: 流量恢复到 3.0 L/min 或以上并连续 7 s，清除当前低流量故障。

## VAL-010 unanswerable

问题：SYN_CoolFlow 传感器的采购料号是什么？

答案：拒答：insufficient_evidence

模式：latest；过滤：`{}`

必需事实：

拒答依据：冷却资料不包含供应商或采购料号，不能从信号名推测。

## VAL-011 partial_evidence

问题：请同时给出冷却状态发布周期和 CAN 报文标识符。

答案：拒答：insufficient_evidence

模式：latest；过滤：`{}`

必需事实：

拒答依据：C06 只提供周期，没有 CAN 报文标识符，按整问拒答处理。

## VAL-012 filtered_unanswerable

问题：只检索 DOCX，冷却状态发布周期是多少？

答案：拒答：insufficient_evidence

模式：latest；过滤：`{"file_types": ["docx"]}`

必需事实：

拒答依据：本验证语料只有 XLSX；合法格式过滤后没有结果。
