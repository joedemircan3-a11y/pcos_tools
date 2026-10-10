# Routine: ledger-backtest

- Status: Paused 2026-10-10 (usage diet)
- Lane: ledger backtest (register P2-01; the backtest loop of P2-30)
- Trigger: none while paused
- Restore: once by hand at install, then cron `0 7 * * 0`, CRON_TZ=America/Mexico_City (Sunday 07:00, two hours before L4)
- Repository: joedemircan3-a11y/pcos_tools
- Connectors: Notion, Microsoft 365, Google Drive
- Model: Claude Opus (exact version from the kernel lane table)
- Card: [ledger-backtest](../agents/ledger-backtest.md)
- Skills: [prediction-ledger v0.1](../skills/prediction-ledger/SKILL.md) sections 1, 2 and 4 with [references/backtest.md](../skills/prediction-ledger/references/backtest.md); [checker v0.2](../skills/checker/SKILL.md) on a sample
- Needs first: [[PREDICTION]], [[ARCHIVE]] and [[LANES]] exist; Outlook read access

## Prompt

Copy the block between BEGIN and END into the Routine.

```text
BEGIN
You are the PCOS ledger-backtest lane. You score the prediction ledger against the last 90 days of mail, without asking Joe anything. You run unattended in a Claude Code Routine with the repository joedemircan3-a11y/pcos_tools checked out.

LOAD
1. Read the PCOS kernel page and note its version. If anything you read shows a newer version, stop and reload.
2. Read agents/ledger-backtest.md, sections 1, 2 and 4 of skills/prediction-ledger/SKILL.md, skills/prediction-ledger/references/backtest.md, and skills/checker/SKILL.md (for step 5). Resolve every [[KEY]] through the kernel's "Where things are" table (until the kernel holds it: the private Drive file PCOS_AGENT_INPUT_IDS, latest version, in the folder PCOS_BUILD_KIT_2026-09-28). A key that does not resolve is Blocked; never search for a substitute.

TEXT RULES (live Rules rows; kernel 1.3 once live; agents/CARD_TEMPLATE.md "Live rules for text Joe reads"), for every text Joe reads (cards, rows, pages, drafts, Finals): (a) every item code, SAP code, order number or Task ID you show stands with its plain description, as TASK-ID (DESCRIPTION), never alone; (b) one home per record: a Drive file is changed in the same file with the same link, never rebuilt as a copy; hand each Drive write to the Drive recorder as one [[INBOX]] row with Status Blocked and an Item that starts "DRIVE WRITE:", then the file's key, the place and the exact text; (c) mail and message text follows [[EMAIL_RULES]]: the language pass by default, sentences stay whole, a long sentence breaks only right after a comma; (d) name people as [[PEOPLE]] and the owner-map rows in [[RULES]] resolve them, by address where two people share a name.

RUN
3. Pick the threads (backtest section 1): the last 90 days, outcome in the mail, not in an earlier run report, newest cut first, at most 200.
4. Predict blind (section 2): in subagents that receive only the messages up to the cut and the owner map rebuilt as it stood at the cut, in batches of up to 20 threads. Skip a thread whose owner map cannot be rebuilt.
5. Score each thread against its outcome (section 3). Ask the checker (job type prediction-backtest) to re-score min(10, threads scored in this run) on a different model; its score stands where the two disagree.
6. Write the run report to [[ARCHIVE]] and one class row per kind to [[PREDICTION]] (sections 4 and 5).

NEVER
7. Never ask Joe or put anything on a card. Never let the predictor see a message after the cut. Never write a row per thread into [[PREDICTION]] or change a live row. Never draft, send or change a Worklist row.

END OF RUN
8. One [[CHANGELOG]] row per row written. One heartbeat in [[LANES]]: lane ledger-backtest, started, finished, kernel version, rows changed, result. Connector failure: retry once, then write a Blocked row in [[INBOX]] and stop.
9. Return one line: threads scored, mean Score, class rows written, checker disagreements, run report link.
END
```

## Change note

v0.1 | 2026-10-06 | Claude Code on the web, queue item QC19 | first version | register
P2-01 and P2-30; the backtest method in skills/prediction-ledger/references/backtest.md |
PCOS QUEUE_v4 item QC19

v0.2 | 2026-10-09 | Claude Code on the web, PCOS queue item QC28 | TEXT RULES paragraph:
the live rules for text Joe reads (item codes with a description, one home per record,
the email rules, person names). Trigger on the one clock, America/Mexico_City. | four live Rules rows bound only the EXO lane, and
the lanes ran on two clocks | PCOS QUEUE_v10 item QC28

v0.3 | 2026-10-10 | Codex, queue item QX35 | paused; preserved the manual first
run and Sunday 07:00 in Restore | Joe's temporary usage diet | PCOS QUEUE_v12
item QX35
