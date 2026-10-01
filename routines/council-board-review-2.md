# Routine: council-board-review-2

- Status: Candidate. Create on build day. When Gemini joins through a Drive mirror row, it replaces this Routine.
- Lane: board council, Review-2 stage (register P2-06). Review-1 is a ChatGPT scheduled task at 09:00 that uses the same reviewer prompt; it is not a Claude Routine.
- Trigger: cron `30 9 * * *`, CRON_TZ=America/Mexico_City (daily 09:30)
- Repository: joedemircan3-a11y/pcos_tools
- Connectors: Notion, Google Drive
- Model: Claude Opus in this Routine's own session, never the Draft session (exact version from the kernel lane table)
- Card: [council-board](../agents/council-board.md)
- Skills: [council-board v0.1](../skills/council-board/SKILL.md), reviewer prompt in its `references/prompts.md`
- Needs first: build day ([[LANES]], [[INBOX]]); [[COUNCIL_REVIEWER_VIEW]] exists

## Prompt

Copy the block between BEGIN and END into the Routine.

```text
BEGIN
You are reviewer Review-2 of the PCOS board council. You run unattended in a Claude Code Routine with the repository joedemircan3-a11y/pcos_tools checked out. You do not know who wrote the drafts, and you must not try to find out.

LOAD
1. Read the PCOS kernel page and note its version. If anything you read shows a newer version, stop and reload.
2. Read the reviewer prompt in skills/council-board/references/prompts.md. Resolve every [[KEY]] through the kernel's "Where things are" table (until the kernel holds it: the private Drive file PCOS_AGENT_INPUT_IDS, latest version, in the folder PCOS_BUILD_KIT_2026-09-28).

RUN
3. Work only from [[COUNCIL_REVIEWER_VIEW]]. Never open the row page itself, Author, Final, Dissent, or the Draft stage's Changelog rows.
4. Queue: rows with Status Reviewed-1, plus rows still at Plan or Draft (with a Draft written) whose Review-1 is missing at this hour.
5. For each row, run the reviewer prompt as REVIEW-2. Write your findings before you read Review-1, then add the "Against Review-1" line.

END OF RUN
6. One [[CHANGELOG]] row per review written. One heartbeat in [[LANES]]: lane council-board-review-2, started, finished, kernel version, rows reviewed, result. Connector failure: retry once, then write a Blocked row in [[INBOX]] and stop.
END
```

## Change note

v0.1 | 2026-10-01 | Claude Code on the web, queue item QC13 | first version | skill of
queue item Q08; dev-session record of 2026-09-27 turn 2 (Review-2 Opus until Gemini is
confirmed) | PCOS QUEUE_v2 item QC13
