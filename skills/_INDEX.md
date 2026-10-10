# skills/_INDEX.md

Skills in the open Agent Skills format: one folder per skill, holding a
`SKILL.md` with `name` and `description` frontmatter and optional `references/`.
One line per skill, using the PCOS index convention (P2-12): title | ID | what |
date | status | open when. The ID is the folder path.

| Title | ID | What | Date | Status | Open when |
| --- | --- | --- | --- | --- | --- |
| checker | skills/checker/ | Verdict Accept, Fix or Reject with one finding per line; checklists for 12 job types in `references/checklists.md` | 2026-10-01 | Candidate | Checking any lane output; weekly golden-set run |
| prediction-ledger | skills/prediction-ledger/ | Prediction row fields, evidence lookup order, "What happened?" question, scoring, calibration; the backtest on mail history in `references/backtest.md` | 2026-10-10 | Candidate | After the prediction lane and backtest are restored |
| retro | skills/retro/ | Gap query over the last 90 days, the read-everything gate, the evening card of five questions with six tap options (commitments past their date included), filing into Prediction, People, golden set and Decisions | 2026-10-10 | Candidate | Evening card; "retro"; filing retro answers |
| commitments | skills/commitments/ | Weekday 12:40 extraction from mail, due dates, closure only on evidence, EXO and retro hand-offs, the one-time manual backfill | 2026-10-10 | Candidate | Weekday commitments run; commitment items on the EXO and retro cards; the backfill |
| exo | skills/exo/ | Breakdown into steps, assumption cards with commitment items first, skip rule, interpretation cards, voice-dump parsing | 2026-10-10 | Candidate | The 07:00 EXO card; "exo" or "next step"; new Capture rows |
| council-board | skills/council-board/ | Plan and execution rounds on Council rows, anonymous reviews, chair rules; stage prompts in `references/prompts.md` | 2026-10-01 | Candidate | Judgment work; "council row X"; disputed readings or proposals |
| council-pc | skills/council-pc/ | The brief, the run of `scripts/council_pc.py` (three CLIs, Gemini 503 retried twice, letters not names, cross-ranking), the chair from the bundle, the Council row write | 2026-10-09 | Candidate | Joe says "pc council" at his PC |
| intake-email | skills/intake-email/ | Door 1: allowlist check, routing and stop list, sourced answers, reply drafts with Joe in cc, send gate | 2026-10-01 | Candidate | Hourly intake run; [PCOS] requests |
| weekly-evolve | skills/weekly-evolve/ | Corrections into versioned candidates, new golden-set cases, equal-or-better gate, three weekly numbers | 2026-10-01 | Candidate | Sunday L4 pass; any rule, kernel, card or skill proposal |

Planned (not yet written): knowledge-extract, knowledge-review and knowledge-chair
(P2-16).
