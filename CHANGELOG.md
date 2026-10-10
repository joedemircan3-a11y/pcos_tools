# Changelog

## Unreleased - 2026-10-10: EXO task distribution v0.1

Why: PCOS queue item QX30 (QUEUE_v12; renamed from QC30 in QUEUE_v10), Joe's
development-list request "task distribution by EXO". EXO already broke work
into steps for Joe but did not turn a front-line owner's step into an instruction,
put it in Joe's Drafts or watch for the answer. Built by Codex from main 106d794.

- `skills/exo/SKILL.md` v0.3: every step assigned to a front-line owner becomes
  a checked Outlook reply draft on the exact source conversation. The recipient
  gate removes every representative, customer, vendor and other external address
  from To, Cc and Bcc; an unprovably internal draft fails closed.
- Instruction form: one to three body lines with the outcome, explicit deadline
  and "loop me only if ..."; `[[EMAIL_RULES]]`, greeting by person, we/us voice,
  item codes with plain descriptions, Outlook signature JOE BM and no typed
  sign-off. EXO never sends.
- The card gives the front-line instruction three one-tap actions: Approve keeps
  the checked draft in Drafts for Joe to send; Edit checks and updates that same
  draft; Skip leaves it unsent and the step open.
- Distribution state waits for evidence: Approved until the exact message appears
  in Sent, Awaiting owner after that, Answered only by a later reply from the
  intended owner on the same conversation that answers the outcome, and Overdue
  after the explicit deadline without one. Subject matches and silence prove
  nothing; the Worklist task is not closed here.
- `agents/exo.md` v0.5 and `routines/exo.md` v0.6 carry the same recipient, draft,
  card and watch rules. The mail-draft and question-card checker lists enforce
  them.
- `tests/test_exo_task_distribution.py` uses mocked internal, external, sent and
  replied mail to pin the recipient filter, no-send approval, exact conversation
  identity and Answered/Overdue evidence rules.
- Codex review, round 1: the EXO threaded reply is an explicit exception to the
  generic Route 2 new-message rule after its recipients pass the internal-only
  gate; Approve/Edit/Skip branch before the generic answer transition, so Skip
  cannot mark a step Answered or queue dependent work.

## Unreleased - 2026-10-09: rules and clock v0.1

Why: PCOS queue item QC28 (QUEUE_v10), from two requests on Joe's development list:
"new rules into the kernel and every lane" and "one clock for every lane". Four live
Rules rows (item codes with a description, one home per record, the email rules
v4.1, person names) bound only the EXO lane, and the lanes ran on two clocks one
hour apart until 2026-11-01. Built by Claude (Claude Code on the web) from main
4a78c92.

- `agents/CARD_TEMPLATE.md` v0.2: section "Live rules for text Joe reads", the four
  rules with their sources; every card inherits them and the one clock.
- Every card in `agents/`: part 4 states the four rules as one "Live text rules"
  line; times on America/Mexico_City.
