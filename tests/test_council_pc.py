"""Checks for the PC council (register P2-08): scripts/council_pc.py with mocked
CLIs, plus the fixed parts of its skill and card.

The mock CLI is a small Python script that stands in for codex, gemini and
claude. It reads the prompt from stdin, as the real CLIs do here, records each
call, and answers, reviews, fails with a 503, fails for good, sleeps past the
timeout or writes its answer to the last-message file, as each test asks.
"""
import json
import re
import sys
import time
from pathlib import Path

import pytest

from scripts import council_pc
from tests.test_agents_skills import PRIVATE, parse_frontmatter, section

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "council-pc" / "SKILL.md"
CARD = ROOT / "agents" / "council-pc.md"
SCRIPT = ROOT / "scripts" / "council_pc.py"
SEATS = ["codex", "gemini", "claude"]
BRIEF = "Question: which of two shipping plans holds up better? Facts: plan one, plan two."

FAKE_CLI = r'''
import pathlib, re, sys, time
name, state, mode = sys.argv[1], pathlib.Path(sys.argv[2]), sys.argv[3]
prompt = sys.stdin.read()
calls = state / f"{name}.calls"
n = int(calls.read_text()) + 1 if calls.exists() else 1
calls.write_text(str(n))
(state / f"{name}.prompt{n}").write_text(prompt, encoding="utf-8")
reviewing = "RANKING:" in prompt
if mode.startswith("503x") and n <= int(mode[4:]):
    sys.stderr.write("[API Error: got status: 503 UNAVAILABLE. The model is currently experiencing high demand.]\n")
    sys.exit(1)
if mode == "fail" or (mode == "noreview" and reviewing):
    sys.stderr.write("error: not signed in\n")
    sys.exit(1)
if mode == "sleep":
    time.sleep(5)
if mode == "sleeptree":  # a child that keeps the pipes open, as node under a Windows .cmd shim does
    import subprocess
    subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
    time.sleep(30)
if reviewing:
    letters = re.findall(r"^ANSWER ([A-C])$", prompt, re.M)
    out = [f"As {name.capitalize()}, here is my review."]
    out += [f"- Answer {letter} misses the cost line | evidence: the brief | verdict: Fix" for letter in letters]
    out += ["Overall: Fix", "RANKING: " + " > ".join(sorted(letters, reverse=name == "gemini"))]
else:
    out = [f"I am {name.capitalize()}, an assistant made by a lab.", f"Plan one holds up (Candidate). Seat {name} out."]
text = "\n".join(out)
if mode == "lastmsg":
    pathlib.Path(sys.argv[4]).write_text(text, encoding="utf-8")
    print("progress line that is not the answer")
else:
    print(text)
'''


@pytest.fixture
def council(tmp_path):
    """Run the script with mocked seats. Returns run(modes, **options) -> (exit code, out folder, state)."""
    fake = tmp_path / "fake_cli.py"
    fake.write_text(FAKE_CLI, encoding="utf-8")
    brief = tmp_path / "brief.md"
    brief.write_text(BRIEF, encoding="utf-8")
    state = tmp_path / "state"
    state.mkdir()

    def run(modes=None, extra=(), out_name="out", seed=7):
        modes = {**dict.fromkeys(SEATS, "ok"), **(modes or {})}
        argv = [str(brief), "--out", str(tmp_path / out_name), "--retry-wait", "0", "--seed", str(seed), *extra]
        for seat, mode in modes.items():
            command = [sys.executable, str(fake), seat, str(state), mode]
            if mode == "lastmsg":
                command.append(council_pc.LAST_MESSAGE)
            if mode == "missing":
                command = ["no-such-council-cli-for-tests"]
            argv += ["--seat", f"{seat}={json.dumps(command)}"]
        return council_pc.main(argv), tmp_path / out_name, state

    return run


def calls(state, seat):
    path = state / f"{seat}.calls"
    return int(path.read_text()) if path.exists() else 0


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


# --- the run ---------------------------------------------------------------

def test_three_answers_reach_the_chair_under_letters_only(council, capsys):
    code, out, _ = council()
    assert code == 0
    authors = read_json(out / "authors.json")
    assert sorted(authors) == ["A", "B", "C"] and sorted(authors.values()) == sorted(SEATS)
    bundle = (out / "bundle.md").read_text(encoding="utf-8")
    for heading in ("## Brief", "## Answer A", "## Answer B", "## Answer C", "## Reviews", "## Ranking"):
        assert heading in bundle
    assert not re.search(r"codex|gemini|claude", bundle, re.I), "a seat name reached the chair"
    assert "Seat [model] out." in bundle and "made by a lab" not in bundle
    assert not re.search(r"codex|gemini|claude", capsys.readouterr().out, re.I)
    record = read_json(out / "run.json")
    assert record["outcome"] == "bundle written"
    assert all(record["seats"][s]["answer"]["status"] == "ok" for s in SEATS)
    assert all(record["seats"][s]["review"]["status"] == "ok" for s in SEATS)


