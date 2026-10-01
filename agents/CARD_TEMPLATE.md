# Agent card template

Version v0.1, 2026-10-01. Register P2-19: every lane needs a card before it gets a
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

## 5. Output contract with evidence labels
- Where it writes: database and fields, or file title pattern and folder key.
- The shape of each output.
- Evidence labels: every claim carries one of the six Law 4 labels.
- Run record: sources opened (keys and IDs), kernel version, rows changed, one
  Lanes heartbeat, one Changelog row per change.
- Done means: when the run is complete. Failure: retry once, then a Blocked row
  that holds the full content.
- Eval: how the lane is measured.

## 6. Trigger and owner model
- Trigger: schedule with time zone, events, on-demand phrase.
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
- A connector failure is retried once. After that the run writes a Blocked row
  that holds the full content and stops. It does not work around the failure.

## Change note

v0.1 | 2026-10-01 | Claude Code on the web, PCOS queue item Q01 | first template |
dispatch PROMPT C1 asks for a six-part card per planned lane; dev-session record
2026-09-28 part 2 adds one mission per card, tools limited to the mission, a
named knowledge scope and an eval per agent | Joe, default acceptance of
2026-09-28; PCOS_DISPATCH_2026-09-29 PROMPT C1
