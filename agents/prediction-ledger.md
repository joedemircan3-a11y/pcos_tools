# Card: prediction-ledger

- Version: v0.1
- Status: Candidate
- Register: P2-01 (prediction ledger: Prediction database, evidence check in the daily run, "What happened?" card, calibration block in the weekly pass)
- Lane ID: pending
- Skills: [prediction-ledger v0.1](../skills/prediction-ledger/SKILL.md); outputs checked with [checker v0.1](../skills/checker/SKILL.md)
- Date: 2026-10-01

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
  first conclusive evidence: [[MAIL_SENT]] (Joe's sent mail on the thread or
  subject); later replies in [[MAIL_INBOX]] and [[MAIL_ROUTED]] (the terminal
  message controls); the task row in [[WORKLIST]] (Status, Updated, Next
  Action); [[CHANGELOG]] rows about the subject or Task ID.
- L2, for Owner and Route: the routing section of [[KERNEL]] and the owner-map
  rows in [[RULES]]; until cutover, [[BRIEF_RULES]] sections B and I.
- Knowledge scope: no domain folders. Mail is read only for subjects already in
  [[PREDICTION]] or in the day's new items.

## 3. Tools allowed

- Notion: create [[PREDICTION]] rows; update their Actual, Score, Status and
  Check date; create [[CHANGELOG]] rows; one heartbeat row in [[LANES]]; one
  [[INBOX]] row for the closeout owner when Joe's answer concerns a Worklist
  task.
- Outlook (Microsoft 365 connector): read Inbox, Sent Items and the routed
  folders. Nothing else.
- Question cards: add "What happened?" questions to the next card slot of the
  EXO lane, built from [[CAL_TEMPLATE]] by [[CAL_STANDARD]].
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

## 5. Output contract with evidence labels

- [[PREDICTION]] row per new item: Subject, Source, Is task (Yes / No /
  Unsure), Owner, Route (Radar / Instruct front line / Joe direct), Candidate
  output, Assumptions (each a yes/no question), Confidence, Check date, Status
  Predicted. Field rules are in the skill.
- After the Check date: Actual (what happened, evidence key and ID, date) and
  Score with Status Scored; or Status Asked Joe with one "What happened?"
  question; or Status Parked with a new Check date when Joe answers "nothing
  yet".
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

- Trigger: daily after the brief lane, weekdays about 07:45 Mexico City. A
  30-minute calibration pass runs on Sunday before the weekly-evolve lane
  (Sunday 15:00 UTC). Times are Candidate until the Lanes row exists.
- Runs on: Claude scheduled task (Notion and Microsoft 365 connectors).
- Model: Claude Opus generates. The checker lane verifies Actual and Score on a
  different Claude model. The weekly-evolve chair reads the calibration block.
- Owner: Claude lanes. The lane is built by the build session's closeout owner.
  Joe only answers "What happened?" questions.
- Escalation: one question per blind subject, inside the EXO card slots. Never
  a separate list.
- Depends on: build day (kernel page, [[INBOX]], [[LANES]]), [[PREDICTION]]
  (exists), the brief lane running.

## Change note

v0.1 | 2026-10-01 | Claude Code on the web, queue item Q01 | first card | register
P2-01; design in the dev-session record of 2026-09-27, turn 5 | Joe's default
acceptance 2026-09-28; PCOS_DISPATCH_2026-09-29 PROMPT C1
