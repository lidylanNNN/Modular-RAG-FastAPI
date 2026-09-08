# 合成评测题

所有参数和记录均为虚构；人工复核待完成，不是冻结发布测试集。

## DEV-001 precise_term

问题：SYN_PowerReq 的发送周期是多少？

答案：发送周期为 20 ms。

模式：latest；过滤：`{}`

必需事实：周期为 20 ms

证据组 DEV-001-G1（组内 OR）：DEV-001-A1

锚点 DEV-001-A1，位置 `{"part": "word/document.xml", "body_child_1based": 5, "requirement_id": "R01"}`

> 动力请求报文名称为 SYN_PowerReq，发送周期为 20 ms。

## DEV-002 precise_term

问题：按当前规范，启动屏蔽结束后 SYN_COMM_TIMEOUT 的置位时间阈值是多少？

答案：距最后一帧有效 SYN_PowerReq 达到 150 ms 时置位。

模式：latest；过滤：`{}`

必需事实：以最后一帧有效报文时间为基准；达到 150 ms

证据组 DEV-002-G1（组内 OR）：DEV-002-A1

锚点 DEV-002-A1，位置 `{"part": "word/document.xml", "body_child_1based": 7, "requirement_id": "R02"}`

> 启动屏蔽期结束后，若距最后一帧有效 SYN_PowerReq 的时间达到 150 ms，则置位通信超时故障 SYN_COMM_TIMEOUT。

## DEV-003 precise_term

问题：SYN_ReqValid 的 0 和 1 分别表示什么？

答案：0 表示无效，1 表示有效，其他值保留。

模式：latest；过滤：`{}`

必需事实：0 为无效；1 为有效；其他值保留

证据组 DEV-003-G1（组内 OR）：DEV-003-A1

锚点 DEV-003-A1，位置 `{"part": "word/document.xml", "body_child_1based": 5, "requirement_id": "R01"}`

> 报文中的请求有效标志 SYN_ReqValid：0 表示无效，1 表示有效，其他值保留。

## DEV-004 precise_term

问题：电压恰好为 9 V 或 16 V 时，会开始累计异常持续时间吗？

答案：不会。正常范围是闭区间 [9 V,16 V]，恰好位于边界不属于异常，尚未完成的异常计时归零。

模式：latest；过滤：`{}`

必需事实：9 V 和 16 V 均正常；未完成异常计时归零

证据组 DEV-004-G1（组内 OR）：DEV-004-A1

锚点 DEV-004-A1，位置 `{"part": "word/document.xml", "body_child_1based": 20, "requirement_id": "R07"}`

> 电压回到闭区间 [9 V, 16 V] 时，尚未完成的异常持续计时归零；恰好 9 V 或 16 V 不属于异常。

## DEV-005 semantic_paraphrase

问题：刚上电头半秒还没有收到动力请求，会立刻报码吗？

答案：按当前 2.0 版，前 500 ms 内不置位通信超时故障，但仍接收和更新时间戳；到屏蔽结束时按超时规则判定。

模式：latest；过滤：`{}`

必需事实：前 500 ms 为屏蔽期；屏蔽内不置位；仍接收并更新时间戳；屏蔽结束后按规则判定

证据组 DEV-005-G1（组内 OR）：DEV-005-A1

锚点 DEV-005-A1，位置 `{"part": "word/document.xml", "body_child_1based": 9, "requirement_id": "R03"}`

> 自控制器上电起的前 500 ms 为通信超时诊断屏蔽期。屏蔽期间仍接收并更新时间戳，但不置位 SYN_COMM_TIMEOUT；屏蔽结束后按通信超时规则判定。

## DEV-006 semantic_paraphrase

问题：超时后恢复两帧正常报文，中间夹一帧无效，再恢复三帧，能清掉当前超时吗？

答案：不能。无效帧使连续计数归零，后面的三帧未达到连续五帧有效的恢复要求。

模式：latest；过滤：`{}`

必需事实：不能清除当前超时；无效帧使计数归零；需要连续 5 帧有效

证据组 DEV-006-G1（组内 OR）：DEV-006-A1

锚点 DEV-006-A1，位置 `{"part": "word/document.xml", "body_child_1based": 11, "requirement_id": "R04"}`

