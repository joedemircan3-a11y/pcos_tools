# Agent card template

Version v0.2, 2026-10-09. Register P2-19: every lane needs a card before it gets a
Lanes row.

An agent is a model plus this card. The card gives it one mission, a restricted
tool set, a named knowledge scope and an output contract. The restrictions make
the agent specialised. A card that cannot say what its lane must never do is not
finished.

## How to write a card

1. Copy this file to `agents/<lane-name>.md`. The lane name is lowercase with
   hyphens and is the same in the title line, the file name and the Lanes row.
2. Fill the header lines, then the six numbered parts below. Keep the headings
   exactly as written and in this order (`tests/test_agents_skills.py` checks
   them).
3. Name every source by its input key, written `[[KEY]]`. Keys are defined in
   [INPUTS.md](INPUTS.md). Each key resolves to exactly one Drive, Notion or
   Outlook object through the private ID map, so an agent opens a known object
   and never searches.
4. **This repository is public.** Never write a Drive or Notion ID, a link to a
   Drive or Notion object, a person's name or address, a price, a customer, a
   vendor term or mail text into a card. Roles ("the order owner"), rule numbers
   ("Rules row R-030") and keys are enough. Values live in the private sources
   the keys point to.
5. Write templates and placeholders in plain words or CAPITALS, never in angle
   brackets: Drive strips angle-bracket placeholders when a file is staged there.
6. Exact model versions are not written on cards. A card names the model family
   and its role. The kernel's lane table pins the version.

## Header lines

- Version: v0.1. Bump it on every change and add a line to the change note.
- Status: Candidate, Live or Retired. A card becomes Live only when its Lanes row
  exists and its first run is in the Changelog.
- Register: the PCOS_PHASE2_REGISTER items the card implements.
- Lane ID: the Lanes table ID (for example L7) once it exists, else "pending".
- Skills: the skills under `/skills` that the lane loads, with versions.
- Date: date of this version, YYYY-MM-DD.

## The six parts

```
# Card: LANE-NAME

- Version: v0.1
- Status: Candidate
- Register: P2-NN
- Lane ID: pending
- Skills: SKILL-NAME vX.Y
- Date: YYYY-MM-DD

## 1. Mission
One or two sentences: what the lane produces and for whom.
Never: the actions outside the mission.

## 2. Inputs by ID
- L0, always loaded: [[KERNEL]].
- L1, read every run: the indexes, database views or row sets the lane starts from.
- L2, opened only when an L1 line or row matches: each source as [[KEY]], what is
  read there, and in which order.
- Knowledge scope: the domains and folders the lane may read. Everything else is
  out of scope; the lane does not hunt.

## 3. Tools allowed
- Each connector with the actions it may take: read, create, update named fields,
  draft.
- Not allowed: the explicit denials (send, pay, commit a price, delete, rename,
  move or trash, edit a governance file in place, mint a Task ID, and anything
  else the mission excludes).

## 4. Rules and kernel version
- Kernel: the version the card was written against and what to do on a mismatch.
- Laws and Rules rows that bind the lane, by number.
- Lane rules with their source (dev-session record, dispatch, Joe's ruling).
- Live text rules: the four rules for text Joe reads, as one line (see below).

## 5. Output contract with evidence labels
- Where it writes: database and fields, or file title pattern and folder key.
- The shape of each output.
- Evidence labels: every claim carries one of the six Law 4 labels.
- Run record: sources opened (keys and IDs), kernel version, rows changed, one
  Lanes heartbeat, one Changelog row per change.
- Done means: when the run is complete. Failure: retry once, then a Blocked row
  that holds the full content.
- Eval: how the lane is measured.
- Text rules: every text Joe reads follows the live rules for text Joe reads
  (this template); an item code in a template is written TASK-ID (DESCRIPTION).

## 6. Trigger and owner model
- Trigger: schedule in America/Mexico_City (the one clock), events, on-demand
  phrase.
- Runs on: the surface (Claude scheduled task, Claude Code Routine, ChatGPT
  scheduled task, Notion agent, PC session).
- Model: generator, checker (never the generator's model), chair if any.
- Owner: who answers for the card, the Lanes row and the fixes.
- Escalation: when and how the lane asks Joe (one card item, never a list).
- Depends on: what must exist before the first run.

## Change note
v0.1 | YYYY-MM-DD | author and session | what | why | authority
```

## Evidence labels (Law 4)

Every claim in an output carries exactly one label:

