---
name: council-pc
description: Run a live PCOS council on Joe's PC in minutes. One brief goes to the Codex CLI, the Gemini CLI and a separate Claude process; each model then reviews and ranks the two answers it did not write, under letters, never names; the Claude Code session that started the run chairs by the council-board rules and writes Final and Dissent to a Council row. Use when Joe, at his PC, says "pc council" with a topic or a Council row. Not for scheduled or cloud runs (board council, council-github) or routine lane outputs (the checker).
compatibility: Runs only in Claude Code on Joe's PC, with Python 3.11 or newer, the Codex CLI signed in with the ChatGPT plan, the Gemini CLI with the GEMINI_API_KEY variable (free tier), the Claude Code CLI, and the Notion connector for the Council row.
metadata:
  version: "0.1"
  status: Candidate
  register: P2-08
  kernel: "1.2"
  card: agents/council-pc.md
---

# PC council

Three models answer the same brief, on Joe's PC, in a few minutes. No model
judges its own answer: each reviews and ranks the other two, and the chair is a
session that wrote none of them. Nobody carries text between apps; the script
does, and the Council row keeps the record.

Sources are named by key, written `[[KEY]]` (defined in `agents/INPUTS.md`, IDs
in the private map named there). The script is
[scripts/council_pc.py](../../scripts/council_pc.py) in this repository.

## 1. When to run it

- Joe starts it, at his PC, with "pc council: TOPIC" or "pc council row X" (a
  [[COUNCIL]] row in Status Plan or Draft). Nothing schedules it: the CLIs and
  their sign-ins live on Joe's PC, so a Routine or a cloud session cannot run
  it.
- Use it for judgment work that cannot wait for the daily board cycle (pricing
  assumptions, rule proposals, vendor terms, readings of a hard instruction,
  plans), and on build days. Routine lane outputs go to the checker; work that
  can wait a day goes to the board council; method and code work without Joe's
  PC goes to council-github.
- One round, no plan round: Joe is present, and the brief states the question,
  the facts and the method in one go (as council-github does).

## 2. The brief

Write the brief before anything else, as a new file in a new run folder on the
PC (never in this repository, never in Drive):

```
QUESTION: one or two sentences, what must be decided or produced.
WHY NOW: one line.
FACTS: each fact the answer needs, quoted as short as possible, with its
evidence label and its source key and ID as opened in this run.
DECIDED: answers already in [[DECISIONS]] and Live rows in [[RULES]] that
apply, quoted, so no answer reopens them.
WHAT A GOOD ANSWER COVERS: the parts, the format, the length.
LIMITS: never send, pay, commit a price or agree a vendor term.
```

1. Open every source the brief quotes in this run: the Council row and the
   sources it names, the Live rows in [[RULES]] and [[DECISIONS]]. Label each
   fact (Law 4); a fact from a source that was not opened is Needs Source
   Check.
2. The outside models cannot open Notion, Drive or mail. They answer from the
   brief and their own knowledge, so the brief carries every fact they need.
3. What leaves the PC: the brief and the answers go to OpenAI (Codex, under
   Joe's ChatGPT plan) and Google (Gemini, on a free API key whose terms may
   let Google read and use prompts to improve its products: Needs Source
   Check). Quote only what the question needs. Personal and Room 10 material
   never enters a brief.
4. Write no model name into the brief unless the question is about the models.

## 3. Run the script

From the repository folder on the PC:

```
python scripts/council_pc.py RUN-FOLDER/brief.md --out RUN-FOLDER/out
```

- Stage 1: the brief goes to the three seats at once: `codex exec` (read-only
  sandbox), `gemini -p` and `claude -p`, a separate Claude process, never this
  session (started without this session's `CLAUDECODE` marker, which some
  Claude Code versions refuse as a nested session). Each runs in an empty
  temporary folder with the prompt on stdin and 15 minutes per call.