> SYN_COMM_TIMEOUT 置位后，连续收到 5 帧校验通过且 SYN_ReqValid=1 的 SYN_PowerReq，清除当前通信超时状态。中途收到无效帧则连续计数归零。

## DEV-007 semantic_paraphrase

问题：进入热降额后温度降到 86 ℃并稳定十秒，可以退出吗？

答案：不可以。必须降至 85 ℃或以下并连续保持 10 s。

模式：latest；过滤：`{}`

必需事实：86 ℃不能退出；退出温度不高于 85 ℃；连续保持 10 s

证据组 DEV-007-G1（组内 OR）：DEV-007-A1

锚点 DEV-007-A1，位置 `{"part": "word/document.xml", "body_child_1based": 16, "requirement_id": "R05"}`

> 温度信号 SYN_MotorTemp 达到 90 ℃时进入热降额；只有温度降至 85 ℃或以下并连续保持 10 s，才退出热降额。

## DEV-008 semantic_paraphrase

问题：收到的新请求标志无效，还能沿用上一帧请求吗？

答案：不能。本周期采用零请求值；只有有效标志为 1 且没有当前通信超时，才允许采用本帧请求。

模式：latest；过滤：`{}`

必需事实：不能沿用旧请求；本周期零请求；有效标志为 1 且无当前超时才采用本帧

证据组 DEV-008-G1（组内 OR）：DEV-008-A1

锚点 DEV-008-A1，位置 `{"part": "word/document.xml", "body_child_1based": 18, "requirement_id": "R06"}`

> 只有 SYN_ReqValid=1 且当前没有 SYN_COMM_TIMEOUT 时，才允许采用本帧请求值；否则本周期采用零请求值。

## DEV-009 history_failure

问题：SYN-F001 为什么在调度抖动时误报，修正措施是什么？

答案：旧实现累加丢帧次数，未使用最后有效帧时间戳；应改为时间差判定，并从所选规范版本读取阈值。

模式：latest；过滤：`{}`

必需事实：按丢帧次数累加导致问题；改为时间差判定；阈值跟随所选版本

证据组 DEV-009-G1（组内 OR）：DEV-009-A1

锚点 DEV-009-A1，位置 `{"sheet": "失效案例", "sheet_part": "xl/worksheets/sheet1.xml", "row": 5, "header_row": 4, "columns": "ABCDE", "record_key": "SYN-F001"}`

> 根因: 旧实现按丢帧次数累加，未使用最后有效帧时间戳
> 修正措施: 改为时间差判定，阈值从所选规范版本读取

## DEV-010 history_failure

问题：SYN-F002 的修正是否应该停掉启动期的报文接收？

答案：不应该。修正是在屏蔽期保留接收和时间戳更新，仅抑制故障置位。

模式：latest；过滤：`{}`

必需事实：不停接收；更新时间戳；仅抑制置位

证据组 DEV-010-G1（组内 OR）：DEV-010-A1

锚点 DEV-010-A1，位置 `{"sheet": "失效案例", "sheet_part": "xl/worksheets/sheet1.xml", "row": 6, "header_row": 4, "columns": "ABCDE", "record_key": "SYN-F002"}`

> 修正措施: 屏蔽期间保留接收和时间戳更新，仅抑制故障置位

## DEV-011 history_failure

问题：SYN-F003 中的 40 ms 越界、20 ms 正常、70 ms 越界序列，期望什么结果？

答案：期望不置位故障。正常电压使异常持续计时归零，不能把前后两段越界累加。

模式：latest；过滤：`{}`

必需事实：不置位故障；正常段清零计时；不能累计不连续越界

证据组 DEV-011-G1（组内 OR）：DEV-011-A1

锚点 DEV-011-A1，位置 `{"sheet": "失效案例", "sheet_part": "xl/worksheets/sheet1.xml", "row": 7, "header_row": 4, "columns": "ABCDE", "record_key": "SYN-F003"}`

> 根因: 正常电压出现后没有清零异常持续计时，多个短脉冲被累加
> 修正措施: 电压回到正常闭区间时将异常持续计时归零
> 验证记录: 注入 40 ms 越界、20 ms 正常、70 ms 越界，期望不置位故障

## DEV-012 history_failure

问题：SYN-F004 的通信恢复为什么过早？如何修正？

答案：无效帧没有清零连续有效帧计数；应在无效帧到来时归零，再等待连续 5 帧有效报文。

