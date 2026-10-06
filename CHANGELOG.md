# Changelog

## Unreleased - 2026-10-06: Codex review fixes, retry (PR 1)

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
- Council-github card v0.3: the chair finds the Council row by the pull request's
  link in the row's Draft field, never by Task title; no bound row, or more than
  one, is Blocked.
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
- Tests: the private-ID guard also flags runs of 25 characters or more with two of
  the three character classes, or with no "-" or "_" (Drive IDs are 28 or more), so
  an ID without a digit or without mixed case is caught; two public names join the
  reviewed list. One test per fix, each failing on the old text. 237 tests pass.

## Unreleased - 2026-10-06: Codex review fixes (PR 1)

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
