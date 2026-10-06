# pcos_tools

The code repository of Joe Demircan's PCOS system. It holds the draft-only Python
toolkit, the agent cards and skills of the PCOS lanes, and the prompts for their
scheduled Routines.

> **This repository is public.** It holds no business data: no Drive or Notion
> IDs or links, no names of people, no prices, customers, vendor terms or mail
> text (Operating Card v7.4, WRITE PATHS). Cards, skills and prompts name their
> sources by key. The IDs live in a private Drive map.

## What this repository holds

| Path | What | Status |
| --- | --- | --- |
| `pcos_tools/` | The toolkit, v0.3.0: `hygiene`, `recon_parse`, `now_build`, `now_check`. Draft-only; documented in "The toolkit" below. | Live |
| `scripts/` | Build helpers (`build_zip.py`) | Live |
| `tests/` | Test suite; synthetic fixtures only | Live |
| `agents/` | One six-part card per lane (`CARD_TEMPLATE.md`), the source keys (`INPUTS.md`), `_INDEX.md` | Candidate |
| `skills/` | Lane skills in the Agent Skills format (`SKILL.md` per folder), `_INDEX.md` | Candidate |
| `routines/` | Paste-ready prompts for the planned Claude Code Routines, one file each, `_INDEX.md` | Candidate |
| `.github/pull_request_template.md` | The review checklist every pull request answers | Live |

The tool scripts stay at `pcos_tools/` and `scripts/` (not under a separate
`/tools` folder), so `python -m pcos_tools` and the Operating Card's CLOSE C commands
keep working unchanged. A card, skill or Routine stays Candidate until its Lanes row
exists and its first run is in the Changelog.

## How PCOS points here

- PCOS_NOW section 7 points to the live rules: the Operating Card now, the kernel
  page after build day. Their WRITE PATHS ("Where things are" in the kernel) name
  this repository as the home of code, skills and cards.
- Operating Card CLOSE C clones this repository in every closeout and runs the
  toolkit checks (see "Quick start" below).
- Each scheduled lane is a Routine created from `routines/`. Its prompt loads the
  kernel, then the lane's card in `agents/` and its skill in `skills/`.
- Sources are named as `[[KEY]]` (`agents/INPUTS.md`). Keys resolve through the
  kernel's "Where things are" table. Until the kernel holds it, they resolve through
  the private Drive file `PCOS_AGENT_INPUT_IDS` in the folder
  `PCOS_BUILD_KIT_2026-09-28`. Nothing in this repository points back to a private
  object by ID.
- Changes arrive as pull requests that answer the checklist in
  `.github/pull_request_template.md`. Commenting "@codex review" asks Codex for a
  review; for council pull requests, the council-github chair Routine decides.

## The toolkit: pcos_tools v0.3.0

Small, standard-library-only Python 3.11 toolkit for Joe Demircan's PCOS system.
It reads exported files (a Worklist CSV, a RECON markdown, the current PCOS_NOW
markdown, unapplied DELTA files) and writes **draft** files and reports next to
them.

> **The rule: these scripts only produce drafts.** Nothing here edits the
> Worklist, the RECON or the live PCOS_NOW. Every output (`proposed_changes.csv`,
> `hygiene_report.md`, `RECON.json`, `PCOS_NOW_draft.md`, `now_check_report.md`)
> is a proposal that a human or a Claude session reviews and then applies. No
> network calls, no Google API, no email. Tool output is advisory: when it
> disagrees with a live read of the source, the live read wins.

## Quick start for a PCOS session

The repository is public at https://github.com/joedemircan3-a11y/pcos_tools.
A Claude session with code execution gets it in seconds, without spending
tokens on the code itself:

```bash
git clone --depth 1 https://github.com/joedemircan3-a11y/pcos_tools.git
cd pcos_tools
# Save the live Worklist as Worklist.csv (Drive export text/csv), PCOS_NOW as
# PCOS_NOW.html (Drive export text/html; .md works too) and the unapplied
# business DELTA files from _PCOS_INBOX into a folder inbox/ (a small .txt per
# DELTA listing the Task IDs it names is enough).
python -m pcos_tools hygiene Worklist.csv --pending inbox --skip-closed --out-dir out
python -m pcos_tools now_check --csv Worklist.csv --now PCOS_NOW.html --pending inbox --out-dir out
```

