# Backtest on mail history

Version v0.1, 2026-10-06. Loaded by the ledger-backtest lane
([card](../../../agents/ledger-backtest.md)) together with
[the prediction-ledger skill](../SKILL.md) sections 1, 2 and 4. Register P2-01,
and the backtest loop of the retro design (P2-30). Keys (`[[KEY]]`) are defined
in `agents/INPUTS.md`.

The live ledger learns one item at a time. The backtest runs the same predictor
over the threads of the last 90 days whose outcome the mail already shows,
scores it without asking Joe, and writes accuracy by class. A thread whose
outcome the mail does not show is a gap for the retro lane, never for the
backtest.

## 1. Pick the threads

- Window: the last 90 days. Threads in [[MAIL_INBOX]], [[MAIL_SENT]] and
  [[MAIL_ROUTED]], identified by conversation ID.
- The cut: the first inbound message that makes the thread an item, one that
  asks something of Joe or his front line and is not Route 1 noise by the
  kernel's Route 1 tests. A thread without such a message is skipped.
- Outcome in the mail: after the cut, the evidence of skill section 2 (Joe's
  sent mail and the later replies, read as one conversation; the terminal
  message controls) reaches a conclusive outcome: the ask was answered, done,
  declined or dropped, and it is visible who acted. Partial or no evidence:
  skip the thread.
- Not scored before: the conversation ID is in no earlier run report.
- Order: newest cut first. Stop at 200 threads per run.

## 2. Predict blind

Predict each thread as skill section 1 does (Is task, Owner, Route, Candidate
output, Assumptions, Confidence), from the messages up to the cut only.

- Run the predictor in a subagent that receives only the messages up to and
  including the cut, the routing section of [[KERNEL]] and the owner map as it
  stood at the cut. Batches of up to 20 threads per subagent.
- Hindsight is the failure to prevent: no message after the cut, no Worklist or
  Changelog row written after the cut, no owner assignment made after the cut,
  and no outcome reaches the predictor.
- The owner map as it stood at the cut: start from the owner-map rows in
  [[RULES]] and undo every change dated after the cut, using the before value
  that its [[CHANGELOG]] row records. A row that was Live at the cut counts
  even if it is Retired now; a row created after the cut does not. When a
  change after the cut has no recorded before value, skip the thread and note
  it in the run report: a map that cannot be rebuilt would leak the later
  owner into Owner, Route, Candidate output and Assumptions alike.
- The routing section of [[KERNEL]] is the method under test, so it stays
  current. The owner map is a fact about the past, so it is rebuilt.

## 3. Score

Score as skill section 4, with two changes:

- Candidate output: 1 when the type of output matches what happened (a reply on
  the thread, an instruction to the owner, a row update, nothing), else 0.
  Nothing was drafted, so "used unedited" does not apply.
- Assumptions: score only those the outcome settles.

The checker re-scores a sample of min(10, threads scored in this run) on a
different model (job type prediction): every thread when the run scored
fewer than 10. Disagreements go into the run report, and the checker's score
stands.

## 4. Classes

The class of a thread is the kind of its ask:

| Kind | The ask is about |
| --- | --- |
| order or shipment | an order, its status, a delivery, a pickup, documents for it |
| quote or price | a quote, a price list, a discount, a cost question |
| invoice or payment | an invoice, a payment, a deposit, a statement, a credit |
| sample or product | a sample, a product detail, a photo, a specification |
| report or data | a report, an export, figures, a recurring data request |
| other | anything else |

Per class: the number of threads, the mean Score, and the accuracy of each
check (Is task, Owner, Route, Candidate output, Assumptions).

## 5. Write

- Run report: LEDGER_BACKTEST_DATE.md in [[ARCHIVE]], created, never edited.
  It holds the window, the threads scored and, per thread, the conversation ID,
  the cut date, the kind, the prediction, the outcome with its message ID, and
  the score; then the checker's sample and its disagreements.
- One [[PREDICTION]] row per class that has at least one thread:
  - Subject: Backtest DATE, KIND.
  - Source: the run report's key and ID.
  - Actual: the number of threads, the mean Score and the accuracy per check,
    Confirmed (computed in this run from the run report); "indicative" when
    fewer than 10 threads.
  - Status Scored. Check date: the run date.
  - Score, Confidence and the prediction fields stay empty, so these rows never
    enter the live mean.
- The weekly calibration (skill section 5) reports the newest class rows as
  their own block, next to the live numbers. A class with low backtest accuracy
  is a candidate for "assume less, ask earlier"; the weekly-evolve gate
  decides.

## Never

- Ask Joe anything, or put anything on a card.
- Let the predictor see a message after the cut.
- Write a row per thread into [[PREDICTION]], or change a live row.
- Score a thread whose outcome the mail does not show.
- Draft, send, or change a Worklist row.
