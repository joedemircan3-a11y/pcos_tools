# Card: ledger-backtest

- Version: v0.2
- Status: Candidate
- Register: P2-01 (prediction ledger) and P2-30 (the backtest loop of the retro design)
- Lane ID: pending
- Skills: [prediction-ledger v0.1](../skills/prediction-ledger/SKILL.md) sections 1, 2 and 4 with [references/backtest.md](../skills/prediction-ledger/references/backtest.md); a sample checked with [checker v0.2](../skills/checker/SKILL.md)
- Date: 2026-10-09

## 1. Mission

Measure the prediction ledger against history without asking Joe. Predict the
threads of the last 90 days whose outcome the mail already shows, as if they had
just arrived; score each prediction against the outcome; write accuracy by class
to the Prediction database, so that the live ledger knows where to assume less.

Never: ask Joe anything; let the predictor see a message after the cut; write a
row per thread into the Prediction database or change a live row; draft, send
or change a Worklist row; take more than 200 threads in one run.

## 2. Inputs by ID

- L0, always loaded: [[KERNEL]].
- L1, every run: the earlier backtest run reports in [[ARCHIVE]] (conversation
  IDs already scored); the class rows of earlier runs in [[PREDICTION]].
- L2, per thread: the whole thread in [[MAIL_INBOX]], [[MAIL_SENT]] and
  [[MAIL_ROUTED]] (the predictor sees it only up to the cut); the routing
  section of [[KERNEL]]; the owner-map rows in [[RULES]], rebuilt as they
  stood at the cut from the before values in [[CHANGELOG]].
- Knowledge scope: the mail of the last 90 days. No domain folders, no personal
  or Room 10 material.

## 3. Tools allowed

- Outlook (Microsoft 365 connector): read Inbox, Sent Items and the routed
  folders. Nothing else.
- Notion: create one class row per class per run in [[PREDICTION]];
  [[CHANGELOG]] rows; one heartbeat in [[LANES]].
- Drive: create one run report per run in [[ARCHIVE]]; never edit it.
- Subagents: the predictor runs in subagents that receive only the messages up
  to the cut.
- Not allowed: questions to Joe or card items; rows per thread in
  [[PREDICTION]]; any change to a live Prediction row; send or draft;
  [[WORKLIST]] changes; Task IDs.

## 4. Rules and kernel version

- Kernel 1.1. The mismatch rule and the live-rules fallback are in
  [CARD_TEMPLATE](CARD_TEMPLATE.md).
- Laws 3 (the terminal message controls), 4 (labels), 5 (no send), 11 (a
  reason with every change).
- Lane rules, from the dev-session record of 2026-10-06, part 7 (turn 20: three
  loops, a backtest on mail history, the live ledger and the weekly method
  loop) and QUEUE_v4 item QC19:
  - Only threads whose outcome is in the mail; the others are gaps for the
    retro lane.
  - Scored without asking Joe.
  - At most 200 threads per run; once at install, then weekly before L4.
- Method rule (this card): the prediction is made blind at the cut, with the
  owner map as it stood then, so that nothing known later can leak into it.
  A thread whose map cannot be rebuilt is skipped.
- Live text rules ([CARD_TEMPLATE](CARD_TEMPLATE.md), "Live rules for text Joe
  reads"; kernel 1.3 once live): (a) every item code, SAP code, order number or Task
  ID with its plain description, written TASK-ID (DESCRIPTION) in templates; (b) one
  home per record: a Drive file is changed in the same file, only through a "DRIVE
  WRITE:" row in [[INBOX]] for the Drive recorder, never rebuilt as a copy; (c) mail
  and message text by [[EMAIL_RULES]]; (d) people named as [[PEOPLE]] and the owner
  map resolve them.

## 5. Output contract with evidence labels

- One [[PREDICTION]] row per class per run: Subject "Backtest DATE, KIND";
  Source the run report; Actual with the thread count, the mean Score and the
  accuracy per check; Status Scored. Score, Confidence and the prediction
  fields stay empty, so the class rows never enter the live mean.
- One run report in [[ARCHIVE]]: per thread the conversation ID, the cut date,
  the kind, the prediction, the outcome with its message ID, and the score;
  the checker's sample and its disagreements.
- Evidence labels: a prediction is Candidate. An outcome is Confirmed when its
  message was opened in this run. Class accuracy is Confirmed, computed in this
  run from the run report.
- Run record: window, threads scored, class rows written, checker
  disagreements, sources opened (keys and IDs), kernel version; one heartbeat;
  one Changelog row per row written.
- Done means: up to 200 new threads scored and their class rows written, or a
  heartbeat that says no new settled thread was found.
- Eval: the checker re-scores min(10, threads scored) per run on a different
  model, with its prediction-backtest checklist; disagreements trend to zero.

## 6. Trigger and owner model

- Trigger: once by hand at install, over the last 90 days; then Sundays 07:00
  America/Mexico_City, two hours before L4, whose calibration reads the class rows.
- Runs on: Claude Code Routine (Notion, Microsoft 365 and Drive connectors).
- Model: Claude Opus predicts (in subagents, blind at the cut) and scores. The
  checker re-scores a sample on a different Claude model.
- Owner: Claude lanes. Joe is never asked.
- Escalation: none.
- Depends on: [[PREDICTION]] and [[ARCHIVE]] (exist); the prediction-ledger
  skill; the L4 Routine reading the class rows.

## Change note

v0.1 | 2026-10-06 | Claude Code on the web, PCOS queue item QC19 | first card |
register P2-01 and P2-30; the backtest loop in the dev-session record of
2026-10-06, part 7, turn 20 | QUEUE_v4 item QC19: one-off and weekly, scored
without Joe, accuracy by class, at most 200 threads per run

v0.2 | 2026-10-09 | Claude Code on the web, PCOS queue item QC28 | part 4 states the
live rules for text Joe reads (item codes with a description, one home per record,
the email rules, person names); times on the one clock, America/Mexico_City | four
live Rules rows bound only the EXO lane, and the lanes ran on two clocks | PCOS
QUEUE_v10 item QC28; PCOS_JOE_DEV_LIST requests "new rules into the kernel and every
lane" and "one clock for every lane"