| Label | Use when |
| --- | --- |
| Confirmed | A source opened in this run states it. For mail: the terminal message of the thread. |
| Candidate | Inference, plan, prediction, proposal or draft. |
| Needs Source Check | A source exists but was not opened in this run, or does not state the claim. |
| Needs Thread Check | The claim rests on mail and the thread's terminal message was not read. |
| Needs Joe Approval | Anything external or committing: a send, price, payment, vendor term or canon change. |
| Blocked | The source could not be opened (connector, permission, missing object). |

Row status values (Predicted, Draft, Reviewed-1, Parked and so on) belong to
each database. They are not evidence labels.

## Live rules for text Joe reads

Four live [[RULES]] rows bind every lane that writes text Joe reads: cards,
briefs, Today, chat answers, Decisions and Inbox rows meant for him, mail
drafts and council Finals. Kernel 1.3 carries them; until it is live, the Rules
rows do. Every card states them in part 4 as one "Live text rules" line, and
every Routine prompt carries them as its TEXT RULES paragraph.

| Rule | What it requires | Source |
| --- | --- | --- |
| (a) Item code with description | Every item code, SAP code, order number or Task ID stands with a plain description, for example "the website stock sync check (TASK-ID)", never "TASK-ID" alone. A code alone is a checker FAIL. Email item lines keep Joe's format: code, description, quantity with unit. An output template writes the slot as TASK-ID (DESCRIPTION), SAP-CODE (DESCRIPTION) and so on (`tests/test_rules_and_clock.py` checks it). | Rules row "No item code without its description", Live 2026-10-08 (Joe, 2026-10-07) |
| (b) One home per record | A Drive file is changed in the same file with the same link, never rebuilt as a new copy, and no parallel list is started. A lane hands each Drive write to the Drive recorder through the Inbox: one [[INBOX]] row with Status Blocked and an Item that starts "DRIVE WRITE:", then the file's key, the place in the file and the exact text. The recorder (the Drive recorder lane, installed 2026-10-08, listed in `routines/_INDEX.md`) writes it in place, reads it back and sets the row Applied. | Rules row "One home per record: Drive files are edited in place; no parallel lists", Live 2026-10-08 (Joe, 2026-10-07) |
| (c) Email rules | Mail and message text follows [[EMAIL_RULES]]: the language pass (grammar, sentence flow, native US business English) by default, keeping Joe's meaning, points and voice; sentences stay whole, never split and never merged; a long sentence breaks onto a new line only right after a comma. | PCOS_EMAIL_FORMAT_RULES v4.1, 2026-10-09 (Joe) |
| (d) Person names | A person is named as [[PEOPLE]] and the owner-map rows in [[RULES]] resolve the name; where two people share a name, the address is used. The kernel holds the identity rules (which person a first name alone means). | Owner-map Rules row, 2026-10-07 (Joe); kernel identity rule |

## Rules every card inherits

These apply to every lane, so cards do not repeat them in full:

- Kernel mismatch: if the kernel version shown on the kernel page is newer than
  the one loaded, stop, reload it and re-read the card before acting.
- Until the build-day cutover, the live rules are [[OPERATING_CARD]] v7.4,
  [[BRIEF_RULES]] v3.3 and [[CANON]]. Where the draft kernel 1.0 differs, the
  live rules win.
- Write rule (kernel): read the row immediately before changing it, change only
  the fields the task needs, fill Summary and Why, add one Changelog row per
  change.
- Laws 5, 11 and 12: no autonomous send, price commitment, payment, vendor
  negotiation, canon promotion or destructive file operation. No change without
  its reason. Nothing closes on silence.
- Personal and Room 10 material never enters a business row or file.
- The live rules for text Joe reads (above), stated in part 4 of every card.
- One clock: every schedule runs on America/Mexico_City, the time zone of Joe's
  Outlook calendar. A card's trigger names no other time zone.
- A connector failure is retried once. After that the run writes a Blocked row
  that holds the full content and stops. It does not work around the failure.

## Change note

v0.1 | 2026-10-01 | Claude Code on the web, PCOS queue item Q01 | first template |
dispatch PROMPT C1 asks for a six-part card per planned lane; dev-session record
2026-09-28 part 2 adds one mission per card, tools limited to the mission, a
named knowledge scope and an eval per agent | Joe, default acceptance of
2026-09-28; PCOS_DISPATCH_2026-09-29 PROMPT C1

v0.2 | 2026-10-09 | Claude Code on the web, PCOS queue item QC28 | the live rules for
text Joe reads (item codes with a description, one home per record, the email rules,
person names), stated in part 4 of every card; one clock, America/Mexico_City | four
live Rules rows bound only the EXO lane; the lanes ran on two clocks one hour apart
until 2026-11-01 | PCOS QUEUE_v10 item QC28; PCOS_JOE_DEV_LIST requests "new rules into
the kernel and every lane" and "one clock for every lane"
