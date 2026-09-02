# pcos_tools v0.2

Small, standard-library-only Python 3.11 toolkit for Joe Demircan's PCOS system.
It reads hand-exported files (a Worklist CSV, a RECON markdown, the previous
PCOS_NOW markdown) and writes **draft** files next to them.

> **The rule: these scripts only produce drafts.** Nothing here edits the
> Worklist, the RECON or the live PCOS_NOW. Every output (`proposed_changes.csv`,
> `hygiene_report.md`, `RECON.json`, `PCOS_NOW_draft.md`) is a proposal that a
> human or a Claude session reviews and then applies. No network calls, no
> Google API, no email.

## Install

Requires Python 3.11 or newer. Nothing else is needed.

```bash
git clone <this repository's URL> pcos_tools
cd pcos_tools
python -m pcos_tools --help
```

The same folder layout is shipped as `pcos_tools_v0.2.zip` (built with
`python scripts/build_zip.py`, kept in the PCOS Drive folder, not in git). On
Windows, use a short path (for example `C:\pcos\`) so fixture paths stay under
the 260-character limit.

Optional extras:

```bash
pip install -e ".[test]"      # pytest, to run the test suite
pip install -e ".[pandas]"    # only if you want the --pandas reader
```

`pip install -e .` (or a plain `pip install .`) also gives you a `pcos-tools`
console command that behaves exactly like `python -m pcos_tools`; the version
comes from `pcos_tools/__init__.py` and `vocab.json` is packaged.

## Vocabulary file

`pcos_tools/vocab.json` holds the allowed values and the stale threshold. It is
read the first time a command needs it, so editing it changes every command:

```json
{
  "status": ["Active", "Active-Low", "Active-Recurring", "Waiting", "Blocked",
             "Needs-Decision", "Candidate", "Backlog", "Open", "Done",
             "Done-Candidate", "Expired", "Superseded", "Stale-Triage", "Archived-Auto"],
  "priority": ["CRITICAL", "HIGH-TODAY", "HIGH", "MED-HIGH", "MED", "LOW", "RECURRING", ""],
  "room": ["1", "2", "3", "4", "10", "13", "PERSONAL"],
  "stale_days": 90
}
```

- The priority list order is the sort rank (first is highest). The empty string
  means a blank priority is allowed.
- `stale_days` is the Stale-Triage age before `Archived-Auto` is proposed.
  `--stale-days N` (1 or more) on the command line overrides it for one run.
- `--vocab PATH` (on `hygiene` and `now_build`) loads a different file, for
  example to test a new status before changing the packaged one.
- A malformed, missing or unreadable file, packaged or passed with `--vocab`,
  is a clean `error:` line, not a crash; `--vocab` keeps working while the
  packaged file is broken. `--version`, `--help` and `recon_parse` never read it.

The status groups that drive behaviour stay in code (`pcos_tools/common.py`):
active for section 2 = Active, Active-Low, Active-Recurring, Needs-Decision,
Blocked; aged = Waiting, Blocked; closed for `--skip-closed` = Done, Expired,
Superseded, Archived-Auto. A new status added to `vocab.json` is valid
everywhere but joins no group until the code says so.

## Commands

`hygiene` and `now_build` accept `--today YYYY-MM-DD` to fix the reference
date for ages (useful for reproducible runs); it defaults to the current date.
`recon_parse` has no reference date; it takes `--year` for dates written
without one. Each command also answers to a dashed alias (`recon-parse`,
`now-build`).

### 1. `hygiene` - check the Worklist CSV

```bash
python -m pcos_tools hygiene Worklist.csv --out-dir out
```

Writes `out/proposed_changes.csv` and `out/hygiene_report.md`. The input is opened
read-only and never modified. Checks:

| Check | Meaning | Default threshold |
| --- | --- | --- |
| `STALE_ARCHIVE` | Stale-Triage row older than `stale_days`; proposes `Archived-Auto` | 90 days (vocab.json) |
| `AGED_WAITING` | Waiting or Blocked row whose Updated is `--aged-days` or older | 7 days |
| `MALFORMED_ID` | Task ID not matching `T-` plus 3 or 4 digits | |
| `DUPLICATE_ID` | Same Task ID on two rows | |
| `INVALID_STATUS` / `INVALID_PRIORITY` / `INVALID_ROOM` | Value outside vocab.json | |
| `BAD_DATE` | Updated empty or not `YYYY-MM-DD` (age checks are skipped for that row) | |
| `DUPLICATE_TITLE` | Normalised title token overlap at or above `--dup-threshold` with an earlier row | 0.80 |
| `EMPTY_SOURCES` / `EMPTY_CONFIDENCE` | Empty cell | |

The report also states the **next free Task ID** (highest well-formed ID plus one;
gaps are not reused), and the same value is the last row of `proposed_changes.csv`
with check `NEXT_FREE_ID`. `STALE_ARCHIVE` rows are the ones the weekly AI pass
applies; everything else is for a human to decide. Hygiene looks at every row,
PERSONAL included.

`proposed_changes.csv` columns: `Task ID, Title, Check, Field, Current, Proposed,
Action, Reason, Row`. `Action` is one of `set-status`, `fix-id`, `fix-value`,
`fix-date`, `fill`, `chase-or-close`, `merge-or-rename`, `review`, `info`.
`Proposed` is only filled where the tool can suggest a concrete value (today: the
`Archived-Auto` status and the next free ID).

Options: `--today YYYY-MM-DD`, `--aged-days N` (0 or more), `--stale-days N`
(1 or more), `--vocab PATH`, `--dup-threshold 0.0-1.0`, `--skip-closed` (do not
flag empty Sources/Confidence on Done, Expired, Superseded, Archived-Auto rows),
`--pandas` (read with pandas; optional), `--out-dir DIR`.

Title similarity is the Sorensen-Dice overlap of the two titles' token sets after
lower-casing, stripping punctuation and dropping short stop words ("the", "for",
"from", ...). "Invoice from Ahmet Yilmaz" vs "Invoice from Ahmet Yilmaz - Aug"
scores 0.86 and is flagged; "Vocabulary check row" vs "Date check row" scores
0.67 and is not.

### 2. `recon_parse` - RECON markdown to JSON

```bash
python -m pcos_tools recon_parse RECON_2026-09-01.md --out RECON_2026-09-01.json
python -m pcos_tools recon_parse RECON.md --people "Ahmet Yilmaz,Fatma Demir" --out -
```

Recognises the six numbered sections (`1. Coverage header`, `2. ACTION ON JOE`,
`3. WAITING ON OTHERS`, `4. DELEGABLE`, `5. Patterns`, `6. Run-log footer`) as
markdown headings (`## 2. ACTION ON JOE`) or, if the file has no such headings,
as plain numbered lines. Bullets (`-`, `*`, `1.`) under each become items;
indented lines continue the previous item; nested bullets get `level` 1+.

Each item carries `text`, `line`, `dates` (`raw` plus ISO `iso` where the date
is unambiguous: `2026-09-03`, `5 Sep 2026`, `Sep 5`; `03/09/2026` is kept raw
with `iso: null`), `people` (with a `confidence` of `known`, `mention`,
`pattern` or `heuristic`), and `task_ids` (`T-005`). Sections 1 and 6 also expose
`Key: value` lines as `fields`. The top level aggregates `dates`, `people`,
`task_ids`, `as_of` (latest date in the coverage header) and `warnings`
(missing or repeated sections).

People detection is heuristic. Pass `--people "Name One,Name Two"` for names that
must always be recognised. Treat the `heuristic` entries as suggestions.

Options: `--out PATH` (default: the RECON path with `.json`; `-` prints to
stdout), `--people "A,B"`, `--year YYYY` (year for dates written without one;
default: the first ISO date in the file, else the current year).

### 3. `now_build` - draft the next PCOS_NOW

```bash
python -m pcos_tools now_build --csv Worklist.csv --recon RECON_2026-09-01.json \
    --prev PCOS_NOW.md --out-dir out
```

`--recon` accepts the JSON from `recon_parse` (a trimmed one with just
`sections` and item `text` also works) or the RECON `.md` directly. Writes
`out/PCOS_NOW_draft.md` with the same numbered sections as the previous file.
Sections are located by their leading number only: `## 3. WAITING ON OTHERS`,
`## 3 Waiting`, `## 3)` and, in a file without `#` headings, `**3. Waiting**`
all count; a body line such as `#2 option` or `### 2.1 Sub` does not. The
previous file's heading lines are reused. When a section 1 to 8 is missing, the
default heading below is used in the previous file's style and a warning is
printed.

| Section | Treatment |
| --- | --- |
| 0 JOE TODAY | carried unchanged when present; never created |
| 1 DECISIONS | carried unchanged, then RECON section 2 items appended as new numbered decisions tagged `[NEW from RECON <date>]` |
| 2 ACTIVE | regenerated: Status in Active, Active-Low, Active-Recurring, Needs-Decision, Blocked; `Done-Candidate` and Room PERSONAL excluded; sorted CRITICAL > HIGH-TODAY > HIGH > MED-HIGH > MED > LOW > RECURRING > blank, then Room, then Task ID. `Active-Low` rows always take LOW rank whatever their Priority cell says, after other LOW rows |
| 3 WAITING ON OTHERS | regenerated: Waiting rows (Room PERSONAL excluded) plus RECON section 3 items, with age in days and `[AGED]` at 7 days or more. A RECON item that names a Task ID already in the table marks that row `[RECON]` instead of adding a duplicate row; a RECON item that names a PERSONAL task is dropped |
| 4 DELTAS | carried unchanged |
| 5 CANDIDATES | carried unchanged, then RECON section 5 items appended as `- [CANDIDATE from RECON] ...` |
| 6 STALE BLOCK | regenerated from Stale-Triage rows (Room PERSONAL excluded), oldest first; `[ARCHIVE?]` at `stale_days` (90) or more |
| 7 POINTERS AND ROOM SOURCE MAPS | copied verbatim from the previous file |
| 8 SYSTEM STATUS | carried unchanged |

Appends are idempotent: re-running with the draft as `--prev` does not add the
same RECON items twice. The preamble above the first section (title line, date)
is carried as-is; update the date by hand when you apply the draft. A generator
comment at the top of the file records what was regenerated. The draft is
written with LF line endings.

Options: `--today YYYY-MM-DD`, `--aged-days N`, `--stale-days N`,
`--vocab PATH`, `--people "A,B"` (only used when `--recon` is a `.md`),
`--pandas`, `--out-dir DIR`.

## Worked example

The test fixtures double as a worked example:

```bash
python -m pcos_tools hygiene tests/fixtures/worklist_fixture.csv --out-dir out --today 2026-09-01
python -m pcos_tools recon_parse tests/fixtures/RECON_sample.md --out out/RECON_sample.json
python -m pcos_tools now_build --csv tests/fixtures/worklist_fixture.csv \
    --recon out/RECON_sample.json --prev tests/fixtures/PCOS_NOW_prev.md \
    --out-dir out --today 2026-09-01
```

## Input schema

Worklist CSV, 12 columns with a header row, UTF-8 (a BOM is tolerated; a file
in another encoding is reported as an error, re-export it as CSV UTF-8):

`Task ID, Title, Room, Status, Priority, Owner, Waiting On, Sources, Next Action, Updated, Confidence, Notes`

- Status, Priority and Room: as listed in `pcos_tools/vocab.json` (see above)
- Task ID: `T-` plus 3 or 4 digits; Updated: `YYYY-MM-DD`

Extra columns are ignored; a missing column is an error.

## Tests

```bash
pip install pytest
python -m pytest -q
```

The fixture worklist has 26 rows covering every Status value in `vocab.json`,
one malformed ID, one invalid-vocabulary row, one bad date, one near-duplicate
title pair, PERSONAL rows in every regenerated section, an `Active-Low` row with
a HIGH priority and a `Done-Candidate` row. The sample RECON has all six
sections. All fixture people, tasks, dates and paths are invented.

## Build the zip

```bash
python scripts/build_zip.py     # writes dist/pcos_tools_v0.2.zip
```

## Workflow

1. Export the Worklist to CSV, save the RECON markdown, keep the current PCOS_NOW.
2. Run `hygiene`; the weekly AI pass applies the `STALE_ARCHIVE` rows; a human
   reviews the rest of `proposed_changes.csv`.
3. Run `recon_parse`, then `now_build`; review `PCOS_NOW_draft.md`; paste the
   accepted sections into the live PCOS_NOW.
4. Nothing is applied by these scripts. They never write to their inputs and
   refuse to write an output over an input path.
5. Keep real exports and drafts out of git: run with `--out-dir out` (ignored)
   and note that `.gitignore` also ignores `Worklist*.csv`, `RECON*.md`,
   `RECON*.json`, `PCOS_NOW*.md` and the three draft file names at the repo
   root, so a real file dropped next to the code cannot be committed by
   accident. Output is safe to pipe or redirect: non-ASCII text is written as
   UTF-8.

## Limitations (v0.2)

- People and date extraction are regex heuristics; check them.
- `dd/mm/yyyy` dates are kept raw because the day/month order is ambiguous.
- Duplicate detection is pairwise over titles only (fine up to a few thousand rows).
- The previous PCOS_NOW must use numbered headings (`## 1 ...`) or bold
  numbered lines (`**1. ...**`) for its sections.
