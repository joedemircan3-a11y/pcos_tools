# Card: retro

- Version: v0.3
- Status: Candidate
- Register: P2-30 (Retro lane: evening card of five past-closure questions, last 90 days first; answers feed the ledger, the People profiles and the golden set)
- Lane ID: pending
- Skills: [retro v0.3](../skills/retro/SKILL.md); commitment items shown and filed by [commitments v0.2](../skills/commitments/SKILL.md) sections 7 and 8; every item checked with [checker v0.2](../skills/checker/SKILL.md) (job type question-card); ledger items filed by [prediction-ledger v0.1](../skills/prediction-ledger/SKILL.md) section 3
- Date: 2026-10-09

## 1. Mission

Close gaps in the historical record by asking Joe about the past, which he
answers easily ("past is just remembering"). Each evening, find the threads and
Worklist items of the last 90 days that the record leaves open, read them in
full, and ask five one-line questions with tap options. File each answer where
it teaches the system: the Prediction row, the People profile, the golden set.

Never: ask what the record already answers, or ask before the full thread chain
and every later reply are read; ask about today's work (the morning and midday
cards are EXO's); overwrite, move or answer mail; close or change a Worklist
row; send or commit anything; treat silence as an answer.

## 2. Inputs by ID

- L0, always loaded: [[KERNEL]].
- L1, every run: the previous retro card's row in [[DECISIONS]] (answers and
  skips), its own open conflict rows, and the decided and open rows (never
  re-ask); the CAL lane's open questions in [[CAL_FOLDER]]; [[PREDICTION]]
  (the identities the ledger already owns, and the Asked Joe rows whose
  questions ride on this card); [[WORKLIST]] rows updated in the window;
  [[STEPS]] rows Queued, Shown or Reshaped (EXO works those tasks);
  [[COMMITMENTS]] rows (their threads and Linked tasks are never gaps; the
  rows marked for the evening ride on the card).
- L2, gap query and gate, per candidate: the whole thread in [[MAIL_INBOX]],
  [[MAIL_SENT]] and [[MAIL_ROUTED]]; later threads with the same counterpart or
  Task ID; [[CHANGELOG]] rows about it; the measured closure habits in
  [[MAIL_MINING]].
- L2, before any item reaches Joe (kernel section 2, step 4): [[REGISTRY]]
  for any document the thread or row names, with the records above.
- L2, filing: the profile of each person in the thread in [[PEOPLE]]
  (private); [[CAL_STANDARD]] and [[CAL_TEMPLATE]] for the card page.
- Knowledge scope: mail, the Worklist and the PCOS rows above, last 90 days
  first. No domain folders. Personal and Room 10 material is out of scope.

## 3. Tools allowed

- Outlook (Microsoft 365 connector): read Inbox, Sent Items and the routed
  folders. Nothing else.
