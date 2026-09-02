# Changelog

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
