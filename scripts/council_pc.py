"""PC council runner (register P2-08): one brief, three model CLIs on Joe's PC.

Stage 1 sends the brief to each seat (``codex exec``, ``gemini -p``, ``claude -p``)
and collects the answers. Stage 2 strips self-identification, shuffles the answers
under the letters A, B and C, and asks every seat that answered to review and rank
the answers it did not write. The bundle is the chair's input: the Claude Code
session that started the run wrote no answer, chairs by
skills/council-pc/SKILL.md, and opens authors.json and run.json only after it has
written Final and Dissent.

Standard library only. This script is not part of the draft-only toolkit: the
CLIs it starts call their vendors over the network. It writes nothing to Notion,
Drive or mail; it reads the brief and writes bundle.md, authors.json and run.json
into a new output folder. Each CLI runs in a fresh temporary folder that holds
only the brief, with a scratch home that holds only a copy of its own sign-in
file, so it never sees the files around it or Joe's settings, MCP servers and
history. When a CLI refreshes its sign-in during the run, the refreshed file goes
back to where the CLI keeps it, so the real sign-in keeps working.

Usage: python scripts/council_pc.py BRIEF.md --out FOLDER
Exit codes: 0 bundle written; 2 usage error; 3 Blocked (fewer than two answers,
bundle not written; run.json says why).
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

LAST_MESSAGE = "{last_message}"  # replaced by a file path; the answer is read from that file
NO_TOOLS = "{no_tools_policy}"  # replaced by a Gemini policy file that denies every tool
FOLLOW = "Follow the instructions above."  # the stdin text comes first; -p appends this line
NO_TOOLS_POLICY = """\
[[rule]]
toolName = "*"
decision = "deny"
priority = 999
denyMessage = "A council seat answers from the prompt alone, without tools."
"""

# The prompt always goes on stdin: a Windows .cmd shim caps the command line at 8,191
# characters, and a brief with two answers is longer than that. Each seat answers from
# the prompt alone, so its host tools are switched off: Claude gets no built-in tools
# and no MCP servers, Gemini a policy that denies every tool. Codex's read-only sandbox
# blocks writes but not reads, so Codex gets no tool that reads a file: shell_tool off
# removes its shell (exec_command and write_stdin, also inside its JavaScript tool and
# in the agents it spawns), view_image off its image reader. What stays is
# apply_patch, which the sandbox and the approval policy stop from writing. An
# unknown feature name stops codex with an error, so a renamed flag fails the seat
# instead of giving it a shell back. Checked against codex-cli 0.162.0.
SEATS = {
    "codex": ["codex", "exec", "--skip-git-repo-check", "--ephemeral", "--ignore-user-config",
              "--sandbox", "read-only", "--disable", "apps", "--disable", "shell_tool",
              "--disable", "view_image", "--output-last-message", LAST_MESSAGE, "-"],
    "gemini": ["gemini", "--skip-trust", "--policy", NO_TOOLS, "-p", FOLLOW],
    # --tools takes a list, so it comes last, after the prompt argument.
    "claude": ["claude", "-p", FOLLOW, "--strict-mcp-config", "--tools", ""],
}
BRIEF_FILE = "brief.md"  # the one file in a seat's working folder
# The one file a seat's scratch home carries: its CLI's sign-in, copied from where the
# CLI keeps it, as (variable that moves the folder, folder under the home, file).
# Gemini signs in with GEMINI_API_KEY and needs no file.
SIGN_IN = {
    "codex": ("CODEX_HOME", ".codex", "auth.json"),
    "claude": ("CLAUDE_CONFIG_DIR", ".claude", ".credentials.json"),
}
GEMINI_KEY = "GEMINI_API_KEY"
# The value as dotenv reads it, as the Gemini CLI does: quoted, or bare up to a # comment.
GEMINI_KEY_LINE = re.compile(rf"^[ \t]*(?:export[ \t]+)?{GEMINI_KEY}[ \t]*=[ \t]*"
                             r"('(?:\\'|[^'])*'|\"(?:\\\"|[^\"])*\"|`(?:\\`|[^`])*`|[^#\r\n]*)", re.M)
# Variables that would make a seat's CLI read a file into its prompt, load settings from
# outside the scratch home, or join an IDE that shares the open files (checked against
# gemini 0.63.0, Claude Code 2.1.296 and codex-cli 0.162.0). No seat inherits them.
SEAT_ENV_DROP = re.compile(
    r"GEMINI_SYSTEM_MD|GEMINI_WRITE_SYSTEM_MD|GEMINI_CLI_SYSTEM_SETTINGS_PATH|GEMINI_CLI_SYSTEM_DEFAULTS_PATH"
    r"|GEMINI_CLI_TRUSTED_FOLDERS_PATH|GEMINI_CLI_IDE_\w+|CLAUDE_CODE_SSE_PORT|ENABLE_IDE_INTEGRATION"
    r"|CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD|CODEX_SQLITE_HOME", re.I)
LABELS = "ABC"
TIMEOUT = 900       # seconds per call
RETRIES = 2         # extra attempts after a transient failure (Gemini's 503)
RETRY_WAIT = 20     # seconds before the first retry; the second waits twice as long

TRANSIENT = re.compile(r"\b503\b|\bUNAVAILABLE\b|high demand|overloaded", re.I)
ANSI = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")
NOISE = re.compile(r"^(Loaded cached credentials\.?)\s*$", re.I)

# Self-identification is always removed, whatever the brief says. Model and vendor
# names are replaced too, but only when the brief does not use them: a brief about
# the models makes them content ("such as Gemini", "Claude costs more" stay).
MODEL_NAMES = r"(?:Claude|Codex|ChatGPT|GPT(?:-[\w.]+)?|Gemini|Bard)"
VENDOR_NAMES = r"(?:Anthropic|OpenAI|Google(?: DeepMind)?|DeepMind)"
IDENTITY = rf"(?:{MODEL_NAMES}|{VENDOR_NAMES})"
VERSION = r"(?:\s+(?:\d[\w.]*|Code|CLI|Opus|Sonnet|Haiku|Fable|Pro|Flash|Ultra))*"
# A self-introduction counts only at the start of a line or a sentence.
START = r"(^[ \t>*#-]*|[.!?;:][ \t]+)"
# The end of an identity clause: a short appositive ("an assistant") and the sentence end,
# or ", and", a comma, or the next word. The rest of the sentence is kept.
CLAUSE_END = r"(?:,\s+(?:an?|the)\s+[^.!?,\n]{0,60}?[.!?]|[.!?]|,?\s+and\b|,|(?=\s)|$)[ \t]*"
# "As X" introduces the writer only when a comma or "I", "we" or "my" follows.
SPEAKER = r"(?:,|(?=\s+(?:I|we|my)\b))"
SELF_ID = [  # (pattern, replacement); each runs on one line
    # I am Claude. / I'm an OpenAI model, so ... / I am Codex, an assistant. / I am Claude, and ...
    # Only the identity clause goes; what follows it in the sentence stays.
    (re.compile(rf"\bI(?: am|'m|’m)\s+(?:an?\s+|the\s+)?{IDENTITY}{VERSION}(?:\s+(?:model|assistant))?\b"
                rf"{CLAUSE_END}", re.I), ""),
    # My name is Gemini.
    (re.compile(rf"\bmy name is\s+{MODEL_NAMES}{VERSION}\b{CLAUSE_END}", re.I), ""),
    # As Claude, ... / As Codex I ... / As a Gemini model, ...
    (re.compile(rf"{START}as\s+(?:an?\s+|the\s+)?{MODEL_NAMES}{VERSION}"
                rf"(?:\s+(?:model|assistant)\b)?{SPEAKER}[ \t]*", re.I), r"\1"),
    # As an OpenAI model, ... / As the Google assistant I ...
    (re.compile(rf"{START}as\s+(?:an?\s+|the\s+)?{VENDOR_NAMES}(?:\s+[\w.-]+)*?\s+(?:model|assistant|AI|system)\b"
                rf"{SPEAKER}[ \t]*", re.I), r"\1"),
    # As an AI language model, ...
    (re.compile(rf"{START}as an? (?:AI(?:\s+(?:language\s+)?(?:model|assistant))?|(?:large\s+)?language\s+model)"
                r"\b,?[ \t]*", re.I), r"\1"),
    # Claude here: ... / This is Gemini speaking. / This is Codex.
    (re.compile(rf"{START}(?:this is\s+)?{MODEL_NAMES}{VERSION}\s+(?:here|speaking)[:,.!—-][ \t]*", re.I), r"\1"),
    (re.compile(rf"{START}this is\s+{MODEL_NAMES}{VERSION}\s*(?:[,.:!]|$)[ \t]*", re.I), r"\1"),
    # I, Claude, think ...
    (re.compile(rf"(?<=\bI),\s+{MODEL_NAMES}{VERSION},", re.I), ""),
    # I was trained by Google.
    (re.compile(rf"\bI(?: am|'m|’m| was)\s+(?:an?\s+[\w -]*?\s*)?(?:made|developed|trained|built|created) by "
                rf"{VENDOR_NAMES}\b[.,]?[ \t]*", re.I), ""),
    # A signature line: "— Claude", "-- Gemini 2.5 Pro"
    (re.compile(rf"^[ \t]*(?:—|--)[ \t]*{IDENTITY}\b.*$", re.I), ""),
]
NAMES = [(name, re.compile(pattern, re.I)) for name, pattern in [
    ("Claude", r"\bClaude(?:\s+(?:Code|Opus|Sonnet|Haiku|Fable))?(?:\s+\d+(?:\.\d+)*)?\b"),
    ("Codex", r"\bCodex\b"),
    ("ChatGPT", r"\bChatGPT\b"),
    ("GPT", r"\bGPT(?:-[\w.]+)?\b"),
    ("Gemini", r"\bGemini(?:\s+\d+(?:\.\d+)*)?(?:\s+(?:Pro|Flash|Ultra))?\b"),
    ("Bard", r"\bBard\b"),
    ("Anthropic", r"\bAnthropic\b"),
    ("OpenAI", r"\bOpenAI\b"),
    ("DeepMind", r"\b(?:Google )?DeepMind\b"),
]]
RANKING = re.compile(r"^[\s*_#>-]*RANKING[\s*_]*:[\s*_]*(.*?)[\s*_]*$", re.I | re.M)

ANSWER_PROMPT = """\
You are one of three independent answerers in a council. Two other answerers, unknown to
you, get the same brief. Each answerer then reviews and ranks the others' answers, and a
chair writes the final answer.

