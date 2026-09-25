import csv
import json

import pytest

from pcos_tools.cli import main
from pcos_tools.common import STATUS_VOCAB, VOCAB, WorklistError, load_vocab, read_worklist
from pcos_tools.hygiene import CHANGES_NAME, REPORT_NAME, run_hygiene

PRIORITIES = ["CRITICAL", "HIGH-TODAY", "HIGH", "MED-HIGH", "MED", "LOW", "RECURRING", ""]
ROOMS = ["1", "2", "3", "4", "10", "13", "PERSONAL"]


@pytest.fixture
def rows(worklist_path):
    return read_worklist(worklist_path)


@pytest.fixture
def result(rows, today):
    return run_hygiene(rows, today=today)


def ids(result, check):
    return set(result.task_ids(check))


def write_vocab(path, **overrides):
    payload = {"status": STATUS_VOCAB, "priority": PRIORITIES, "room": ROOMS, "stale_days": 90,
               "aged_days": 7, "done_candidate_days": 7}
    payload.update(overrides)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def stale_ids_in(csv_path):
    with csv_path.open(newline="", encoding="utf-8") as handle:
        return {record["Task ID"] for record in csv.DictReader(handle) if record["Check"] == "STALE_ARCHIVE"}


def test_fixture_shape(rows):
    assert len(rows) >= 15
    assert set(STATUS_VOCAB) <= {row["Status"] for row in rows}


def test_vocab_loaded_from_packaged_json():
    assert VOCAB.source == "packaged vocab.json"
    assert VOCAB.stale_days == 90
    assert VOCAB.aged_days == 7
    assert VOCAB.done_candidate_days == 7
    assert {"Active-Low", "Done-Candidate"} <= set(STATUS_VOCAB)
    assert VOCAB.priority_rank("CRITICAL") == 0
    assert VOCAB.priority_rank("LOW") < VOCAB.priority_rank("RECURRING")
    assert VOCAB.priority_rank("") == len(VOCAB.priority_order)
    assert VOCAB.priority_rank("URGENT") == len(VOCAB.priority_order)


def test_input_is_never_modified(worklist_path, tmp_path):
    before = worklist_path.read_bytes()
    assert main(["hygiene", str(worklist_path), "--out-dir", str(tmp_path), "--today", "2026-09-01"]) == 0
    assert worklist_path.read_bytes() == before


def test_aged_waiting_and_blocked(result):
    assert ids(result, "AGED_WAITING") == {"T-005", "T-006", "T-019"}


def test_empty_sources(result):
    assert ids(result, "EMPTY_SOURCES") == {"T-006", "T-008", "T-18"}


def test_empty_confidence(result):
    assert ids(result, "EMPTY_CONFIDENCE") == {"T-006", "T-008", "T-016", "T-027"}


def test_skip_closed_drops_closed_rows_including_done_candidate(rows, today):
    result = run_hygiene(rows, today=today, skip_closed=True)
    assert ids(result, "EMPTY_CONFIDENCE") == {"T-006", "T-008"}


def test_duplicate_title_pair(result):
    dups = [f for f in result.findings if f.check == "DUPLICATE_TITLE"]
    assert [f.task_id for f in dups] == ["T-017"]
    assert "T-005" in dups[0].reason


def test_duplicate_title_skipped_when_both_rows_are_closed(today):
    base = {"Title": "Renew the office lease", "Room": "1", "Priority": "MED", "Owner": "Joe",
            "Waiting On": "", "Sources": "s", "Next Action": "", "Updated": "2026-08-30",
            "Confidence": "High", "Notes": ""}
    closed_pair = [dict(base, **{"Task ID": "T-200", "Status": "Done", "_row": 2}),
                   dict(base, **{"Task ID": "T-201", "Status": "Done-Candidate", "_row": 3})]
    assert ids(run_hygiene(closed_pair, today=today), "DUPLICATE_TITLE") == set()
    open_pair = [dict(base, **{"Task ID": "T-200", "Status": "Done", "_row": 2}),
                 dict(base, **{"Task ID": "T-201", "Status": "Active", "_row": 3})]
    assert ids(run_hygiene(open_pair, today=today), "DUPLICATE_TITLE") == {"T-201"}


def test_done_promote_uses_vocab_default_of_7_days(result):
    promote = [f for f in result.findings if f.check == "DONE_PROMOTE"]
    assert [f.task_id for f in promote] == ["T-027"]  # 12 days; T-024 is 2 days old
    assert promote[0].proposed == "Done"
    assert result.done_candidate_days == 7


def test_done_candidate_days_argument_overrides_vocab(rows, today):
    assert ids(run_hygiene(rows, today=today, done_candidate_days=1), "DONE_PROMOTE") == {"T-024", "T-027"}
    assert ids(run_hygiene(rows, today=today, done_candidate_days=30), "DONE_PROMOTE") == set()