模式：latest；过滤：`{}`

必需事实：无效帧未清零；无效帧到来归零；重新累计连续 5 帧

证据组 DEV-012-G1（组内 OR）：DEV-012-A1

锚点 DEV-012-A1，位置 `{"sheet": "失效案例", "sheet_part": "xl/worksheets/sheet1.xml", "row": 8, "header_row": 4, "columns": "ABCDE", "record_key": "SYN-F004"}`

> 根因: 无效帧没有清零连续有效帧计数
> 修正措施: 无效帧使计数归零，再等待连续 5 帧有效报文

## DEV-013 multi_evidence

问题：SYN-F001 记录了什么误报现象和旧实现根因？结合当前规范，说明应采用的超时判定及具体阈值。

答案：调度抖动时出现通信超时误报，旧实现累加丢帧次数且未用最后有效帧时间戳；应按时间差判定，当前版在启动屏蔽结束后达到 150 ms 置位。

模式：latest；过滤：`{}`

必需事实：F001 的现象为调度抖动时通信超时误报；旧实现按丢帧次数累加且未使用时间戳；改用最后有效帧时间差；启动屏蔽结束后达到 150 ms 置位

证据组 DEV-013-G1（组内 OR）：DEV-013-A1

证据组 DEV-013-G2（组内 OR）：DEV-013-A2

锚点 DEV-013-A1，位置 `{"part": "word/document.xml", "body_child_1based": 7, "requirement_id": "R02"}`

> 启动屏蔽期结束后，若距最后一帧有效 SYN_PowerReq 的时间达到 150 ms，则置位通信超时故障 SYN_COMM_TIMEOUT。

锚点 DEV-013-A2，位置 `{"sheet": "失效案例", "sheet_part": "xl/worksheets/sheet1.xml", "row": 5, "header_row": 4, "columns": "ABCDE", "record_key": "SYN-F001"}`

> 现象: 任务调度抖动时出现通信超时误报
> 根因: 旧实现按丢帧次数累加，未使用最后有效帧时间戳

## DEV-014 multi_evidence

问题：依据电压规范及 SYN-F003，40 ms 越界后恢复正常 20 ms、再越界 70 ms，是否应报故障？原因是什么？

答案：不应报故障。规范要求连续越界 100 ms，正常的 20 ms 已清零计时，后段只有 70 ms；SYN-F003 的同一测试序列也明确期望不置位。

模式：latest；过滤：`{}`

必需事实：连续越界需 100 ms；正常 20 ms 清零；70 ms 未满足阈值；SYN-F003 明确期望不置位

证据组 DEV-014-G1（组内 OR）：DEV-014-A1

证据组 DEV-014-G2（组内 OR）：DEV-014-A2

锚点 DEV-014-A1，位置 `{"part": "word/document.xml", "body_child_1based": 20, "requirement_id": "R07"}`

> 供电电压 SYN_SupplyVoltage 严格低于 9 V 或严格高于 16 V，并连续保持 100 ms，才置位电压故障。电压回到闭区间 [9 V, 16 V] 时，尚未完成的异常持续计时归零；恰好 9 V 或 16 V 不属于异常。

锚点 DEV-014-A2，位置 `{"sheet": "失效案例", "sheet_part": "xl/worksheets/sheet1.xml", "row": 7, "header_row": 4, "columns": "ABCDE", "record_key": "SYN-F003"}`

> 验证记录: 注入 40 ms 越界、20 ms 正常、70 ms 越界，期望不置位故障

## DEV-015 version_query

问题：只按 1.0 版规范，通信超时的时间阈值是多少？

答案：1.0 版规定：启动屏蔽结束后，距最后一帧有效报文达到 100 ms 置位。

模式：explicit；过滤：`{"revision_ids": ["b4ea42b0299d43025303cb85e8f8667ea57333e6d18887970e9b5e01e258a9fe"]}`

必需事实：引用 1.0 版；阈值为 100 ms

证据组 DEV-015-G1（组内 OR）：DEV-015-A1

锚点 DEV-015-A1，位置 `{"part": "word/document.xml", "body_child_1based": 7, "requirement_id": "R02"}`

> 启动屏蔽期结束后，若距最后一帧有效 SYN_PowerReq 的时间达到 100 ms，则置位通信超时故障 SYN_COMM_TIMEOUT。

