# Checker checklists, one per job type

Version v0.1, 2026-10-01. Loaded by [the checker skill](../SKILL.md) step 2.
Keys (`[[KEY]]`) are defined in `agents/INPUTS.md`. "Required" sources are
opened by the checker itself in every check. Rule numbers refer to the kernel
laws (L1 to L12) and Rules rows. Until cutover, the same laws are in
[[OPERATING_CARD]] and the routes and owner map in [[BRIEF_RULES]].

Every checklist ends with the common checks:

- C1 Labels: every claim carries one of the six Law 4 labels, and each label
  matches the evidence (checker skill step 5).
- C2 Re-ask: no question to Joe is already answered (skill step 6).
- C3 Hard stops: none present (skill step 7).
- C4 Run record: kernel version, sources opened with keys and IDs, one Changelog
  row per change.

## mail-draft

A Route 2 instruction or a Route 3 reply drafted into Outlook (brief lane, EXO
clarifying line, intake reply).

Required: the whole thread, every branch, including its terminal message
([[MAIL_INBOX]], [[MAIL_ROUTED]], [[MAIL_SENT]]); the owner-map rows in
[[RULES]]; [[DECISIONS]]; for a recurring report, Joe's last sent version.

1. The route follows the evaluation order: Route 1 tests first, then Route 3
   criteria (name the one that fired), then Route 2 as the default.
2. No Route 3 when the terminal message of the thread is Joe's.
3. Route 2 is a new internal email to the owner from the owner map: one to three
   lines with the outcome, the deadline and "loop me only if". It is never a
   reply into an external chain.
4. Route 3 is a reply on the original thread, never a retyped new message.
5. Where two people share a name, the address is used, never the bare name.
6. Language and style follow the brief rules: the thread's language for that
   counterpart, sign-off "best regards", signature inserted, no duplicate typed
   sign-off.
7. A correction email to a team member uses observations with evidence per
   bullet, closes with "Please review below observations and let me know", and
   has no commands, no money commitments and no recalculated totals.
8. No price, payment, quantity or date promise to an external party.
9. It is in Drafts and not sent. At most 5 drafts per run.

## routing

The classification of an incoming item (brief lane, the Route field of the
prediction ledger, intake).

Required: the thread's terminal message; the owner-map rows in [[RULES]]; the
task row in [[WORKLIST]] when a task exists.

1. Thread identity uses the conversation ID (or References and In-Reply-To),
   never the subject alone.
2. The evaluation order is applied, and the firing criterion is named.
3. The owner comes from the owner map; ownership-level senders are ask-only.
4. Radar thresholds come from the brief rules, not from memory.
5. Credentials or secrets seen in mail: Route 3 security item, named by thread,
   sender and date only, never transcribed.
6. Loop detection: when a counterpart replies to an older message after an
   answer exists, the item is flagged "answer exists, re-point".

## state-write

A change to a Worklist row, PCOS_NOW, or a Notion row.

Required: the row as read immediately before the write (in the run record); the
source that justifies the change; the [[CHANGELOG]] row.

1. The row was read immediately before the write.
2. Only the fields the task needs changed.
3. Summary and Why are filled.
4. One Changelog row per change: what, why, authority (Joe's words with date,
   the rule, or the source), tool and session, before and after, kernel version.
5. No close, expiry or archive without Joe's explicit answer, cited (L12).
6. No Task ID minted outside a closeout.
7. Status, Priority and Room values come from the vocabulary in
   `pcos_tools/vocab.json`. Where code execution exists, run
   `python -m pcos_tools hygiene` on the exported Worklist.
8. No personal or Room 10 content in a business row.

## delta

A DELTA row in [[INBOX]] or a DELTA file in [[INBOX_FOLDER]].

1. All five fields are present: Task ID, what changed, why (reason and
   authority), next action, confidence. Files created are listed with title and
   ID.
2. One scope: business and personal content never share a DELTA.
3. A file name follows DELTA_YYYY-MM-DD_source_topic.md. No placeholder or
   no-change file.
4. The Why names its authority. A DELTA without a reason is not applied until
   the reason is recovered (L11).

## question-card

A CAL card, an EXO card, a retro card or a "What happened?" question.

Required: [[CAL_STANDARD]]; [[DECISIONS]]; Joe's replies in the chain and
[[MAIL_SENT]]; for EXO, the [[STEPS]] rows shown; for a retro item, the whole
thread in [[MAIL_INBOX]], [[MAIL_SENT]] and [[MAIL_ROUTED]] when the gap has
one, and the [[WORKLIST]], [[CHANGELOG]] and [[PREDICTION]] rows about it.

1. Every question passes CAL-R5: it is not already answered in Decisions, in
   Joe's replies or in a later reply.
2. One decision per question. Self-contained, in plain words, with the key
   facts, numbers and dates inside it; no internal ID without its meaning.
3. 2 to 4 options, the recommended option first; options are concrete actions
   with owner and date where relevant; no "Other". A retro item has its six
   fixed tap options instead (item 7).
4. The "Not needed / wrong direction" option is present (the template adds it).
   A "What happened?" question also offers "unrelated / wrong direction".
5. EXO: 2 to 4 items, assumption form unless no assumption is defensible, a
   progress line at the end, no overdue list and no count of late items.