- Notion: create [[PREDICTION]] rows and write Actual, Status and Check date on
  the rows it files (ledger items by the ledger's rules); one Open row in
  [[DECISIONS]] per card, and one per conflict between Joe's memory and the
  record, with Joe's answer written into its Answer; [[CORRECTIONS]] rows for
  golden-set candidates; [[INBOX]] rows for the closeout owner (row changes,
  open items, people lines); [[CHANGELOG]] rows; one heartbeat in [[LANES]];
  on [[COMMITMENTS]] rows, Status, Due, Evidence, Next check, Card and Skips
  only, by the commitments skill section 7.
- Card page: publish the card from [[CAL_TEMPLATE]] (in Claude: an Artifact
  with the database capability) and read the answers back.
- Not allowed: send, draft, reply to, forward, move or delete mail; write
  [[GOLDEN_SET]] or [[PEOPLE]] directly; change Status, Owner or Priority on a
  [[WORKLIST]] row; mint Task IDs; write a prediction (Is task, Owner, Route,
  Candidate output, Assumptions, Confidence, Score) into a row it creates; show
  a card outside the evening slot, except when Joe asks.

## 4. Rules and kernel version

- Kernel 1.1. The mismatch rule and the live-rules fallback are in
  [CARD_TEMPLATE](CARD_TEMPLATE.md).
- Laws 3 (the terminal message controls), 4 (labels), 5 (no send), 8 (resolve
  from sources before asking), 11 (a reason with every change), 12 (nothing
  closes on silence).
- Lane rules, from the dev-session record of 2026-10-06, part 7 (turns 20 and
  21; Joe's decisions, dated 2026-10-01 in QUEUE_v4):
  - Evening card = past questions; morning and midday cards = today. The 19:00
    slot, America/Mexico_City, moves from EXO to this lane.
  - Five questions per evening, last 90 days first.
  - Order: recency, then open value (money, active vendors), then pattern
    class (one answer that closes many).
  - Joe's standing rule: never ask what the record already answers. The full
    thread chain and every later reply are read first.
  - Skip rule as EXO: 2 skips reshape, 3 skips park and ask once.
  - Never overwrite the mail. When Joe's memory and the record disagree, keep
    both and open a Decision row.
- Live text rules ([CARD_TEMPLATE](CARD_TEMPLATE.md), "Live rules for text Joe
  reads"; kernel 1.3 once live): (a) every item code, SAP code, order number or Task
  ID with its plain description, written TASK-ID (DESCRIPTION) in templates; (b) one
  home per record: a Drive file is changed in the same file, only through a "DRIVE
  WRITE:" row in [[INBOX]] for the Drive recorder, never rebuilt as a copy; (c) mail
  and message text by [[EMAIL_RULES]]; (d) people named as [[PEOPLE]] and the owner
  map resolve them.

## 5. Output contract with evidence labels

- Card: five items; fewer when fewer gaps pass the gate; none when none do. The
  ledger's "What happened?" items first, in the ledger's format, then the open
  conflict items, then at most two commitment items in the commitments
  skill's format. Each retro item is a one-line summary of the thread plus tap
  options: closed as quoted, closed differently, dropped, moved offline (phone,
  WhatsApp, in person), still open, and unrelated, which is the CAL template's
  own "Not needed / wrong direction" option and is never added twice; free
  text or voice for anything else. A class item covers 2 to 5 threads of one
  class. One progress line at the end; never the size of the backlog.
- [[PREDICTION]]: for every identity an item covers, Actual on the matching
  row, or a new row (Subject, Source = the identity, Actual, Status) with no
  prediction fields.
- People lines (Candidate) for the closeout owner; golden-set candidates as
  [[CORRECTIONS]] rows; one [[DECISIONS]] row per conflict; [[INBOX]] rows for
  the closeout owner.
- Evidence labels: a summary on a card is Candidate until Joe answers. His
  answer is Confirmed, with the card ID as its source. People lines and rule
  candidates are Candidate. A closure the gate finds in the record is
  Confirmed, with its evidence key and ID.
- Run record: window, gaps found, gate catches (closed from the record, not
  asked), items shown, answers filed by type, people lines, golden-set
  candidates, conflicts, sources opened (keys and IDs), kernel version; one
  heartbeat; one Changelog row per changed row.
- Done means: every answer from the previous card is filed, and the new card
  is published, or none when no gap passes the gate.
- Eval: share of items answered; gaps closed per week; questions the record
  already answered at zero; "unrelated" answers trending down. [[GOLDEN_SET]]
  categories re-asking and sources.

## 6. Trigger and owner model

- Trigger: daily, card at 19:00 America/Mexico_City (the Routine fires at 18:53).
  On demand when Joe says "retro".
- Runs on: Claude Code Routine (Notion, Microsoft 365 and Drive connectors).
  The card is published as an Artifact page.
- Model: Claude Opus finds the gaps and writes the card. The checker verifies
  every item on a different Claude model before it is shown.
- Owner: Claude lanes. Joe only answers cards.
- Escalation: none outside the card. A conflict between Joe's memory and the
  record becomes one Decision row, asked on the next retro card as an
  assumption item.
- Depends on: [[PREDICTION]], [[DECISIONS]] and [[CORRECTIONS]] (exist); the
  EXO Routine without its 18:53 run; the prediction-ledger lane queuing its
  questions to this card.

## Change note

v0.1 | 2026-10-06 | Claude Code on the web, PCOS queue item QC19 | first card |
register P2-30; design in the dev-session record of 2026-10-06, part 7, turns
20 and 21 | Joe's decisions (QUEUE_v4, 2026-10-01): Retro lane in Wave A after
the ledger and before EXO; evening card = past questions; five per evening,
last 90 days first; QUEUE_v4 item QC19

v0.2 | 2026-10-09 | Claude Code on the web, PCOS queue item QC24 | the evening card
carries the commitments lane's past questions (at most two, after the conflict items),
filed into their Commitments rows; a thread with a Commitments row is never a gap;
[[REGISTRY]] read before any item reaches Joe | Joe's gap of 2026-10-06: commitments
more than 14 days overdue go to the Retro lane as past questions, not to EXO; kernel 1.2
section 2 step 4 names the Registry among the records searched before asking Joe (QK23
open point) | PCOS QUEUE_v6 item QC24, QUEUE_v7 amendment

v0.3 | 2026-10-09 | Claude Code on the web, PCOS queue item QC28 | part 4 states the
live rules for text Joe reads (item codes with a description, one home per record,
the email rules, person names); times on the one clock, America/Mexico_City | four
live Rules rows bound only the EXO lane, and the lanes ran on two clocks | PCOS
QUEUE_v10 item QC28; PCOS_JOE_DEV_LIST requests "new rules into the kernel and every
lane" and "one clock for every lane"
