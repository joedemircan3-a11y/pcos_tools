---
name: retro
description: Close gaps in the PCOS historical record by asking Joe about the past, which he answers easily ("past is just remembering"). Use for the evening card at 19:00 America/Matamoros, when Joe says "retro", and when filing retro answers. Finds threads and Worklist items of the last 90 days with no closure evidence, reads every thread in full before asking, asks five one-line questions with fixed tap options, and files the answers into Prediction rows, People candidates, golden-set candidates and Decision rows.
compatibility: Needs the PCOS Notion hub (Prediction, Decisions, Corrections, Changelog, Inbox, Lanes, Steps), the Drive Worklist, mail-mining outputs and people profiles, the CAL card template, and read access to Outlook through the Microsoft 365 connector.
metadata:
  version: "0.1"
  status: Candidate
  register: P2-30
  kernel: "1.1"
  card: agents/retro.md
---

# Retro

The past is just remembering. Joe tells how a thread ended far more easily than
he decides open work, so the evening card asks him about the past and the lane
writes what he remembers into the record. The lane never decides, sends or
changes anything beyond filing his answers.

Sources are named by key, written `[[KEY]]` (defined in `agents/INPUTS.md`, IDs
in the private map named there).

## 1. Where the lane sits

- Morning and midday cards (EXO, 07:00 and 13:00) are about today. The evening
  card (19:00 America/Matamoros) is about the past, and it is this lane's.
- The evening card is the only place for past questions. It carries the
  prediction-ledger lane's queued "What happened?" questions first, then the
  retro questions of this skill: five items in all.
- The ledger backtest
  ([backtest](../prediction-ledger/references/backtest.md)) scores the threads
  whose outcome the mail shows, without asking Joe. This lane asks about the
  threads whose outcome the mail does not show. No thread is in both.

## 2. Find the gaps

Window: the last 90 days, by the date of a thread's last message or a row's last
update. When no gap is left in the window, step back 90 days at a time, and
write the window into the run record.

Two kinds of candidate:

1. Threads in [[MAIL_INBOX]], [[MAIL_SENT]] and [[MAIL_ROUTED]], identified by
   conversation ID, that carry an ask to or from Joe or his front line, Joe's
   own unanswered asks included (notifications, marketing and system mail are
   not asks), and that have been quiet for at least 7 days.
2. Rows of [[WORKLIST]] updated in the window whose Status waits on an event
   that may have happened offline (Waiting, Blocked, Done-Candidate,
   Stale-Triage), quiet for at least 7 days, and with no Queued or Shown step
   in [[STEPS]], identified by Task ID. Active rows are today's work and
   EXO's.

A candidate is a gap only when the record shows no closure evidence:

- no final reply: the terminal message (Law 3) leaves the ask open;
- no sales-order, shipment or invoice confirmation for it in the mail;
- no Done on its Worklist row;
- no [[CHANGELOG]] row that closes it.

[[MAIL_MINING]] sharpens the test: it shows where each counterpart usually
closes (by invoice only, by a reply from the front line, by a confirmation from
the company system). It never replaces reading the thread.

Never a candidate:

- a thread or item that is answered or that another card already asks: a
  decided row in [[DECISIONS]]; an open row there that is not this lane's own
  card or conflict row; an open question in the CAL lane's state
  ([[CAL_FOLDER]]). Match by identity (the conversation ID or Task ID), never
  by subject: two threads with one subject are two gaps. A question that names
  no identity counts only when its subject matches this candidate alone, with
  no other thread or row in the window under that subject;
- a thread or item whose identity is already in the Source of a [[PREDICTION]]
  row, whatever its Status.
  The ledger owns it. Its "What happened?" question, if it queued one, rides on
  this card as a ledger item (section 5), and a Parked row is never asked;
- personal or Room 10 material.

## 3. Order

Sort the gaps by three keys, in this order:

1. Recency, counted in calendar weeks: the newest week of last activity first.
   Weeks, not days, so that the next two keys can still order a week.
2. Open value: money at stake first (an unpaid invoice, an open deposit, a
   quoted order), then a thread with an active vendor (one with an open order
   or shipment on [[WORKLIST]]), then the rest.
3. Pattern class: gaps of one class, the same counterpart and the same kind of
   ask (the kinds in the [backtest](../prediction-ledger/references/backtest.md)
   section 4), rank by the size of the class, largest first, because one answer
   can close the whole class.

