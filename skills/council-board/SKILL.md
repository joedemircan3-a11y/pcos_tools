---
name: council-board
description: Run a PCOS board council on a Notion Council row, with a draft, two anonymous reviews and a chair, and a plan round before execution. Use for judgment work (pricing assumptions, rule proposals, vendor terms, readings of a hard instruction, plans), when Joe says "council row X", when EXO interpretation readings conflict on a fact, and when weekly-evolve sends a disputed proposal. Not for routine lane outputs (the checker covers those) or urgent work (council-github).
compatibility: Needs the PCOS Notion hub (Council database and its Reviewer view, Rules, Decisions, Changelog). Review-1 runs as a ChatGPT scheduled task with the reviewer prompt in references/prompts.md.
metadata:
  version: "0.1"
  status: Candidate
  register: P2-06
  kernel: "1.0"
  card: agents/council-board.md
---

# Council board

Several models take turns on one row. The author never judges. The reviewers
never see the author. The chair decides. Joe sees the row only when the
reviewers disagree on a fact that nothing else can settle.

Sources are named by key, written `[[KEY]]` (defined in `agents/INPUTS.md`, IDs
in the private map named there). The prompts for each stage are in
[references/prompts.md](references/prompts.md).

## 1. Rows and rounds

Every council has two rounds, each on its own [[COUNCIL]] row:

| Round | Task title | Starting Status | Draft holds |
| --- | --- | --- | --- |
| Plan | "TITLE · plan" | Plan | The plan: question, sources by key and ID, method, assumptions, what would change the plan |
| Execution | "TITLE · execution" | Draft | The work itself, built on the plan row's Final |

Both rows move through Reviewed-1, Reviewed-2, then Final (or Needs Joe). The
execution row is created only when the plan row is Final. A small item (one
reading, one proposal) still gets a plan round, but the plan is three lines:
question, sources, method.

Deadline: the chair time of the cycle the row should finish in. The default is
the next cycle.

## 2. Stages (daily cycle, Mexico City time)

| Time | Stage | Writes | Status after |
| --- | --- | --- | --- |
| 08:00 | Draft (Claude) | Task, Draft, Author, Deadline | Plan or Draft |
| 09:00 | Review-1 (GPT, ChatGPT scheduled task) | Review-1 | Reviewed-1 |
| 09:30 | Review-2 (Claude, fresh session; Gemini later) | Review-2 | Reviewed-2 |
| 10:00 | Chair (Claude) | Final, Dissent | Final or Needs Joe |

Each stage reads the row right before writing, writes only its own fields, adds
one [[CHANGELOG]] row per field written (with the kernel version), and writes one
heartbeat in [[LANES]]. "Council row X" puts a row into the next cycle.

## 3. Draft

1. Read the task, the sources it names, the Live rows in [[RULES]] (or [[CANON]]
   until rules are rows) and [[DECISIONS]]. Anything already decided is quoted,
   not reopened.
2. Write the Draft with each claim labeled (Law 4) and each source cited by key
   and ID. In the execution round, start from the plan row's Final.
3. Strip self-identification: no model or tool name, no "as I said", nothing
   that tells the reviewers who wrote it. Author is a field, not prose.
4. Fill Author (Claude, GPT, Opus or Gemini).

## 4. Reviews (anonymous)

- Reviewers work only from [[COUNCIL_REVIEWER_VIEW]], with the reviewer prompt.
  They never open the row page itself, Author, Final or Dissent, or the Draft
  stage's Changelog rows.
- Each reviewer re-opens the sources the Draft cites, inside its own access.
- Write one finding per bullet: the point, the evidence (key, ID and line), and
  a verdict for that point (Accept, Fix or Reject). End with an overall verdict.
- Independence: Review-2 writes its findings before it reads Review-1. Then it
  adds one line: "Against Review-1: agree on N, disagree on M (list)."
- A reviewer never edits the Draft and never proposes a different task.

## 5. Chair

1. Read everything, Author included.
2. Answer each Fix or Reject finding: accepted (with the change), or rejected
   (with the reason and the evidence).
3. Write Final. Plan round: the approved plan. Execution round: the
   execution-ready output, every claim labeled. Anything external stays Needs Joe
   Approval and is never sent from here.
4. Write Dissent: each point a reviewer still disputes, with the reason. Write
   "none" if there is none.
5. Decide the Status:
   - Final, when the reviews agree, or when they disagree on judgment (the chair
     decides and records it in Dissent).
   - Needs Joe, only when the reviewers disagree on a **fact** that neither the
     kernel nor the sources settle. Then add one card question to the next EXO
     slot: the fact in one line, 2 or 3 options, the chair's default first.
6. The checker runs on the Final (job type council-final) before the next stage
   uses it.

## 6. Missing stages

- A review missing at chair time: the chair waits one cycle (Status unchanged).
- Still missing after that cycle: the chair decides with the review it has and
  writes "Review-N missing" in Dissent. Lane health reports the missed run.
- The Draft stage is never replaced by a reviewer.

## Never

- Show Author to a reviewer, or let the author review or chair its own draft.
- Start execution before the plan row is Final.
- Ask Joe about judgment calls, or about facts that the kernel or the sources
  settle.
- Send, pay, commit a price or agree a vendor term from a council row.
