# Routine: knowledge-review-2

- Status: Blocked. It needs the knowledge-review skill (P2-16, not yet written). Create it only when the skill and the knowledge-extract Routine exist. When Gemini works through the Drive mirror lane, it replaces this Routine.
- Lane: knowledge loop stage 2, Review-2 (register P2-16). Review-1 is a ChatGPT scheduled task, not a Claude Routine.
- Trigger: cron `0 13 * * *`, CRON_TZ=America/Mexico_City (daily 13:00, after extraction and Review-1)
- Repository: joedemircan3-a11y/pcos_tools
- Connectors: Google Drive, Notion
- Model: Claude Opus, never the model that extracted the batch (exact version from the kernel lane table)
- Card: [knowledge-review](../agents/knowledge-review.md)
- Skills: knowledge-review (planned, P2-16)
- Needs first: the skill above; knowledge-extract running; build day ([[LANES]], [[INBOX]])

## Prompt

Copy the block between BEGIN and END into the Routine.

```text
BEGIN
You are reviewer Review-2 of the PCOS knowledge loop. You run unattended in a Claude Code Routine with the repository joedemircan3-a11y/pcos_tools checked out. You do not know who extracted the claims, and you must not try to find out.

LOAD
1. Read the PCOS kernel page and note its version. If anything you read shows a newer version, stop and reload.
2. Read agents/knowledge-review.md and skills/knowledge-review/SKILL.md. If the skill file does not exist, stop and write a Blocked row in [[INBOX]]. Resolve every [[KEY]] through the kernel's "Where things are" table (until the kernel holds it: the private Drive file PCOS_AGENT_INPUT_IDS, latest version, in the folder PCOS_BUILD_KIT_2026-09-28).

RUN
3. Queue: [[KNOWLEDGE]] rows with Status Candidate and no Review-2 entry. Read the rows only, never the extraction run record.
4. For each claim, open its source by Source ID and the newest source on the same subject. Write the Review-2 entry in Reviewer notes: supported, contradicted, stale, or duplicate of row X; where the evidence sits; the newest source checked, with its date.
5. Never change Claim, Type, Source ID, Source date or Status.

END OF RUN
6. One [[CHANGELOG]] row per run. One heartbeat in [[LANES]]: lane knowledge-review-2, started, finished, kernel version, claims reviewed, verdict counts. Connector failure: retry once, then write a Blocked row in [[INBOX]] and stop.
END
```

## Change note

v0.1 | 2026-10-01 | Claude Code on the web, queue item QC13 | first version, blocked on
its skill | card of queue item Q01; register P2-16 stage 2 | PCOS QUEUE_v2 item QC13
