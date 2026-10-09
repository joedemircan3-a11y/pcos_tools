# Card: council-pc

- Version: v0.1
- Status: Candidate
- Register: P2-08 (PC CLI council: "codex exec" and "gemini -p" on Joe's PC, anonymized cross-rank, chair)
- Lane ID: pending
- Skills: [council-pc v0.1](../skills/council-pc/SKILL.md), which runs [scripts/council_pc.py](../scripts/council_pc.py); the chair follows [council-board v0.1](../skills/council-board/SKILL.md) section 5; the Final is checked with [checker v0.1](../skills/checker/SKILL.md) (job type council-final)
- Date: 2026-10-09

## 1. Mission

Give urgent judgment work a three-model council in minutes while Joe is at his
PC: one brief to Codex, Gemini and a separate Claude process, each answer
reviewed and ranked by the two models that did not write it, then chaired into
Final and Dissent on a Council row. No copy and paste between apps.

Never: run on a schedule or from the cloud; let a model review its own answer;
chair from a session that wrote an answer; open the letter-to-seat map before
Final and Dissent are written; send, pay, commit a price or agree a vendor
term; put a brief, an answer or a run file into the public repository.

## 2. Inputs by ID

- L0, always loaded: [[KERNEL]].
- L1: the [[COUNCIL]] row Joe names, or his topic for a new row.
- L2, for the brief: the sources the row or the topic names, by key and ID;
  Live rows in [[RULES]]; [[DECISIONS]]. Each fact the brief quotes is opened
  in this run.
- L2, before any question reaches Joe (kernel section 2, step 4): [[REGISTRY]],
  the operating document registry, with the other records that step names, so
  that no question asks what a registered document already answers.
- The run folder on the PC: `bundle.md` for the chair, then `authors.json`
  and `run.json` after Final and Dissent.
- Knowledge scope: what the question needs, quoted into the brief; the outside
  models open nothing themselves. Personal and Room 10 material is out of
  scope.

## 3. Tools allowed

- Terminal on Joe's PC: `python scripts/council_pc.py`, which starts the
  Codex CLI (read-only sandbox, apps off), the Gemini CLI (every tool denied)
  and the Claude Code CLI (no tools, no MCP servers) in an empty temporary
  folder and writes only into the new run folder. Open risk (Candidate, for
  Joe): Codex has no switch for its shell, so a prompt could lead it to read
  a file on the PC.
- A checker subagent on a different Claude model.
- Notion: write Task, Draft, Review-1, Review-2, Final, Dissent, Status,
  Deadline and, last, Author on the one [[COUNCIL]] row; [[CHANGELOG]] rows;
  one heartbeat in [[LANES]].
- Drive: one Blocked DELTA file in [[INBOX_FOLDER]] when the Notion write fails
  twice.
- Not allowed: send mail or messages; commit a price, payment or vendor term;
  edit or delete files outside the run folder; commit the run folder to
  [[REPO]]; change another Council row; sign the Gemini CLI in with a consumer
  Google login; add Grok.

## 4. Rules and kernel version

- Kernel 1.2. The mismatch rule and the live-rules fallback are in
  [CARD_TEMPLATE](CARD_TEMPLATE.md).
- Laws 4, 5, 8, 10 and 11.
- Lane rules, from the dev-session record of 2026-09-27 (turns 2 and 3,
  accepted by default by Joe; register P2-08):
  - Mechanism B, the live council on the PC: a Claude Code skill runs
    "codex exec" and "gemini -p", collects the answers, strips names,
    cross-ranks, chairs and writes Notion, in 3 to 8 minutes.
  - Models rank their own answers higher, so the judge is never the author.
  - Codex signs in with the ChatGPT plan; Gemini uses a free API key (the
    consumer login was withdrawn on 2026-06-18). Grok stays manual paste.
- Queue rules (QUEUE_v4 item QC22): each model ranks the other two; the chair
  follows the council-board skill; a Gemini 503 is retried twice; it runs only
  when Joe starts it on his PC, nothing is scheduled.
- Board rules apply: one finding per bullet with evidence and a verdict; Needs
  Joe only for a factual disagreement the kernel and the sources cannot settle.

## 5. Output contract with evidence labels

- [[COUNCIL]] row: Draft = the brief and the answers A, B and C; Review-1 = the
  cross-reviews, each headed by the letter of its author's answer; Review-2 =
  the ranking table; Final; Dissent (disputed points, the ranking line, missing
  seats and reviews); Status Final or Needs Joe; Author written last, after
  Final and Dissent.
- Evidence labels: every fact in the brief and every claim in Final carries
  one. A claim is Confirmed only when a source opened in this run states it;
  the outside models' claims are Candidate until then. Anything external stays
  Needs Joe Approval.
- Run record: the script's `run.json` (attempts, exit codes, times per seat),
  sources opened (keys and IDs), kernel version; one Changelog row per field;
  one Lanes heartbeat per run.
- Done means: the row says Final or Needs Joe, or the run stopped Blocked
  (fewer than two answers, or no checker Accept) with Joe told why.
- Eval: minutes from brief to Final (target 3 to 8); seats missing per run;
  Finals that Joe overturns, logged in [[CORRECTIONS]].

## 6. Trigger and owner model

- Trigger: on demand only, "pc council: TOPIC" or "pc council row X", said by
  Joe at his PC; never scheduled.
- Runs on: Claude Code on Joe's PC, with the Codex, Gemini and Claude Code
  CLIs installed there (installed at PC-1).
- Model: answerers Codex (ChatGPT plan), Gemini (free API key) and Claude in a
  separate process; chair Claude, the session Joe started, which writes no
  answer; checker on a different Claude model.
- Owner: Claude lanes. Joe starts each run and answers at most one Needs Joe
  question in the session.
- Escalation: one question in the session, or the next EXO card when Joe does
  not answer it there.
- Depends on: Codex CLI sign-in, the GEMINI_API_KEY variable and the Claude
  Code CLI on Joe's PC; [[COUNCIL]], [[CHANGELOG]], [[LANES]] (exist); a
  Lanes row for council-pc before the first run.

## Change note

v0.1 | 2026-10-09 | Claude Code on the web, PCOS queue item QC22 | first card |
register P2-08; design in the dev-session record of 2026-09-27, turns 2 and 3 |
Joe's default acceptance 2026-09-28; PCOS QUEUE_v4 item QC22, carried in
QUEUE_v8