Use `git clone` or raw files
(`https://raw.githubusercontent.com/joedemircan3-a11y/pcos_tools/main/...`); the
GitHub zip download is blocked by the Claude session proxy. If the clone fails,
skip the tools and work by hand: a run never stops for them.

## Install

Requires Python 3.11 or newer. Nothing else is needed.

```bash
git clone <this repository's URL> pcos_tools
cd pcos_tools
python -m pcos_tools --help
```

The same folder layout can be shipped as `pcos_tools_v0.3.zip` (built with
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
  "stale_days": 90,
  "aged_days": 7,
  "done_candidate_days": 7
}
```

- The priority list order is the sort rank (first is highest). The empty string
  means a blank priority is allowed.
- `stale_days` is the Stale-Triage age before `Archived-Auto` is proposed.
  `--stale-days N` (1 or more) on the command line overrides it for one run.
- `aged_days` is the Waiting/Blocked age behind `AGED_WAITING` and the `[AGED]`
  mark; `--aged-days N` (0 or more) overrides it. `done_candidate_days` is the
  Done-Candidate age with no change behind `DONE_PROMOTE`;
  `--done-candidate-days N` (1 or more) overrides it. A file without these two
  keys falls back to 7 for both.
- `--vocab PATH` (on `hygiene` and `now_build`) loads a different file, for
  example to test a new status before changing the packaged one.
- A malformed, missing or unreadable file, packaged or passed with `--vocab`,
  is a clean `error:` line, not a crash; `--vocab` keeps working while the
  packaged file is broken. `--version`, `--help` and `recon_parse` never read it.

The status groups that drive behaviour stay in code (`pcos_tools/common.py`):
active for section 2 = Active, Active-Low, Active-Recurring, Needs-Decision,
Blocked; aged = Waiting, Blocked; closed for `--skip-closed` and the
duplicate-title skip = Done, Done-Candidate, Expired, Superseded,
Archived-Auto. A new status added to `vocab.json` is valid everywhere but
joins no group until the code says so.

## Commands

`hygiene`, `now_build` and `now_check` accept `--today YYYY-MM-DD` to fix the
reference date (useful for reproducible runs); it defaults to the current date.
`recon_parse` has no reference date; it takes `--year` for dates written
without one. Each command also answers to a dashed alias (`recon-parse`,
`now-build`, `now-check`).

`hygiene` and `now_check` take `--pending PATH [PATH ...]`: unapplied DELTA
files, or folders whose `.md`, `.markdown` and `.txt` files are read (not
recursive; this package's own report files are skipped). Every Task ID named in
them, ranges included, counts as having unapplied evidence. A warning is
printed when the paths hold no such file.

### 1. `hygiene` - check the Worklist CSV

```bash
python -m pcos_tools hygiene Worklist.csv --out-dir out
```

Writes `out/proposed_changes.csv` and `out/hygiene_report.md`. The input is opened
read-only and never modified. Checks:

| Check | Meaning | Default threshold |
| --- | --- | --- |
| `STALE_ARCHIVE` | Stale-Triage row older than `stale_days`; proposes `Archived-Auto` | 90 days (vocab.json) |
| `DONE_PROMOTE` | Done-Candidate row unchanged for `done_candidate_days`; proposes `Done` | 7 days (vocab.json) |
| `AGED_WAITING` | Waiting or Blocked row whose Updated is `aged_days` or older | 7 days (vocab.json) |
| `MALFORMED_ID` | Task ID not matching `T-` plus 3 or 4 digits | |
| `DUPLICATE_ID` | Same Task ID on two rows | |
| `INVALID_STATUS` / `INVALID_PRIORITY` / `INVALID_ROOM` | Value outside vocab.json | |
| `BAD_DATE` | Updated empty or not `YYYY-MM-DD` (age checks are skipped for that row) | |
| `DUPLICATE_TITLE` | Normalised title token overlap at or above `--dup-threshold` with an earlier row; skipped when both rows are closed | 0.80 |
| `EMPTY_SOURCES` / `EMPTY_CONFIDENCE` | Empty cell | |

The report also states the **next free Task ID** (highest well-formed ID plus one;
gaps are not reused), and the same value is the last row of `proposed_changes.csv`
with check `NEXT_FREE_ID`. `STALE_ARCHIVE` and `DONE_PROMOTE` rows are the ones
the weekly AI pass applies; everything else is for a human to decide. Hygiene
looks at every row, PERSONAL included.

`proposed_changes.csv` columns: `Task ID, Title, Check, Field, Current, Proposed,
Action, Reason, Row`. `Action` is one of `set-status`, `fix-id`, `fix-value`,
`fix-date`, `fill`, `chase-or-close`, `merge-or-rename`, `review`, `hold`, `info`.

With `--pending`, a `STALE_ARCHIVE` or `DONE_PROMOTE` proposal for a row named in
an unapplied DELTA gets Action `hold` instead of `set-status`, and its Reason
names the DELTA file. The weekly pass applies only `set-status` rows. Example:
a Done-Candidate row whose DELTA says new work started must not be promoted to
Done before that DELTA is applied.
`Proposed` is only filled where the tool can suggest a concrete value (today: the
`Archived-Auto` status and the next free ID).

Options: `--today YYYY-MM-DD`, `--aged-days N` (0 or more), `--stale-days N`
(1 or more), `--done-candidate-days N` (1 or more), `--vocab PATH`,
`--dup-threshold 0.0-1.0`, `--skip-closed` (do not flag empty
Sources/Confidence on Done, Done-Candidate, Expired, Superseded, Archived-Auto
rows), `--pending PATH ...`, `--pandas` (read with pandas; optional), `--out-dir DIR`.

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

**Runbook v1.4 layout.** A RECON written by runbook 01-EM-02 v1.4 uses
`## COVERAGE DISCLOSURE`, `## SECTION 1 — NEW TASK CANDIDATES`,
`## SECTION 2 — UPDATES TO EXISTING TASKS`,
`## SECTION 3 — FOLLOW-UPS REQUIRING OPERATOR ACTION`,
`## SECTION 4 — SENSITIVE / LEADERSHIP-WATCH`, `## SECTION 5 — IGNORE / NO-ACTION`
and `## RUN LOG`. A `SECTION n —` heading whose title only v1.4 uses (new task,
updates to existing, follow-up, sensitive, ignore) switches the parser to this layout
(`"layout": "runbook-v1.4"` in the JSON; the old layout reports `"legacy"`). Its
section keys are `coverage`, `new_task_candidates`, `task_updates`,
`action_on_joe` (the follow-ups), `sensitive`, `ignore` and `run_log`; only
those headings change the section, so a `### sub-heading` stays in place. Items are
the `**3.1**` / `**2.1 — title**` blocks; their `- **Field:** value` bullets go
into the item's `fields` (not separate items), and an item with no header text
takes its `text` from Title, What is needed, What changed, Subject (verbatim) or
Contact. Dates, people and Task IDs are read from the header and all fields.
The coverage table becomes `fields`, and `as_of` comes from its dates (ISO
timestamps such as `2026-09-23T16:08Z` count).

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
| 2 ACTIVE | regenerated: Status in Active, Active-Low, Active-Recurring, Needs-Decision, Blocked; `Done-Candidate` and Room PERSONAL excluded; sorted CRITICAL > HIGH-TODAY > HIGH > MED-HIGH > MED > LOW > RECURRING > blank, then Room, then Task ID. `Active-Low` rows always take LOW rank whatever their Priority cell says, after other LOW rows. A row whose Updated is empty or not `YYYY-MM-DD` shows `[BAD DATE]` in the Age column |
| 3 WAITING ON OTHERS | regenerated: Waiting rows (Room PERSONAL excluded) plus RECON section 3 items, with age in days and `[AGED]` at 7 days or more. A RECON item that names a Task ID already in the table marks that row `[RECON]` instead of adding a duplicate row; a RECON item that names a PERSONAL task is dropped |
| 4 DELTAS | carried unchanged |
| 5 CANDIDATES | carried unchanged, then RECON section 5 items appended as `- [CANDIDATE from RECON] ...` |
| 6 STALE BLOCK | regenerated from Stale-Triage rows (Room PERSONAL excluded), oldest first; `[ARCHIVE?]` at `stale_days` (90) or more |
| 7 POINTERS AND ROOM SOURCE MAPS | copied verbatim from the previous file |
| 8 SYSTEM STATUS | carried unchanged |

