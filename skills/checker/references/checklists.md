# Checker checklists, one per job type

Version v0.2, 2026-10-09. Loaded by [the checker skill](../SKILL.md) step 2.
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
- C5 Live text rules (`agents/CARD_TEMPLATE.md`, "Live rules for text Joe
  reads"), on every output Joe reads. Required: [[EMAIL_RULES]] for mail and
  message text; [[PEOPLE]] and the owner-map rows in [[RULES]] for names.
  (a) Every item code, SAP code, order number or Task ID stands with its plain
  description; a code alone is a FAIL. (b) Only when the run changed a Drive
  file: the change went through a "DRIVE WRITE:" row in [[INBOX]] for the Drive
  recorder, the file was not rebuilt as a copy, and no parallel list was started.
  (c) Only when the output holds mail or message text: it passes [[EMAIL_RULES]]:
  the language pass done, no sentence split or merged, a line breaks only right
  after a comma. (d) Every person is named as [[PEOPLE]] and the owner map
  resolve the name; where two people share a name, by address. A clause that
  does not apply to the output is PASS with the evidence "not applicable: no
  Drive write" or "not applicable: no mail or message text".

## mail-draft

A Route 2 instruction or a Route 3 reply drafted into Outlook (brief lane, EXO
front-line instruction or clarifying line, intake reply), or a commitments-lane
draft (item 10).

Required: the whole thread, every branch, including its terminal message
([[MAIL_INBOX]], [[MAIL_ROUTED]], [[MAIL_SENT]]); the owner-map rows in
[[RULES]]; [[DECISIONS]]; for a recurring report, Joe's last sent version;
for a commitments-lane draft, its [[COMMITMENTS]] row.

1. The route follows the evaluation order: Route 1 tests first, then Route 3
   criteria (name the one that fired), then Route 2 as the default.
2. No Route 3 when the terminal message of the thread is Joe's.
3. Route 2 is a new internal email to the owner from the owner map: one to three
   lines with the outcome, the deadline and "loop me only if". It is never a
   reply into an external chain.
4. Route 3 is a reply on the original thread, never a retyped new message.
5. Where two people share a name, the address is used, never the bare name.
6. Language and style follow the brief rules and [[EMAIL_RULES]]: the thread's
   language for that counterpart, the language pass by default, sentences whole,
   line breaks only right after a comma, sign-off "best regards", signature
   inserted, no duplicate typed sign-off.
7. A correction email to a team member uses observations with evidence per
   bullet, closes with "Please review below observations and let me know", and
   has no commands, no money commitments and no recalculated totals.
8. No price, payment, quantity or date promise to an external party.
9. It is in Drafts and not sent. At most 5 drafts per run.
10. A commitments-lane draft (commitments skill section 6) follows its own form
    instead of items 1 to 4: what Joe owes is a reply on the original thread,
    even when Joe's message is terminal, that delivers what the cited
    commitment promised and promises nothing new; what others owe is a new
    internal email, never a reply into an external chain, to the team member
    who owes it or to the front-line owner the owner map names. The commitment
    row it cites exists and is marked for the next card.
11. An EXO front-line instruction (exo skill section 8) follows its own form
    instead of items 1 to 4. It is the Route 2 exception: a reply on the exact
    source conversation, including an externally started conversation, matched
    by conversation ID and source message ID; To, Cc and Bcc contain only the
    intended internal owner addresses from [[PEOPLE]] and [[RULES]], with every
    representative, customer, vendor and other external address removed. If an
    internal-only recipient set cannot be proved, the only passing result is no
    draft and a Blocked step.
12. Its instruction body is one to three lines apart from the greeting and
    signature, and contains the outcome, the explicit deadline and the phrase
    "loop me only if" with a real exception. It greets the owner by person, uses
    we/us voice and [[EMAIL_RULES]], writes each item code with its plain
    description, selects the Outlook signature JOE BM and types no sign-off or
    signature. It is a draft, never sent. Never send it.

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

Required: the sources each line cites: the files, rows, commits or pull requests
listed under what changed, and the authority named under why.

1. All five fields are present: Task ID, what changed, why (reason and
   authority), next action, confidence. Files created are listed with title and
   ID.
2. One scope: business and personal content never share a DELTA.
3. A file name follows DELTA_YYYY-MM-DD_source_topic.md. No placeholder or
   no-change file.
4. The Why names its authority. A DELTA without a reason is not applied until
   the reason is recovered (L11).
5. Each line matches its sources, reopened in this run: every file, row, commit
   or pull request listed exists with that title and ID; what changed is what
   the source shows; the authority says what the Why claims; the next action
   follows from them. A line that a source contradicts, or that no source
   shows, fails.

## question-card

A CAL card, an EXO card, a retro card or a "What happened?" question.

Required: [[CAL_STANDARD]]; [[DECISIONS]]; Joe's replies in the chain and
[[MAIL_SENT]]; for EXO, the [[STEPS]] rows shown; for a retro item, the whole
thread in [[MAIL_INBOX]], [[MAIL_SENT]] and [[MAIL_ROUTED]] when the gap has
one, and the [[WORKLIST]], [[CHANGELOG]] and [[PREDICTION]] rows about it.

1. Every question passes CAL-R5: it is not already answered in Decisions, in
   Joe's replies or in a later reply.
2. One decision per question. Self-contained, in plain words, with the key
   facts, numbers and dates inside it; no internal ID without its meaning: every
   item code, SAP code, order number or Task ID with its plain description (a
   bare code is a FAIL).
3. 2 to 4 options, the recommended option first; options are concrete actions
   with owner and date where relevant; no "Other". A retro item has its six
   fixed tap options instead (item 7); a commitment item has the fixed options
   of the commitments skill section 7.
4. The "Not needed / wrong direction" option is present (the template adds it).
   A "What happened?" question also offers "unrelated / wrong direction".
5. EXO: 2 to 4 items (one when only one is open), assumption form unless no assumption is defensible, a
   progress line at the end, no overdue list and no count of late items; at
   most two commitment items, a Joe-owes item due within 48 hours first. A
   front-line instruction item names the owner, outcome and deadline and offers
   the three one-tap actions Approve / Edit / Skip; Approve explicitly leaves
   the draft in Drafts for Joe to send and never sends it. Edit says the
   accepted draft changes only after another checker Accept; Fix or Reject keeps
   the last accepted draft unchanged.
6. One Open row in [[DECISIONS]] for the card.
7. Retro: at most five items; the ledger's "What happened?" items first, then
   the open conflict items, then at most two commitment items, for which the
   card keeps room. A retro item is one line that sums up the thread
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
   the item is the ledger's own queued question; no [[COMMITMENTS]] row has the
   thread as Thread or the Worklist row as Linked task, unless the item is the
   commitments lane's own marked item. Matching is by identity, never by
   subject.

## prediction

A Prediction row or its scoring.

Required: the [[PREDICTION]] row; for scoring, the evidence sources of
prediction-ledger section 2: the row's whole conversation (Joe's sent mail in
[[MAIL_SENT]] and the replies in [[MAIL_INBOX]] and [[MAIL_ROUTED]], read
together), then [[WORKLIST]], then [[CHANGELOG]].

