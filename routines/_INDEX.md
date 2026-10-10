# routines/_INDEX.md

Paste-ready prompts for the planned Claude Code Routines: one file per Routine.
PC-1 (step 4) and build day create them from here. Each prompt is a loader: it reads
the kernel, then the lane's card in `agents/` and its skill in `skills/`, and
resolves source keys through the kernel's "Where things are" table. Until the kernel
holds that table, keys resolve through the private Drive map. Lane logic lives in
the cards and skills, so a Routine prompt rarely changes.

One clock: every Routine runs on America/Mexico_City, the time zone of Joe's Outlook
calendar ("Central Standard Time (Mexico)", read through the Microsoft 365 connector on
2026-10-09, queue item QC28); every cron line names it as CRON_TZ, and
`tests/test_rules_and_clock.py` fails on any other zone. Every prompt carries the TEXT
RULES paragraph, the live rules for text Joe reads (`agents/CARD_TEMPLATE.md`).

Usage diet (Joe, 2026-10-10; queue item QX35): a paused Routine has `Trigger:
none while paused` and keeps its former trigger on a `Restore:` line. A Routine
that is not installed stays off. The diet is temporary until Joe restores it.

Times: all in that clock. The session that creates a Routine
may shift a minute value by a few minutes to avoid the top-of-hour load, but it must
keep the order of dependent active lanes. Restore lines preserve the old dependency
order for paused lanes (the council stages; the ledger backtest before L4).

One line per file, using the PCOS index convention (P2-12): title | ID | what | date
| status | open when.

## Claude Code Routines (files in this folder)

| Title | ID | What | Date | Status | Open when |
| --- | --- | --- | --- | --- | --- |
| L1 Brief | routines/L1-brief.md | Weekdays 06:30: sweep, route, Inbox rows, at most 5 checked drafts, never send | 2026-10-10 | Kept (usage diet) | Changing the brief |
| L2 Render | routines/L2-render.md | Daily 07:15: Today page from rows; mirrors only after cutover | 2026-10-09 | Candidate | Build day; changing Today |
| L3 Health | routines/L3-health.md | Paused; Restore: daily 07:30 for missed runs, stale kernel, old Inbox rows, REASON-MISSING, naming and governance count | 2026-10-10 | Paused 2026-10-10 (usage diet) | Joe restores the lane |
| L4 Weekly | routines/L4-weekly.md | Sunday 09:00: calibration, golden-set eval, weekly-evolve, knowledge chair later | 2026-10-09 | Candidate | Build day; rule and skill evolution |
| council-github chair | routines/council-github-chair.md | Paused; Restore: PR review/comment events plus every 2 hours for the missing-review fallback | 2026-10-10 | Paused 2026-10-10 (usage diet) | Joe restores the lane |
| prediction-ledger | routines/prediction-ledger.md | Paused; Restore: weekdays 07:45 to predict, check, ask when blind and score | 2026-10-10 | Paused 2026-10-10 (usage diet) | Joe restores the lane |
| exo | routines/exo.md | Daily 07:00 only: one card about today's work, at most two commitment items first, answers filed, skip rule; 13:00 is off | 2026-10-10 | Kept (usage diet) | Changing the EXO lane |
| retro | routines/retro.md | Daily 18:53: the evening card, five questions about the past (commitments past their date included), answers filed | 2026-10-10 | Kept (usage diet) | Changing the Retro lane |
| commitments | routines/commitments.md | Weekdays 12:40 only: promises in mail into Commitments rows, evidence check, rows marked for the next EXO and retro cards; 06:40 and 18:40 are off | 2026-10-10 | Kept (usage diet) | Changing the Commitments lane |
| commitments-backfill | routines/commitments-backfill.md | Once by hand: the last 30 days of sent mail into Commitments rows, no card, no draft; no recurring schedule | 2026-10-10 | One-time manual | Resume until its heartbeat says complete |
| ledger-backtest | routines/ledger-backtest.md | Paused; Restore: once by hand, then Sunday 07:00 for the predictor over settled mail | 2026-10-10 | Paused 2026-10-10 (usage diet) | Joe restores the lane |
| council-board Draft | routines/council-board-draft.md | Paused; Restore: daily 08:00 to draft queued Council rows, plan round first | 2026-10-10 | Paused 2026-10-10 (usage diet) | Joe restores the lane |
| council-board Review-2 | routines/council-board-review-2.md | Paused; Restore: daily 09:30 anonymous Review-2 (Claude until Gemini) | 2026-10-10 | Paused 2026-10-10 (usage diet) | Joe restores the lane |
| council-board chair | routines/council-board-chair.md | Paused; Restore: daily 10:00 for Final, Dissent and execution rows | 2026-10-10 | Paused 2026-10-10 (usage diet) | Joe restores the lane |
| intake-email | routines/intake-email.md | Not installed; Restore: weekdays hourly 08:05 to 18:05 for Door 1 requests, drafts and send gate | 2026-10-10 | Stay off (usage diet) | After PC-2, the allowlist and Joe's restore |
| knowledge-extract | routines/knowledge-extract.md | Not installed; Restore: daily 11:00 during the backlog, then weekly, for claims into Knowledge | 2026-10-10 | Stay off (usage diet) | After P2-16 is built and Joe restores it |
| knowledge-review Review-2 | routines/knowledge-review-2.md | Not installed; Restore: daily 13:00 anonymous Review-2 of claims (Claude until Gemini) | 2026-10-10 | Stay off (usage diet) | After P2-16 is built and Joe restores it |

## Scheduled lanes that are not Claude Code Routines (no file here)

| Lane | Runs on | Prompt lives in | Note |
| --- | --- | --- | --- |
| L5 CAL | Claude Routine, paused 2026-10-10 (usage diet); Restore: daily 07:00 | The CAL lane's own folder ([[CAL_FOLDER]]) | No routine file in this repository |
| PCOS hub sync | Claude scheduled task, paused 2026-10-10 (usage diet); Restore: daily 06:00 | Its installed task | No routine file in this repository |
| Drive recorder (Claude side) | Claude Routine, installed 2026-10-08 (Lanes row "Drive recorder (Claude side)"), daily 20:10 only (was 08:10, 14:10 and 20:10) | The installed Routine, created outside this repository because existing Routines cannot take new connectors; it has Google Docs and Google Sheets | Consumes every [[INBOX]] row with Status Blocked and an Item that starts "DRIVE WRITE:" (TEXT RULES b): writes the text in place in the same file, reads it back, sets the row Applied, one Changelog row; a row it cannot apply stays Blocked with the reason. The GPT-side recorder is planned (queue item Q31) |
| L6 07-SAP-01 | Cowork desktop task on Joe's computer | Its existing task | The only lane that needs Joe's computer |
| G1 Project Watch | ChatGPT scheduled task, every 6 hours | ChatGPT project | Writes Inbox rows |
| G2 Weekly leadership page | ChatGPT scheduled task, Sunday | ChatGPT project | |
| council-board Review-1 | ChatGPT scheduled task, daily 09:00 | The reviewer prompt in `skills/council-board/references/prompts.md` | Joe pastes it at PC-1 step 5 |
| knowledge-review Review-1 | ChatGPT scheduled task, daily 12:00 | Planned with the knowledge-review skill (P2-16) | |
| N1 Decision processor, N2 Hub hygiene, N3 Inbox mail | Notion custom agents | Notion (build day, Business plan) | |
| X1 Codex Watchdog | Codex, weekdays 07:45 | Codex | Re-triggers missed Claude lanes |
| checker (L7) | No schedule of its own | Runs as a subagent inside each lane; the weekly eval runs inside L4 | |
