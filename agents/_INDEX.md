# agents/_INDEX.md

One line per file, using the PCOS index convention (P2-12): title | ID | what | date
| status | open when. In this repository the ID is the file path. Status is
Candidate for every card until its Lanes row exists and its first run is in the
Changelog.

| Title | ID | What | Date | Status | Open when |
| --- | --- | --- | --- | --- | --- |
| Card template | agents/CARD_TEMPLATE.md | The six-part card, evidence labels, rules every card inherits | 2026-10-09 | Candidate | Writing or reviewing a card |
| Input keys | agents/INPUTS.md | The `[[KEY]]` names for sources; IDs stay in the private map | 2026-10-09 | Candidate | Resolving a source key, adding a source |
| prediction-ledger | agents/prediction-ledger.md | Predict each incoming item, check what happened, score, calibrate; asks on the evening retro card (P2-01) | 2026-10-09 | Candidate | Building or running the prediction lane |
| ledger-backtest | agents/ledger-backtest.md | The ledger's predictor run blind over settled mail threads of the last 90 days, scored without Joe; accuracy by class (P2-01, P2-30) | 2026-10-09 | Candidate | Building or running the backtest; reading class accuracy |
| retro | agents/retro.md | Evening card of five questions about the past, last 90 days first, commitments past their date included; answers feed the ledger, People profiles and golden set (P2-30) | 2026-10-09 | Candidate | Building or running the Retro lane; the 19:00 card |
| exo | agents/exo.md | Single steps and two assumption cards a day; checked internal Outlook drafts distribute front-line work and track the owner's answer (P2-02) | 2026-10-10 | Candidate | Building or running the EXO lane |
| commitments | agents/commitments.md | Every promise in Joe's mail as a tracked row with a due date; closure only on evidence; at most two items per EXO or retro card (P2-31) | 2026-10-09 | Candidate | Building or running the Commitments lane; what Joe owes or is owed |
| checker | agents/checker.md | Accept, Fix or Reject on every lane output; golden-set eval (P2-03, P2-04) | 2026-10-09 | Candidate | Any lane hands over an output |
| council-board | agents/council-board.md | Draft, two reviews and a chair on a Notion Council row (P2-06) | 2026-10-09 | Candidate | Judgment work with a day's time |
| council-pc | agents/council-pc.md | Live council on Joe's PC: Codex, Gemini and a separate Claude answer one brief, each ranks the two answers it did not write, the session chairs (P2-08) | 2026-10-09 | Candidate | Urgent judgment work with Joe at his PC; "pc council" |
| council-github | agents/council-github.md | On-demand council through a pull request, method and code work only (P2-07) | 2026-10-09 | Candidate | Urgent council on non-business content |
| intake-email | agents/intake-email.md | Door 1: team requests by [PCOS] mail, routed and answered as drafts (P2-09) | 2026-10-09 | Candidate | Building the intake lane, naming the allowlist |
| weekly-evolve | agents/weekly-evolve.md | Weekly versioned rule, kernel and skill candidates behind the golden-set gate (P2-05) | 2026-10-09 | Candidate | Sunday L4 pass, any rule proposal |
| knowledge-extract | agents/knowledge-extract.md | Claims from indexed files into the Knowledge database (P2-16 stage 1) | 2026-10-09 | Candidate | Knowledge backlog pass |
| knowledge-review | agents/knowledge-review.md | Supported, contradicted, stale or duplicate per claim, author-blind (P2-16 stage 2) | 2026-10-09 | Candidate | After an extraction batch |
| knowledge-chair | agents/knowledge-chair.md | Claim status, decisions on contradictions, REFINED versions behind the gate (P2-16 stages 3 and 4) | 2026-10-09 | Candidate | Sunday consolidation |