1. Every field is filled with an allowed value (Is task: Yes, No or Unsure;
   Route: Radar, Instruct front line or Joe direct).
2. Assumptions are yes/no questions; 1 to 4 of them.
3. The Check date is the source date plus 3 days, or plus 1 day for a crisis
   item (Route 3 money-or-deadline test).
4. Actual cites its evidence by key and ID, matched by the row's Source
   identity. For mail, the sent messages and the replies were read together as
   one conversation, and Actual rests on the terminal message (Law 3): Joe's
   sent message counts only while no later reply follows it. An Actual taken
   from a sent message that a later reply overtakes fails.
5. The Score follows the scoring rule in the prediction-ledger skill.
6. No question was asked about a subject that has evidence.
7. A "What happened?" answer that settles a Worklist task (handled offline or
   dropped, Scored or Parked) filed one [[INBOX]] row for the closeout owner.

## prediction-backtest

One thread of a ledger-backtest run and its score (prediction-ledger skill,
references/backtest.md). Never checked with the `prediction` checklist: the
backtest scores by its own rule.

Required: the thread's line in the run report; the whole conversation in
[[MAIL_SENT]], [[MAIL_INBOX]] and [[MAIL_ROUTED]], before and after the cut;
the owner map as rebuilt for the cut (backtest section 2).