Rules:
- Answer the brief below directly and completely, from the brief and your own knowledge.
- Do not run a council, a skill or any tool that calls another model, and do not create,
  change or delete any file.
- Do not name yourself, your model, your vendor or your tool anywhere in the answer.
- Label every claim with one evidence label: Confirmed (a source opened in this run, or
  quoted in the brief with its key and ID, states it), Candidate (inference, plan,
  proposal), Needs Source Check, Needs Thread Check, Needs Joe Approval (anything external
  or committing: a send, price, payment, vendor term), Blocked.
- Never send, pay, commit a price or agree a vendor term; anything like that stays Needs
  Joe Approval.

BRIEF
{brief}
END OF BRIEF
"""

REVIEW_PROMPT = """\
You are a reviewer in a council. Below are a brief and {count} written by other
answerers. You do not know who wrote them, and you must not try to find out.

For each answer, write one finding per bullet:
- POINT | evidence: the line of the brief or the answer that shows it | verdict for this
  point: Accept, Fix or Reject
Check in particular: claims without support in the brief, wrong evidence labels
(Confirmed needs a quoted or opened source that states it), rules applied wrongly,
anything that would send, pay or commit, and what the answer misses.
End each answer's findings with: Overall: Accept, Fix or Reject.

Then rank the answers on one last line, best first, each letter once, in this form:
RANKING: {example}
Rank on correctness first, then completeness, then use to the person who must act on it.
If an answer still names the model that wrote it, ignore the name and judge the content.
Do not name yourself, your model, your vendor or your tool.

