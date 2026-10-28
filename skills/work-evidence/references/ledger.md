# Private ledger format

Use JSON with `period_start`, `period_end`, `as_of` (YYYY-MM-DD), `timezone` (IANA name), `tasks`, and `entries`. Dates are inclusive local dates. The helper supports a reporting period within one calendar month. Write separate ledgers for separate months.

Each task has a unique `id`, `title`, `output` (accurate status), and `evidence` array of `{label, url}`. Evidence can be empty when unavailable; do not invent links. HTTP(S) URLs with embedded credentials are rejected. Private authorized links may appear in a private report, never the public sample.

Each entry has a unique `id`, `task_id`, `kind`, `basis`, and either:

- `date` plus positive integer `minutes`; or
- offset-aware `start` and `end` on the same local date. Duration must be whole minutes. The offset must agree with the ledger's timezone.

Kinds are `recorded`, `recalled`, `estimated`, `forecast`. `basis` explains the source or estimate; it must not contain credentials. Nonforecast entries cannot fall after `as_of`, and forecast entries must be after it. All entries must lie within the reporting period. Avoid duplicating a forecast with an actual entry when updating a month.

For tasks active on separate dates, use multiple entries rather than treating the entire start-to-end window as continuous work. The helper groups task dates into reporting-month week labels. For untimed entries, the helper checks that combined daily work does not exceed 24 hours, but cannot detect overlap without clock times. Review those allocations yourself.

Timed entries across all tasks must not overlap. If two sources describe the same attendance, consolidate their union before entering it. Repeated IDs are errors, not silently dropped: investigate whether they are duplicates or distinct activities.

The synthetic [sample ledger](../assets/example-ledger.json) demonstrates the format. Do not copy its hours into a real worker's report. Use evidence collection and recollection to supply values.