## DEV-016 version_query

问题：对比 1.0 与 2.0 版，通信超时阈值和启动屏蔽时长分别怎样变化？

答案：1.0 版的超时阈值是 100 ms，启动屏蔽为 300 ms；2.0 版分别是 150 ms 和 500 ms。

模式：compare；过滤：`{"revision_ids": ["b4ea42b0299d43025303cb85e8f8667ea57333e6d18887970e9b5e01e258a9fe", "f53ac61a0ca8d50c454fc1a123174fe8e11462d237b9d3ddede6aadaf8c1f159"]}`

必需事实：1.0 超时 100 ms；1.0 屏蔽 300 ms；2.0 超时 150 ms；2.0 屏蔽 500 ms

证据组 DEV-016-G1（组内 OR）：DEV-016-A1

证据组 DEV-016-G2（组内 OR）：DEV-016-A2

证据组 DEV-016-G3（组内 OR）：DEV-016-A3

证据组 DEV-016-G4（组内 OR）：DEV-016-A4

锚点 DEV-016-A1，位置 `{"part": "word/document.xml", "body_child_1based": 7, "requirement_id": "R02"}`

> 启动屏蔽期结束后，若距最后一帧有效 SYN_PowerReq 的时间达到 100 ms，则置位通信超时故障 SYN_COMM_TIMEOUT。

锚点 DEV-016-A2，位置 `{"part": "word/document.xml", "body_child_1based": 9, "requirement_id": "R03"}`

> 自控制器上电起的前 300 ms 为通信超时诊断屏蔽期。

锚点 DEV-016-A3，位置 `{"part": "word/document.xml", "body_child_1based": 7, "requirement_id": "R02"}`

> 启动屏蔽期结束后，若距最后一帧有效 SYN_PowerReq 的时间达到 150 ms，则置位通信超时故障 SYN_COMM_TIMEOUT。

锚点 DEV-016-A4，位置 `{"part": "word/document.xml", "body_child_1based": 9, "requirement_id": "R03"}`

> 自控制器上电起的前 500 ms 为通信超时诊断屏蔽期。

## DEV-017 unanswerable

问题：SYN_PowerReq 对应的最大允许扭矩是多少 N·m？

答案：拒答：insufficient_evidence

模式：latest；过滤：`{}`

必需事实：

拒答依据：两版 R06 均明确未提供物理量程或最大扭矩；不能把零请求规则推导为最大值。

## DEV-018 unanswerable

问题：清除已存储通信诊断历史的服务编号是什么？

答案：拒答：insufficient_evidence

模式：latest；过滤：`{}`

必需事实：

拒答依据：两版 R04 均未规定历史清除服务；当前故障状态恢复不等于历史清除。

## DEV-019 unanswerable

问题：该合成控制器使用哪一型号的 MCU？

答案：拒答：insufficient_evidence

模式：latest；过滤：`{}`

必需事实：

拒答依据：两版 R08 明确未指定 MCU 型号，失效表也没有芯片型号。

## DEV-020 unanswerable

问题：上述修正使量产车辆事故率下降了百分之多少？

答案：拒答：insufficient_evidence

模式：latest；过滤：`{}`

必需事实：

拒答依据：所有资料均为虚构开发样本，没有量产事故统计，不能从案例数量推导事故率。

## DEV-021 equivalent_evidence

问题：SYN_AuxReq 在 CAN-A 运行模式下的超时边界是多少？

答案：距最后有效帧达到 150 ms（0.150 s）时置位。

模式：latest；过滤：`{}`

必需事实：CAN-A 运行模式；150 ms 与 0.150 s 等价；达到边界即置位

证据组 DEV-021-G1（组内 OR）：DEV-021-G1-A1 / DEV-021-G1-A2

锚点 DEV-021-G1-A1，位置 `{"sheet": "接口规范", "sheet_part": "xl/worksheets/sheet1.xml", "row": 5, "header_row": 4, "columns": "ABCDE", "record_key": "P01"}`

> 对象: SYN_AuxReq
> 条件: CAN-A，运行模式
> 规则: 距最后有效帧达到 150 ms 时置位超时。

锚点 DEV-021-G1-A2，位置 `{"sheet": "接口规范", "sheet_part": "xl/worksheets/sheet1.xml", "row": 10, "header_row": 4, "columns": "ABCDE", "record_key": "P06"}`

