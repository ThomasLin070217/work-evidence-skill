# Work Evidence · 工作产出与工时说明

把散落在聊天、会议、调研和交付物里的工作，整理成按任务归并、有证据入口的工时报告。适合远程实习、兼职与项目协作，也适合需要向负责人解释个人贡献的人。

**它帮助还原工作，不替你证明未经记录的每一分钟。** 构思、prompt迭代、验证、会议、交接和回复都可以进入实际投入估算；无人值守的Agent运行、重复时段和未发生的工作需要单独处理。公司是否认可某类工时，仍由其核算规则决定。

## 使用

将 `skills/work-evidence` 文件夹复制到你的 Codex skills 目录（通常为 `~/.codex/skills/`）。同名技能存在时先比较，不要直接覆盖。其他支持 `SKILL.md` 的工具可使用同一个入口；UI元数据是Codex可选项。

```text
使用 $work-evidence，整理我这个月的工作。
按任务汇总构思、执行、沟通和开会时间，开展时间按周写。
把我产出的文档和PR放进证据栏，月底计划单独标明。
先给我一页Markdown，不要代我发给上级。
```

无需指定某个平台。可以使用已连接的工作聊天、会议、文档工具，也可以直接提供导出记录或个人回忆。飞书、Notion等外部文档写入需要环境中有相应连接工具，核心技能和校验脚本不依赖这些服务。

## 本地校验与生成

Python 3.9+，仅使用标准库：

```bash
python3 skills/work-evidence/scripts/report.py skills/work-evidence/assets/example-ledger.json
python3 -m unittest discover -s tests -v
```

脚本检查分项加总、日期和月底预计投入、重复ID及显式时间重叠，输出按周汇总的Markdown。示例全部虚构，使用 `example.org` 链接。真实资料请放在被忽略的 `work/` 或其他私有位置。

## 设计重点

- 以任务而非聊天条数计量；包含思考、研究和沟通成本。
- 区分记录、本人回忆、估算与未来计划，支持固定的申报估算总数。
- 已交付、待验收、原型与正式上线分别描述，不把目标数量当完成数量。
- 文档能支持工作发生与产出，不能自动认证估算时长。
- 发布技能时只包含通用方法和合成样例，不包含个人或雇主资料。

## English

An agent skill for reconstructing task-level contributions and timesheet drafts from work evidence and personal recollection. Includes thinking, AI prompt iteration, human review, meetings and handoffs; separates recorded, recalled, estimated and forecast time. Outputs concise evidence-linked reports. A dependency-free ledger helper catches arithmetic, date and overlap errors. It does not certify time or guarantee employer approval.

Licensed under MIT. Contributions should use synthetic examples only.