BRIEF
{brief}
END OF BRIEF

{answers}
"""


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def clean(text):
    """CLI output without colour codes, known banner lines and outer blank lines."""
    lines = ANSI.sub("", text).replace("\r\n", "\n").split("\n")
    while lines and (not lines[0].strip() or NOISE.match(lines[0])):
        lines.pop(0)
    return "\n".join(lines).strip()


def anonymize(text, brief):
    """Return (text without self-identification, number of removals).

    Works line by line and tidies only the lines it changed, so indentation, tables
    and code elsewhere keep their spacing.
    """
    names = [pattern for name, pattern in NAMES if not re.search(rf"\b{re.escape(name)}\b", brief, re.I)]
    count, lines = 0, []
    for line in text.split("\n"):
        new = line
        for pattern, replacement in SELF_ID:
            new, n = pattern.subn(replacement, new)
            count += n
        for pattern in names:
            new, n = pattern.subn("[model]", new)
            count += n
        if new != line:
            indent = line[:len(line) - len(line.lstrip())]
            new = indent + re.sub(r"[ \t]{2,}", " ", new.strip())
        lines.append(new)
    return "\n".join(lines).strip(), count


def gemini_key():
    """GEMINI_API_KEY from the environment, else from the Gemini CLI's own .env files."""
    if os.environ.get(GEMINI_KEY):
        return os.environ[GEMINI_KEY]
    for path in (Path.home() / ".gemini" / ".env", Path.home() / ".env"):
        try:
            found = GEMINI_KEY_LINE.findall(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError):
            continue
        if found:
            value = found[-1].strip()
            if len(value) > 1 and value[0] == value[-1] and value[0] in "'\"`":
                value = value[1:-1]
            return value or None
    return None