A class item covers 2 to 5 gaps of one class in one question. Each gap in it
still passes the gate on its own.

## 4. Gate before any question

Joe's standing rule: never ask what the record already answers. Before a gap
becomes a question:

1. Read the full thread chain: every message of the conversation in every
   folder (Inbox, Sent Items, the routed folders), every branch and forward,
   through the terminal message. Record each message ID read.
2. Read every later reply: later messages in the same conversation, and later
   threads with the same counterpart or the same Task ID, up to today. A
   later thread answers the gap only when it concerns the same ask (the Task
   ID, or the order, document or request it names), not merely the same
   counterpart.
3. Check the other records: the Worklist row and the sources it names,
   [[CHANGELOG]], [[DECISIONS]], [[PREDICTION]] and the CAL lane's questions
   in [[CAL_FOLDER]].
4. If anything read answers the question, do not ask. Write what the record
   shows instead, on a new [[PREDICTION]] row built as section 6 step 1 builds
   one (Subject, Source = the identity, no prediction fields): Actual,
   Confirmed, with the evidence key and ID; Status Scored. Note it as a gate
   catch for the weekly method loop.
5. Hand every item to the checker (job type question-card, retro items) on a
   different model. Only Accepted items are shown. A Rejected item is dropped
   and the next gap takes its place.

## 5. Build the card

Five items, never more, in this order:

1. Ledger items: [[PREDICTION]] rows with Status Asked Joe whose question has
   not been answered, oldest first, each in the ledger's own format
   (prediction-ledger skill section 3). Items beyond five wait for the next
   evening; waiting is not a skip.
2. Conflict items: the "Which version stands?" rows this lane opened in
   [[DECISIONS]] (section 6, step 5), each as one assumption item.
3. Retro items, in the order of section 3, until the card holds five.

Write each retro item:

- One line that sums up the thread so Joe recognizes it: the counterpart's role,
  what was asked, the date, the last state. For example: "Sample request from
  the stone vendor, Aug 12: you asked for two samples; their quote got no
  reply." Self-contained, in plain words; no internal ID without its meaning.
  Quote no more mail text than Joe needs to remember the thread.
- Tap options, in this order: closed as quoted; closed differently; dropped;
  moved offline (phone, WhatsApp, in person); still open; unrelated. The item
  lists the first five. The sixth, unrelated, is the CAL template's own "Not
  needed / wrong direction" option, which the template adds to every item, so
  it is never added a second time. Put one option first as recommended only
  when the record leans that way.
- Free text or a voice note for anything else.
- A class item names each of its threads in one line, and its answer applies
  to every thread unless the note names an exception.

End the card with one progress line: what the last answers closed. For example:
"Last night's answers closed four threads and added two people notes." Never
the size of the backlog or a count of open gaps.

Build the page from [[CAL_TEMPLATE]] by [[CAL_STANDARD]]. Add one Open row to
[[DECISIONS]] for the card: link, each item with every identity it covers (the
conversation ID or Task ID of each thread; a class item covers 2 to 5), due
the next evening.

## 6. File the answers

At the start of the next run, before the new card. Ledger items are filed by
the prediction-ledger skill section 3, into their own rows. For each retro
item, in this order:

1. Prediction rows, one per identity. A retro item covers one identity (the
   conversation ID, else the Task ID or source row ID); a class item covers
   one per thread. For every identity, find the [[PREDICTION]] row with it in
   Source, and create one if none: Subject (at most 12 words), Source (the
   identity), Actual, Status. Steps 2 to 5 apply to each identity. A thread
   that Joe's note names as an exception gets the answer the note gives it;
   one the note leaves unanswered stays a gap and can come back as a single
   item. A row this lane creates holds no prediction: Is task, Owner, Route,
   Candidate output, Assumptions, Confidence and Score stay empty, so the
   weekly calibration leaves it out. Scored on such a row means settled.