def test_each_seat_reviews_only_the_answers_it_did_not_write(council):
    code, out, state = council()
    assert code == 0
    label_of = {seat: label for label, seat in read_json(out / "authors.json").items()}
    for seat in SEATS:
        prompt = (state / f"{seat}.prompt2").read_text(encoding="utf-8")
        shown = re.findall(r"^ANSWER ([A-C])$", prompt, re.M)
        assert sorted(shown) == sorted(set("ABC") - {label_of[seat]})
        assert f"Seat {seat} out" not in prompt and "Seat [model] out" in prompt
        assert "you must not try to find out" in prompt and "RANKING: LETTER > LETTER" in prompt


def test_rankings_are_read_and_tallied_without_the_author(council):
    _, out, _ = council()
    bundle = (out / "bundle.md").read_text(encoding="utf-8")
    assert bundle.count("Ranking read: ") == 3 and "not parsed" not in bundle
    assert "| Answer | First places | Pairwise wins | Pairwise losses | Ranked by |" in bundle
    for label in "ABC":
        row = re.search(rf"^\| {label} \| (\d) \| (\d) \| (\d) \| (\d) \|$", bundle, re.M)
        assert row and row.group(4) == "2", "each answer is ranked by the two seats that did not write it"


def test_letters_follow_a_shuffle_not_the_seat_order(council):
    orders = {tuple(read_json(council(out_name=f"out{seed}", seed=seed)[1] / "authors.json").values())
              for seed in range(8)}
    assert len(orders) > 1


def test_gemini_503_is_retried_twice_and_then_answers(council):
    code, out, state = council({"gemini": "503x2"})
    assert code == 0
    answer = read_json(out / "run.json")["seats"]["gemini"]["answer"]
    assert answer["status"] == "ok" and [a["exit"] for a in answer["attempts"]] == [1, 1, 0]
    assert calls(state, "gemini") == 4  # three answer attempts, one review
    assert "gemini" in read_json(out / "authors.json").values()


def test_gemini_503_three_times_leaves_the_seat_out_and_the_council_runs_on(council, capsys):
    code, out, state = council({"gemini": "503x3"})
    assert code == 0
    answer = read_json(out / "run.json")["seats"]["gemini"]["answer"]
    assert answer["status"] == "failed" and len(answer["attempts"]) == 3
    assert "503" in answer["error"]
    assert calls(state, "gemini") == 3, "a seat without an answer is not asked to review"
    assert sorted(read_json(out / "authors.json").values()) == ["claude", "codex"]
    bundle = (out / "bundle.md").read_text(encoding="utf-8")
    assert "- Seats without an answer: gemini (failed)" in bundle
    assert "## Answer C" not in bundle
    assert "no answer from gemini (failed)" in capsys.readouterr().out


def test_a_failure_that_is_not_a_503_is_not_retried(council):
    _, out, state = council({"codex": "fail"})
    assert calls(state, "codex") == 1
    assert read_json(out / "run.json")["seats"]["codex"]["answer"]["status"] == "failed"


def test_retries_option_sets_the_number_of_extra_attempts(council):
    _, out, state = council({"gemini": "503x1"}, extra=["--retries", "0"])
    assert calls(state, "gemini") == 1
    assert read_json(out / "run.json")["seats"]["gemini"]["answer"]["status"] == "failed"


def test_fewer_than_two_answers_is_blocked_and_writes_no_bundle(council, capsys):
    code, out, _ = council({"codex": "fail", "gemini": "503x9"})
    assert code == 3
    assert not (out / "bundle.md").exists() and not (out / "authors.json").exists()
    record = read_json(out / "run.json")
    assert record["outcome"].startswith("Blocked")
    assert "Blocked" in capsys.readouterr().out


def test_a_cli_missing_from_path_is_reported_not_found(council):
    _, out, _ = council({"claude": "missing"})
    answer = read_json(out / "run.json")["seats"]["claude"]["answer"]
    assert answer["status"] == "not found" and answer["attempts"] == []


def test_a_seat_past_its_timeout_is_stopped_and_not_retried(council):
    _, out, state = council({"claude": "sleep"}, extra=["--timeout", "1"])
    answer = read_json(out / "run.json")["seats"]["claude"]["answer"]
    assert answer["status"] == "timeout" and len(answer["attempts"]) == 1
    assert calls(state, "claude") == 1