def seat_env(name, home):
    """Joe's environment with every home and config folder moved into the scratch home."""
    # The chair's Claude Code session sets CLAUDECODE; some Claude Code versions refuse to
    # start "claude -p" as a nested session while it is set. The seat is a separate process.
    env = {key: value for key, value in os.environ.items()
           if key != "CLAUDECODE" and not SEAT_ENV_DROP.fullmatch(key)}
    env.update({
        "CLAUDE_CODE_DISABLE_CLAUDE_MDS": "1",  # no CLAUDE.md, also none above the working folder
        "HOME": str(home), "USERPROFILE": str(home),  # Node and Python read USERPROFILE on Windows
        "CODEX_HOME": str(home / ".codex"), "CLAUDE_CONFIG_DIR": str(home / ".claude"),
        "GEMINI_CLI_HOME": str(home),
        "XDG_CONFIG_HOME": str(home / ".config"), "XDG_DATA_HOME": str(home / ".local" / "share"),
        "XDG_STATE_HOME": str(home / ".local" / "state"), "XDG_CACHE_HOME": str(home / ".cache"),
    })
    # The scratch home hides ~/.gemini/.env, where the Gemini CLI may keep its key.
    key = gemini_key() if name == "gemini" else None
    if key:
        env[GEMINI_KEY] = key
    return env


def copy_sign_in(name, home):
    """Copy the seat's sign-in file into the scratch home.

    Returns (copied, notes): copied is [(real path, copy, bytes)], notes go to run.json.
    """
    if name not in SIGN_IN:
        return [], {}
    variable, folder, filename = SIGN_IN[name]
    real = (Path(os.environ[variable]) if os.environ.get(variable) else Path.home() / folder) / filename
    try:
        data = real.read_bytes()
    except OSError:
        return [], {filename: "not found where the CLI keeps it; the seat starts signed out"}
    copy = home / folder / filename
    copy.parent.mkdir(parents=True, exist_ok=True)
    copy.write_bytes(data)
    return [(real, copy, data)], {}


