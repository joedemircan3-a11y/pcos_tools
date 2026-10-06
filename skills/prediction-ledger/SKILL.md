---
name: prediction-ledger
description: Predict what each incoming PCOS item needs (task or not, owner, route, candidate output, assumptions), then check what actually happened and score the guess. Use in the daily prediction run after the brief, when scoring Prediction rows past their check date, when writing a "What happened?" question for Joe, and for the weekly calibration block.
compatibility: Needs the PCOS Notion hub (Prediction, Decisions, Changelog), read access to Outlook through the Microsoft 365 connector, and the Drive Worklist.
metadata:
  version: "0.1"
  status: Candidate
  register: P2-01
  kernel: "1.0"
  card: agents/prediction-ledger.md
---

# Prediction ledger

Guess first, check later, learn from the difference. The ledger never acts on a
guess: it does not draft, send or change a task row.

Sources are named by key, written `[[KEY]]` (defined in `agents/INPUTS.md`, IDs
in the private map named there).

## 1. Predict: one row per new item

Items come from the day's [[INBOX]] rows written by the brief and project-watch
lanes. Until [[INBOX]] exists, they come from the day's DELTA files in
[[INBOX_FOLDER]].

Match items by identity, never by subject. An item's identity is the
conversation ID of its mail thread, when it has one (an Inbox row or DELTA line
that points to a thread uses that thread's conversation ID). Otherwise it is the
ID of its source: the Inbox row ID, or the DELTA file ID with the line's Task ID.
Skip an item only when a [[PREDICTION]] row already has the same identity in
Source; a later message in a thread that already has a row is not a new item.
Two items with the same subject and different identities get two rows.

Fill the row:

| Field | How to fill it |
| --- | --- |
| Subject | What the item is about, in plain words, at most 12 words, with the Task ID if one exists |
| Source | The item's identity with its key: the thread's conversation ID, or the Inbox row ID, or the DELTA file ID with the line's Task ID |
| Is task | Yes when someone needs an action from Joe or his front line; No for information only; Unsure otherwise |
| Owner | From the owner-map rows in [[RULES]] (until cutover, [[BRIEF_RULES]] section I). Use the address when two people share a name |
| Route | Radar, Instruct front line or Joe direct, by the kernel evaluation order: Route 1 tests first, then Route 3 criteria, then Route 2 as the default |
| Candidate output | What the system would produce: nothing, a draft to the owner, a reply on the thread, a row update, or a decision card; link it if it exists |
| Assumptions | 1 to 4 lines, each a yes/no question ("Is the owner already on it?"), the one most likely to be wrong first |
| Confidence | 0 to 100 percent for the whole row |
| Check date | Source date + 3 days; + 1 day when the item meets the Route 3 money-or-deadline test (a crisis item) |
| Status | Predicted |

A prediction is Candidate (Law 4).

## 2. Check: rows whose Check date has passed

Look for what actually happened, in this order, and stop at the first
conclusive evidence. Evidence belongs to a row through its Source identity (the
conversation ID, the Task ID, or the source row or file ID), never through its
subject:

1. Sent mail: Joe's messages in [[MAIL_SENT]] after the source date, in the
   row's conversation; for an item without a thread, messages that name its
   Task ID.
2. Thread replies: later messages in the same conversation in [[MAIL_INBOX]] and
   [[MAIL_ROUTED]]. Read steps 1 and 2 together, as one conversation, before
   deciding: the terminal message controls (Law 3). Joe's sent message is
   conclusive only while it is still the terminal message; a later reply
   decides instead.
3. Worklist: the row in [[WORKLIST]] with the item's Task ID (Status, Updated,
   Next Action).
4. Changelog: [[CHANGELOG]] rows that name the Task ID or the Source identity.

A message or row that matches only by subject counts only when the match is
unique: no other [[PREDICTION]] row and no other thread in the window has that
subject. Such a match is labeled Candidate in Actual and is never conclusive on
its own.

Write Actual: what happened, the evidence key and ID, the date, and a label.
Use Confirmed when the evidence was opened in this run, and Needs Thread Check
when the thread's terminal message could not be read. When the evidence is
partial, set Status Checking and move the Check date 3 days later, once. After
that the row is scored on conclusive evidence, or asked when it is blind
(section 3). A row that still has only nonconclusive evidence (partial, or a
subject-only match) is set Parked, with that evidence in Actual labeled
Candidate. It is not asked, because its subject has evidence; the weekly
calibration re-checks it like every Parked row.

## 3. Ask only when blind