> 对象: SYN_AuxReq
> 条件: CAN-A，运行模式
> 规则: 通信超时边界为自最后有效报文起 0.150 s，达到边界即置位。

## DEV-022 hard_negative

问题：SYN_AuxReq 在 CAN-B 运行模式下，是 150 ms 还是 240 ms 超时？

答案：CAN-B 运行模式采用 240 ms。

模式：latest；过滤：`{}`

必需事实：CAN-B 运行模式；达到 240 ms 置位

证据组 DEV-022-G1（组内 OR）：DEV-022-G1-A1

锚点 DEV-022-G1-A1，位置 `{"sheet": "接口规范", "sheet_part": "xl/worksheets/sheet1.xml", "row": 6, "header_row": 4, "columns": "ABCDE", "record_key": "P02"}`

> 对象: SYN_AuxReq
> 条件: CAN-B，运行模式
> 规则: 距最后有效帧达到 240 ms 时置位超时。

## DEV-023 hard_negative

问题：SYN_AuxReq 在 CAN-A 诊断模式下能直接套用运行模式的 150 ms 吗？

答案：不能，CAN-A 诊断模式的边界为 900 ms。

模式：latest；过滤：`{}`

必需事实：不能套用运行模式；诊断模式为 900 ms

证据组 DEV-023-G1（组内 OR）：DEV-023-G1-A1

锚点 DEV-023-G1-A1，位置 `{"sheet": "接口规范", "sheet_part": "xl/worksheets/sheet1.xml", "row": 7, "header_row": 4, "columns": "ABCDE", "record_key": "P03"}`

> 对象: SYN_AuxReq
> 条件: CAN-A，诊断模式
> 规则: 距最后有效帧达到 900 ms 时置位超时。

## DEV-024 multi_evidence

问题：运行模式下，CAN-A 的 SYN_AuxReq 发送周期和 SYN_AuxWorker 的任务周期分别是多少？

答案：报文发送周期为 25 ms，任务调度周期为 5 ms。

模式：latest；过滤：`{}`

必需事实：报文周期 25 ms；任务周期 5 ms

证据组 DEV-024-G1（组内 OR）：DEV-024-G1-A1

证据组 DEV-024-G2（组内 OR）：DEV-024-G2-A1

锚点 DEV-024-G1-A1，位置 `{"sheet": "接口规范", "sheet_part": "xl/worksheets/sheet1.xml", "row": 8, "header_row": 4, "columns": "ABCDE", "record_key": "P04"}`

> 对象: SYN_AuxReq
> 条件: CAN-A，运行模式
> 规则: 发送周期为 25 ms。

锚点 DEV-024-G2-A1，位置 `{"sheet": "接口规范", "sheet_part": "xl/worksheets/sheet1.xml", "row": 11, "header_row": 4, "columns": "ABCDE", "record_key": "P07"}`

> 对象: SYN_AuxWorker
> 条件: 运行模式
> 规则: 处理任务调度周期为 5 ms。

## DEV-025 multi_evidence

问题：SYN-AUX-F01 的历史根因是什么？CAN-A 运行模式应使用哪个超时阈值？

答案：误套了 CAN-B 的 240 ms 参数；CAN-A 运行模式应采用 150 ms。

模式：latest；过滤：`{}`

必需事实：历史根因是误套 CAN-B 的 240 ms；CAN-A 应采用 150 ms

证据组 DEV-025-G1（组内 OR）：DEV-025-G1-A1

证据组 DEV-025-G2（组内 OR）：DEV-025-G2-A1 / DEV-025-G2-A2

锚点 DEV-025-G1-A1，位置 `{"sheet": "接口规范", "sheet_part": "xl/worksheets/sheet1.xml", "row": 12, "header_row": 4, "columns": "ABCDE", "record_key": "P08"}`

> 对象: SYN-AUX-F01
> 条件: CAN-A，运行模式
> 规则: 历史根因是误套 CAN-B 的 240 ms 超时参数。

锚点 DEV-025-G2-A1，位置 `{"sheet": "接口规范", "sheet_part": "xl/worksheets/sheet1.xml", "row": 5, "header_row": 4, "columns": "ABCDE", "record_key": "P01"}`