def return_sign_in(copied):
    """Put a sign-in the CLI refreshed during the run back where the CLI keeps it.

    A refresh token can be good for one use only, so a refreshed copy thrown away with
    the scratch home would leave the real sign-in dead. Only a complete JSON file goes
    back, and only when nothing else changed the real file during the run. Neither CLI
    offers a lock to share, so that check comes last, right before the replace: a
    refresh by another process in that instant is the one write that could still be lost.
    """
    notes = {}
    for real, copy, before in copied:
        try:
            after = copy.read_bytes()
        except OSError:
            continue
        if after == before:
            continue
        temp = None
        try:
            json.loads(after)
            # A staging file of its own, next to the real one: another council run may be
            # writing back the same sign-in at the same time.
            handle, name = tempfile.mkstemp(dir=real.parent, prefix=f"{real.name}.", suffix=".council-pc")
            temp = Path(name)
            with os.fdopen(handle, "wb") as staged:
                staged.write(after)
            shutil.copymode(real, temp)
            if real.read_bytes() == before:
                os.replace(temp, real)
                notes[real.name] = "refreshed in the run and written back"
            else:
                notes[real.name] = "refreshed in the run; the real file changed too, so it was kept"
        except ValueError:
            notes[real.name] = "changed in the run but not complete JSON; not written back"
        except OSError as exc:
            notes[real.name] = f"refreshed in the run; writing it back failed: {exc}"[:300]
        finally:
            try:
                if temp is not None:
                    temp.unlink(missing_ok=True)  # gone already after a replace
            except OSError:
                pass
    return notes


def run_one(args, prompt, timeout, workdir, env):
    """One CLI run with the prompt on stdin. Returns (exit code, stdout, stderr).

    On timeout the whole process tree is killed before TimeoutExpired is raised: on
    Windows the CLI is a .cmd shim whose node child would otherwise keep the pipes
    open and hang the run.
    """
    windows = os.name == "nt"
    proc = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, encoding="utf-8", errors="replace", cwd=workdir, env=env,
                            start_new_session=not windows)
    try:
        stdout, stderr = proc.communicate(prompt, timeout=timeout)
    except subprocess.TimeoutExpired:
        if windows:
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(proc.pid)], capture_output=True)
        else:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        proc.kill()
        try:
            proc.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            pass
        raise
    return proc.returncode, stdout, stderr


def call(name, argv, prompt, brief, timeout, retries, retry_wait):
    """Run one seat's CLI with the prompt on stdin. Returns (text, record); text is None on failure.

    Every attempt gets a new working folder that holds only the brief and a new scratch
    home that holds only the seat's sign-in file.
    """
    record = {"attempts": [], "status": None}
    program = shutil.which(argv[0])
    if program is None:
        record["status"] = "not found"
        record["error"] = f"{argv[0]} is not on PATH"
        return None, record
    for attempt in range(retries + 1):
        if attempt:
            time.sleep(retry_wait * attempt)
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as workdir, \
                tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as homedir, \
                tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as outdir:
            (Path(workdir) / BRIEF_FILE).write_text(brief, encoding="utf-8")
            home = Path(homedir)
            for _, folder, _ in SIGN_IN.values():  # codex stops if CODEX_HOME does not exist
                (home / folder).mkdir()
            copied, notes = copy_sign_in(name, home)
            last = Path(outdir) / "last_message.txt"
            policy = Path(outdir) / "no_tools.toml"
            policy.write_text(NO_TOOLS_POLICY, encoding="utf-8")
            files = {LAST_MESSAGE: str(last), NO_TOOLS: str(policy)}
            args = [program, *(files.get(a, a) for a in argv[1:])]
            started = time.monotonic()
            try:
                returncode, stdout, stderr = run_one(args, prompt, timeout, workdir, seat_env(name, home))
            except subprocess.TimeoutExpired:
                record["attempts"].append({"exit": None, "seconds": round(time.monotonic() - started, 1)})
                record["status"] = "timeout"
                record["error"] = f"no answer within {timeout} seconds"
                return None, record
            except OSError as exc:
                record["attempts"].append({"exit": None, "seconds": round(time.monotonic() - started, 1)})
                record["status"] = "failed"
                record["error"] = str(exc)[:300]
                return None, record
            finally:  # also after a timeout: the CLI may have refreshed its sign-in first
                notes.update(return_sign_in(copied))
                if notes:
                    record.setdefault("sign_in", {}).update(notes)
            text = last.read_text(encoding="utf-8", errors="replace") if last.is_file() else ""
            text = clean(text) or clean(stdout)
        record["attempts"].append({"exit": returncode, "seconds": round(time.monotonic() - started, 1)})
        if returncode == 0 and text:
            record["status"] = "ok"
            return text, record
        output = f"{stderr}\n{stdout}"
        record["error"] = clean(output)[-300:]
        if TRANSIENT.search(output) and attempt < retries:
            continue
        record["status"] = "failed" if returncode else "empty"
        return None, record
    return None, record  # not reached


