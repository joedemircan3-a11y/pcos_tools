import json
import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

from pcos_tools import __version__

ROOT = Path(__file__).resolve().parent.parent
FIXTURE_CSV = ROOT / "tests" / "fixtures" / "worklist_fixture.csv"


def run(*args, cwd=ROOT):
    return subprocess.run([sys.executable, "-m", "pcos_tools", *args], cwd=cwd,
                          capture_output=True, text=True)


def test_version():
    completed = run("--version")
    assert completed.returncode == 0
    assert f"pcos_tools {__version__}" in completed.stdout
    assert __version__ == "0.2.1"


def test_help_lists_commands():
    completed = run("--help")
    assert completed.returncode == 0
    for command in ("hygiene", "recon_parse", "now_build"):
        assert command in completed.stdout


def test_missing_file_is_a_clean_error(tmp_path):
    completed = run("hygiene", str(tmp_path / "nope.csv"), "--out-dir", str(tmp_path))
    assert completed.returncode == 1
    assert completed.stderr.startswith("error:")
    assert "Traceback" not in completed.stderr


def test_stale_and_aged_days_are_range_checked(tmp_path):
    for flags in (["--stale-days", "0"], ["--stale-days", "-5"], ["--aged-days", "-1"], ["--stale-days", "x"],
                  ["--done-candidate-days", "0"]):
        completed = run("hygiene", str(FIXTURE_CSV), "--out-dir", str(tmp_path), *flags)
        assert completed.returncode == 2, flags
        assert "Traceback" not in completed.stderr
    assert run("hygiene", str(FIXTURE_CSV), "--out-dir", str(tmp_path), "--aged-days", "0").returncode == 0


def test_non_utf8_csv_is_a_clean_error(tmp_path):
    bad = tmp_path / "cp1252.csv"
    header = FIXTURE_CSV.read_text(encoding="utf-8").splitlines()[0]
    bad.write_bytes((header + "\nT-001,Café lease — renew,1,Active,MED,Joe,,x,,2026-09-01,Med,\n")
                    .encode("cp1252"))
    completed = run("hygiene", str(bad), "--out-dir", str(tmp_path))
    assert completed.returncode == 1
    assert completed.stderr.startswith("error:") and "UTF-8" in completed.stderr
    assert "Traceback" not in completed.stderr


def test_invalid_recon_json_is_a_clean_error(tmp_path):
    prev = ROOT / "tests" / "fixtures" / "PCOS_NOW_prev.md"
    for payload in ("[]", "null", '{"sections": {"waiting_on_others": {"items": [42]}}}', "{ not json",
                    '{"sections": {"waiting_on_others": {"items": [{"text": "x", "people": ["Ahmet"]}]}}}',
                    '{"sections": {"waiting_on_others": {"items": [{"text": "x", "people": [{"confidence": "p"}]}]}}}',
                    '{"sections": {"waiting_on_others": {"items": [{"text": "x", "dates": ["2026-08-15"]}]}}}',
                    '{"sections": {"waiting_on_others": {"items": [{"text": "x", "task_ids": "T-005"}]}}}',
                    '{"sections": {"waiting_on_others": {"items": [{"text": "x", "level": "0"}]}}}'):
        recon = tmp_path / "recon.json"
        recon.write_text(payload, encoding="utf-8")
        completed = run("now_build", "--csv", str(FIXTURE_CSV), "--recon", str(recon), "--prev", str(prev),
                        "--out-dir", str(tmp_path), "--today", "2026-09-01")
        assert completed.returncode == 1, payload
        assert completed.stderr.startswith("error:"), payload
        assert "Traceback" not in completed.stderr


def test_broken_packaged_vocab_is_a_clean_error(tmp_path):
    """A typo in the packaged vocab.json must not traceback, and --vocab must still work."""
    pkg_root = tmp_path / "pkg"
    shutil.copytree(ROOT / "pcos_tools", pkg_root / "pcos_tools",
                    ignore=shutil.ignore_patterns("__pycache__"))
    good = tmp_path / "good_vocab.json"
    shutil.copy(ROOT / "pcos_tools" / "vocab.json", good)
    (pkg_root / "pcos_tools" / "vocab.json").write_text("{ not json", encoding="utf-8")

    def check_broken(label):
        for args in (["--version"], ["--help"], ["hygiene", "--help"],
                     ["recon_parse", str(ROOT / "tests" / "fixtures" / "RECON_sample.md"), "--out", "-"]):
            unaffected = run(*args, cwd=pkg_root)
            assert unaffected.returncode == 0, (label, args, unaffected.stderr)
        broken = run("hygiene", str(FIXTURE_CSV), "--out-dir", str(tmp_path / label / "a"), cwd=pkg_root)
        assert broken.returncode == 1, label
        assert broken.stderr.startswith("error: vocab file") and "Traceback" not in broken.stderr, label
        rescued = run("hygiene", str(FIXTURE_CSV), "--out-dir", str(tmp_path / label / "b"),
                      "--vocab", str(good), "--today", "2026-09-01", cwd=pkg_root)
        assert rescued.returncode == 0, (label, rescued.stderr)
        return broken.stderr

    check_broken("corrupt")
    (pkg_root / "pcos_tools" / "vocab.json").unlink()
    assert check_broken("missing").startswith("error: vocab file not found")
    (pkg_root / "pcos_tools" / "vocab.json").mkdir()  # unreadable: a directory where the file should be
    assert "cannot be read" in check_broken("unreadable")


