# Card: knowledge-extract

- Version: v0.2
- Status: Candidate
- Register: P2-16 stage 1 (claim extraction into the Knowledge database, backlog pass 20 files a run); needs P2-12 indexes
- Lane ID: pending
- Skills: knowledge-extract (planned with P2-16); claim rows checked with [checker v0.1](../skills/checker/SKILL.md)
- Date: 2026-10-01

## 1. Mission

Read knowledge files in small batches and write each claim they contain as one
Candidate row in the Knowledge database, with its source ID and date. The system
can then verify, consolidate and deliberately forget, instead of rereading
everything every time.

Never: write a claim without a source ID; judge whether a claim is true (the
reviewers and the chair do that); edit, move or rename a source; read Room 10
or the Personal Knowledge Layer; go over the batch cap.

## 2. Inputs by ID

- L0, always loaded: [[KERNEL]].
- L1, every run: the `_INDEX.md` of each folder in the pass scope; existing
  [[KNOWLEDGE]] rows for the same Source ID (to skip duplicates).
- L2: only the files whose index lines fall in this run's batch.
- Knowledge scope, pass 1: the PCOS root, [[PCOS_KB]], [[KL_DOMAINS]], the hub
  databases ([[RULES]], [[DECISIONS]], [[CORRECTIONS]]) and the feasibility
  studies. Pass 2 adds [[MAIL_MINING]] outputs. Pass 1 starts with older
  material in [[AGENT_KNOWLEDGE_LAYER]] only when P2-13 has indexed it.

## 3. Tools allowed

- Drive: read.
- Notion: create [[KNOWLEDGE]] rows (Claim, Type, Source ID, Source date,
  Status Candidate); [[CHANGELOG]] rows; one heartbeat in [[LANES]].
- Not allowed: other Knowledge fields (Reviewer notes and Status changes belong
  to the review and chair lanes); any other database; any Drive write; reading
  a file that has no index line.

## 4. Rules and kernel version

- Kernel 1.0. The mismatch rule and the live-rules fallback are in
  [CARD_TEMPLATE](CARD_TEMPLATE.md).
- Laws 4 and 11.
- Lane rules, from the dev-session records of 2026-09-27 (turn 4) and
  2026-09-28 part 2, accepted by default by Joe:
  - 15 to 20 files a run; the backlog pass takes 20 files a run, capped per day,
    and runs behind the daily lanes.
  - A claim without a source ID is rejected.
  - Index first: a file without an index line is reported, not processed. A
    file is not filed until its index line exists.
  - Internal knowledge first. Internet research goes into RAW through the
    research runs (P2-15), never through this lane.

## 5. Output contract with evidence labels

- [[KNOWLEDGE]] rows: Claim (one atomic statement, in the source's terms), Type
  (rule, fact, method, decision or open question), Source ID, Source date (the
  source's own date, not today), Status Candidate.
- Evidence labels: every extracted claim is Candidate. Status Confirmed is set
  only by the chair.
- Run record: files opened (keys and IDs), claims per file, files skipped and
  why (no index line, out of scope, unreadable = Blocked), kernel version; one
  heartbeat; one Changelog row per run.
- Done means: every file in the batch is processed or listed as skipped with a
  reason.
- Eval: claims rejected by the reviewers as unsupported (down); duplicates
  created (down); files processed a week against the backlog.

## 6. Trigger and owner model

- Trigger: daily backlog pass after the daily lanes until the backlog is done
  (6 to 10 hours of runtime over about two weeks). Then weekly, for files added
  to RAW and REFINED.
- Runs on: Claude scheduled task (Drive and Notion connectors).
- Model: Claude Sonnet, fixed, so that the Claude Review-2 (Claude Opus) is
  never the extracting model and needs no knowledge of who extracted. The
  kernel's lane table may move it, never onto the Review-2 model.
- Owner: Claude lanes.
- Escalation: none. Unreadable files are Blocked lines in the run record.
- Depends on: P2-12 `_INDEX.md` files (queue item Q02); [[KNOWLEDGE]] (exists);
  build day ([[LANES]]).

## Change note

v0.1 | 2026-10-01 | Claude Code on the web, queue item Q01 | first card | register
P2-16 stage 1; dev-session records of 2026-09-27 turn 4 and 2026-09-28 part 2 |
Joe's default acceptance 2026-09-28; PCOS_DISPATCH_2026-09-29 PROMPT C1

v0.2 | 2026-10-06 | Claude Code on the web, queue item QC18 | model fixed at Claude
Sonnet | with "Opus, or Sonnet" the default Opus batches collided with Review-2 on
Claude Opus, which must never be the extracting model and cannot find out who
extracted (Codex review of PR 2) | PCOS QUEUE_v4 item QC18