def parse_ranking(text, letters):
    """The letters of the last RANKING line, best first, or None unless it ranks exactly letters."""
    found = RANKING.findall(text)
    if not found:
        return None
    ranked = [re.sub(r"[^A-Za-z]", "", part).upper() for part in found[-1].split(">")]
    if sorted(ranked) != sorted(letters) or len(set(ranked)) != len(ranked):
        return None
    return ranked


def tally(rankings, labels):
    """Per label: first places, pairwise wins and losses, and how many rankings include it."""
    table = {label: {"first": 0, "wins": 0, "losses": 0, "ranked_by": 0} for label in labels}
    for ranked in rankings:
        for position, label in enumerate(ranked):
            table[label]["ranked_by"] += 1
            if position == 0 and len(ranked) > 1:
                table[label]["first"] += 1
            table[label]["wins"] += len(ranked) - position - 1
            table[label]["losses"] += position
    return table


def beaten(rankings):
    """The set of (winner, loser) pairs the rankings show."""
    return {(ranked[i], ranked[j]) for ranked in rankings
            for i in range(len(ranked)) for j in range(i + 1, len(ranked))}


def missing_pairs(rankings, labels):
    """Pairs of answers that no parsed ranking compares."""
    seen = {frozenset(pair) for pair in beaten(rankings)}
    return [(a, b) for i, a in enumerate(labels) for b in labels[i + 1:] if frozenset((a, b)) not in seen]


def undefeated(rankings, labels):
    """Labels compared with every other answer and never ranked below one."""
    pairs = beaten(rankings)
    return [label for label in labels if len(labels) > 1
            and all((label, other) in pairs and (other, label) not in pairs
                    for other in labels if other != label)]


def review_prompt(brief, answers, letters):
    blocks = "\n\n".join(f"ANSWER {label}\n{answers[label]}\nEND OF ANSWER {label}" for label in letters)
    count = "one answer" if len(letters) == 1 else f"{len(letters)} answers"
    # The example names no real letter, so no order is suggested.
    return REVIEW_PROMPT.format(count=count, example=" > ".join("LETTER" for _ in letters),
                                brief=brief, answers=blocks)


def run_parallel(jobs, brief, timeout, retries, retry_wait):
    """jobs: {name: (argv, prompt)}. Returns {name: (text, record)}."""
    with ThreadPoolExecutor(max_workers=max(1, len(jobs))) as pool:
        futures = {name: pool.submit(call, name, argv, prompt, brief, timeout, retries, retry_wait)
                   for name, (argv, prompt) in jobs.items()}
        return {name: future.result() for name, future in futures.items()}