def test_a_timeout_kills_the_children_that_hold_the_pipes(council):
    started = time.monotonic()
    _, out, _ = council({"claude": "sleeptree"}, extra=["--timeout", "1"])
    assert time.monotonic() - started < 8  # 1 s timeout; without the tree kill the run waits 10 s more
    assert read_json(out / "run.json")["seats"]["claude"]["answer"]["status"] == "timeout"


def test_the_last_message_file_is_the_answer_when_the_cli_writes_one(council):
    code, out, _ = council({"codex": "lastmsg"})
    assert code == 0
    bundle = (out / "bundle.md").read_text(encoding="utf-8")
    assert "progress line that is not the answer" not in bundle
    assert bundle.count("Plan one holds up (Candidate).") == 3


def test_a_missing_review_is_named_by_letter_never_by_seat(council, capsys):
    code, out, _ = council({"gemini": "noreview"})
    assert code == 0
    label = {seat: letter for letter, seat in read_json(out / "authors.json").items()}["gemini"]
    bundle = (out / "bundle.md").read_text(encoding="utf-8")
    block = section(bundle, f"### Review by the author of Answer {label}, of "
                    + " and ".join(sorted(set("ABC") - {label})))
    assert "Review missing" in block
    assert "Reviews: 2 of 3 written, 2 rankings parsed" in bundle
    assert "gemini" not in bundle.lower() and "gemini" not in capsys.readouterr().out.lower()


def test_the_output_folder_must_be_new(council, tmp_path):
    (tmp_path / "used").mkdir()
    (tmp_path / "used" / "bundle.md").write_text("old run", encoding="utf-8")
    code, _, state = council(out_name="used")
    assert code == 2 and calls(state, "codex") == 0


def test_an_empty_brief_is_a_usage_error(tmp_path):
    brief = tmp_path / "brief.md"
    brief.write_text("  \n", encoding="utf-8")
    assert council_pc.main([str(brief), "--out", str(tmp_path / "out")]) == 2


@pytest.mark.parametrize("value", ["grok=grok -p", "codex", "gemini=", 'claude=["claude", 1]'])
def test_seat_override_accepts_only_the_three_seats_with_a_command(value, tmp_path):
    with pytest.raises(SystemExit) as exc:
        council_pc.main([str(tmp_path / "b.md"), "--out", str(tmp_path / "o"), "--seat", value])
    assert exc.value.code == 2


def test_default_commands_read_the_prompt_from_stdin():
    codex, gemini, claude = (council_pc.SEATS[s] for s in SEATS)
    assert codex[:2] == ["codex", "exec"] and codex[-1] == "-"
    assert "--skip-git-repo-check" in codex and codex[codex.index("--sandbox") + 1] == "read-only"
    assert codex[codex.index("--output-last-message") + 1] == council_pc.LAST_MESSAGE
    assert gemini[0] == "gemini" and gemini[gemini.index("-p") + 1] == council_pc.FOLLOW
    assert claude[0] == "claude" and claude[claude.index("-p") + 1] == council_pc.FOLLOW
    assert council_pc.RETRIES == 2


# --- the pieces --------------------------------------------------------------

@pytest.mark.parametrize("text, expected", [
    ("As Claude, I would pick plan one.", "I would pick plan one."),
    ("I'm Gemini, a model. Plan one.", "Plan one."),
    ("As an AI language model, I think plan one.", "I think plan one."),
    ("Trained by OpenAI, I pick plan two.", "Trained by [model], I pick plan two."),
    ("I was trained by Google, so plan one.", "so plan one."),
    ("I am a model built by Anthropic. Plan one.", "Plan one."),
    ("- As Gemini, I pick plan one.", "- I pick plan one."),
    ("Plan one. As Codex, I agree.", "Plan one. I agree."),
    ("As a model for next year, plan one fits.", "As a model for next year, plan one fits."),
    ("Codex and GPT-5 agree.", "[model] and [model] agree."),
])
def test_anonymize_removes_self_identification(text, expected):
    assert council_pc.anonymize(text, BRIEF)[0] == expected


def test_anonymize_keeps_names_the_brief_uses_but_still_removes_self_identification():
    brief = "Should Gemini replace the Review-2 seat?"
    text, removed = council_pc.anonymize("As Gemini, yes. Gemini is free; Claude costs more.", brief)
    assert text == "yes. Gemini is free; [model] costs more." and removed == 2
    kept = "Use a reviewer such as Gemini, trained by its vendor."
    assert council_pc.anonymize(kept, brief) == (kept, 0)


