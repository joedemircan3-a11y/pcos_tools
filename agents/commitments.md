# Card: commitments

- Version: v0.3
- Status: Candidate
- Register: P2-31 (Commitments lane: every promise in email becomes a tracked item with a due date, closure only on evidence, follow-up through the EXO and retro cards)
- Lane ID: pending
- Skills: [commitments v0.3](../skills/commitments/SKILL.md); every draft checked with [checker v0.2](../skills/checker/SKILL.md) (job type mail-draft)
- Date: 2026-10-10

## 1. Mission

Turn every promise in Joe's mail into a tracked commitment: what is owed, by
whom, by when, in which thread. Keep the due date, close the row only on
evidence, and hand at most two rows to the next card, with a checked draft
where a reply is the deliverable, so that what Joe owes gets finished and what
he is owed gets chased.

Never: send, forward or reply to mail; commit a price, lead time, quantity,
payment or new date; close, drop or move a row on silence or a subject match;
change a Worklist row or mint a Task ID; show Joe a list or a count of open or
late items; ask Joe anything outside the EXO and retro cards.

## 2. Inputs by ID

- L0, always loaded: [[KERNEL]].
- L1, every run: the last commitments heartbeat in [[LANES]] (window end);
  every [[COMMITMENTS]] row that is not Done or Dropped; [[DECISIONS]] rows of
  the cards that showed commitment items (answers are filed by the showing
  lane, never twice).
- L2, extraction: Joe's messages in [[MAIL_SENT]] in the window; messages in
  [[MAIL_INBOX]] and [[MAIL_ROUTED]] in the window with Joe in To; the whole
  thread of each before a row is written.
- L2, per open row: its whole thread through the terminal message; the
  [[WORKLIST]] row of its Linked task, or the rows whose sources name the
  thread.
- L2, direction, owner and time zone: the owner-map rows in [[RULES]] (until
  cutover, [[BRIEF_RULES]] section I); the sender's profile in [[PEOPLE]]
  (private).
- L2, before any item reaches Joe (kernel section 2, step 4): [[REGISTRY]] and
  [[CHANGELOG]], with the rows above, so that no item asks what the record
  already answers.
- Knowledge scope: mail of the window (the last 30 days in the backfill) and
  the rows above. No domain folders; personal and Room 10 material is out of
  scope.

## 3. Tools allowed

- Outlook (Microsoft 365 connector): read Inbox, Sent Items and the routed
  folders; write checked drafts into [[MAIL_DRAFTS]], threaded, at most 5 per
  run.
- Notion: create and update [[COMMITMENTS]] rows (every field); [[INBOX]] rows
  for the closeout owner; [[CHANGELOG]] rows; one heartbeat in [[LANES]].
- The checker skill on a different model, for every draft.
- Not allowed: send, forward or reply to mail; move or delete mail; change
  Status, Owner or Priority on a [[WORKLIST]] row; mint Task IDs; publish a card
  (the EXO and retro lanes show the items); write [[DECISIONS]] rows; commit a
  price, lead time, quantity, payment or date in a draft.

## 4. Rules and kernel version

- Kernel 1.2. The mismatch rule and the live-rules fallback are in
  [CARD_TEMPLATE](CARD_TEMPLATE.md).
- Laws 3 (the terminal message controls), 4 (labels), 5 (no send, no price or
  payment commitment), 7 (execution objects: the ready draft), 8 (resolve from
  sources before asking), 11 (a reason with every change), 12 (nothing closes
  on silence). Kernel section 5: thread identity by conversation ID with the
  References / In-Reply-To fallback, never by subject alone. Kernel section 7:
  drafts in Outlook Drafts only, threaded, never sent.
- Lane rules, from Joe on 2026-10-06 (PCOS QUEUE_v6, item QC24): the mail Joe
  receives and sends commits to deadlines and tasks, but they do not turn into
  tasks, and nothing checks their status, asks him about them or pulls him to
  finish them.
  - Extract from Joe's sent mail and from incoming mail where Joe is in To and
    someone asks him for something, or promises him something, with a date.
  - Due from the words of the mail, in the sender's time zone; a vague word
    leaves Due empty and sets Next check two business days out.
  - Dedupe by thread plus deliverable.
  - Closure only with evidence: delivery shown by the thread, the Worklist row
    Done, or Joe's answer. Nothing closes on silence (Law 3, email scope).
  - Joe-owes items due within 48 hours: the first item of the next EXO card, as
    one small step with a ready draft when a reply is the deliverable. Overdue
    items: one item each; owed-to-Joe and team-member items with an internal
    follow-up draft, never sent. Team-member items follow the owner map and
    surface only once overdue.
  - More than 14 days overdue without evidence: the retro card, as a past
    question, never EXO.
  - At most two commitment items per card; the EXO skip rule applies; no list
    views (Joe's standing preference: one step at a time, no walls of open
    items).