def write_bundle(path, brief, answers, removed, reviews, rankings, missing_seats, started, finished):
    lines = [
        "# PC council bundle",
        "",
        "For the chair only. Answers and reviews carry letters, never seat names. Write Final and",
        "Dissent (skills/council-pc/SKILL.md section 4) before opening authors.json or run.json.",
        "",
        f"- Run: {started} to {finished}",
        f"- Answers: {len(answers)} ({', '.join(answers)})",
        f"- Seats without an answer: {', '.join(missing_seats) if missing_seats else 'none'}",
        f"- Reviews: {sum(1 for r in reviews.values() if r['text'])} of {len(reviews)} written, "
        f"{sum(1 for r in reviews.values() if r['ranking'])} rankings parsed",
        "- Self-identification removed: " + ", ".join(f"{label} {removed[label]}" for label in answers),
        "",
        "## Brief",
        "",
        brief,
        "",
    ]
    for label, text in answers.items():
        lines += [f"## Answer {label}", "", text, "", f"(end of Answer {label})", ""]
    lines += ["## Reviews", ""]
    for author, review in reviews.items():
        reviewed = " and ".join(review["letters"])
        lines += [f"### Review by the author of Answer {author}, of {reviewed}", ""]
        if review["text"] is None:
            lines += ["Review missing: the seat gave no review.", ""]
            continue
        lines += [review["text"], ""]
        ranking = " > ".join(review["ranking"]) if review["ranking"] else "not parsed"
        lines += [f"Ranking read: {ranking}", "", f"(end of the review by the author of Answer {author})", ""]
    lines += [
        "## Ranking",
        "",
        "Pairwise wins and losses over the parsed rankings; a ranking never includes its",
        "author's own answer. Advice for the chair, not a vote.",
        "",
        "| Answer | First places | Pairwise wins | Pairwise losses | Ranked by |",
        "| --- | --- | --- | --- | --- |",
    ]
    labels = list(answers)
    for label, row in tally(rankings, labels).items():
        lines.append(f"| {label} | {row['first']} | {row['wins']} | {row['losses']} | {row['ranked_by']} |")
    best = undefeated(rankings, labels)
    gaps = missing_pairs(rankings, labels)
    lines += ["", f"Undefeated: {', '.join(best) if best else 'none (no answer was compared with every other and won)'}"]
    if gaps:
        lines.append("Comparisons missing (a review or its ranking is missing): "
                     + ", ".join(f"{a} and {b}" for a, b in gaps))
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_seat(text):
    name, sep, command = text.partition("=")
    if not sep or name not in SEATS:
        raise argparse.ArgumentTypeError(f"expected SEAT=COMMAND with SEAT one of {', '.join(SEATS)}, got {text!r}")
    command = command.strip()
    try:
        argv = json.loads(command) if command.startswith("[") else shlex.split(command)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"cannot read the command for {name}: {exc}") from exc
    if not argv or not all(isinstance(a, str) for a in argv):
        raise argparse.ArgumentTypeError(f"the command for {name} is empty")
    return name, argv


def non_negative(kind):
    def convert(text):
        try:
            value = kind(text)
        except ValueError as exc:
            raise argparse.ArgumentTypeError(f"expected a number, got {text!r}") from exc
        if value < 0:
            raise argparse.ArgumentTypeError(f"expected 0 or more, got {text}")
        return value
    return convert