> 对象: SYN_AuxReq
> 条件: CAN-A，运行模式
> 规则: 距最后有效帧达到 150 ms 时置位超时。

锚点 DEV-025-G2-A2，位置 `{"sheet": "接口规范", "sheet_part": "xl/worksheets/sheet1.xml", "row": 10, "header_row": 4, "columns": "ABCDE", "record_key": "P06"}`

> 对象: SYN_AuxReq
> 条件: CAN-A，运行模式
> 规则: 通信超时边界为自最后有效报文起 0.150 s，达到边界即置位。

## DEV-026 multi_span

问题：SYN_AuxReq 的 CAN-A 运行模式恢复需要几帧，中途无效帧怎样影响计数？

答案：需要连续 6 帧有效；无效帧使计数归零。

模式：latest；过滤：`{}`

必需事实：连续 6 帧有效；无效帧归零

证据组 DEV-026-G1（组内 OR）：DEV-026-G1-A1

锚点 DEV-026-G1-A1，位置 `{"sheet": "接口规范", "sheet_part": "xl/worksheets/sheet1.xml", "row": 9, "header_row": 4, "columns": "ABCDE", "record_key": "P05"}`

> 对象: SYN_AuxReq
> 条件: CAN-A，运行模式
> 恢复条件为连续 6 帧有效。
> 无效帧使恢复计数归零。

## DEV-027 filtered_unanswerable

问题：SYN_PowerReq 的发送周期是多少？仅使用 XLSX 资料。

答案：拒答：insufficient_evidence

模式：latest；过滤：`{"file_types": ["xlsx"]}`

必需事实：

拒答依据：周期 20 ms 仅在 DOCX R01，XLSX 没有 SYN_PowerReq 的发送周期；不能采用被过滤的来源。

## DEV-028 filtered_unanswerable

问题：只根据历史失效表，SYN_COMM_TIMEOUT 当前版的具体毫秒阈值是多少？

答案：拒答：insufficient_evidence

模式：latest；过滤：`{"document_ids": ["b1704f3b-7a80-5627-a676-3f13a35bfb55"]}`

必需事实：

拒答依据：F001 要求读取所选规范的阈值，失效表本身不提供当前超时毫秒值。其他资料被 document_ids 排除。

## DEV-029 filter_query

问题：在失效案例工作表中，SYN-F005 遗漏了哪些退出要求，如何修正？

答案：遗漏 85 ℃回差与持续 10 s 要求；修正为同时判断退出温度与保持时间。

模式：latest；过滤：`{"file_types": ["xlsx"], "sheet": "失效案例"}`

必需事实：遗漏 85 ℃回差；遗漏持续 10 s；温度与保持时间同时判断

证据组 DEV-029-G1（组内 OR）：DEV-029-G1-A1

锚点 DEV-029-G1-A1，位置 `{"sheet": "失效案例", "sheet_part": "xl/worksheets/sheet1.xml", "row": 9, "header_row": 4, "columns": "ABCDE", "record_key": "SYN-F005"}`

> 根因: 退出条件遗漏 85 ℃回差和连续 10 s 要求
> 修正措施: 按退出温度与保持时间联合判定

## DEV-030 filter_query

问题：在指定接口文档的接口规范工作表中，SYN_AuxReq 的 CAN-B 运行超时值是多少？

答案：达到 240 ms 时置位。

模式：latest；过滤：`{"file_types": ["xlsx"], "sheet": "接口规范", "document_ids": ["b6a4b797-4e21-5ef6-9650-a85e36a302ae"]}`

必需事实：CAN-B 运行模式；240 ms

证据组 DEV-030-G1（组内 OR）：DEV-030-G1-A1

锚点 DEV-030-G1-A1，位置 `{"sheet": "接口规范", "sheet_part": "xl/worksheets/sheet1.xml", "row": 6, "header_row": 4, "columns": "ABCDE", "record_key": "P02"}`

> 对象: SYN_AuxReq
> 条件: CAN-B，运行模式
> 规则: 距最后有效帧达到 240 ms 时置位超时。

## DEV-031 filtered_unanswerable

问题：只查不存在的工作表“归档参数”，SYN_AuxReq 的周期是多少？

答案：拒答：insufficient_evidence

模式：latest；过滤：`{"sheet": "归档参数"}`

必需事实：