- Every Routine prompt in `routines/`: a TEXT RULES paragraph right after LOAD (after
  the key load, so the council-github chair's GitHub-only filter stays key-free).
  L1 drafts follow `[[EMAIL_RULES]]`; L2 shows codes as TASK-ID (DESCRIPTION) and
  keeps each mirror in one file through the Drive recorder instead of new copies.
- One clock: Joe's Outlook calendar is in "Central Standard Time (Mexico)", read
  through the Microsoft 365 connector, so every Routine runs on
  CRON_TZ=America/Mexico_City. exo, retro, commitments and commitments-backfill
  keep their wall-clock times (from America/Matamoros); L4-weekly `0 15 * * 0` UTC
  becomes `0 9 * * 0` and ledger-backtest `0 13 * * 0` UTC becomes `0 7 * * 0` (the
  same instants); council-github-chair names the zone on its 2-hour cron.
- Checker: common check C5 (the four rules on every output Joe reads); mail-draft
  item 6 names `[[EMAIL_RULES]]`; question-card item 2 fails a bare code. Checklists
  v0.2, checker skill 0.2.
- `agents/INPUTS.md` v0.4: key `EMAIL_RULES`.
- Codex review, round 1: the Drive recorder lane that applies "DRIVE WRITE:" rows
  (installed 2026-10-08 outside this repository) is listed in `routines/_INDEX.md`
  and named as L2's dependency for its mirrors, so no lane hands writes to a
  consumer the repository does not show.
- Codex review, round 2: keys `NOW_MIRROR` and `KERNEL_MIRROR` (planned, at cutover)
  for L2's two mirrors; the first render records each file's ID under its key, later
  renders name the key in their "DRIVE WRITE:" rows; the L2 heartbeat counts the
  queued rows and logs each in the Changelog.
- Codex review, round 3: check C5's Drive clause applies only to a run that changed
  a Drive file and its email clause only to mail or message text (a clause that does
  not apply is PASS, not applicable), so outputs without either can still be
  accepted; L2 replaces an open "DRIVE WRITE:" row for a mirror with the newest text
  instead of queuing a second one.
- `tests/test_rules_and_clock.py`: fails when a card or Routine drops the rules,
  when an output template shows an item code without a DESCRIPTION slot, or when a
  Routine, card or skill names a time zone other than America/Mexico_City.
## Unreleased - 2026-10-09: PC council isolation v0.2 (P2-08, issue #6)

Why: PCOS queue item QC27 (QUEUE_v9) closes issue #6, the QC22 follow-up:
the Codex seat could read any file on Joe's PC through its shell, and what it
read would go to OpenAI and, in its answer, to the other seats. The gap had to
close before the first live council run. Built by Claude (Claude Code on the
web) from main 4a78c92.

- Checked against codex-cli 0.162.0, the version on Joe's PC, by running
  the Linux build against a mock model: with the old flags
  (`--sandbox read-only --disable apps`) a `cat` of a file outside the work
  folder returned the file to the model. `codex exec` has a switch the issue
  missed: `--disable shell_tool` removes `exec_command` and `write_stdin`,
  also inside its JavaScript tool and in the agents it spawns;
  `--disable view_image` removes the image reader. With both, the same reads
  fail ("tools.exec_command is not a function", "unsupported call").
  `unified_exec` cannot be turned off in 0.162.0 and needs no flag. An
  unknown feature name stops codex with an error, so a renamed flag fails the
  seat instead of giving it a shell back.
- `scripts/council_pc.py`: the Codex seat runs with `--disable shell_tool`,
  `--disable view_image`, `--ignore-user-config` and `--ephemeral`. Every
  call of every seat runs in a new temporary folder that holds only
  `brief.md`, with HOME, USERPROFILE, CODEX_HOME, CLAUDE_CONFIG_DIR,
  GEMINI_CLI_HOME and the XDG folders pointed at a scratch home that holds
  only a copy of that CLI's sign-in file (Codex `auth.json`, Claude
  `.credentials.json`; Gemini gets `GEMINI_API_KEY` from the environment or
  `~/.gemini/.env`). A sign-in the CLI refreshed during the run is written
  back, but only as complete JSON and only when the real file did not change
  meanwhile; `run.json` notes it under `sign_in`, and also a sign-in file
  that was not found.
