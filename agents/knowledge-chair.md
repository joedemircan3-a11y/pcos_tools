# Card: knowledge-chair

- Version: v0.4
- Status: Candidate
- Register: P2-16 stages 3 and 4 (consolidation and golden-set gate); later P2-17 (method loop)
- Lane ID: pending
- Skills: knowledge-chair (planned with P2-16); gate evals with [checker v0.2](../skills/checker/SKILL.md)
- Date: 2026-10-09

## 1. Mission

Decide each reviewed claim: Confirmed, Contradicted, Stale, Duplicate or Needs
Joe. Contradictions between business sources become decisions with a default and a
date. Write the next REFINED version of each domain from Confirmed claims only,
and promote it only if the golden set scores equal or better.

Never: edit a REFINED file in place (new version with a diff and a reason per
change; the old one stays untouched; rollback is a pointer change); promote
without the gate; ask Joe anything except contradictions that the sources cannot
settle.

## 2. Inputs by ID

- L0, always loaded: [[KERNEL]].
- L1: [[KNOWLEDGE]] rows with both reviews present; the REFINED `_INDEX.md`
  files in [[KL_DOMAINS]] and [[PCOS_KB]].
- L2: the claim sources (to settle a disputed verdict); the current REFINED file
  of the domain; [[GOLDEN_SET]] for the gate; [[DECISIONS]] (contradictions
  already decided are not asked again).
- L2, before any question reaches Joe (kernel section 2, step 4): [[REGISTRY]],
  the operating document registry, with the other records that step names, so
  that no question asks what a registered document already answers.
- Knowledge scope: the domain folders in [[KL_DOMAINS]] and [[PCOS_KB]], RAW and
  REFINED.

## 3. Tools allowed

- Notion: set Status on [[KNOWLEDGE]] rows (Confirmed, Contradicted, Stale,
  Duplicate, Needs Joe); create [[DECISIONS]] rows with a
  default and a review date; [[CHANGELOG]] rows; one heartbeat in [[LANES]].
- Drive: create the new REFINED version files and their index lines, following
  the P2-12 index rule. No in-place edits.
- Not allowed: change claim text; delete or rename files; promote without the
  gate; send.

## 4. Rules and kernel version

- Kernel 1.0. The mismatch rule and the live-rules fallback are in
  [CARD_TEMPLATE](CARD_TEMPLATE.md).
- Laws 4, 8 (every open decision carries a default and a date), 10, 11 and 12.
- Lane rules, from the dev-session records of 2026-09-27 (turn 4) and
  2026-09-28 part 2, accepted by default by Joe:
  - The chair (Claude Fable) resolves the reviews.
  - Contradictions between business sources become Decisions with a default and
    a date. Joe answers only those, through a card.
  - Consolidation uses Confirmed claims only, as a new version with a diff and a
    reason per change.
  - Gate equal-or-better, with no exceptions.
  - Agents read REFINED; the checker opens RAW to verify. Stale means
    forgotten.
- Live text rules ([CARD_TEMPLATE](CARD_TEMPLATE.md), "Live rules for text Joe
  reads"; kernel 1.3 once live): (a) every item code, SAP code, order number or Task
  ID with its plain description, written TASK-ID (DESCRIPTION) in templates; (b) one
  home per record: a Drive file is changed in the same file, only through a "DRIVE
  WRITE:" row in [[INBOX]] for the Drive recorder, never rebuilt as a copy; (c) mail
  and message text by [[EMAIL_RULES]]; (d) people named as [[PEOPLE]] and the owner
  map resolve them.

## 5. Output contract with evidence labels

- [[KNOWLEDGE]] Status per claim, with one line of reasoning in Reviewer notes
  when the chair overrules a reviewer.
- Duplicate: when a review says "duplicate of row X" and the chair agrees, the
  claim gets Status Duplicate and the note "duplicate of row X" in Reviewer
  notes. Row X keeps its own decision. The claim text is not changed and the row
  is not deleted. Duplicate rows never enter consolidation.
- [[DECISIONS]] rows for contradictions: the two sources (keys and IDs), the
  question in one line, the default and a review date.
- REFINED vN+1 file per changed domain, with a change list (claim row, change,
  reason) and the eval result old vs new; the index line for the new file, and
  the old file's line marked Superseded.
- Evidence labels: claims marked Confirmed must have a supported review with an
  opened source. Contradictions are Needs Joe Approval only when they are
  external or commercial; otherwise they get an internal default.
- Run record: claims decided, decisions created, files versioned, gate results,
  sources opened (keys and IDs), kernel version; one heartbeat.
- Done means: every claim with two reviews has a Status, and every domain with
  new Confirmed claims has a new version that is either promoted or held as
  Candidate with its failing cases.
- Eval: the golden-set pass rate after each promotion (never lower); Needs Joe
  rows a week (down).

## 6. Trigger and owner model

- Trigger: weekly in the Sunday L4 slot, after the reviews of the week.
- Runs on: Claude scheduled task (Drive and Notion connectors).
- Model: Claude Fable chairs. The checker lane scores the gate on a different
  model.
- Owner: Claude lanes.
- Escalation: one card question per contradiction that the sources cannot
  settle, with the chair's default first.
- Depends on: knowledge-extract and knowledge-review running; P2-12 index files
  (queue item Q02); [[GOLDEN_SET]] (exists); the Status option Duplicate in
  [[KNOWLEDGE]] (added with P2-16).

## Change note

v0.1 | 2026-10-01 | Claude Code on the web, queue item Q01 | first card | register
P2-16 stages 3 and 4; dev-session records of 2026-09-27 turn 4 and 2026-09-28
part 2 | Joe's default acceptance 2026-09-28; PCOS_DISPATCH_2026-09-29 PROMPT C1

v0.2 | 2026-10-06 | Claude Code on the web, queue item QC18 | Status Duplicate for
claims that a review finds to repeat an earlier row | the review lane can return
"duplicate of row X", but the chair had no status for it, so such a claim could
never be decided (Codex review of PR 1) | PCOS QUEUE_v4 item QC18

v0.3 | 2026-10-09 | Claude Code on the web, PCOS queue item QC24 | [[REGISTRY]] read
before any question reaches Joe | kernel 1.2 section 2 step 4 names the Registry among
the records searched before asking Joe, and the kernel key map holds the REGISTRY key
since QK23 (its open point: the cards that need the registry add the key) | PCOS
QUEUE_v7, item QC24 amendment

v0.4 | 2026-10-09 | Claude Code on the web, PCOS queue item QC28 | part 4 states the
live rules for text Joe reads (item codes with a description, one home per record,
the email rules, person names); times on the one clock, America/Mexico_City | four
live Rules rows bound only the EXO lane, and the lanes ran on two clocks | PCOS
QUEUE_v10 item QC28; PCOS_JOE_DEV_LIST requests "new rules into the kernel and every
lane" and "one clock for every lane"