1. Blind at the cut: the prediction uses no message, Worklist or Changelog row,
   or owner assignment dated after the cut.
2. Every field is filled with an allowed value (Is task: Yes, No or Unsure;
   Route: Radar, Instruct front line or Joe direct); Assumptions are 1 to 4
   yes/no questions.
3. The outcome is conclusive and rests on the terminal message (Law 3), cited
   by message ID.
4. The Score follows backtest section 3, not the live rule of skill section 4:
   Is task, Owner and Route compared with the outcome; Candidate output 1 when
   the output type matches what happened, else 0 ("used unedited" does not
   apply); only the assumptions the outcome settles are scored.
5. Nothing was asked of Joe, and no [[PREDICTION]] row was written for the
   thread.

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
5. The result carries exactly one evidence label, Needs Joe Approval (a price
   is committing), and names the approval step. That it is still a preparation
   is recorded as its status, never as a second label.
6. Nothing is sent, quoted or entered in any system.

## research-raw

A RAW research file (domain research runs, P2-15).

Required: every source the file cites, opened by its URL in this run.

1. One sub-topic per file, with a date in the title.
2. Sources listed with URLs and access dates. Verbatim quotes only where quoting
   is allowed; paraphrase otherwise, marked as such. Each substantive claim and
   each quote matches the cited source as opened in this run. A source that
   cannot be opened is Blocked; a claim or quote that no opened source supports
   fails.
3. No REFINED claims: no recommendation stated as fact, no "we should".
4. The folder's `_INDEX.md` has the file's line, written in the same run.
5. Status Candidate.

## knowledge-claim

A Knowledge row.

Required: the source behind the Source ID.

1. One atomic claim per row.
2. Type is rule, fact, method, decision or open question.
3. The Source ID resolves, and the source supports the claim with the right
   evidence label: a claim labeled Confirmed is stated by the source; a claim
   that needs inference is labeled Candidate and follows from what the source
   states. A claim the source does not support fails, and so does an inferred
   claim labeled Confirmed.
4. Source date is the source's own date, not the run date.
5. Status is Candidate at extraction.
6. No duplicate of an existing row for the same source.

## council-final

The Final and Dissent of a Council row (board, GitHub or PC council).

Required: both reviews (the [[COUNCIL]] row's review fields; for the GitHub
council, the two reviews on the pull request; for the PC council, the
run's `bundle.md`), or one review when the chair decided after the full-cycle
wait (council-board skill section 6); the sources the Draft cites.

1. Board council: the plan round was Final before execution started. GitHub
   council: there is no plan round (one pull request carries the draft, the
   reviews and the Final), so this check does not apply. PC council: there is
   no plan round (one live run), so this check does not apply.
2. Both reviews are present, one finding per bullet, each with evidence and a
   verdict. After the full-cycle wait, one review is enough when Dissent says
   "Review-N missing" for the other; it then meets the same standard. PC
   council: every seat that answered reviewed the answers it did not write;
   Dissent names each seat without an answer and each missing review.
3. The chair answered each Fix or Reject finding: accepted, or rejected with a
   reason.
4. Dissent records each disagreement that is still open.
5. Needs Joe is used only for a factual disagreement that the kernel and the
   sources cannot settle.
6. The reviewers did not see the author. Board council: they worked from the
   Reviewer view (Author hidden). GitHub council: the pull request names no
   author model (council-github card section 5), and neither reviewer is the
   drafting model. PC council: the chair worked from the bundle (letters, no
   seat names), wrote no answer itself, and filled Author only after Final and
   Dissent (council-pc skill section 4).

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