def build_parser():
    parser = argparse.ArgumentParser(
        prog="python scripts/council_pc.py",
        description="PC council: one brief to codex, gemini and claude; anonymous cross-ranking; "
                    "a bundle for the chair. Writes nothing outside the output folder, except a "
                    "sign-in a CLI refreshed during the run, written back to that CLI's own file.")
    parser.add_argument("brief", type=Path, help="the brief, a UTF-8 text or markdown file")
    parser.add_argument("--out", type=Path, required=True,
                        help="new output folder for bundle.md, authors.json and run.json")
    parser.add_argument("--seat", type=parse_seat, action="append", default=[], metavar="SEAT=COMMAND",
                        help="replace a seat's command (codex, gemini or claude); a JSON list or a "
                             "shell-style string; the prompt goes on stdin; {last_message} becomes a "
                             "file the CLI writes its answer to")
    parser.add_argument("--timeout", type=non_negative(int), default=TIMEOUT,
                        help=f"seconds per call (default {TIMEOUT})")
    parser.add_argument("--retries", type=non_negative(int), default=RETRIES,
                        help=f"extra attempts after a 503 or overload answer (default {RETRIES})")
    parser.add_argument("--retry-wait", type=non_negative(float), default=RETRY_WAIT,
                        help=f"seconds before the first retry, doubled for the second (default {RETRY_WAIT})")
    parser.add_argument("--seed", type=int, default=None, help="fix the letter order (tests only)")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        brief = args.brief.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeDecodeError) as exc:
        print(f"error: cannot read the brief: {exc}", file=sys.stderr)
        return 2
    if not brief:
        print("error: the brief is empty", file=sys.stderr)
        return 2
    if args.out.exists() and (not args.out.is_dir() or any(args.out.iterdir())):
        print(f"error: {args.out} is not an empty folder; use a new folder for each run", file=sys.stderr)
        return 2
    args.out.mkdir(parents=True, exist_ok=True)
    seats = {**SEATS, **dict(args.seat)}
    started = utc_now()
    record = {"started": started, "seats": {name: {"command": argv[0]} for name, argv in seats.items()}}
    policy = (args.timeout, args.retries, args.retry_wait)

    # Stage 1: every seat answers the brief.
    prompt = ANSWER_PROMPT.format(brief=brief)
    results = run_parallel({name: (argv, prompt) for name, argv in seats.items()}, brief, *policy)
    answered = [name for name in seats if results[name][0] is not None]
    for name in seats:
        record["seats"][name]["answer"] = results[name][1]
    missing = [f"{name} ({results[name][1]['status']})" for name in seats if name not in answered]
    if len(answered) < 2:
        record["finished"] = utc_now()
        record["outcome"] = "Blocked: fewer than two answers"
        (args.out / "run.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
        print(f"Blocked: {len(answered)} answer(s); no answer from {', '.join(missing)}. "
              f"See {args.out / 'run.json'}.")
        return 3

    # Letters in random order, so the seat order never shows through.
    rng = random.Random(args.seed) if args.seed is not None else random.SystemRandom()
    order = answered[:]
    rng.shuffle(order)
    authors = {LABELS[i]: name for i, name in enumerate(order)}
    label_of = {name: label for label, name in authors.items()}
    answers, removed = {}, {}
    for label, name in authors.items():
        answers[label], removed[label] = anonymize(results[name][0], brief)

    # Stage 2: every seat that answered reviews and ranks the answers it did not write.
    jobs, letters_of = {}, {}
    for name in answered:
        letters = [label for label in answers if label != label_of[name]]
        letters_of[name] = letters
        jobs[name] = (seats[name], review_prompt(brief, answers, letters))
    reviewed = run_parallel(jobs, brief, *policy)
    reviews = {}
    for label in answers:
        name = authors[label]
        text, review_record = reviewed[name]
        record["seats"][name]["review"] = review_record
        cleaned = anonymize(text, brief)[0] if text is not None else None
        ranking = parse_ranking(cleaned, letters_of[name]) if cleaned else None
        reviews[label] = {"letters": letters_of[name], "text": cleaned, "ranking": ranking}
    rankings = [r["ranking"] for r in reviews.values() if r["ranking"]]

    finished = utc_now()
    write_bundle(args.out / "bundle.md", brief, answers, removed, reviews, rankings, missing, started, finished)
    (args.out / "authors.json").write_text(json.dumps(authors, indent=2), encoding="utf-8")
    record["finished"] = finished
    record["outcome"] = "bundle written"
    (args.out / "run.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    # Seat names only for seats without an answer: they have no letter to give away.
    written = sum(1 for r in reviews.values() if r["text"])
    print(f"Bundle ready: {args.out / 'bundle.md'}. Answers {len(answers)} of {len(seats)}"
          f"{'; no answer from ' + ', '.join(missing) if missing else ''}. Reviews {written} of {len(reviews)}. "
          "Chair from bundle.md; open authors.json and run.json after Final and Dissent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
