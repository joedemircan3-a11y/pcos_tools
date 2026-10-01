# Changelog

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