6. One Open row in [[DECISIONS]] for the card.
7. Retro: at most five items; the ledger's "What happened?" items first, then
   the open conflict items. A retro item is one line that sums up the thread
   (for a gap with no thread, the Worklist row: the task, what it waited on,
   since when),
   with the tap options closed as quoted, closed differently, dropped, moved
   offline and still open, plus the template's "Not needed / wrong direction"
   as the sixth, unrelated (never a second unrelated option), and free text or
   voice. A class item covers 2 to 5 threads of one class, each listed with its
   identity in the card's [[DECISIONS]] row. The skip rule's last-chance item
   offers keep or let go instead of the six options. A progress line ends the
   card; no count of open gaps.
8. Retro gate, for every gap of the item: for a thread, every message and
   every later reply was read (the message IDs are in the run record); for a
   Worklist row alone, the row and the sources it names were read; no
   closure evidence exists in the mail, [[WORKLIST]], [[CHANGELOG]] or
   [[DECISIONS]]; no [[PREDICTION]] row has any identity the gap carries (the
   conversation ID, and the Task ID of a linked Worklist row) in Source, unless
   the item is the ledger's own queued question. Matching is by identity, never
   by subject.

## prediction

A Prediction row or its scoring.

Required: the [[PREDICTION]] row; for scoring, the evidence sources in lookup
order (Joe's sent mail, thread replies, [[WORKLIST]], [[CHANGELOG]]).

1. Every field is filled with an allowed value (Is task: Yes, No or Unsure;
   Route: Radar, Instruct front line or Joe direct).
2. Assumptions are yes/no questions; 1 to 4 of them.
3. The Check date is the source date plus 3 days, or plus 1 day for a crisis
   item (Route 3 money-or-deadline test).
4. Actual cites its evidence by key and ID, found in lookup order.
5. The Score follows the scoring rule in the prediction-ledger skill.
6. No question was asked about a subject that has evidence.

## pricing-prep

A quote preparation, price candidate or cost bridge. Preparation only: no price
leaves PCOS without Joe.

Required: the Live pricing rows in [[RULES]] (until they are rows: [[CANON]]);
the cost documents named on the task row; [[DECISIONS]] for rulings.

1. Every number traces to a source with its key and ID.
2. Markups, floors and buffers come from the cited rule rows by number, never
   from memory or from an older draft.
3. Units are consistent (per piece, per area, per lot), and every conversion is
   shown.
4. No component is counted twice when a price already bundles it.
5. The result is labeled Candidate and Needs Joe Approval, and names the
   approval step.
6. Nothing is sent, quoted or entered in any system.

## research-raw

A RAW research file (domain research runs, P2-15).

1. One sub-topic per file, with a date in the title.
2. Sources listed with URLs and access dates. Verbatim quotes only where quoting
   is allowed; paraphrase otherwise, marked as such.
3. No REFINED claims: no recommendation stated as fact, no "we should".
4. The folder's `_INDEX.md` has the file's line, written in the same run.
5. Status Candidate.

## knowledge-claim

A Knowledge row.

Required: the source behind the Source ID.

1. One atomic claim per row.
2. Type is rule, fact, method, decision or open question.
3. The Source ID resolves, and the source states the claim.
4. Source date is the source's own date, not the run date.
5. Status is Candidate at extraction.
6. No duplicate of an existing row for the same source.

## council-final

The Final and Dissent of a Council row (board or GitHub council).

Required: both reviews (the [[COUNCIL]] row's review fields; for the GitHub
council, the two reviews on the pull request), or one review when the chair
decided after the full-cycle wait (council-board skill section 6); the sources
the Draft cites.

1. The plan round was Final before execution started.
2. Both reviews are present, one finding per bullet, each with evidence and a
   verdict. After the full-cycle wait, one review is enough when Dissent says
   "Review-N missing" for the other; it then meets the same standard.
3. The chair answered each Fix or Reject finding: accepted, or rejected with a
   reason.
4. Dissent records each disagreement that is still open.
5. Needs Joe is used only for a factual disagreement that the kernel and the
   sources cannot settle.
6. The reviewers worked from the Reviewer view (Author hidden).

## rule-candidate

A rule, kernel or skill candidate (weekly-evolve, knowledge-chair).

Required: the incident rows it cites ([[CORRECTIONS]], [[CHANGELOG]]);
[[GOLDEN_SET]] results.

1. A named incident plus evidence, or Joe's direct yes, is cited (L10).
2. Reason, source and the diff old to new are present.
3. It is a new version, and the old version is untouched.
4. The golden-set result old vs new is attached; promotion only if equal or
   better.
5. A rule Joe owns (the [JOE] sections of the brief rules, anything external) is
   not promoted without his recorded yes.

## repo-change

A card, skill or pcos_tools change in [[REPO]] (pull request).

1. A card has the six parts in order (`agents/CARD_TEMPLATE.md`).
2. A skill's frontmatter is valid: the name equals the folder name; the
   description says what the skill does and when to use it.
3. Sources are named by `[[KEY]]`, and every key exists in `agents/INPUTS.md`.
4. No business data: no Drive or Notion ID or link, no person's name or address,
   no price, customer, vendor term or mail text.
5. `python -m pytest -q` passes, including `tests/test_agents_skills.py`.
6. The version is bumped and the change note is written.