**Narrative (v3) PCOS_NOW.** Since September 2026 the live PCOS_NOW is written
by hand: section 2 is "Current work and stopping points", 3 "Dependencies", 6
"Stale matters". Regenerating those from the Worklist would delete the
narrative. When the previous file uses any of those titles (or with
`--carry-all`), every section is carried unchanged, nothing is appended from
the RECON, and a warning points to `now_check`. The table above applies only to
the older layout. Headings from a Google Docs Markdown export (`# 2\. Current
work`) are recognised.

Appends are idempotent: re-running with the draft as `--prev` does not add the
same RECON items twice. The preamble above the first section (title line, date)
is carried as-is; update the date by hand when you apply the draft. A generator
comment at the top of the file records what was regenerated. The draft is
written with LF line endings.

Options: `--today YYYY-MM-DD`, `--aged-days N` (0 or more), `--stale-days N`
(1 or more), `--vocab PATH`, `--people "A,B"` (only used when `--recon` is a
`.md`), `--carry-all`, `--pandas`, `--out-dir DIR`.

### 4. `now_check` - cross-check PCOS_NOW against the Worklist

```bash
python -m pcos_tools now_check --csv Worklist.csv --now PCOS_NOW.md --pending inbox --out-dir out
```

The state file and the Worklist are written by different runs and drift apart.
`now_check` reads both (a Google Docs Markdown export, or an `.html` export, is fine) and writes
`out/now_check_report.md` and `out/now_check.csv` (`Check, Task ID, Worklist
Status, Section, Detail`). It never edits either file.