- A 503 or overload answer (Gemini's usual failure) is retried twice, after 20
  and 40 seconds. Any other failure, a timeout or a CLI that is not installed
  is not retried; that seat is left out and the run goes on.
- Stage 2: the script removes self-identification (model, vendor and tool
  names the brief does not use), shuffles the answers under the letters A, B
  and C, and asks every seat that answered to review the answers it did not
  write: one finding per bullet with evidence and a verdict, then a ranking.
- It writes three files into the new folder: `bundle.md` (brief, answers,
  reviews and a pairwise ranking table, letters only), `authors.json` (letter
  to seat) and `run.json` (attempts, exit codes, times).
- Exit 3, Blocked: fewer than two answers. There is no bundle. Tell Joe which
  seats failed and why (from the script's last line and `run.json`), write
  nothing to [[COUNCIL]], write the heartbeat (section 5) and stop. A rerun is
  Joe's call.

## 4. Chair

The chair is this session. It wrote no answer. It follows council-board skill
section 5, with these differences:

1. Read `bundle.md` only. Do not open `authors.json` or `run.json` yet; the
   answers stay letters while you judge.
2. Answer each Fix or Reject finding in the reviews: accepted (with the
   change) or rejected (with the reason and the evidence from the brief).
3. Write Final: the execution-ready answer, built from the best-supported
   parts of the answers, every claim labeled. Anything external stays Needs
   Joe Approval and is never sent. The ranking is advice, not a vote: when
   Final departs from the undefeated answer, say why in Dissent.
4. Write Dissent: each point a reviewer still disputes, with the reason; the
   ranking in one line ("A undefeated, B 1 of 2, C 0 of 2"); each missing
   seat or review ("Seat without an answer: gemini (failed)", "Review by the
   author of Answer B missing"). Write "none" for the disputed points if there
   are none.
5. Status: Final, or Needs Joe only when the reviews disagree on a fact that
   neither the kernel nor the sources settle. Joe started the run, so ask him
   that one question here: the fact in one line, 2 or 3 options, your default
   first. His answer goes into Final with Joe as its source, and the Status is
   Final. If he does not answer in the session, the Status stays Needs Joe and
   the question goes to the next EXO card, as the board chair does it.
6. Only after Final and Dissent are written, open `authors.json` and
   `run.json`, and fill Author from them.

## 5. Write the Council row

1. Run the checker (job type council-final) on Final and Dissent, as a
   subagent on a different Claude model. On Fix, repair and re-check, at most 5
   rounds. Write to the row only after an Accept; with no Accept, write nothing
   and tell Joe the open findings.
2. The row: the one Joe named, read right before writing; otherwise a new row
   "TOPIC · pc council" with Deadline today. Fields:
   - Draft: the brief, then the answers as the bundle shows them (A, B, C).
   - Review-1: the reviews, each headed "Review by the author of Answer X".
   - Review-2: the ranking table and the undefeated line from the bundle.
   - Final, Dissent and Status from section 4.
   - Author: "PC council: A SEAT, B SEAT, C SEAT", written last.
3. One [[CHANGELOG]] row per field written, with the kernel version.
4. One heartbeat in [[LANES]] per run, Blocked runs included: lane
   council-pc, started, finished, kernel version, seats answered, reviews
   written, result. An on-demand lane: Health never counts a missed run.
5. A Notion write that fails is retried once. After that, the full row content
   goes into one DELTA file in [[INBOX_FOLDER]], labeled Blocked, and the run
   stops.
6. The run folder stays on the PC. It is never committed to [[REPO]] or
   uploaded to Drive; the Council row is the record.

## Never

- Schedule this council, or start it from a Routine or a cloud session.
- Chair from a session that wrote one of the answers, or let the Claude seat
  run inside this session.
- Let a seat review or rank its own answer, or show a seat name to a reviewer.
- Open `authors.json` or `run.json` before Final and Dissent are written.
- Send, pay, commit a price or agree a vendor term from a council run.
- Put a brief, an answer or a run file into this public repository.
- Sign the Gemini CLI in with a consumer Google login: the API key only. Google
  withdrew the consumer login for the Gemini CLI on 2026-06-18 (dev-session
  record of 2026-09-27, turn 2).
- Add Grok to the run: it is manual paste only.