def test_aged_days_comes_from_vocab_and_can_be_overridden(rows, today, tmp_path):
    assert run_hygiene(rows, today=today).aged_days == 7
    assert ids(run_hygiene(rows, today=today, aged_days=15), "AGED_WAITING") == {"T-005", "T-006"}
    vocab = load_vocab(write_vocab(tmp_path / "vocab.json", aged_days=20))
    assert ids(run_hygiene(rows, today=today, vocab=vocab), "AGED_WAITING") == {"T-006"}
    assert ids(run_hygiene(rows, today=today, vocab=vocab, aged_days=10), "AGED_WAITING") == {"T-005", "T-006", "T-019"}


def test_vocab_without_the_new_keys_falls_back_to_7(tmp_path):
    bare = tmp_path / "bare.json"
    bare.write_text(json.dumps({"status": STATUS_VOCAB, "priority": PRIORITIES, "room": ROOMS, "stale_days": 90}),
                    encoding="utf-8")
    vocab = load_vocab(bare)
    assert (vocab.aged_days, vocab.done_candidate_days) == (7, 7)


def test_invalid_vocabulary(result):
    assert ids(result, "INVALID_STATUS") == {"T-020"}
    assert ids(result, "INVALID_PRIORITY") == {"T-020"}
    assert ids(result, "INVALID_ROOM") == {"T-020"}


def test_new_statuses_are_valid(result):
    assert "T-022" not in ids(result, "INVALID_STATUS")  # Active-Low
    assert "T-024" not in ids(result, "INVALID_STATUS")  # Done-Candidate


def test_malformed_id(result):
    assert ids(result, "MALFORMED_ID") == {"T-18"}


def test_bad_date(result):
    assert ids(result, "BAD_DATE") == {"T-021"}


def test_stale_archive_uses_vocab_default_of_90_days(result):
    stale = {f.task_id: f for f in result.findings if f.check == "STALE_ARCHIVE"}
    assert set(stale) == {"T-014", "T-025", "T-026"}
    assert all(f.proposed == "Archived-Auto" for f in stale.values())
    assert result.stale_days == 90


def test_stale_days_argument_overrides_vocab(rows, today):
    assert ids(run_hygiene(rows, today=today, stale_days=120), "STALE_ARCHIVE") == {"T-014", "T-025"}
    assert ids(run_hygiene(rows, today=today, stale_days=30), "STALE_ARCHIVE") == {"T-014", "T-015", "T-025", "T-026"}


def test_next_free_task_id(result):
    assert result.next_id == "T-028"


def test_duplicate_id_detected(today):
    base = {"Title": "x", "Room": "1", "Status": "Active", "Priority": "MED", "Owner": "Joe",
            "Waiting On": "", "Sources": "s", "Next Action": "", "Updated": "2026-09-01",
            "Confidence": "High", "Notes": ""}
    rows = [dict(base, **{"Task ID": "T-100", "_row": 2}), dict(base, **{"Task ID": "T-100", "_row": 3})]
    result = run_hygiene(rows, today=today)
    assert ids(result, "DUPLICATE_ID") == {"T-100"}
    assert result.next_id == "T-101"


def test_outputs_written(worklist_path, tmp_path):
    assert main(["hygiene", str(worklist_path), "--out-dir", str(tmp_path), "--today", "2026-09-01"]) == 0
    with (tmp_path / CHANGES_NAME).open(newline="", encoding="utf-8") as handle:
        records = list(csv.DictReader(handle))
    assert records[-1]["Check"] == "NEXT_FREE_ID"
    assert records[-1]["Proposed"] == "T-028"
    assert any(r["Check"] == "STALE_ARCHIVE" and r["Proposed"] == "Archived-Auto" for r in records)
    assert any(r["Check"] == "DONE_PROMOTE" and r["Proposed"] == "Done" and r["Task ID"] == "T-027" for r in records)
    report = (tmp_path / REPORT_NAME).read_text(encoding="utf-8")
    assert "DRAFT ONLY" in report
    assert "T-028" in report
    assert "## AGED_WAITING (3)" in report
    assert "## DONE_PROMOTE (1)" in report
    assert "stale >= 90 days" in report and "done-candidate >= 7 days" in report
    assert "Vocabulary: packaged vocab.json" in report
    assert "C:\\" not in report and "/Users/" not in report


def test_custom_vocab_file(rows, today, tmp_path):
    custom = write_vocab(tmp_path / "vocab.json", status=STATUS_VOCAB + ["Parked"],
                         priority=["P1", "P2", ""], stale_days=30)
    vocab = load_vocab(custom)
    parked = dict(rows[0], **{"Task ID": "T-900", "Status": "Parked", "Priority": "P1", "_row": 99})
    result = run_hygiene(rows + [parked], today=today, vocab=vocab)
    assert "T-900" not in ids(result, "INVALID_STATUS")
    assert "T-900" not in ids(result, "INVALID_PRIORITY")
    assert "T-001" in ids(result, "INVALID_PRIORITY")  # CRITICAL is not in the custom list
    assert "T-011" not in ids(result, "INVALID_PRIORITY")  # blank stays allowed
    assert "T-015" in ids(result, "STALE_ARCHIVE")  # 43 days >= custom 30
    assert result.stale_days == 30
    assert result.vocab_source == str(custom)


