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

Times: all in that clock. The session that creates a Routine
may shift a minute value by a few minutes to avoid the top-of-hour load, but it must
keep the order of dependent lanes (L1, then L2 and L3, then prediction-ledger; the
council at 08:00, 09:00, 09:30 and 10:00; on Sunday the ledger backtest before L4;
commitments before the EXO and retro cards it feeds).

One line per file, using the PCOS index convention (P2-12): title | ID | what | date
| status | open when.

## Claude Code Routines (files in this folder)

| Title | ID | What | Date | Status | Open when |
| --- | --- | --- | --- | --- | --- |
| L1 Brief | routines/L1-brief.md | Weekdays 06:30: sweep, route, Inbox rows, at most 5 checked drafts, never send | 2026-10-09 | Candidate | Build day; changing the brief |
| L2 Render | routines/L2-render.md | Daily 07:15: Today page from rows; mirrors only after cutover | 2026-10-09 | Candidate | Build day; changing Today |
| L3 Health | routines/L3-health.md | Daily 07:30: missed runs, stale kernel, old Inbox rows, REASON-MISSING, naming, governance count | 2026-10-09 | Candidate | Build day; a lane goes quiet |
| L4 Weekly | routines/L4-weekly.md | Sunday 09:00: calibration, golden-set eval, weekly-evolve, knowledge chair later | 2026-10-09 | Candidate | Build day; rule and skill evolution |
| council-github chair | routines/council-github-chair.md | GitHub PR events, plus a run every 2 hours for the missing-review fallback: chairs council PRs only, writes Final and Dissent to the PR and the Council row | 2026-10-09 | Candidate | PC-1 step 4 (P2-07) |
| prediction-ledger | routines/prediction-ledger.md | Weekdays 07:45: predict, check, ask when blind, score | 2026-10-09 | Candidate | Build day plus three Brief runs |
| exo | routines/exo.md | 07:00 and 13:00: distribute front-line steps as checked internal Outlook drafts, watch answers, and show one today's-work card with commitment items first | 2026-10-10 | Candidate | Build day; QW21 removes the 18:53 run |
| retro | routines/retro.md | Daily 18:53: the evening card, five questions about the past (commitments past their date included), answers filed | 2026-10-09 | Candidate | QW21, with the EXO 18:53 run removed |
| commitments | routines/commitments.md | Weekdays 06:40, 12:40 and 18:40: promises in mail into Commitments rows, evidence check, at most two rows marked for the next card with checked drafts | 2026-10-09 | Candidate | QW21, after the Commitments database exists |
| commitments-backfill | routines/commitments-backfill.md | Once at install: the last 30 days of sent mail into Commitments rows, no card, no draft | 2026-10-09 | Candidate | QW21: run once after the first commitments run |
| ledger-backtest | routines/ledger-backtest.md | Once at install, then Sunday 07:00: the ledger's predictor over settled threads of the last 90 days, scored without Joe, accuracy by class | 2026-10-09 | Candidate | QW21: run once, then before L4 |
| council-board Draft | routines/council-board-draft.md | Daily 08:00: drafts queued Council rows, plan round first | 2026-10-09 | Candidate | Build day |
| council-board Review-2 | routines/council-board-review-2.md | Daily 09:30: anonymous Review-2 (Claude until Gemini) | 2026-10-09 | Candidate | Build day |
| council-board chair | routines/council-board-chair.md | Daily 10:00: Final, Dissent, Status; creates execution rows | 2026-10-09 | Candidate | Build day |
| intake-email | routines/intake-email.md | Weekdays hourly 08:05 to 18:05: Door 1 requests, drafts, send gate | 2026-10-09 | Candidate | After PC-2 and the allowlist |
| knowledge-extract | routines/knowledge-extract.md | Daily 11:00 during the backlog, then weekly: claims into Knowledge | 2026-10-09 | Blocked (skill P2-16, Q02 indexes) | When P2-16 is built |
| knowledge-review Review-2 | routines/knowledge-review-2.md | Daily 13:00: anonymous Review-2 of claims (Claude until Gemini) | 2026-10-09 | Blocked (skill P2-16) | When P2-16 is built |

## Scheduled lanes that are not Claude Code Routines (no file here)

| Lane | Runs on | Prompt lives in | Note |
| --- | --- | --- | --- |
| L5 CAL | Claude Routine, already installed | The CAL lane's own folder ([[CAL_FOLDER]]) | Not rewritten here |
| Drive recorder (Claude side) | Claude Routine, installed 2026-10-08 (Lanes row "Drive recorder (Claude side)"), 08:10, 14:10 and 20:10 | The installed Routine, created outside this repository because existing Routines cannot take new connectors; it has Google Docs and Google Sheets | Consumes every [[INBOX]] row with Status Blocked and an Item that starts "DRIVE WRITE:" (TEXT RULES b): writes the text in place in the same file, reads it back, sets the row Applied, one Changelog row; a row it cannot apply stays Blocked with the reason. The GPT-side recorder is planned (queue item Q31) |
| L6 07-SAP-01 | Cowork desktop task on Joe's computer | Its existing task | The only lane that needs Joe's computer |
| G1 Project Watch | ChatGPT scheduled task, every 6 hours | ChatGPT project | Writes Inbox rows |
| G2 Weekly leadership page | ChatGPT scheduled task, Sunday | ChatGPT project | |
| council-board Review-1 | ChatGPT scheduled task, daily 09:00 | The reviewer prompt in `skills/council-board/references/prompts.md` | Joe pastes it at PC-1 step 5 |
| knowledge-review Review-1 | ChatGPT scheduled task, daily 12:00 | Planned with the knowledge-review skill (P2-16) | |
| N1 Decision processor, N2 Hub hygiene, N3 Inbox mail | Notion custom agents | Notion (build day, Business plan) | |
| X1 Codex Watchdog | Codex, weekdays 07:45 | Codex | Re-triggers missed Claude lanes |
| checker (L7) | No schedule of its own | Runs as a subagent inside each lane; the weekly eval runs inside L4 | |