2. Actual, by answer, each Confirmed with the card ID and item as source:
   - closed as quoted: "closed on the terms last quoted or proposed in the
     thread". Status Scored.
   - closed differently: "closed on other terms", with Joe's note verbatim, or
     "terms not recorded" without one. Status Scored.
   - dropped: "dropped". Status Scored. When a Worklist row covers it, one
     [[INBOX]] row for the closeout owner quoting Joe's answer. The lane never
     closes a row.
   - moved offline: "handled offline". The channel (phone, WhatsApp, in
     person) and the outcome are added only when Joe's note gives them;
     never a guessed channel. Status Scored.
   - still open: no Actual. Status Parked, Check date 7 days later, so the
     ledger's evidence check can still settle it, without a Score
     (prediction-ledger skill section 4). One [[INBOX]] row for the closeout
     owner when no open Worklist row covers it, so the open item reaches the
     lanes that work today. Never asked again by this lane.
   - unrelated (the template's "Not needed / wrong direction"): "unrelated;
     should not have been asked". Status Scored. The miss goes to the
     gap-query misses for the weekly method loop.
   - free text or voice only: parse it as an EXO voice dump and file the option
     it states. If it states none, Actual holds Joe's words verbatim,
     Confirmed as his statement; Status Parked, Check date 7 days later, so
     the ledger's evidence check can still settle it, without a Score. It
     counts as answered and is never asked again by this lane.
3. People. When the answer says how someone in the thread works (moves price
   talks to the phone, confirms orders only by invoice, answers through a
   colleague), write a Candidate line for that person, by role and address as
   [[PEOPLE]] names them, with the card ID and conversation ID as source.
   Until the People database exists (register P2-21), the run's lines go into
   one [[INBOX]] row for the closeout owner, scope people (private), who folds
   them into the next [[PEOPLE]] version. A people line never goes into a
   Prediction row, a Today line or any view the team can see.
4. Golden set. When the answer reveals a rule (how a kind of thread really
   closes, who really owns it, a step the record never shows), write one
   [[CORRECTIONS]] row: lane retro, what the record implied, Joe's answer
   verbatim with the card ID, the rule it implies. The weekly-evolve lane turns
   it into a [[GOLDEN_SET]] case (its section 4). This lane never writes the
   golden set directly.
5. Memory against record. When Joe's answer contradicts a fact the record
   states (a date, quantity, party, decision or status, not a missing step):
   record both in Actual, each with its source (the card for Joe's memory, the
   message ID for the record), and open one [[DECISIONS]] row, "Which version
   stands for SUBJECT?", with both versions and the default "Joe's account is
   the outcome; the mail stays as written". The next retro card asks it as one
   assumption item, and Joe's answer goes into the row's Answer, where the
   decision processor applies it. Never overwrite, move, delete or answer the
   mail.
6. One [[CHANGELOG]] row per row written or changed.

## 7. Skip rule (as EXO)

An item still unanswered at the next evening counts as one skip for every
identity it covers. Skips are counted per identity from the card rows in
[[DECISIONS]]: an identity listed on N earlier cards without an answer has N
skips, so a class item that is split keeps its count.

- 2 skips: reshape. A shorter summary, a likelier option first, or a class item
  split into single threads.
- 3 skips: park and ask once. Create a [[PREDICTION]] row for each identity of
  the item with Status Parked, no Actual, and a Check date 7 days later, so the
  ledger's evidence check can still settle it, without a Score. The next card
  shows one last item: "Keep this open, or let it go?", keep as the default.
  Let it go: Actual "let go", Confirmed with the card ID, Status Scored. No
  answer leaves it Parked. Nothing closes on silence, and the lane never asks
  about it again.

Ledger items follow the ledger's own skip rule (prediction-ledger skill section
3). A conflict item skipped three times is not shown again: its Decision row
stays Open with its default, and both versions stay in Actual. Nothing changes
on silence.

## 8. Learn

Weekly, for the weekly-evolve lane: gaps asked and answered by answer type, gate
catches and "unrelated" answers grouped by pattern (both are gap-query misses),
the classes Joe skips, people lines and golden-set candidates filed. These are
candidates; the lane never writes a rule.

## Never

- Ask what the record already answers, or ask before the full thread chain and
  every later reply are read.
- Ask about a subject that has a [[PREDICTION]] row, except by carrying the
  ledger's own queued question; ask about a Parked row.
- Overwrite, move, delete, forward or reply to mail; send or draft anything.
- Close, drop or change a Worklist row; mint a Task ID.
- Ask about today's work: that is the morning and midday cards' job.
- Show the size of the backlog or a count of open gaps.
- Put a people line where the team can see it, or personal or Room 10 material
  on a card.
- Treat silence as an answer.