| Check | Meaning |
| --- | --- |
| `CITED_MISSING` | Task ID cited in a live section (0 to 3) but not in the Worklist |
| `CITED_CLOSED` | Task ID cited in a live section but Done, Expired, Superseded or Archived-Auto in the Worklist |
| `STATUS_MISMATCH` | A Status word written within 60 characters after the Task ID (before the next ID) differs from the Worklist Status, e.g. PCOS_NOW says "T-006 (Active)", the sheet says Blocked |
| `OPEN_NOT_CITED` | Active, Needs-Decision, Blocked or Waiting row with CRITICAL, HIGH-TODAY or HIGH priority that PCOS_NOW never mentions (Room PERSONAL excluded) |
| `ROW_COUNT` | The "N rows" written next to the Worklist pointer in section 7 differs from the CSV |
| `PENDING_DELTA` | Task ID named in an unapplied DELTA (`--pending`) |
| `PENDING_NEW_ID` | Task ID named in an unapplied DELTA but not in the Worklist (a new row, or one kept elsewhere such as the private sheet) |

Ranges count: "T-067 to T-071 unchanged" cites T-068, T-069 and T-070 too.
A range is `to`, `through`, `thru` or `..` between two IDs on the same line, or
an en dash with no spaces (`T-067–T-071`); spans over 60 are ignored. A spaced
hyphen or em dash is a clause break, and "from T-001 to T-020" is a move, so
neither is a range. Range members are only marked as cited: a range naturally
spans gaps and closed rows, so they are never reported as missing or closed.

`CITED_CLOSED` is skipped when PCOS_NOW itself writes the closed status right
after the ID ("T-011 Done yesterday"). Status words match the vocabulary
exactly and case-sensitively, longest first, so "Done-Candidate" is not read as
"Done" and a lowercase "blocked" in prose is not a status; the search stops at
the end of the clause or table cell (`.`, `;`, `!`, `?`, `|`). Sections are the
numbered headings at the level of the first one, so a sub-heading such as
`## 7 vendors to call` inside `# 2.` stays body text. For `ROW_COUNT` the line
with "Live Worklist" wins over other worklist lines. A warning is printed when
PCOS_NOW has no numbered sections at all.

Options: `--pending PATH ...`, `--today YYYY-MM-DD`, `--vocab PATH`, `--pandas`,
`--out-dir DIR`.

## Worked example

