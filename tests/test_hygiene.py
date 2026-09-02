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
    payload = {"status": STATUS_VOCAB, "priority": PRIORITIES, "room": ROOMS, "stale_days": 90}
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
    assert ids(result, "EMPTY_CONFIDENCE") == {"T-006", "T-008", "T-016"}


def test_skip_closed_drops_closed_rows(rows, today):
    result = run_hygiene(rows, today=today, skip_closed=True)
    assert ids(result, "EMPTY_CONFIDENCE") == {"T-006", "T-008"}


def test_duplicate_title_pair(result):
    dups = [f for f in result.findings if f.check == "DUPLICATE_TITLE"]
    assert [f.task_id for f in dups] == ["T-017"]
    assert "T-005" in dups[0].reason


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
    assert result.next_id == "T-027"


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
    assert records[-1]["Proposed"] == "T-027"
    assert any(r["Check"] == "STALE_ARCHIVE" and r["Proposed"] == "Archived-Auto" for r in records)
    report = (tmp_path / REPORT_NAME).read_text(encoding="utf-8")
    assert "DRAFT ONLY" in report
    assert "T-027" in report
    assert "## AGED_WAITING (3)" in report
    assert "stale >= 90 days" in report
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
