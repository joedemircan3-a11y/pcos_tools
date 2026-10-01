# Card: council-board

- Version: v0.1
- Status: Candidate
- Register: P2-06 (board council on Notion: Draft, Review-1, Review-2, Final, Dissent; plan round before execution; chair)
- Lane ID: pending
- Skills: council-board (planned, queue item Q08); the chair's Final is checked with [checker v0.1](../skills/checker/SKILL.md)
- Date: 2026-10-01

## 1. Mission

Run judgment work through several models that take turns on one Notion row:
pricing assumptions, rule proposals, vendor terms, readings of a hard
instruction, plans. A decision then reaches Joe already drafted, reviewed twice
and chaired, or it never needs to reach him.

Never: let a reviewer see who wrote the draft; let the author judge its own
draft; execute before the plan round is Final; ask Joe anything the kernel or the
sources settle.

## 2. Inputs by ID

- L0, always loaded: [[KERNEL]].
- L1: [[COUNCIL]] rows by Status. Reviewers read only through
  [[COUNCIL_REVIEWER_VIEW]] (Task, Draft, Review-1, Review-2, Status, Deadline;
  Author, Final and Dissent hidden).
- L2: the sources the Draft cites by key and ID; reviewers re-open them. Live
  rows in [[RULES]]; [[DECISIONS]]; [[CANON]] until rules are rows.
- Knowledge scope: the REFINED material in [[KL_DOMAINS]] and [[PCOS_KB]] that
  the task names. RAW only to verify a quoted source.

## 3. Tools allowed

- Notion, by stage. Draft: writes Task, Draft, Author, Deadline and Status Plan
  or Draft. Review-1: writes Review-1 and Status Reviewed-1. Review-2: writes
  Review-2 and Status Reviewed-2. Chair: writes Final, Dissent and Status Final
  or Needs Joe. Every stage writes [[CHANGELOG]] rows and a heartbeat in
  [[LANES]].
- ChatGPT scheduled task for Review-1; it writes Notion itself.
- Not allowed: send; commit a price, payment or vendor term; edit another
  stage's field; change Author after creation; read Author as a reviewer.

## 4. Rules and kernel version

- Kernel 1.0. The mismatch rule and the live-rules fallback are in
  [CARD_TEMPLATE](CARD_TEMPLATE.md).
- Laws 4, 5, 8, 10 and 11.
- Lane rules, from the dev-session record of 2026-09-27 (turns 1 to 4, accepted
  by default by Joe):
  - Plan round first: the Draft is a plan, the reviews critique the plan, and
    execution starts only when the plan is Final.
  - Reviewers read the Draft, never the Author. Models rank their own answers
    higher, so the judge is never the author.
  - Review-1 is GPT. Review-2 is Claude Opus until Gemini is confirmed. The
    chair is Claude Fable.
  - Reviews give one finding per bullet, with evidence and a verdict: Accept,
    Fix or Reject.
  - Needs Joe only when the reviewers disagree on a fact that neither the kernel
    nor the sources can settle.

## 5. Output contract with evidence labels

- Complete [[COUNCIL]] row: Draft with sources by key and ID; Review-1 and
  Review-2 as one finding per bullet with evidence and verdict; Final, the
  execution-ready decision or plan; Dissent, what a reviewer still disputes and
  why; Status Final or Needs Joe.
- Evidence labels on every claim in Draft and Final. Final may not label a claim
  Confirmed unless some stage opened a source that states it. Anything external
  stays Needs Joe Approval.
- Needs Joe: one card question with 2 or 3 options and the chair's default
  first.
- Run record per stage: sources opened (keys and IDs), kernel version; one
  Changelog row per field written.
- Done means: Status Final, or Needs Joe with the disputed fact in one line.
- Eval: Needs Joe rows per week (down); Finals that Joe overturns, logged in
  [[CORRECTIONS]]; cycle time.

## 6. Trigger and owner model

- Trigger: a daily cycle in Mexico City time: 08:00 Draft, 09:00 Review-1, 09:30
  Review-2, 10:00 Chair. On demand, "council row X" joins the next cycle. Urgent
  work goes to council-github instead.
- Runs on: Claude scheduled tasks (Draft, Review-2, Chair) and a ChatGPT
  scheduled task (Review-1).
- Model: Draft Claude Opus; Review-1 GPT (ChatGPT Pro); Review-2 Claude Opus in a
  fresh session, never the Draft session, until Gemini joins through a Drive
  mirror row; chair Claude Fable.
- Owner: Claude lanes own the cycle and the chair. The GPT lane owns Review-1
  reliability (three-day write test pending).
- Escalation: Needs Joe only as in part 4.
- Depends on: build day; [[COUNCIL]] and [[COUNCIL_REVIEWER_VIEW]] (exist); the
  council-board skill (queue item Q08); a ChatGPT scheduled task that writes
  Notion on three days running.

## Change note

v0.1 | 2026-10-01 | Claude Code on the web, queue item Q01 | first card | register
P2-06; design in the dev-session record of 2026-09-27, turns 2 to 4 | Joe's
default acceptance 2026-09-28; PCOS_DISPATCH_2026-09-29 PROMPT C1