The test fixtures double as a worked example:

```bash
python -m pcos_tools hygiene tests/fixtures/worklist_fixture.csv --out-dir out --today 2026-09-01
python -m pcos_tools recon_parse tests/fixtures/RECON_sample.md --out out/RECON_sample.json
python -m pcos_tools now_build --csv tests/fixtures/worklist_fixture.csv \
    --recon out/RECON_sample.json --prev tests/fixtures/PCOS_NOW_prev.md \
    --out-dir out --today 2026-09-01
python -m pcos_tools now_check --csv tests/fixtures/worklist_fixture.csv \
    --now tests/fixtures/PCOS_NOW_v3_gdocs.md --pending tests/fixtures/pending \
    --out-dir out --today 2026-09-01
python -m pcos_tools recon_parse tests/fixtures/RECON_v14_sample.md --out out/RECON_v14.json
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

The fixture worklist has 27 rows covering every Status value in `vocab.json`,
one malformed ID, one invalid-vocabulary row, one bad date, one near-duplicate
title pair, PERSONAL rows in every regenerated section, an `Active-Low` row with
a HIGH priority and a `Done-Candidate` row. The sample RECON has all six
sections; `RECON_v14_sample.md` has the runbook v1.4 layout;
`PCOS_NOW_v3_gdocs.md` is a narrative PCOS_NOW as Google Docs exports it, with
one example of every `now_check` finding; `pending/` holds one DELTA. All
fixture people, tasks, dates and paths are invented. Never add real business
data to this public repository.

`tests/test_agents_skills.py` checks the cards and skills. Each card must keep the
six parts in order. Each skill's frontmatter must follow the Agent Skills format.
Every source key must be defined, and every relative link must resolve. It also
fails on anything that looks like a Drive or Notion ID, an e-mail address or a
Drive or Notion link in `agents/` or `skills/`. `tests/test_retro_lane.py` pins
what the Retro lane and the ledger backtest fixed: the evening slot, five
questions with six tap options, the 90-day window, the read-everything gate, and
a backtest that is blind at the cut, capped at 200 threads and never asks Joe.

## Build the zip

```bash
python scripts/build_zip.py     # writes dist/pcos_tools_v0.3.zip
```

## Workflow

1. Export the Worklist to CSV and the current PCOS_NOW to Markdown; copy the
   unapplied business DELTA files into a folder.
2. Run `hygiene --pending`; the weekly AI pass applies the `STALE_ARCHIVE` and
   `DONE_PROMOTE` rows whose Action is `set-status`; `hold` rows wait for their
   DELTA; a human reviews the rest of `proposed_changes.csv`.
3. Run `now_check`; the closeout writer resolves each finding in the same pass
   (fix PCOS_NOW, fix the row, or leave it and record why).
4. Old layout only: run `recon_parse`, then `now_build`; review
   `PCOS_NOW_draft.md`; paste the accepted sections into the live PCOS_NOW.
5. Nothing is applied by these scripts. They never write to their inputs and
   refuse to write an output over an input path.
6. Keep real exports and drafts out of git: run with `--out-dir out` (ignored)
   and note that `.gitignore` also ignores `Worklist*.csv`, `RECON*.md`,
   `RECON*.json`, `PCOS_NOW*.md`, `DELTA*.md`, the `inbox/` and `pending/`
   folders and the draft and report file names at the repo root, so a real
   file dropped next to the code cannot be committed by accident. Output is safe to pipe or redirect: non-ASCII text is written as
   UTF-8.

## Limitations (v0.3)

- People and date extraction are regex heuristics; check them.
- `dd/mm/yyyy` dates are kept raw because the day/month order is ambiguous.
- Duplicate detection is pairwise over titles only (fine up to a few thousand rows).
- The previous PCOS_NOW must use numbered headings (`## 1 ...`, `# 1\. ...`)
  or bold numbered lines (`**1. ...**`) for its sections.
- `now_check` reads Task IDs, not meaning: it cannot tell that a paragraph is
  out of date if it cites no ID. `STATUS_MISMATCH` can misfire when a status
  word right after an ID describes something else; check the quoted line.
- `--pending` holds a row for any mention of its ID in a DELTA, including a
  passing reference.
