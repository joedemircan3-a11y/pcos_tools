# Card: prediction-ledger

- Version: v0.7
- Status: Candidate
- Register: P2-01 (prediction ledger: Prediction database, evidence check in the daily run, "What happened?" card, calibration block in the weekly pass)
- Lane ID: pending
- Skills: [prediction-ledger v0.1](../skills/prediction-ledger/SKILL.md); outputs checked with [checker v0.2](../skills/checker/SKILL.md); the [ledger-backtest](ledger-backtest.md) lane runs the same predictor over settled mail history
- Date: 2026-10-10

## 1. Mission

For every incoming item, record in advance what the system expects: is it a task,
whose is it, which route, what output, on which assumptions. Later, check what
actually happened and score the guess, so the next guesses need less of Joe.

Never: act on a prediction (no draft, no row change, no new task), ask Joe about
a subject that already has evidence, ask twice about one row, or treat silence as
an answer.

## 2. Inputs by ID

- L0, always loaded: [[KERNEL]].
- L1, every run: open rows in [[PREDICTION]] (Status Predicted, Checking, Asked
  Joe, Parked); decided rows in [[DECISIONS]] (answered questions are never
  asked again).
- L2, new items to predict: the day's [[INBOX]] rows from the brief and
  project-watch lanes. Until [[INBOX]] exists: the day's DELTA files in
  [[INBOX_FOLDER]].
