---
name: work-evidence
description: Reconstruct task-level work contributions and estimated hours from chats, deliverables, meetings, and personal recollections; produce concise evidence-linked internship or remote-work reports and timesheet drafts.
---

# Work Evidence

Help interns and other workers explain their contributions with task totals, working periods, deliverables, and evidence. Match the user's language. Default to a concise local Markdown report; use an external document only when requested and its connector is available.

## Establish the reporting boundary

Identify the period, timezone, cutoff date, account/workspace, intended reader, and required deliverable. Use provided context before asking. Clarify whether submission covers the full calendar month, including forecast days. Never infer company schedules, holidays, daily hours, overtime recognition, or pay rules from location or calendar alone.

Read only relevant authorized work sources. Prefer connected APIs and chat-history tools, then user-provided exports or project files. Keep personal and employer accounts separate; follow local account-routing instructions. Do not collect unrelated messages or credentials. Describe material gaps without treating missing messages as proof of no work.

## Reconstruct work by task

Read [references/accounting.md](references/accounting.md) before estimating or changing hours. Create a private ledger using [references/ledger.md](references/ledger.md) when reproducibility or arithmetic checking is useful.

- Group repeated discussions, iterations, documents, and PRs under the same actual task. Separate tasks when they have distinct deliverables or objectives, not merely different chats.
- Count task-directed research, conception, prompt writing, reading and correcting AI output, manual operation, verification, debugging, meeting preparation, presentation, feedback, handoff, and asynchronous communication. Allocate each activity once to its task.
- Distinguish personally performed work from teammates' output and unattended agent execution. Preserve incomplete, blocked, prototype, submitted, accepted, and deployed states as the evidence supports them.
- Use actual human activity, meeting attendance, recollection, and task scope as estimation anchors. Message counts, commit counts, and elapsed chat spans are clues, not conversions into hours.
- A requested total is a claim or proposal to reconcile, not a reason to distribute unexplained extra hours. Accept user-supplied actual-time recollections as attributed inputs without demanding minute-level proof. If a fixed estimate is needed, select and explain a best estimate from task inputs, then sum it; do not silently rebalance tasks to hit a target.
- Keep recorded, recalled, estimated, and forecast time distinguishable. Future work must remain forecast even when included in a full-month submission. Use explicit timezone offsets for timed records.

## Attach evidence that answers the reader's question

For each task, name the contribution, outcome/status, period, hours, and supporting artifact. Prefer the worker's deliverable documents and PRs over generic chat links. Include every relevant identified deliverable, including coauthored documents labeled as such; distinguish reference material from authored output. Do not create documents solely to manufacture evidence.

Verify links and authorship/status using accessible sources when possible. State unresolved access or provenance gaps. Evidence of an artifact supports that the task occurred; it does not independently certify every estimated hour or prove impact. Do not infer ROI, adoption, acceptance, or publication from a draft or proposed plan.

## Produce a short, reviewable report

Use [assets/report-template.md](assets/report-template.md) as a starting point, adapting rather than copying unused sections. Include:

1. Reporting period, cutoff, task count, and a single clearly labeled total when requested. Separate forecast hours in one short sentence.
2. One table: task and concrete output, working period, task hours including handoff/communication, and evidence links.
3. Only material limitations or outstanding acceptance items.

Use weeks by default for a management summary. Define week numbering: Monday–Sunday, clipped to the reporting month; October 1 falling on Thursday starts a partial Week 1, not a new seven-day rolling window. A task spanning weeks does not imply continuous work every day. Retain dates in the underlying ledger.

For structured ledgers, run:

```bash
python3 scripts/report.py path/to/private-ledger.json
```

The helper writes Markdown to stdout. It validates and sums the ledger; it cannot determine whether reported work actually happened. Its report shows precision consistent with the input, not a certification. Read private inputs locally; do not upload them to an issue or public repository.

When editing a requested external document, use its available document skill/connector and current state. Preserve user edits and existing links. Follow applicable identity and sharing rules; a request to produce a report does not authorize sending it to a supervisor or changing its permissions.

Before delivery, verify the task count, sums, distinct versus forecast hours, week labels, task states, duplicate time, and evidence links. If a retrospective total changes after new recollections, explain the changed assumptions briefly instead of presenting the old estimate as a measured baseline.

## Reuse and publication

Keep generated ledgers and reports out of the skill package. Examples must be synthetic: no real company names, emails, account IDs, private links, chat extracts, compensation, or authorization material. Follow [references/publication.md](references/publication.md) when preparing public examples or publishing a repository. Open-source publication and installing the skill into a protected location are separate operations with their own authorization.