When there is no evidence after the wait, set Status Asked Joe and put one
question into the next evening card of the retro lane, built from
[[CAL_TEMPLATE]] by [[CAL_STANDARD]]. Past questions belong to the evening
card; the retro lane shows the question and files the answer by the rules
below. Never ask about a subject that has any evidence. Never ask twice about
one row.

A blind row whose subject already has evidence or a question through another
row (a different identity with the same subject) is not asked either. It is set
Parked, with a note naming that other row, and the weekly calibration re-checks
it like every Parked row.

The "What happened?" question:

- Title: "What happened with SUBJECT?"
- Context, one or two lines: what came in, when, from whom (role and address),
  and what the system guessed.
- Options, in this order. Put the recommended one first only when the evidence
  leans one way.
  - A. Handled offline, by me or by the owner.
  - B. Nothing yet; still open.
  - C. Dropped; not needed.
  - D. Unrelated or wrong direction: the guess itself was wrong. This option is
    mandatory and is never removed.
- Note: free text or a voice note. Under option A the note asks: "Who handled
  it, and was the system's draft or output used?"

Filing the answer:

- A: Actual "handled offline", Confirmed, source = the card ID, plus what Joe's
  note adds: who handled it, whether the Candidate output was used, which
  assumptions held. Score the row only when the answer, the note and the
  evidence (section 2) together settle each of the row's guesses: Is task,
  Owner, Route, Candidate output and every assumption. Otherwise never guess the
  missing checks and never leave them out to reach a Score: set Status Parked
  with Actual kept. It is not asked again; the weekly calibration re-checks it
  and scores it once new evidence settles the rest. Scored or Parked, the item
  itself was handled: if the subject is a Worklist task, file one [[INBOX]] row
  for the closeout owner quoting Joe's answer and note, as under C.
- B: Status Parked and Check date 3 days later.
- C: Actual "dropped", Confirmed, source = the card ID. Status Scored. If the
  subject is a Worklist task, file one [[INBOX]] row for the closeout owner
  quoting Joe's answer. The ledger never closes a task itself.

The subject is a Worklist task when the row names a Task ID (in its Subject,
in its Source, or in the Inbox row or DELTA line its Source points to), or when
a [[WORKLIST]] row's sources name the row's conversation ID. One [[INBOX]] row
per answer, never one per identity.
- D: Is task and Route score 0. Status Scored. Joe's note goes into the miss
  patterns.
- Skipped twice: Status Parked, and the question is withdrawn from the card. No
  answer is never treated as an answer.

A Parked row is never asked again. It stays in the evidence check (section 2):
on its Check date if it has one, and in every weekly calibration. It leaves
Parked only on new evidence (then Actual, Confirmed, and Score) or on Joe's own
action: he answers the question after all, or sets the row back to Predicted.

## 4. Score

Score each check 1 when the guess was right and 0 when it was wrong. Leave out
checks that do not apply.

- Is task, Owner, Route: compared with Actual.
- Candidate output: used unedited 1; used after edits 0.5; not used 0.
- Each assumption: right 1, wrong 0.

Score = the sum divided by the number of checks, as a percent. Set Status
Scored.

A row without a prediction (Is task, Owner, Route, Candidate output and
Assumptions all empty: the rows the retro lane creates) has no check to
score. When evidence settles it, write Actual, set Status Scored and leave
Score empty, so the week's numbers never count it.

## 5. Calibrate: weekly, Sunday, before the weekly-evolve lane

- Re-run the evidence check (section 2) on every Parked row. Score the rows
  that now have evidence; the others stay Parked, never asked.
- The week's numbers: prediction accuracy (mean Score), drafts used unedited
  (count and share), questions asked (count). The target direction is up, up,
  down.
- Per project (a Task ID, or one subject that keeps recurring): after three
  wrong guesses in a row, note "assume less, ask earlier". The next prediction
  for that project then puts its weakest assumption into the next card at
  Predict time, instead of waiting for the Check date.
- Group the misses by pattern ("owner wrong when X", "Route 3 overcalled for
  Y"), with row links, and hand them to the weekly-evolve lane as rule
  candidates. The ledger never writes a rule.
- Backtest class rows (Subject starting with "Backtest") are measurements, not
  predictions: report the newest ones as their own block, and never average
  them into the week's numbers.

## 6. Backtest on mail history

The ledger-backtest lane runs sections 1, 2 and 4 over the threads of the
last 90 days whose outcome the mail already shows, blind at the cut and
without asking Joe, and writes accuracy by class. The method is in
[references/backtest.md](references/backtest.md). Threads whose outcome the
mail does not show are the retro lane's.

## Never

- Act on a prediction: no send, no draft, no Worklist change, no new Task ID.
- Ask Joe when there is evidence, or ask twice about one row.
- Treat silence as an answer.