- Residual risk (Candidate, in issue #6): Codex keeps `apply_patch`, which has
  no switch. The read-only sandbox and the approval policy stop it from
  writing, and it returns no file content, but its error shows whether a
  guessed line is in a named file. The Windows build was not run here; the
  skill's pre-run check (`codex --disable shell_tool --disable view_image
  features list`) confirms the flags on Joe's PC.
- `skills/council-pc/` v0.2 and `agents/council-pc.md` v0.2: the isolation,
  the pre-run check, the residual risk, and a Never line against a `--seat`
  override that gives a seat back a tool that reads files.
- `tests/test_council_pc.py`: the mocked CLI records its working folder, its
  home and its environment; tests assert the folder holds only the brief and
  is new for every call, the scratch home holds only the seat's own sign-in
  (no settings, MCP servers, history or business files), the Gemini key
  source, the write-back (also after a timeout) and that a torn or
  concurrently changed sign-in is never written over a good one. Each test
  run uses a stand-in home, never the tester's own sign-ins.
- Codex review, round 1 (P2): the write-back compared the real sign-in file
  before writing its temporary copy, so a refresh by another process during
  that write could be overwritten. The temporary copy is now prepared first
  and the comparison runs last, right before the replace. Neither CLI offers
  a lock to share, so a refresh in that one instant is the only write that
  could still be lost.
- Codex review, round 2 (P2): the staging file had a fixed name
  (`auth.json.council-pc`), so two council runs writing back the same
  sign-in at once could overwrite or delete each other's staged token. Each
  write-back now stages in a temporary file of its own next to the real one.
- Codex review, round 3 (P2): (1) the seats inherited variables that make a
  CLI read a file into its prompt or join an IDE that shares open files
  (`GEMINI_SYSTEM_MD`, `GEMINI_CLI_SYSTEM_SETTINGS_PATH`, `GEMINI_CLI_IDE_*`,
  `CLAUDE_CODE_SSE_PORT` and others, checked in each CLI). No seat inherits
  them now, and `CLAUDE_CODE_DISABLE_CLAUDE_MDS=1` keeps Claude from reading a
  CLAUDE.md in the folders above the working folder. (2) The Gemini key in
  `~/.gemini/.env` is read as dotenv reads it, so a quoted value with an
  inline comment works. Per the stop rule this is the last Codex round.

## Unreleased - 2026-10-09: PC council v0.1 (P2-08)

Why: PCOS queue item QC22 (QUEUE_v4, carried to QUEUE_v8) builds the live
council on Joe's PC that Joe accepted on 2026-09-28 (dev-session record of
2026-09-27, turns 2 and 3: Mechanism B). Codex and Gemini CLIs were installed
on his PC at PC-1; the skill was the missing piece. Built by Claude (Claude
Code on the web) from main 98a1943.

- `scripts/council_pc.py`: one brief to three seats at once, `codex exec`
  (read-only sandbox), `gemini -p` and `claude -p` (a separate Claude process,
  so the chairing session writes no answer), each in an empty temporary
  folder with the prompt on stdin (a Windows `.cmd` shim caps the command
  line). A 503 or overload answer is retried twice (20 and 40 seconds); other
  failures, timeouts and missing CLIs are not retried, and the run goes on
  without that seat. A timeout kills the CLI's whole process tree (a Windows
  `.cmd` shim's node child would otherwise keep the pipes open). Self-identification is removed (model and vendor names
  only when the brief does not use them), the answers are shuffled under the
  letters A, B and C, and every seat that answered reviews and ranks the
  answers it did not write. Output: `bundle.md` for the chair (letters only,
  a pairwise ranking table), `authors.json` and `run.json`. Fewer than two
  answers is Blocked (exit 3, no bundle). Standard library only; it writes
  nothing outside the new run folder.
- `skills/council-pc/` and `agents/council-pc.md`: the brief (facts quoted
  with keys and IDs, since the outside models open nothing; what leaves the
  PC), the run, the chair (council-board section 5 from the bundle alone;
  Author filled only after Final and Dissent; one Needs Joe question asked in
  the session), the Council row write behind the checker's Accept, and the
  Never list. On demand only: no Routine file.
- Codex review, round 1: the seats start without the chair session's
  `CLAUDECODE` marker, since some Claude Code versions refuse `claude -p` as a
  nested session and the Claude seat would always fail.
- Codex review, round 2: self-identification is removed even when the brief
  names the model or vendor ("As an OpenAI model, ...", "Claude here:", "This
  is Gemini speaking", "I, Claude, ...", signature lines), while content
  mentions stay ("such as Gemini", "As Claude suggested"); reviewers and the
  chair ignore a name that slips through. The skill's data-flow note names
  Anthropic too, and says each vendor receives the other seats' answers in
  the review stage.
- Codex review, round 3: the seats' host tools are off (Claude `--tools ""`
  and `--strict-mcp-config`; Gemini a policy file that denies every tool;
  Codex its read-only sandbox and `--disable apps`; flags checked against
  codex-cli 0.162.0, gemini 0.63.0 and Claude Code 2.1.295). Codex has no
  switch for its shell, so a file read stays possible there: an open risk
  for Joe and a codex-followup issue. A self-introduction loses only its
  identity clause ("I am Claude, and Plan A is best" keeps "Plan A is
  best"). "Undefeated" needs every comparison of the answer; missing
  comparisons are listed in the bundle.
- Main (34768f5, the commitments lane of QC24) merged in: the card reads
  [[REGISTRY]] before any question reaches Joe, as QC24's rule asks of every
  card that can ask him, and the chair searches it before Needs Joe.
- `skills/checker/references/checklists.md`: council-final covers the PC
  council (no plan round, cross-reviews, the chair worked from letters).
- The indexes list the new card and skill; the README names the runner.
  `tests/test_council_pc.py` runs the script against a mocked CLI (answers,
  reviews, 503s, failures, timeouts, the last-message file) and pins the
  skill's fixed parts.
## Unreleased - 2026-10-09: Commitments lane v0.1 (P2-31)

Why: PCOS queue item QC24 (QUEUE_v6, amended in QUEUE_v7). Joe, 2026-10-06: the
mail he receives and sends commits to deadlines and tasks, but they do not turn
into tasks, and nothing checks their status, asks him about them or pulls him to
finish them. The auditor confirmed the gap: L1 triages incoming mail and the
prediction ledger scores incoming items, but no lane extracts commitments from
sent mail, keeps a due date or follows up. Built by Claude (Claude Code on the
web) from main 98a1943.

- `skills/commitments/` and `agents/commitments.md`: one Commitments row for
  every promise Joe makes in sent mail (with or without a date), every dated
  ask he makes, and every dated ask or promise to him in incoming mail with Joe
  in To
  (Commitment, Direction, Counterparty, Due, Thread, Source message, Status,
  Evidence, Linked task, Draft link, Next check; Card and Skips for the card
  hand-off). Due dates are read from the words of the mail in the sender's time
  zone, by a fixed table; a vague word leaves Due empty with a check two
  business days out. Threads by conversation ID with the References /
  In-Reply-To fallback, never by subject; dedupe by thread plus deliverable.
  Rows close only on evidence: delivery shown by the thread (its terminal
  message controls), the linked Worklist row Done, or Joe's answer.
- Follow-up through the cards Joe already answers, never a list: at most two
  commitment items per card. What Joe owes and is due within 48 hours is the
  first item of the next EXO card, with a checked reply draft when a reply is
  the deliverable; overdue items get one item each, owed-to-Joe and team-member
  items with an internal follow-up draft; team-member items surface only once
  overdue; more than 14 days overdue goes to the evening retro card as a past
  question. The EXO skip rule applies. Drafts only, never sent.
- `routines/commitments.md` (weekdays 06:40, 12:40, 18:40 America/Matamoros)
  and `routines/commitments-backfill.md` (once: the last 30 days of sent mail,
  fed to EXO two at a time through the regular runs).
- EXO (card v0.3, skill v0.2, Routine v0.4) and retro (card v0.2, skill v0.2,
  Routine v0.2) show the marked rows and file the answers into the
  Commitments row; a thread with a Commitments row is never a retro gap. The
  checker's mail-draft and question-card checklists cover the new drafts and
  items.
- `agents/INPUTS.md` v0.3: keys `COMMITMENTS` (planned; QW21 creates the
  database) and `REGISTRY` (the operating document registry, in the kernel key
  map since kernel 1.2). Every card whose lane asks Joe now reads
  `[[REGISTRY]]` before a question reaches him (kernel 1.2 section 2 step 4;
  the QK23 open point): checker, council-board, council-github, exo,
  intake-email, knowledge-chair, prediction-ledger, retro, weekly-evolve and
  commitments.
- `tests/test_commitments_lane.py`.
- Codex review, three rounds under the QUEUE_v7 stop rule (round 1, then two
  after the first fix pass), nine findings (1 P1, 8 P2), all fixed with tests:
  every promise Joe makes is tracked even without a date; a refusal by the
  party who owes drops the row; the index rows keep their width (a test now
  checks every index row); an approved draft or step waits off the cards
  without inventing a date, overdue follow-ups included; the retro card keeps
  room for commitment items; a row without a Due never reaches a card before
  its Next check; a later message that reopens a deliverable reopens its row;
  EXO shows a lone item when only one is open.

## Unreleased - 2026-10-06: Retro lane v0.1 (P2-30)

Why: PCOS queue item QC19 (QUEUE_v4) builds the Retro lane that Joe accepted:
an evening card of five questions about the past, which he answers easily
("past is just remembering"), last 90 days first, plus a backtest of the
prediction ledger over the same 90 days of mail. Built by Claude (Claude Code on
the web) on top of pull request 2, because the Routines it changes exist only
there. Changed cards are bumped; skill versions stay 0.1.

- `skills/retro/` and `agents/retro.md`: the gap query (threads and Worklist
  items of the last 90 days with no closure evidence), the order (recency in
  weeks, then open value, then pattern class), the gate (the full thread chain
  and every later reply are read before any question, and nothing the record
  answers is asked), the five-item card with its six tap options, the filing
  (Prediction rows; People candidates through the closeout owner; golden-set
  candidates as Corrections rows, which weekly-evolve turns into cases; a
  Decision row when Joe's memory and the record disagree; the mail is never
  touched), and the EXO skip rule.
- `routines/retro.md`: daily 18:53 America/Matamoros, the evening slot that
  the EXO Routine gives up. `routines/exo.md` now runs at 07:00 and 13:00 only.
- Past questions have one home: the prediction-ledger lane's "What happened?"
  questions move from the EXO cards to the evening retro card (ledger card
  v0.4, skill section 3, Routine step 5; EXO card v0.2, Routine step 6). Why:
  Joe's decision "evening = past questions, morning and midday = today", and
  one card that owns every past question cannot ask about a thread twice.
- `agents/ledger-backtest.md`, `routines/ledger-backtest.md` and
  `skills/prediction-ledger/references/backtest.md`: the ledger's predictor
  runs blind at the cut over threads of the last 90 days whose outcome the mail
  shows, scored without asking Joe, at most 200 threads per run, once at
  install and then on Sundays before L4. One Prediction row per class of ask,
  kept out of the live mean (skill section 5 says so).
- `skills/checker/references/checklists.md`: the question-card checklist covers
  retro items (six tap options, the read-everything gate).
- Codex review, round 1: the backtest rebuilds the owner map as it stood at
  the cut (a later owner would leak into Owner, Route and output); a class
  item files and counts every thread it covers; the ledger settles a row
  without a prediction without scoring it; the CAL template's own "Not
  needed / wrong direction" is the sixth tap option, never a seventh.
- Codex review, round 2: earlier questions and rows match a gap by identity,
  never by subject; a later thread answers a gap only when it concerns the
  same ask; a gate catch is filed with its identity in Source; "moved
  offline" never guesses a channel; an unmatched free-text answer is Parked;
  the checker's backtest sample is min(10, threads scored).
- Codex review, round 3: the Never list and the checker match a gap by
  identity too, so no subject-based veto is left; at three skips the
  last-chance "Keep this open, or let it go?" item is shown before any row
  parks the gap (a Parked row would have hidden it).
- Codex review, round 4: the backtest undoes owner-map changes newest first;
  a thread and the Worklist row that names it are one gap with both
  identities, never two questions.
- Codex review, round 5: a gap with no thread (a Worklist row alone) is
  summed up from the row, and "closed as quoted" means done as its Next
  Action planned; a row with a Reshaped EXO step stays EXO's; the checker
  checks every identity a gap carries.
- Codex review, round 6: every answer that settles a Worklist-covered gap
  reaches the closeout owner as an Inbox row; the checker accepts a gap
  with no thread (row summary, row and its sources read).
- Codex review, round 7: a gate catch on a Worklist row reaches the
  closeout owner; Inbox, Corrections and Decision rows are filed once per
  gap, only the Prediction write repeats per identity; an explicit "keep"
  on the last-chance item is handed on like "still open".
- Codex review, round 8 (fixed in the QC19-R retry): a Done-Candidate
  Worklist row is closed, never a retro gap, and any closed status counts as
  closure evidence; a "What happened?" answer of handled offline, Scored or
  Parked, now hands a Worklist task to the closeout owner as dropped already
  did (prediction-ledger skill section 3, checker `prediction` item 7).
- Codex review, round 9: the backtest sample is checked with its own
  checklist, `prediction-backtest`, which scores by the backtest's rule
  (output type; settled assumptions only), never the live one; an item that
  reaches the ledger through an Inbox row or DELTA line counts as a Worklist
  task when that row names a Task ID.
- The three indexes list the new cards, skill and Routines.
  `tests/test_retro_lane.py` pins the lane's fixed parts: 61 new tests; with
  main merged in (pull requests 1 and 2 and the QC18-R fixes), 410 pass.

## Unreleased - 2026-10-06: Codex review fixes, retry (PR 1 and PR 2)

Why: PCOS queue item QC18-R (QUEUE_v6) fixes the four Codex findings left open on
pull request 1 when QC18 hit its time box. Built by Claude (Claude Code on the web).

- Checker `prediction` checklist: the sent mail and the replies are read together
  as one conversation and Actual rests on the terminal message, as in the
  prediction-ledger skill section 2; the old sent-mail-first lookup order is gone.
- Prediction ledger: a "handled offline" answer scores the row only when the
  answer, Joe's note and the evidence settle every guess (Owner, Route, Candidate
  output, each assumption); otherwise the row is Parked with Actual kept and the
  weekly calibration scores it later. The note under that option asks who handled
  it and whether the draft was used (prediction-ledger card v0.3).
- Checker `knowledge-claim` checklist: an inferred claim passes when it is labeled
  Candidate and follows from the source, matching the knowledge-extract card; an
  inferred claim labeled Confirmed fails.
- Council-github card v0.3 and the `council-github-chair` Routine (step 3): the
  chair finds the Council row by the pull request's link in the row's Draft field,
  never by Task title; no bound row, or more than one, is Blocked.
- Checker `council-final` check 6 covers the GitHub council: there the pull
  request names no author model and neither reviewer drafted; the Reviewer view
  applies to the board council only.
- Checker `pricing-prep`: the result carries exactly one evidence label, Needs Joe
  Approval; being a preparation is its status, not a second label.
- Checker `delta`: the sources each line cites are required, reopened and
  compared; a line that a source contradicts or no source shows fails.
- Checker golden set, lane run: a case passes only when the output satisfies Joe's
  correction and the checker's overall verdict is Accept, so a fix that adds a
  new failure or hard stop cannot be promoted.
- Checker `council-final` check 1 (plan round) applies to the board council only;
  the GitHub council has no plan round.
- Checker `research-raw`: the cited sources are required and opened by URL; each
  claim and quote must match an opened source.
- Routines (Codex review of PR 2): L1-brief v0.4 resumes from the window end in
  its last heartbeat, so mail beyond the 5-day cap is read by later runs and never
  dropped; L2-render v0.4 keeps every open Needs Joe row on Today, however old, and
  links the rest in the Inbox when they do not fit in 12 lines;
  council-github-chair v0.9 ends a council only on its own "Chair: Final", counts
  only reviews tied to the current head commit (Codex by commit, Gemini by its
  Action run), re-checks the head before writing and again before posting, and
  restores missing Changelog rows before replaying a Final.
- Tests: the private-ID guard also flags runs of 25 characters or more with two of
  the three character classes, or with no "-" or "_" (Drive IDs are 28 or more), so
  an ID without a digit or without mixed case is caught; public names on the
  reviewed list stay allowed. One test per fix, each failing on the old text.

## Unreleased - 2026-10-06: Codex review fixes (PR 1 and PR 2)

Why: PCOS queue item QC18 (QUEUE_v4) applies the six Codex review suggestions on
pull request 1, recorded at PC-1 (DELTA_PC-1 step B3). Built by Claude (Claude
Code on the web). Card versions are bumped where a card changed; skill versions
stay 0.1 because the skills are not released yet.

- Golden set: the lane run now scores whether a lane's output satisfies Joe's
  correction; a separate checker run scores the checker on the case's Wrong
  output and on known-good outputs, which it must Accept. Before, a version that
  kept the defect passed and a version that fixed it failed. Checker card v0.2;
  checker and weekly-evolve skills follow.
- Prediction ledger: items match by identity (thread conversation ID, Inbox row
  ID, or DELTA file ID with the Task ID), never by subject, so two unrelated
  items with one subject get two rows. Evidence is matched the same way; a
  subject-only match counts only when it is unique, and only as Candidate.
  Mail is read as the whole conversation: Joe's sent message counts only while
  it is the terminal message (prediction-ledger card v0.2). A row left with only
  nonconclusive evidence after the extra wait is Parked, not stranded, and so is
  a blind row whose subject another row already covers.
- Intake-email skill: a sender off the allowlist, a stop-list ask or a checker
  failure keeps the row at Needs Joe; Drafted only when the Door 1 rule alone is
  missing.
- Prediction ledger: a Parked row is never asked again; new evidence or Joe's
  own action reopens it, and the weekly calibration re-checks Parked rows.
- Knowledge chair card v0.2: Status Duplicate for claims a review finds to
  repeat an earlier row (needs the Status option in the Knowledge database).
- Checker `council-final` checklist: one review is enough after the full-cycle
  wait when Dissent names the missing review, so the documented fallback can
  pass.
- Knowledge-extract card v0.2: model fixed at Claude Sonnet, so the Claude
  Review-2 (Opus) is never the extracting model; the evidence label is kept
  apart from Status (a claim the source states is Confirmed evidence, Status
  Candidate until the chair decides).
- `agents/INPUTS.md` v0.2: one key per domain folder, `KL_00` to `KL_07`;
  `KL_DOMAINS` is a group of those keys; `MAIL_ROUTED` documented as the one set.
- Tests: the private-ID guard now covers Drive IDs that contain `-` or `_`: every
  run of the URL-safe alphabet with both cases and a digit fails, except a short
  list of public folder names kept in the test. Notion IDs and UUIDs are caught
  in upper or lower case. One test per fix above. 219 tests pass, 1 is skipped.
- Routines (Codex review of pull request 2, same queue item):
  - L1, L2 and L3 read their lane card (`agents/L1-brief.md` and so on) in
    LOAD once P2-19 writes it; L4 reads every card in its header and runs both
    golden-set runs.
  - council-board chair: the Reviewed-2 arm needs both review fields, so a row
    with a missed Review-1 waits the full cycle of skill section 6.
  - council-github chair: a schedule every 2 hours runs the missing-review
    fallback, which no event would otherwise wake. The fallback chairs only
    with exactly one review; with none it files one Blocked Inbox row and a
    scheduled run goes on to the next pull request. A pull request that
    already has a Final is not chaired again.
  - knowledge-extract: a claim is written only after a checker Accept, and the
    Routine runs Claude Sonnet, apart from the Opus Review-2.
  - council-board chair: the Final is written only after a checker Accept;
    after five failed rounds the row keeps its Status and Joe gets one card
    item (Needs Joe stays for factual disagreements). The council-github
    chair runs the same check before it posts a Final, with the pull
    request's reviews as the checklist's reviews; it writes and reads back
    the Council row before posting, and repairs a run that failed in between
    (same head commit only). It acts only on pull requests from the
    repository owner's account on a branch of this repository that are bound
    to their Council row, and it loads the key map before any Notion access.
  - Every Routine that names the checker loads `skills/checker/SKILL.md`
    (council-board chair, exo, intake-email, prediction-ledger added).
  - L3 Health: the stale-kernel check looks at the last 24 hours only.
  - L1: a thread is skipped only when a row already has its current terminal
    message; a newer terminal message gets a new row that names the earlier one.
  - prediction-ledger: a Parked row is never asked again.
  - Tests: every Routine prompt reads the cards in its header (except the
    anonymous Review-2), has a schedule and numbers its steps in order; the
    chair's queue needs both reviews. The public-name list adds the dispatch
    file name the routines cite. 325 tests pass, 1 is skipped.

## Unreleased - 2026-10-01: agent cards and skills v0.1

Why: PCOS queue item Q01 (PCOS_DISPATCH_2026-09-29 PROMPT C1, register P2-19,
P2-03, P2-01, P2-02) puts the phase-2 agent cards and the first skills in this
repository, so that build day installs them instead of writing them. Built by
Claude (Claude Code on the web, session_01Urw9UiZSQ2c6DofLwbgk1t). The
`pcos_tools` package is unchanged and stays at 0.3.0.

- `agents/`: `CARD_TEMPLATE.md` (six parts: mission, inputs by ID, tools,
  rules and kernel version, output contract with the Law 4 evidence labels,
  trigger and owner model), `INPUTS.md` (46 source keys), `_INDEX.md`, and one
  card for each planned lane: prediction-ledger, exo, checker, council-board,
  council-github, intake-email, weekly-evolve, knowledge-extract,
  knowledge-review, knowledge-chair.
- `skills/`: checker (with checklists for 12 job types), prediction-ledger and
  exo, in the Agent Skills format; `_INDEX.md`.
- Sources are named by key. The Drive and Notion IDs stay in a private Drive map.
  Why: this repository is public (Operating Card v7.4: never put real business
  data in it), and one map means one line to change when a governance file is
  superseded and its ID changes.
- `tests/test_agents_skills.py`: card parts, skill frontmatter, keys, links,
  and a guard against private identifiers. 171 tests pass (was 116), 1 is
  skipped.
- `scripts/build_zip.py` also ships `agents/` and `skills/`, so the test suite
  passes when it is run from the zip.
- Queue item Q08 (dispatch batch 3, C4; register P2-06, P2-09, P2-05) added
  three skills:
  - `council-board`: plan and execution rounds; anonymous reviews in which
    Review-2 writes before it reads Review-1; chair rules. The stage prompts
    are in `references/prompts.md`.
  - `intake-email`: allowlist check, stop list, sourced answers, reply drafts
    with Joe in cc, and a send gate. Mail content is treated as data.
  - `weekly-evolve`: candidates with reason and diff, new golden-set cases,
    the equal-or-better gate (no category may drop), and the three weekly
    numbers.
  The four cards that use these skills link them and moved to v0.2. 182 tests
  pass, 1 is skipped.
- Queue item QC13 (register P2-07, P2-19), in its own pull request
  "repo-structure-v0.1", stacked on this one:
  - The README now opens with what the repository holds and how PCOS points
    here. The toolkit manual follows, unchanged.
  - `routines/` holds 13 paste-ready Routine prompts, one file each:
    L1 Brief, L2 Render, L3 Health, L4 Weekly, the council-github chair,
    prediction-ledger, exo, the three council-board stages, intake-email,
    and two knowledge Routines that are blocked until their skills exist.
    Each prompt is a loader (kernel, then card, then skill, then key map).
    `_INDEX.md` also lists the scheduled lanes that are not Claude Routines.
  - `.github/pull_request_template.md` carries the review checklist: six-part
    card, sources by ID, evidence labels, no pricing commitment, no external
    send, no business data, tests.
  - Tests cover the Routine format and the checklist: 227 pass, 1 is skipped.
    The zip also ships `routines/` and `.github/`.

## 0.3.0 - 2026-09-25

Why: on 2026-09-25 v0.2.1 was run against the live PCOS files (102-row
Worklist, the Sep 24 PCOS_NOW, the Sep 23 RECON, nine unapplied DELTAs).
`hygiene` worked, but three things no longer matched how PCOS runs since v3:
PCOS_NOW is hand-written narrative, the RECON runbook moved to v1.4, and
automatic status proposals ignored evidence waiting in the inbox. Asked for by
Joe on 2026-09-25 ("yes" to: fix what does not match, then wire the tools into
the closeout and scheduled tasks). Built by Claude (Cowork chat,
session_01Gs556kSndwU6XuZNVztAhj).

- New command `now_check`: cross-checks PCOS_NOW against the Worklist and
  reports CITED_MISSING, CITED_CLOSED, STATUS_MISMATCH, OPEN_NOT_CITED,
  ROW_COUNT, PENDING_DELTA and PENDING_NEW_ID. Why: the audits keep finding
  drift between the state file and the sheet (stale row counts, closed rows
  described as live), and nothing checked it mechanically. Task ID ranges
  ("T-067 to T-071 unchanged") count as cited; without that, the live file
  produced two false OPEN_NOT_CITED lines.
- `hygiene --pending PATH ...`: a STALE_ARCHIVE or DONE_PROMOTE proposal for a
  row named in an unapplied DELTA gets Action `hold`. Why: on the live data
  v0.2.1 proposed a Done-Candidate row -> Done while an unapplied DELTA said new
  work had started on that row.
- `now_build` no longer regenerates sections 2, 3 and 6 of a narrative (v3)
  PCOS_NOW (titles "Current work and stopping points", "Dependencies", "Stale
  matters") and appends nothing from the RECON to it; every section is carried
  unchanged and a warning points to `now_check`. `--carry-all` forces this on
  any file. Why: on the live file v0.2.1 would have replaced the hand-written
  current-work narrative with a table. The old layout behaves exactly as before.
- `now_check --now` also takes a Google Docs `.html` export (stdlib HTML
  parser, headings keep their level, table rows become `|` lines). Why: large
  Drive exports reach a scheduled session as files, and the HTML export is the
  one large enough to arrive that way; no pandoc needed.
- PCOS_NOW headings from a Google Docs Markdown export (`# 0\. Joe today`) are
  recognised; `common.unescape_md` removes the export's backslash escapes. Why:
  v0.2.1 found no section at all in the exported live file.
- `recon_parse` reads the runbook 01-EM-02 v1.4 layout (`SECTION n —`
  headings, `**3.1**` item blocks with `- **Field:** value` bullets) and
  reports `layout` (`runbook-v1.4` or `legacy`). Follow-ups map to
  `action_on_joe`. ISO timestamps (`2026-09-23T16:08Z`) now count as dates, so
  `as_of` is filled. Why: v0.2.1 read the latest RECON as 94 coverage items and
  74 "action on Joe" items, the sensitive section included; a legacy
  `now_build` run would have appended them to the decisions section.
- Hardened after an independent review of the first draft: ranges never span
  lines, plain or spaced dashes and "from X to Y" are not ranges, and range
  members are never reported closed or missing; a status word counts only in
  the same clause or table cell; CITED_CLOSED is skipped when PCOS_NOW writes
  the closed status itself; a numbered sub-heading is not a section; narrative
  carry copies the file exactly (order, CRLF, final newline); a legacy RECON
  with "Section n:" headings stays legacy; v1.4 sub-headings do not switch
  sections; `--pending` expands ranges, skips this package's own reports and
  warns when it finds no file; `now_check` warns when PCOS_NOW has no sections.
- Tests: 117 (was 88). New synthetic fixtures `PCOS_NOW_v3_gdocs.md`,
  `RECON_v14_sample.md` and `pending/DELTA_2026-09-01_sample.md`; nothing from
  the real files was added to the repository.
- `.gitignore` also ignores `DELTA*.md`, `inbox/`, `pending/` and the
  `now_check` outputs at the repo root.

## 0.2.1 - 2026-09-02

Applies the answers in PCOS_DISPATCH_2026-09-02.

- `Done-Candidate` counts as closed for `--skip-closed` and stays out of
  PCOS_NOW sections 2, 3 and 6. New hygiene check `DONE_PROMOTE` proposes
  `Done` when a Done-Candidate row has not changed for `done_candidate_days`
  (7, in `vocab.json`; `--done-candidate-days` overrides). The weekly AI pass
  applies `DONE_PROMOTE` alongside `STALE_ARCHIVE`.
- `aged_days` (7) moved into `vocab.json`; `--aged-days` still overrides it.
  A vocab file without the two new keys falls back to 7 for both.
- `DUPLICATE_TITLE` is skipped when both rows are closed.
- Section 2 shows `[BAD DATE]` in the Age column for rows whose Updated is
  empty or not `YYYY-MM-DD`, instead of a blank cell.
- Commit author switched to a GitHub noreply address.

## 0.2.0 - 2026-09-02

- Status, Priority and Room vocabularies plus `stale_days` moved to
  `pcos_tools/vocab.json`. It is read the first time a command needs it, never
  at import or while parsing arguments, so a typo in it, a missing file or an
  unreadable file is a normal `error:` line. `--vocab PATH` points at another
  file; `--stale-days` still overrides the file value and must be 1 or more
  (`--aged-days` must be 0 or more).
- New Status values `Active-Low` and `Done-Candidate`. `stale_days` is now 90.
- `now_build`: section 0 (JOE TODAY) is carried through unchanged when present
  and never created. Default headings match the live PCOS_NOW: 1 DECISIONS,
  2 ACTIVE, 3 WAITING ON OTHERS, 4 DELTAS, 5 CANDIDATES, 6 STALE BLOCK,
  7 POINTERS AND ROOM SOURCE MAPS, 8 SYSTEM STATUS, in the previous file's
  heading style. Sections are located by the leading number only (`## 3`,
  `## 3.`, `## 3.WAITING`, `**3. x**`); a body line such as `#2 option` or
  `### 2.1 Sub` is not a heading, and nothing inside a code fence is.
- Section 2 includes `Active-Low` rows at LOW rank whatever their Priority
  cell says, after other LOW rows, and excludes `Done-Candidate`.
- Sections 2, 3 and 6 exclude Room PERSONAL, including RECON lines that only
  name PERSONAL tasks; a RECON line naming a work task still marks that row.
- RECON items with no letters or digits (an empty checkbox, `???`) are never
  appended, so re-runs stay idempotent.
- Non-UTF-8 inputs, invalid RECON JSON (including wrong per-item shapes) and a
  broken vocab file are reported as clean errors. Drafts, the report and the
  RECON JSON are written with LF line endings. Console and piped output are
  UTF-8 safe on Windows.
- `now_build` refuses to write its draft over any of its three inputs.
- Hygiene report names the vocabulary source and the effective stale threshold.
- `pyproject.toml` takes the version from the package and ships `vocab.json`.
- `.gitignore` blocks real exports and drafts at the repo root; added
  `scripts/build_zip.py`, `.gitattributes`, this changelog.

## 0.1.0 - 2026-09-01

- First release: `hygiene`, `recon_parse`, `now_build`, tests, README.