- Live text rules ([CARD_TEMPLATE](CARD_TEMPLATE.md), "Live rules for text Joe
  reads"; kernel 1.3 once live): (a) every item code, SAP code, order number or Task
  ID with its plain description, written TASK-ID (DESCRIPTION) in templates; (b) one
  home per record: a Drive file is changed in the same file, only through a "DRIVE
  WRITE:" row in [[INBOX]] for the Drive recorder, never rebuilt as a copy; (c) mail
  and message text by [[EMAIL_RULES]]; (d) people named as [[PEOPLE]] and the owner
  map resolve them.

## 5. Output contract with evidence labels

- [[COMMITMENTS]] rows, fields as in skill section 2: Commitment, Direction,
  Counterparty, Due, Thread, Source message, Status (Open, Due soon, Overdue,
  Done, Moved, Dropped), Evidence, Linked task, Draft link, Next check, plus
  Card and Skips for the card hand-off and the skip rule.
- Drafts in [[MAIL_DRAFTS]] for the marked rows only, each with the checker's
  Accept: a reply on the original thread for what Joe owes; an internal
  follow-up for what others owe.
- [[INBOX]] rows for the closeout owner when an answer settles a row with a
  Linked task.
- Evidence labels: the quoted time phrase is Confirmed (its message opened in
  this run); the reading of it (deliverable, direction, due) is Candidate until
  the thread or Joe confirms it; closure evidence is Confirmed with its key and
  ID; Joe's answer is Confirmed with the card ID; a row whose thread cannot be
  identified carries Needs Thread Check; a draft is Candidate.
- Run record: window, messages read, rows created, updated, closed (by
  evidence type), rows marked per card, drafts written and checker verdicts,
  sources opened (keys and IDs), kernel version; one heartbeat with the window
  end; one Changelog row per row changed.
- Done means: the window is read, every open row is checked, and the next
  card's rows are marked (none when none qualifies).
- Eval: commitments closed on evidence per week; Joe-owes items finished by
  their date; "Not needed / wrong direction" answers trending to zero; drafts
  approved as they were. [[GOLDEN_SET]] categories drafting and sources.

## 6. Trigger and owner model

- Trigger: weekdays at 12:40 America/Mexico_City. It marks rows for the next
  EXO 07:00 card and that evening's retro 19:00 card. The 06:40 and 18:40 runs
  are off under the usage diet. The commitments-backfill Routine runs once by
  hand over the last 30 days of sent mail.
- Runs on: Claude Code Routine (Microsoft 365, Notion and Drive connectors).
- Model: Claude Opus extracts, checks evidence and drafts. The checker verifies
  every draft on a different Claude model.
- Owner: Claude lanes. Joe only answers the EXO and retro items.
- Escalation: none outside the cards. At most two commitment items per card,
  shown by the EXO and retro lanes; a row skipped three times is asked once,
  keep or let go, and stays tracked by default.
- Depends on: [[COMMITMENTS]] (created by queue item QW21); the EXO and retro
  Routines reading the marked rows; [[LANES]], [[INBOX]] and [[CHANGELOG]]
  (exist).

## Change note

v0.1 | 2026-10-09 | Claude Code on the web, PCOS queue item QC24 | first card |
register P2-31; Joe's gap of 2026-10-06 (promises in mail never become tracked
items), confirmed by the auditor: no lane extracts commitments from sent mail,
keeps a due date or follows up | PCOS QUEUE_v6 item QC24 with the QUEUE_v7
amendment

v0.2 | 2026-10-09 | Claude Code on the web, PCOS queue item QC28 | part 4 states the
live rules for text Joe reads (item codes with a description, one home per record,
the email rules, person names); times on the one clock, America/Mexico_City | four
live Rules rows bound only the EXO lane, and the lanes ran on two clocks | PCOS
QUEUE_v10 item QC28; PCOS_JOE_DEV_LIST requests "new rules into the kernel and every
lane" and "one clock for every lane"

v0.3 | 2026-10-10 | Codex, queue item QX35 | one weekday run at 12:40 marks the
next 07:00 EXO and evening retro rows; backfill is manual | Joe's temporary
usage diet | PCOS QUEUE_v12 item QX35
