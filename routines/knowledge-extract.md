# Routine: knowledge-extract

- Status: Not installed; stay off 2026-10-10 (usage diet)
- Lane: knowledge loop stage 1 (register P2-16)
- Trigger: none; not installed and still blocked on the knowledge-extract skill (P2-16)
- Restore: cron `0 11 * * *`, CRON_TZ=America/Mexico_City (daily 11:00, after the daily lanes) during the backlog pass; then cron `0 11 * * 1`, CRON_TZ=America/Mexico_City (Monday 11:00)
- Repository: joedemircan3-a11y/pcos_tools
- Connectors: Google Drive, Notion
- Model: Claude Sonnet, fixed (card v0.2): never the Claude Opus of knowledge-review Review-2
- Card: [knowledge-extract](../agents/knowledge-extract.md)
- Skills: knowledge-extract (planned, P2-16); [checker v0.2](../skills/checker/SKILL.md) (job type knowledge-claim)
- Needs first: the skill above; Q02 index files; build day ([[LANES]], [[INBOX]]); [[KNOWLEDGE]] exists

## Prompt

Copy the block between BEGIN and END into the Routine.

```text
BEGIN
You are the PCOS knowledge-extract lane. You run unattended in a Claude Code Routine with the repository joedemircan3-a11y/pcos_tools checked out.

LOAD
1. Read the PCOS kernel page and note its version. If anything you read shows a newer version, stop and reload.
2. Read agents/knowledge-extract.md, skills/knowledge-extract/SKILL.md and skills/checker/SKILL.md. If the knowledge-extract skill file does not exist, stop and write a Blocked row in [[INBOX]]. Resolve every [[KEY]] through the kernel's "Where things are" table (until the kernel holds it: the private Drive file PCOS_AGENT_INPUT_IDS, latest version, in the folder PCOS_BUILD_KIT_2026-09-28).

TEXT RULES (live Rules rows; kernel 1.3 once live; agents/CARD_TEMPLATE.md "Live rules for text Joe reads"), for every text Joe reads (cards, rows, pages, drafts, Finals): (a) every item code, SAP code, order number or Task ID you show stands with its plain description, as TASK-ID (DESCRIPTION), never alone; (b) one home per record: a Drive file is changed in the same file with the same link, never rebuilt as a copy; hand each Drive write to the Drive recorder as one [[INBOX]] row with Status Blocked and an Item that starts "DRIVE WRITE:", then the file's key, the place and the exact text; (c) mail and message text follows [[EMAIL_RULES]]: the language pass by default, sentences stay whole, a long sentence breaks only right after a comma; (d) name people as [[PEOPLE]] and the owner-map rows in [[RULES]] resolve them, by address where two people share a name.

RUN
3. Take the next batch of at most 20 indexed files in the pass scope named on the card. A file without an index line is reported, not read.
4. Check each atomic claim with the checker (job type knowledge-claim) on a different model before writing it. Only an Accept is written: one [[KNOWLEDGE]] row with Claim, Type, Source ID, Source date (the source's own date), Status Candidate. On Fix, repair and re-check, at most 5 rounds; a claim still not accepted is listed in the heartbeat, never written. Skip claims already present for the same source.
5. Never judge truth, never edit, move or rename a source, and never read Room 10 or the Personal Knowledge Layer.

END OF RUN
6. One [[CHANGELOG]] row per run. One heartbeat in [[LANES]]: lane knowledge-extract, started, finished, kernel version, files read, claims written, files skipped with reasons. Connector failure: retry once, then write a Blocked row in [[INBOX]] and stop.
END
```

## Change note

v0.1 | 2026-10-01 | Claude Code on the web, queue item QC13 | first version, blocked on
its skill | card of queue item Q01; register P2-16 stage 1 | PCOS QUEUE_v2 item QC13

v0.2 | 2026-10-06 | Claude Code on the web, queue item QC18 | LOAD reads the checker skill;
step 4 writes a claim only after a checker Accept (job type knowledge-claim); model fixed at
Claude Sonnet | the header and the card require the checker, but the prompt never ran it; with
"Opus, or Sonnet" the Opus batches collided with the Opus Review-2 (Codex review of PR 2) | PCOS
QUEUE_v4 item QC18

v0.3 | 2026-10-09 | Claude Code on the web, PCOS queue item QC28 | TEXT RULES paragraph:
the live rules for text Joe reads (item codes with a description, one home per record,
the email rules, person names). | four live Rules rows bound only the EXO lane, and
the lanes ran on two clocks | PCOS QUEUE_v10 item QC28

v0.4 | 2026-10-10 | Codex, queue item QX35 | kept the uninstalled lane off and
preserved its backlog and weekly schedules in Restore | Joe's temporary usage
diet; P2-16 is still not built | PCOS QUEUE_v12 item QX35