@pytest.mark.parametrize("payload", [
    "not json",
    "[1, 2]",
    '{"status": [], "priority": ["x"], "room": ["1"], "stale_days": 90}',
    '{"status": ["A"], "priority": ["x"], "room": ["1"]}',
    '{"status": ["A"], "priority": ["x"], "room": ["1"], "stale_days": "90"}',
    '{"status": ["A"], "priority": ["x"], "room": ["1"], "stale_days": 0}',
    '{"status": ["A", 3], "priority": ["x"], "room": ["1"], "stale_days": 90}',
    '{"status": ["A"], "priority": ["x"], "room": ["1"], "stale_days": 90, "aged_days": -1}',
    '{"status": ["A"], "priority": ["x"], "room": ["1"], "stale_days": 90, "done_candidate_days": 0}',
    '{"status": ["A"], "priority": ["x"], "room": ["1"], "stale_days": 90, "aged_days": true}',
])
def test_malformed_vocab_rejected(tmp_path, payload):
    bad = tmp_path / "bad.json"
    bad.write_text(payload, encoding="utf-8")
    with pytest.raises(WorklistError):
        load_vocab(bad)


def test_missing_vocab_rejected(tmp_path):
    with pytest.raises(WorklistError):
        load_vocab(tmp_path / "nope.json")
    assert main(["hygiene", "x.csv", "--vocab", str(tmp_path / "nope.json")]) == 1


def test_cli_vocab_flag_and_stale_days_override(worklist_path, tmp_path):
    custom = write_vocab(tmp_path / "vocab.json", stale_days=200)
    out_a, out_b = tmp_path / "a", tmp_path / "b"
    assert main(["hygiene", str(worklist_path), "--out-dir", str(out_a), "--today", "2026-09-01",
                 "--vocab", str(custom)]) == 0
    assert main(["hygiene", str(worklist_path), "--out-dir", str(out_b), "--today", "2026-09-01",
                 "--vocab", str(custom), "--stale-days", "100"]) == 0
    assert stale_ids_in(out_a / CHANGES_NAME) == {"T-025"}  # only 212 days clears 200
    assert stale_ids_in(out_b / CHANGES_NAME) == {"T-014", "T-025", "T-026"}  # flag wins over file


def test_pandas_reader_matches_csv_reader(worklist_path):
    pytest.importorskip("pandas")
    assert read_worklist(worklist_path, use_pandas=True) == read_worklist(worklist_path)


# ------------------------------------------------------------ v0.3.0: pending --

def test_rows_named_in_a_pending_delta_are_held(rows, today):
    from pcos_tools.hygiene import HOLD_ACTION
    from pcos_tools.pending import load_pending
    from .conftest import FIXTURES

    pending, files = load_pending([FIXTURES / "pending"])
    held = run_hygiene(rows, today=today, pending=pending, pending_files=files)
    actions = {(f.check, f.task_id): f.action for f in held.findings}
    assert actions[("DONE_PROMOTE", "T-027")] == HOLD_ACTION
    assert actions[("STALE_ARCHIVE", "T-014")] == HOLD_ACTION
    assert actions[("STALE_ARCHIVE", "T-026")] == "set-status"  # not named, still applied
    assert {f.task_id for f in held.held()} == {"T-014", "T-027"}
    reason = next(f.reason for f in held.findings if f.task_id == "T-014" and f.check == "STALE_ARCHIVE")
    assert "HOLD: named in unapplied DELTA DELTA_2026-09-01_sample.md" in reason
    plain = run_hygiene(rows, today=today)
    assert not plain.held()
    assert [f.check for f in plain.findings] == [f.check for f in held.findings]


def test_cli_pending_flag(worklist_path, tmp_path, capsys):
    from .conftest import FIXTURES

    code = main(["hygiene", str(worklist_path), "--out-dir", str(tmp_path), "--today", "2026-09-01",
                 "--pending", str(FIXTURES / "pending")])
    assert code == 0
    assert "proposals on hold: 2" in capsys.readouterr().out
    with (tmp_path / CHANGES_NAME).open(newline="", encoding="utf-8") as handle:
        holds = {r["Task ID"] for r in csv.DictReader(handle) if r["Action"] == "hold"}
    assert holds == {"T-014", "T-027"}
    report = (tmp_path / REPORT_NAME).read_text(encoding="utf-8")
    assert "Pending DELTAs read: 1 (DELTA_2026-09-01_sample.md); proposals on hold: 2" in report
