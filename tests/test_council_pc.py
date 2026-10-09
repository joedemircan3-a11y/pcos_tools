"""Checks for the PC council (register P2-08): scripts/council_pc.py with mocked
CLIs, plus the fixed parts of its skill and card.

The mock CLI is a small Python script that stands in for codex, gemini and
claude. It reads the prompt from stdin, as the real CLIs do here, records each
call (with its working folder, its home and its environment), and answers,
reviews, fails with a 503, fails for good, sleeps past the timeout, writes its
answer to the last-message file or refreshes its sign-in, as each test asks.
Each run gets a stand-in for Joe's real home, so no test reads or writes the
sign-in of the person running the tests.
"""
import json
import os
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

SEEN_ENV = ["HOME", "USERPROFILE", "CODEX_HOME", "CLAUDE_CONFIG_DIR", "GEMINI_CLI_HOME", "XDG_CONFIG_HOME",
            "XDG_DATA_HOME", "XDG_STATE_HOME", "XDG_CACHE_HOME", "GEMINI_API_KEY", "CLAUDECODE"]

FAKE_CLI = r'''
import json, os, pathlib, re, sys, time
name, state, mode = sys.argv[1], pathlib.Path(sys.argv[2]), sys.argv[3]
prompt = sys.stdin.read()
calls = state / f"{name}.calls"
n = int(calls.read_text()) + 1 if calls.exists() else 1
calls.write_text(str(n))
(state / f"{name}.prompt{n}").write_text(prompt, encoding="utf-8")
cwd, home = pathlib.Path.cwd(), pathlib.Path(os.environ["HOME"])
brief = cwd / "brief.md"
(state / f"{name}.seen{n}").write_text(json.dumps({
    "cwd": str(cwd),
    "cwd_files": sorted(p.name for p in cwd.iterdir()),
    "brief": brief.read_text(encoding="utf-8") if brief.is_file() else None,
    "home_files": {p.relative_to(home).as_posix(): p.read_text(encoding="utf-8")
                   for p in sorted(home.rglob("*")) if p.is_file()},
    "env": {key: os.environ.get(key) for key in json.loads(sys.argv[-1])},
    "config_folders_exist": all(os.path.isdir(os.environ[key]) for key in ("CODEX_HOME", "CLAUDE_CONFIG_DIR")),
}), encoding="utf-8")
if mode in ("refresh", "torn", "race", "refreshsleep") and n == 1:  # the CLI renews its token
    signed_in = pathlib.Path(os.environ["CODEX_HOME"]) / "auth.json"
    signed_in.write_text('{"tokens": "new"' + ("" if mode == "torn" else "}"), encoding="utf-8")
    if mode == "race":  # meanwhile another codex on the PC renews the real file
        pathlib.Path(sys.argv[4]).write_text('{"tokens": "other"}', encoding="utf-8")
reviewing = "RANKING:" in prompt
if mode == "nested" and "CLAUDECODE" in __import__("os").environ:
    sys.stderr.write("Error: Claude Code cannot be launched inside another Claude Code session.\n")
    sys.exit(1)
if mode.startswith("503x") and n <= int(mode[4:]):
    sys.stderr.write("[API Error: got status: 503 UNAVAILABLE. The model is currently experiencing high demand.]\n")
    sys.exit(1)
if mode == "policy" and 'toolName = "*"' not in pathlib.Path(sys.argv[4]).read_text():
    sys.exit(1)
if mode == "fail" or (mode == "noreview" and reviewing):
    sys.stderr.write("error: not signed in\n")
    sys.exit(1)
if mode in ("sleep", "refreshsleep"):
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
def real_home(tmp_path, monkeypatch):
    """A stand-in for Joe's home, with his sign-ins, settings and a private file."""
    home = tmp_path / "joe"
    files = {
        ".codex/auth.json": '{"tokens": "codex-old"}',
        ".codex/config.toml": '[mcp_servers.files]\ncommand = "files-mcp"\n',
        ".claude/.credentials.json": '{"claudeAiOauth": "claude-old"}',
        ".claude/settings.json": '{"permissions": {}}',
        ".claude.json": '{"projects": {"C:/Business": {}}}',
        ".gemini/settings.json": '{"mcpServers": {}}',
        "Documents/prices.xlsx": "private",
    }
    for relative, text in files.items():
        (home / relative).parent.mkdir(parents=True, exist_ok=True)
        (home / relative).write_text(text, encoding="utf-8")
    for variable in ("CODEX_HOME", "CLAUDE_CONFIG_DIR", "GEMINI_CLI_HOME", "GEMINI_API_KEY",
                     "XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_STATE_HOME", "XDG_CACHE_HOME"):
        monkeypatch.delenv(variable, raising=False)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))
    return home


@pytest.fixture
def council(tmp_path, real_home):
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
            if mode == "policy":
                command.append(council_pc.NO_TOOLS)
            if mode == "race":
                command.append(str(real_home / ".codex" / "auth.json"))
            command.append(json.dumps(SEEN_ENV))
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


def seen(state, seat, n):
    """What the seat's CLI saw on its n-th call: working folder, home files, environment."""
    return read_json(state / f"{seat}.seen{n}")


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


def test_the_claude_seat_starts_without_the_chair_sessions_nested_session_marker(council, monkeypatch):
    monkeypatch.setenv("CLAUDECODE", "1")
    code, out, state = council({"claude": "nested"})
    assert code == 0 and calls(state, "claude") == 2
    assert read_json(out / "run.json")["seats"]["claude"]["answer"]["status"] == "ok"


def test_the_no_tools_policy_file_is_written_and_passed_to_the_seat(council):
    _, out, state = council({"gemini": "policy"})
    assert read_json(out / "run.json")["seats"]["gemini"]["answer"]["status"] == "ok"
    assert calls(state, "gemini") == 2


# --- isolation: what each seat can see (issue 6) -------------------------------

def test_each_seat_runs_in_a_new_folder_that_holds_only_the_brief(council, tmp_path):
    code, _, state = council()
    assert code == 0
    folders = set()
    for seat in SEATS:
        for n in (1, 2):  # the answer, then the review
            what = seen(state, seat, n)
            assert what["cwd_files"] == ["brief.md"] and what["brief"] == BRIEF
            cwd = Path(what["cwd"])
            assert not cwd.is_relative_to(tmp_path) and not cwd.is_relative_to(ROOT)
            assert not cwd.exists(), "the folder is removed after the call"
            folders.add(cwd)
    assert len(folders) == 6, "a new folder for every call"


def test_each_seat_gets_a_scratch_home_with_every_config_folder_inside_it(council, real_home):
    _, _, state = council()
    homes = set()
    for seat in SEATS:
        env = seen(state, seat, 1)["env"]
        home = Path(env["HOME"])
        assert not home.is_relative_to(real_home) and not home.exists()
        assert env["USERPROFILE"] == env["GEMINI_CLI_HOME"] == env["HOME"]
        assert env["CODEX_HOME"] == str(home / ".codex") and env["CLAUDE_CONFIG_DIR"] == str(home / ".claude")
        for variable in ("XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_STATE_HOME", "XDG_CACHE_HOME"):
            assert Path(env[variable]).is_relative_to(home)
        assert env["CLAUDECODE"] is None
        homes.add(home)
    assert len(homes) == 3


@pytest.mark.parametrize("seat, carried", [
    ("codex", {".codex/auth.json": '{"tokens": "codex-old"}'}),
    ("claude", {".claude/.credentials.json": '{"claudeAiOauth": "claude-old"}'}),
    ("gemini", {}),
])
def test_the_scratch_home_carries_only_the_seats_own_sign_in(council, seat, carried):
    _, _, state = council()
    for n in (1, 2):  # no settings, MCP servers, history or business files
        assert seen(state, seat, n)["home_files"] == carried


def test_a_sign_in_folder_moved_by_its_variable_is_read_from_there(council, tmp_path, monkeypatch):
    moved = tmp_path / "elsewhere" / "codex"
    moved.mkdir(parents=True)
    (moved / "auth.json").write_text('{"tokens": "moved"}', encoding="utf-8")
    monkeypatch.setenv("CODEX_HOME", str(moved))
    _, _, state = council()
    what = seen(state, "codex", 1)
    assert what["home_files"] == {".codex/auth.json": '{"tokens": "moved"}'}
    assert what["env"]["CODEX_HOME"] != str(moved)


def test_a_seat_without_a_sign_in_file_starts_signed_out_and_run_json_says_so(council, real_home):
    (real_home / ".claude" / ".credentials.json").unlink()
    (real_home / ".codex" / "auth.json").unlink()
    _, out, state = council()
    assert seen(state, "claude", 1)["home_files"] == {}
    # codex stops at once when CODEX_HOME does not exist, so the folders are always made
    assert all(seen(state, seat, 1)["config_folders_exist"] for seat in SEATS)
    note = read_json(out / "run.json")["seats"]["claude"]["answer"]["sign_in"][".credentials.json"]
    assert note.startswith("not found")


def test_the_gemini_key_comes_from_the_environment_or_the_gemini_env_file(council, real_home, monkeypatch):
    (real_home / ".gemini" / ".env").write_text('OTHER=1\nexport GEMINI_API_KEY="key-from-file"\n',
                                               encoding="utf-8")
    _, _, state = council(out_name="from-file")
    assert seen(state, "gemini", 1)["env"]["GEMINI_API_KEY"] == "key-from-file"
    assert seen(state, "codex", 1)["env"]["GEMINI_API_KEY"] is None, "only the Gemini seat reads the file"
    monkeypatch.setenv("GEMINI_API_KEY", "key-from-env")
    council(out_name="from-env")
    assert seen(state, "gemini", 3)["env"]["GEMINI_API_KEY"] == "key-from-env"  # calls 3 and 4: the second run


def test_a_sign_in_the_cli_refreshes_goes_back_where_the_cli_keeps_it(council, real_home):
    code, out, _ = council({"codex": "refresh"})
    assert code == 0
    assert (real_home / ".codex" / "auth.json").read_text(encoding="utf-8") == '{"tokens": "new"}'
    notes = read_json(out / "run.json")["seats"]["codex"]["answer"]["sign_in"]
    assert notes == {"auth.json": "refreshed in the run and written back"}
    assert not list((real_home / ".codex").glob("*.council-pc")), "no temporary file is left"
    assert (real_home / ".claude" / ".credentials.json").read_text(encoding="utf-8") == '{"claudeAiOauth": "claude-old"}'


def test_a_sign_in_refreshed_before_a_timeout_still_goes_back(council, real_home):
    _, out, _ = council({"codex": "refreshsleep"}, extra=["--timeout", "1"])
    assert read_json(out / "run.json")["seats"]["codex"]["answer"]["status"] == "timeout"
    assert (real_home / ".codex" / "auth.json").read_text(encoding="utf-8") == '{"tokens": "new"}'


@pytest.mark.parametrize("mode, kept, note", [
    ("torn", '{"tokens": "codex-old"}', "not complete JSON"),
    ("race", '{"tokens": "other"}', "the real file changed too"),
])
def test_a_refreshed_sign_in_never_overwrites_a_good_one(council, real_home, mode, kept, note):
    _, out, _ = council({"codex": mode})
    assert (real_home / ".codex" / "auth.json").read_text(encoding="utf-8") == kept
    assert note in read_json(out / "run.json")["seats"]["codex"]["answer"]["sign_in"]["auth.json"]
    assert not list((real_home / ".codex").glob("*.council-pc")), "no temporary file is left"


def test_a_refresh_that_lands_while_the_write_back_is_prepared_is_kept(council, real_home, monkeypatch):
    real = real_home / ".codex" / "auth.json"
    copymode = council_pc.shutil.copymode

    def another_codex_refreshes_meanwhile(source, target):
        copymode(source, target)
        if Path(source) == real:
            real.write_text('{"tokens": "other"}', encoding="utf-8")

    monkeypatch.setattr(council_pc.shutil, "copymode", another_codex_refreshes_meanwhile)
    _, out, _ = council({"codex": "refresh"})
    assert real.read_text(encoding="utf-8") == '{"tokens": "other"}', "the check runs last, right before the replace"
    assert "the real file changed too" in read_json(out / "run.json")["seats"]["codex"]["answer"]["sign_in"]["auth.json"]
    assert not list(real.parent.glob("*.council-pc"))


def test_the_codex_seat_has_no_tool_that_reads_a_file():
    codex = council_pc.SEATS["codex"]
    disabled = {codex[i + 1] for i, arg in enumerate(codex) if arg == "--disable"}
    assert {"shell_tool", "view_image", "apps"} <= disabled
    assert codex[codex.index("--sandbox") + 1] == "read-only"
    assert "--ignore-user-config" in codex and "--ephemeral" in codex


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
    others = sorted(set("ABC") - {label})
    assert f"Comparisons missing (a review or its ranking is missing): {others[0]} and {others[1]}" in bundle
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


def test_default_commands_switch_the_seats_host_tools_off():
    codex, gemini, claude = (council_pc.SEATS[s] for s in SEATS)
    assert codex[codex.index("--disable") + 1] == "apps"
    assert gemini[gemini.index("--policy") + 1] == council_pc.NO_TOOLS
    assert 'toolName = "*"' in council_pc.NO_TOOLS_POLICY and 'decision = "deny"' in council_pc.NO_TOOLS_POLICY
    assert "--strict-mcp-config" in claude and claude[-2:] == ["--tools", ""], "--tools takes a list: keep it last"
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


@pytest.mark.parametrize("text, brief, expected", [
    ("As an OpenAI model, I recommend A.", "Compare OpenAI and Google", "I recommend A."),
    ("Claude here: choose A.", "Should Claude replace Gemini?", "choose A."),
    ("This is Gemini speaking. Choose B.", "Is Gemini cheaper?", "Choose B."),
    ("This is Claude. Choose A.", "Claude or Codex?", "Choose A."),
    ("As Codex I would pick A.", "Codex or Gemini?", "I would pick A."),
    ("As Claude Opus 4, I pick A.", "Claude for Review-2?", "I pick A."),
    ("I'm an OpenAI model, so A.", "OpenAI terms?", "so A."),
    ("I am Claude, and Plan A is best because it costs less.", "Claude or Codex?",
     "Plan A is best because it costs less."),
    ("I am Gemini 2.5 Pro and I pick B.", "Gemini quota?", "I pick B."),
    ("My name is Gemini. Choose B.", "Gemini quota?", "Choose B."),
    ("I, Claude, think A.", "Claude or Gemini?", "I think A."),
    ("Plan A.\n— Gemini 2.5 Pro", "Gemini or Codex?", "Plan A."),
])
def test_anonymize_removes_self_identification_even_for_names_the_brief_uses(text, brief, expected):
    assert council_pc.anonymize(text, brief)[0] == expected


@pytest.mark.parametrize("text", [
    "As Claude suggested, plan one is cheaper.",
    "Claude here is the cheaper seat.",
    "This is Claude's strength.",
    "- Gemini is cheaper; Codex is faster.",
    "As OpenAI notes, the quota resets daily.",
])
def test_anonymize_keeps_content_about_models_the_brief_names(text):
    brief = "Compare Claude, Gemini and Codex (OpenAI) as reviewers."
    assert council_pc.anonymize(text, brief) == (text, 0)


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
    rankings = [["B", "C"], ["A", "C"], ["A", "B"]]
    table = council_pc.tally(rankings, ["A", "B", "C"])
    assert table["A"] == {"first": 2, "wins": 2, "losses": 0, "ranked_by": 2}
    assert table["C"] == {"first": 0, "wins": 0, "losses": 2, "ranked_by": 2}
    assert council_pc.undefeated(rankings, ["A", "B", "C"]) == ["A"]
    assert council_pc.missing_pairs(rankings, ["A", "B", "C"]) == []
    assert council_pc.undefeated([["B", "C"], ["C", "A"], ["A", "B"]], ["A", "B", "C"]) == []


def test_undefeated_needs_every_comparison_of_the_answer():
    rankings = [["B", "C"], ["A", "B"]]  # the review that compares A and C is missing
    assert council_pc.undefeated(rankings, ["A", "B", "C"]) == []
    assert council_pc.missing_pairs(rankings, ["A", "B", "C"]) == [("A", "C")]
    assert council_pc.undefeated([["A", "B"], ["A", "C"]], ["A", "B", "C"]) == ["A"]
    assert council_pc.undefeated([["B"], ["A"]], ["A", "B"]) == []


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


def test_skill_and_card_keep_the_seats_away_from_files_on_the_pc():
    run = flat(section(read(SKILL), "## 3. Run the script"))
    assert "`--disable shell_tool`" in run and "`--disable view_image`" in run
    assert "holds only the brief" in run and "holds only a copy of that CLI's sign-in file" in run
    assert "Pre-run check" in run and "features list" in run and "Unknown feature flag" in run
    assert "Residual risk" in run and "apply_patch" in run
    assert "--disable shell_tool" in flat(section(read(SKILL), "## Never"))
    tools = flat(section(read(CARD), "## 3. Tools allowed"))
    assert "no shell, no image reader" in tools and "apply_patch" in tools
    assert "give a seat a tool that reads files" in tools


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
