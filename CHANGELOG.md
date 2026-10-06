# Changelog

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
  v0.2, skill section 3, Routine step 5; EXO card v0.2, Routine step 6). Why:
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
- The three indexes list the new cards, skill and Routines.
  `tests/test_retro_lane.py` pins the lane's fixed parts: 325 tests pass (was
  285), 1 is skipped.

## Unreleased - 2026-10-06: Codex review fixes (PR 1 and PR 2)

Why: PCOS queue item QC18 (QUEUE_v4) applies the six Codex review suggestions on
pull request 1, recorded at PC-1 (DELTA_PC-1 step B3). Built by Claude (Claude
Code on the web). Card versions are bumped where a card changed; skill versions
stay 0.1 because the skills are not released yet.

- Golden set: the lane run now scores whether a lane's output satisfies Joe's
  correction; a separate checker run scores the checker on the case's Wrong
  output. Before, a version that kept the defect passed and a version that fixed
  it failed. Checker card v0.2; checker and weekly-evolve skills follow.
- Prediction ledger: items match by identity (thread conversation ID, Inbox row
  ID, or DELTA file ID with the Task ID), never by subject, so two unrelated
  items with one subject get two rows.
- Prediction ledger: a Parked row is never asked again; new evidence or Joe's
  own action reopens it, and the weekly calibration re-checks Parked rows.
- Knowledge chair card v0.2: Status Duplicate for claims a review finds to
  repeat an earlier row (needs the Status option in the Knowledge database).
- `agents/INPUTS.md` v0.2: one key per domain folder, `KL_00` to `KL_07`;
  `KL_DOMAINS` is a group of those keys; `MAIL_ROUTED` documented as the one set.
- Tests: the private-ID guard now covers Drive IDs that contain `-` or `_`, and
  one test per fix above. 200 tests pass, 1 is skipped.
- Routines (Codex review of pull request 2, same queue item):
  - L1, L2 and L3 read their lane card (`agents/L1-brief.md` and so on) in
    LOAD once P2-19 writes it; L4 reads every card in its header and runs both
    golden-set runs.
  - council-board chair: the Reviewed-2 arm needs both review fields, so a row
    with a missed Review-1 waits the full cycle of skill section 6.
  - council-github chair: a schedule every 2 hours runs the missing-review
    fallback, which no event would otherwise wake.
  - prediction-ledger: a Parked row is never asked again.
  - Tests: every Routine prompt reads the cards in its header (except the
    anonymous Review-2), has a schedule and numbers its steps in order; the
    chair's queue needs both reviews. 285 tests pass, 1 is skipped.

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