def test_non_ascii_output_survives_a_cp1252_pipe(tmp_path):
    recon = tmp_path / "recon_tr.md"
    sample = (ROOT / "tests" / "fixtures" / "RECON_sample.md").read_text(encoding="utf-8")
    recon.write_text(sample.replace("Ahmet Yilmaz", "Ahmet Yılmaz"), encoding="utf-8")
    env = {**os.environ, "PYTHONIOENCODING": "cp1252", "PYTHONUTF8": "0", "PYTHONLEGACYWINDOWSSTDIO": "1"}
    completed = subprocess.run([sys.executable, "-m", "pcos_tools", "recon_parse", str(recon), "--out", "-"],
                               cwd=ROOT, capture_output=True, env=env)
    assert completed.returncode == 0, completed.stderr.decode("utf-8", "replace")
    names = {person["name"] for person in json.loads(completed.stdout.decode("utf-8"))["people"]}
    assert "Ahmet Yılmaz" in names
    hygiene = subprocess.run([sys.executable, "-m", "pcos_tools", "hygiene", str(FIXTURE_CSV), "--out-dir",
                              str(tmp_path), "--today", "2026-09-01"], cwd=ROOT, capture_output=True, env=env)
    assert hygiene.returncode == 0


def test_outputs_never_overwrite_inputs(tmp_path):
    csv_copy = tmp_path / "proposed_changes.csv"
    shutil.copy(FIXTURE_CSV, csv_copy)
    before = csv_copy.read_bytes()
    completed = run("hygiene", str(csv_copy), "--out-dir", str(tmp_path))
    assert completed.returncode == 1 and "refusing" in completed.stderr
    assert csv_copy.read_bytes() == before

    recon_md = tmp_path / "RECON.md"
    shutil.copy(ROOT / "tests" / "fixtures" / "RECON_sample.md", recon_md)
    completed = run("recon_parse", str(recon_md), "--out", str(recon_md))
    assert completed.returncode == 1 and "refusing" in completed.stderr

    prev = ROOT / "tests" / "fixtures" / "PCOS_NOW_prev.md"
    draft_slot = tmp_path / "PCOS_NOW_draft.md"
    shutil.copy(ROOT / "tests" / "fixtures" / "RECON_sample.md", draft_slot)
    before = draft_slot.read_bytes()
    completed = run("now_build", "--csv", str(FIXTURE_CSV), "--recon", str(draft_slot), "--prev", str(prev),
                    "--out-dir", str(tmp_path), "--today", "2026-09-01")
    assert completed.returncode == 1 and "refusing" in completed.stderr
    assert draft_slot.read_bytes() == before
    shutil.copy(prev, draft_slot)
    completed = run("now_build", "--csv", str(FIXTURE_CSV), "--recon", str(recon_md), "--prev", str(draft_slot),
                    "--out-dir", str(tmp_path), "--today", "2026-09-01")
    assert completed.returncode == 1 and "refusing" in completed.stderr


def test_outputs_use_lf_line_endings(tmp_path):
    prev = ROOT / "tests" / "fixtures" / "PCOS_NOW_prev.md"
    recon = ROOT / "tests" / "fixtures" / "RECON_sample.md"
    assert run("hygiene", str(FIXTURE_CSV), "--out-dir", str(tmp_path), "--today", "2026-09-01").returncode == 0
    assert run("now_build", "--csv", str(FIXTURE_CSV), "--recon", str(recon), "--prev", str(prev),
               "--out-dir", str(tmp_path), "--today", "2026-09-01").returncode == 0
    assert run("recon_parse", str(recon), "--out", str(tmp_path / "recon.json")).returncode == 0
    for name in ("hygiene_report.md", "PCOS_NOW_draft.md", "recon.json"):
        assert b"\r\n" not in (tmp_path / name).read_bytes(), name


def test_pyproject_version_and_package_data():
    with (ROOT / "pyproject.toml").open("rb") as handle:
        data = tomllib.load(handle)
    project = data["project"]
    if "version" in project:
        assert project["version"] == __version__
    else:
        assert "version" in project["dynamic"]
        assert data["tool"]["setuptools"]["dynamic"]["version"]["attr"] == "pcos_tools.__version__"
    assert "vocab.json" in data["tool"]["setuptools"]["package-data"]["pcos_tools"]