拒答依据：sheet 是合法精确过滤值，但语料没有该工作表，检索应为空。不是 InvalidFilter。

## DEV-032 version_conflict

问题：按指定两份现行接口规范，SYN_ResetGuard 在初始化模式同一项目配置的唯一超时阈值是多少？

答案：拒答：version_conflict

模式：latest；过滤：`{"document_ids": ["b6a4b797-4e21-5ef6-9650-a85e36a302ae", "76dea989-c9b5-50b0-9d29-2262f468e28f"]}`

必需事实：

锚点 DEV-032-G1-A1，位置 `{"sheet": "接口规范", "sheet_part": "xl/worksheets/sheet1.xml", "row": 14, "header_row": 4, "columns": "ABCDE", "record_key": "X01"}`

> 对象: SYN_ResetGuard
> 条件: 初始化模式，同一项目配置
> 规则: 等待确认的超时阈值为 120 ms。
> 备注: 与其他同范围现行规范同等优先级，无覆盖声明。

锚点 DEV-032-G2-A1，位置 `{"sheet": "复位接口", "sheet_part": "xl/worksheets/sheet1.xml", "row": 5, "header_row": 4, "columns": "ABCDE", "record_key": "X02"}`

> 对象: SYN_ResetGuard
> 条件: 初始化模式，同一项目配置
> 规则: 等待确认的超时阈值为 180 ms。
> 备注: 与其他同范围现行规范同等优先级，无覆盖声明。

拒答依据：同一对象、条件和项目配置的两份现行文档分别规定 120 ms 与 180 ms，且同等优先级无覆盖声明。不能按文件名或索引顺序选一个值。

## DEV-033 version_query

问题：对照指定两个修订，SYN_ResetGuard 初始化超时条款分别写了什么？

答案：辅助接口规范 X01 为 120 ms，复位接口规范 X02 为 180 ms；二者不一致，不能合并为一个值。

模式：compare；过滤：`{"revision_ids": ["6033d345bf0b4f987c0107d7803a720ec14f8a9baaac0e154ea355143b216b34", "ce66bba774b35197c7e941d08387ced7191d681a57b0b94be2ca08c309ef7238"]}`

必需事实：辅助接口规范 X01 为 120 ms；复位接口规范 X02 为 180 ms；明确不一致

证据组 DEV-033-G1（组内 OR）：DEV-033-G1-A1

证据组 DEV-033-G2（组内 OR）：DEV-033-G2-A1

锚点 DEV-033-G1-A1，位置 `{"sheet": "接口规范", "sheet_part": "xl/worksheets/sheet1.xml", "row": 14, "header_row": 4, "columns": "ABCDE", "record_key": "X01"}`

> 对象: SYN_ResetGuard
> 条件: 初始化模式，同一项目配置
> 规则: 等待确认的超时阈值为 120 ms。
> 备注: 与其他同范围现行规范同等优先级，无覆盖声明。

锚点 DEV-033-G2-A1，位置 `{"sheet": "复位接口", "sheet_part": "xl/worksheets/sheet1.xml", "row": 5, "header_row": 4, "columns": "ABCDE", "record_key": "X02"}`

> 对象: SYN_ResetGuard
> 条件: 初始化模式，同一项目配置
> 规则: 等待确认的超时阈值为 180 ms。
> 备注: 与其他同范围现行规范同等优先级，无覆盖声明。

## DEV-034 unanswerable

问题：SYN_AuxReq 在 CAN-C 运行模式的超时阈值是多少？

答案：拒答：insufficient_evidence

模式：latest；过滤：`{}`

必需事实：

拒答依据：资料只定义该对象的 CAN-A/CAN-B 条件，没有 CAN-C；不能从相近通道外推。

## DEV-035 partial_evidence

问题：请同时给出 CAN-A 运行模式 SYN_AuxReq 的发送周期和有效载荷字节数。

答案：拒答：insufficient_evidence

模式：latest；过滤：`{}`

必需事实：

拒答依据：P04 提供周期，但语料未给出有效载荷字节数。按整问拒答规则不能仅返回已知周期作为成功答案。

## DEV-036 unanswerable

问题：SYN_AuxReq 使用的 CRC 多项式是什么？

答案：拒答：insufficient_evidence

模式：latest；过滤：`{}`

必需事实：