def test_anonymize_leaves_untouched_lines_and_their_spacing_alone():
    text = "Plan:\n  - step one\n    detail  aligned\n```\ncode  block\n```\nAs Codex,  I agree."
    cleaned, removed = council_pc.anonymize(text, BRIEF)
    assert cleaned.splitlines()[:6] == text.splitlines()[:6] and cleaned.endswith("\nI agree.")
    assert removed == 1


@pytest.mark.parametrize("text, letters, expected", [
    ("findings\nRANKING: B > C", ["B", "C"], ["B", "C"]),
    ("**RANKING:** c > a", ["A", "C"], ["C", "A"]),
    ("RANKING: A > B\nmore\nRANKING: B > A", ["A", "B"], ["B", "A"]),
    ("RANKING: **B**", ["B"], ["B"]),
    ("RANKING: A > B > C", ["B", "C"], None),
    ("RANKING: B > B", ["B", "C"], None),
    ("RANKING: LETTER > LETTER", ["B", "C"], None),
    ("no ranking line", ["B", "C"], None),
])
def test_parse_ranking(text, letters, expected):
    assert council_pc.parse_ranking(text, letters) == expected


def test_tally_counts_pairwise_wins_and_finds_the_undefeated_answer():
    table = council_pc.tally([["B", "C"], ["A", "C"], ["A", "B"]], ["A", "B", "C"])
    assert table["A"] == {"first": 2, "wins": 2, "losses": 0, "ranked_by": 2}
    assert table["C"] == {"first": 0, "wins": 0, "losses": 2, "ranked_by": 2}
    assert council_pc.undefeated(table) == ["A"]
    cycle = council_pc.tally([["B", "C"], ["C", "A"], ["A", "B"]], ["A", "B", "C"])
    assert council_pc.undefeated(cycle) == []


def test_clean_drops_colour_codes_and_the_credentials_banner():
    assert council_pc.clean("\nLoaded cached credentials.\n\x1b[32mPlan one.\x1b[0m\n") == "Plan one."


# --- the skill and the card --------------------------------------------------

def read(path):
    return path.read_text(encoding="utf-8")


def flat(text):
    return " ".join(text.split())


def test_skill_frontmatter_names_the_register_item_and_the_card():
    fields, body = parse_frontmatter(read(SKILL))
    assert fields["name"] == "council-pc"
    assert fields["metadata"]["register"] == "P2-08"
    assert fields["metadata"]["card"] == "agents/council-pc.md"
    assert body.startswith("\n# PC council\n")


def test_skill_runs_on_demand_only_and_nothing_is_scheduled():
    text = flat(read(SKILL))
    assert "Nothing schedules it" in text
    assert not (ROOT / "routines" / "council-pc.md").exists()
    assert "routines/council-pc" not in read(ROOT / "routines" / "_INDEX.md")
    trigger = flat(section(read(CARD), "## 6. Trigger and owner model"))
    assert "on demand only" in trigger and "never scheduled" in trigger


def test_skill_retries_gemini_503_twice_and_runs_the_script():
    text = flat(read(SKILL))
    assert "retried twice" in text and "503" in text
    assert "python scripts/council_pc.py" in text


def test_chair_reads_the_bundle_only_until_final_and_dissent_are_written():
    chair = flat(section(read(SKILL), "## 4. Chair"))
    assert "Read `bundle.md` only." in chair
    assert "Only after Final and Dissent are written" in chair and "authors.json" in chair
    assert "council-board skill section 5" in chair


def test_chair_never_wrote_an_answer_and_no_seat_reviews_its_own():
    never = flat(section(read(SKILL), "## Never"))
    assert "Chair from a session that wrote one of the answers" in never
    assert "Let a seat review or rank its own answer" in never
    assert "Schedule this council" in never


def test_council_row_write_runs_the_checker_first():
    write = flat(section(read(SKILL), "## 5. Write the Council row"))
    assert "council-final" in write and "only after an Accept" in write
    assert "[[CHANGELOG]] row per field" in write and "[[INBOX_FOLDER]]" in write


def test_checker_council_final_covers_the_pc_council():
    text = read(ROOT / "skills" / "checker" / "references" / "checklists.md")
    council_final = flat(section(text, "## council-final"))
    assert "PC council: there is no plan round" in council_final
    assert "PC council: every seat that answered reviewed the answers it did not write" in council_final
    assert "PC council: the chair worked from the bundle" in council_final


@pytest.mark.parametrize("path", [SKILL, CARD, SCRIPT], ids=lambda p: str(p.relative_to(ROOT)))
def test_new_files_hold_no_private_identifiers(path):
    text = read(path)
    for what, find in PRIVATE.items():
        assert not find(text), f"{what} in {path.relative_to(ROOT)}"