- L2, evidence for rows past their Check date, in this order, stopping at the
  first conclusive evidence: the row's whole conversation, Joe's sent mail in
  [[MAIL_SENT]] with the replies in [[MAIL_INBOX]] and [[MAIL_ROUTED]] (the
  terminal message controls; Joe's message counts only while it is terminal);
  the row in [[WORKLIST]] with the item's Task ID
  (Status, Updated, Next Action); [[CHANGELOG]] rows that name the Task ID or the
  Source identity. Evidence is matched by the row's Source identity; a match by
  subject alone counts only when it is unique (skill section 2).
- L2, for Owner and Route: the routing section of [[KERNEL]] and the owner-map
  rows in [[RULES]]; until cutover, [[BRIEF_RULES]] sections B and I.
- L2, before any question reaches Joe (kernel section 2, step 4): [[REGISTRY]],
  the operating document registry, with the other records that step names, so
  that no question asks what a registered document already answers.
- Knowledge scope: no domain folders. Mail is read only for items already in
  [[PREDICTION]] or in the day's new items.

## 3. Tools allowed

- Notion: create [[PREDICTION]] rows; update their Actual, Score, Status and
  Check date; create [[CHANGELOG]] rows; one heartbeat row in [[LANES]]; one
  [[INBOX]] row for the closeout owner when Joe's answer concerns a Worklist
  task.
- Outlook (Microsoft 365 connector): read Inbox, Sent Items and the routed
  folders. Nothing else.
- Question cards: add "What happened?" questions to the next evening card of
  the [retro](retro.md) lane (past questions belong to the evening card), built
  from [[CAL_TEMPLATE]] by [[CAL_STANDARD]]. The retro lane shows them and
  files the answers by this lane's rules.
- Not allowed: send or draft mail; change [[WORKLIST]] or any row outside
  [[PREDICTION]]; mint Task IDs; edit Drive files; read Room 10 or personal
  material.

## 4. Rules and kernel version

- Kernel 1.0 (draft in [[BUILD_KIT]]; the Notion kernel page replaces it on
  build day). The mismatch rule and the live-rules fallback are in
  [CARD_TEMPLATE](CARD_TEMPLATE.md).
- Laws 3 (terminal message controls), 4 (labels), 5 (no send), 8 (resolve from
  sources before asking), 11 (reason with every change), 12 (nothing closes on
  silence).
- Lane rules, from the dev-session record of 2026-09-27 (turn 5, decisions 3 and
  7, accepted by default by Joe):
  - Evidence wait 3 days; 1 day for a crisis item. An item is a crisis when it
    meets the Route 3 money-or-deadline test, so no extra field is needed.
  - Ask only when blind. One question per subject. Never ask about a subject
    that has any evidence.
  - Every "What happened?" question offers "unrelated / wrong direction".
  - Three wrong guesses in a row on one project: assume less there and ask one
    small question earlier.
- Live text rules ([CARD_TEMPLATE](CARD_TEMPLATE.md), "Live rules for text Joe
  reads"; kernel 1.3 once live): (a) every item code, SAP code, order number or Task
  ID with its plain description, written TASK-ID (DESCRIPTION) in templates; (b) one
  home per record: a Drive file is changed in the same file, only through a "DRIVE
  WRITE:" row in [[INBOX]] for the Drive recorder, never rebuilt as a copy; (c) mail
  and message text by [[EMAIL_RULES]]; (d) people named as [[PEOPLE]] and the owner
  map resolve them.

## 5. Output contract with evidence labels

- [[PREDICTION]] row per new item: Subject, Source, Is task (Yes / No /
  Unsure), Owner, Route (Radar / Instruct front line / Joe direct), Candidate
  output, Assumptions (each a yes/no question), Confidence, Check date, Status
  Predicted. Field rules are in the skill.
- After the Check date: Actual (what happened, evidence key and ID, date) and
  Score with Status Scored; or Status Asked Joe with one "What happened?"
  question; or Status Parked with a new Check date when Joe answers "nothing
  yet"; or Status Parked with Actual kept when Joe answers "handled offline" and
  the answer, his note and the evidence do not settle every guess (Owner, Route,
  Candidate output, each assumption). Such a row is never scored on part of its
  checks.
- Evidence labels: a prediction is Candidate. Actual is Confirmed only when its
  evidence was opened in this run. Otherwise it is Needs Thread Check (mail) or
  Needs Source Check (row or Changelog).
- Weekly calibration block for the weekly-evolve lane: prediction accuracy,
  drafts used unedited, questions asked, and misses grouped by pattern with row
  links. These are rule candidates; the ledger never writes a rule.
- Run record: items predicted, rows checked and scored, questions queued,
  sources opened (keys and IDs), kernel version; one heartbeat; one Changelog
  row per changed row.
- Done means: every new item has a row, and every row past its Check date is
  Scored, Asked Joe or Parked.
- Eval: the weekly numbers should move up (accuracy), up (drafts used unedited)
  and down (questions per week). [[GOLDEN_SET]] categories routing and
  re-asking.

## 6. Trigger and owner model

- Trigger: paused 2026-10-10 (usage diet). Restore weekdays about 07:45 Mexico
  City after the brief lane; the 30-minute calibration pass restores on Sunday
  before the weekly-evolve lane (Sunday 09:00 America/Mexico_City). The
  [ledger-backtest](ledger-backtest.md) lane scores the same predictor against
  settled mail history on Sundays before the calibration pass.
- Runs on: Claude scheduled task (Notion and Microsoft 365 connectors).
- Model: Claude Opus generates. The checker lane verifies Actual and Score on a
  different Claude model. The weekly-evolve chair reads the calibration block.
- Owner: Claude lanes. The lane is built by the build session's closeout owner.
  Joe only answers "What happened?" questions.
- Escalation: one question per blind subject, on the evening retro card. Never
  a separate list.
- Depends on: build day (kernel page, [[INBOX]], [[LANES]]), [[PREDICTION]]
  (exists), the brief lane running.

## Change note

v0.1 | 2026-10-01 | Claude Code on the web, queue item Q01 | first card | register
P2-01; design in the dev-session record of 2026-09-27, turn 5 | Joe's default
acceptance 2026-09-28; PCOS_DISPATCH_2026-09-29 PROMPT C1

v0.2 | 2026-10-06 | Claude Code on the web, queue item QC18 | evidence is matched
by the row's Source identity, not by subject, and mail is read as the whole
conversation (Joe's sent message counts only while terminal) | two unrelated items
with one subject could take each other's evidence, and a sent message could hide a
later reply (Codex review of PR 1) | PCOS QUEUE_v4 item QC18

v0.3 | 2026-10-06 | Claude Code on the web, queue item QC18-R | a "handled offline"
answer scores the row only when the answer, Joe's note and the evidence settle every
guess; otherwise the row is Parked with Actual kept | the row was marked Scored with
Owner, Route, output use and assumptions unknown (Codex review of PR 1) | PCOS
QUEUE_v6 item QC18-R

v0.4 | 2026-10-06 | Claude Code on the web, queue item QC19 | "What happened?"
questions go on the evening retro card; the backtest lane named | Joe's decision:
evening = past questions (dev-session record of 2026-10-06, part 7, turn 21); the
backtest loop of turn 20 | PCOS QUEUE_v4 item QC19

v0.5 | 2026-10-09 | Claude Code on the web, PCOS queue item QC24 | [[REGISTRY]] read
before any question reaches Joe | kernel 1.2 section 2 step 4 names the Registry among
the records searched before asking Joe, and the kernel key map holds the REGISTRY key
since QK23 (its open point: the cards that need the registry add the key) | PCOS
QUEUE_v7, item QC24 amendment

v0.6 | 2026-10-09 | Claude Code on the web, PCOS queue item QC28 | part 4 states the
live rules for text Joe reads (item codes with a description, one home per record,
the email rules, person names); times on the one clock, America/Mexico_City | four
live Rules rows bound only the EXO lane, and the lanes ran on two clocks | PCOS
QUEUE_v10 item QC28; PCOS_JOE_DEV_LIST requests "new rules into the kernel and every
lane" and "one clock for every lane"

v0.7 | 2026-10-10 | Codex, queue item QX35 | daily prediction and Sunday
calibration paused; restore times retained | Joe's temporary usage diet | PCOS
QUEUE_v12 item QX35