拒答依据：资料出现校验失败和有效帧，但没有 CRC 算法或多项式，不能用常见协议知识补齐。

## DEV-037 hard_negative

问题：SYN_AuxReq_64 的超时阈值和发送周期分别是多少？

答案：超时为 480 ms，周期为 15 ms。

模式：latest；过滤：`{}`

必需事实：完整对象名 SYN_AuxReq_64；480 ms；15 ms

证据组 DEV-037-G1（组内 OR）：DEV-037-G1-A1

锚点 DEV-037-G1-A1，位置 `{"sheet": "接口规范", "sheet_part": "xl/worksheets/sheet1.xml", "row": 78, "header_row": 4, "columns": "ABCDE", "record_key": "D64"}`

> 对象: SYN_AuxReq_64
> 条件: CAN-B，运行模式
> 规则: 本对象距最后有效帧达到 480 ms 时置位超时；发送周期为 15 ms。

## DEV-038 hard_negative

问题：SYN_AuxReq_01 的超时阈值是否与无编号 SYN_AuxReq 的 CAN-A 运行规则相同？

答案：不同，SYN_AuxReq_01 为 165 ms，无编号对象 CAN-A 运行模式为 150 ms。

模式：latest；过滤：`{}`

必需事实：编号对象 165 ms；无编号对象 CAN-A 运行模式 150 ms；二者不同

证据组 DEV-038-G1（组内 OR）：DEV-038-G1-A1

证据组 DEV-038-G2（组内 OR）：DEV-038-G2-A1 / DEV-038-G2-A2

锚点 DEV-038-G1-A1，位置 `{"sheet": "接口规范", "sheet_part": "xl/worksheets/sheet1.xml", "row": 15, "header_row": 4, "columns": "ABCDE", "record_key": "D01"}`

> 对象: SYN_AuxReq_01
> 条件: CAN-A，运行模式
> 规则: 本对象距最后有效帧达到 165 ms 时置位超时；发送周期为 15 ms。

锚点 DEV-038-G2-A1，位置 `{"sheet": "接口规范", "sheet_part": "xl/worksheets/sheet1.xml", "row": 5, "header_row": 4, "columns": "ABCDE", "record_key": "P01"}`

> 对象: SYN_AuxReq
> 条件: CAN-A，运行模式
> 规则: 距最后有效帧达到 150 ms 时置位超时。

锚点 DEV-038-G2-A2，位置 `{"sheet": "接口规范", "sheet_part": "xl/worksheets/sheet1.xml", "row": 10, "header_row": 4, "columns": "ABCDE", "record_key": "P06"}`

> 对象: SYN_AuxReq
> 条件: CAN-A，运行模式
> 规则: 通信超时边界为自最后有效报文起 0.150 s，达到边界即置位。

## DEV-039 precise_term

问题：SYN_AuxReq 的 CAN-A 运行模式连续校验失败时，状态码是多少？

答案：状态码为 0x32。

模式：latest；过滤：`{}`

必需事实：状态码 0x32

证据组 DEV-039-G1（组内 OR）：DEV-039-G1-A1

锚点 DEV-039-G1-A1，位置 `{"sheet": "接口规范", "sheet_part": "xl/worksheets/sheet1.xml", "row": 13, "header_row": 4, "columns": "ABCDE", "record_key": "P09"}`

> 对象: SYN_AuxReq
> 条件: CAN-A，运行模式
> 规则: 连续校验失败时状态码为 0x32。

## DEV-040 semantic_paraphrase

问题：CAN-A 运行模式的 SYN_AuxReq 恢复三帧有效、中间一帧无效、再三帧有效，当前超时能清除吗？

答案：不能；无效帧清零后只有三帧，未达到连续六帧。

模式：latest；过滤：`{}`

必需事实：不能清除；无效帧归零；需要连续 6 帧

证据组 DEV-040-G1（组内 OR）：DEV-040-G1-A1

锚点 DEV-040-G1-A1，位置 `{"sheet": "接口规范", "sheet_part": "xl/worksheets/sheet1.xml", "row": 9, "header_row": 4, "columns": "ABCDE", "record_key": "P05"}`

> 对象: SYN_AuxReq
> 条件: CAN-A，运行模式
> 恢复条件为连续 6 帧有效。
> 无效帧使恢复计数归零。
