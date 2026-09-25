import csv

import pytest

from pcos_tools.cli import main
from pcos_tools.common import read_worklist, task_id_ranges, unescape_md
from pcos_tools.now_check import CSV_NAME, REPORT_NAME, run_now_check
from pcos_tools.pending import load_pending

from .conftest import FIXTURES

V3_NOW = FIXTURES / "PCOS_NOW_v3_gdocs.md"
PENDING_DIR = FIXTURES / "pending"


@pytest.fixture
def rows(worklist_path):
    return read_worklist(worklist_path)


def by_check(findings):
    grouped = {}
    for finding in findings:
        grouped.setdefault(finding.check, set()).add(finding.task_id)
    return grouped


def test_v3_fixture_findings(rows):
    findings, summary = run_now_check(rows, V3_NOW.read_text(encoding="utf-8"))
    grouped = by_check(findings)
    assert grouped["CITED_MISSING"] == {"T-099"}
    assert grouped["CITED_CLOSED"] == {"T-011", "T-013", "T-016"}
    assert grouped["STATUS_MISMATCH"] == {"T-006"}
    assert grouped["OPEN_NOT_CITED"] == {"T-003"}
    assert grouped["ROW_COUNT"] == {""}
    assert "PENDING_DELTA" not in grouped
    assert summary["sections_found"] == list(range(9))
    assert summary["stated_rows"] == 20 and summary["rows"] == 27
    assert summary["next_id"] == "T-028"


def test_range_members_count_as_cited_and_are_never_missing(rows):
    text = "# 2. Current work\n\n- T-013 to T-016 unchanged; T-120 to T-125 skipped on purpose.\n"
    findings, _ = run_now_check(rows, text)
    grouped = by_check(findings)
    assert "T-014" not in grouped.get("OPEN_NOT_CITED", set())
    assert grouped["CITED_MISSING"] == {"T-120", "T-125"}  # only the explicit endpoints
    assert task_id_ranges("T-013 to T-016") == {"T-014", "T-015"}
    assert task_id_ranges("T-0201..T-0203") == {"T-0202"}
    assert task_id_ranges("T-001 to T-500") == set()  # too wide to be a real range


def test_escaped_export_and_plain_text_agree(rows):
    escaped = V3_NOW.read_text(encoding="utf-8")
    plain = unescape_md(escaped)
    assert "\\." not in plain and "PCOS_NOW" in plain
    first = sorted((f.check, f.task_id) for f in run_now_check(rows, escaped)[0])
    second = sorted((f.check, f.task_id) for f in run_now_check(rows, plain)[0])
    assert first == second


def test_status_word_must_follow_the_id_closely(rows):
    text = "# 2. Work\n\n- T-001 lease: " + "x" * 80 + " Blocked\n- T-007 (Needs-Decision)\n"
    grouped = by_check(run_now_check(rows, text)[0])
    assert "STATUS_MISMATCH" not in grouped


def test_personal_rows_are_never_reported_as_not_cited(rows):
    rows = [dict(row) for row in rows]
    rows[17].update({"Priority": "HIGH"})  # T-18, Room PERSONAL, Active
    grouped = by_check(run_now_check(rows, "# 0. Today\n")[0])
    assert "T-18" not in grouped["OPEN_NOT_CITED"]


def test_pending_deltas_are_listed(rows):
    pending, files = load_pending([PENDING_DIR])
    assert files == ["DELTA_2026-09-01_sample.md"]
    assert pending == {"T-014": files, "T-027": files, "T-200": files}
    grouped = by_check(run_now_check(rows, V3_NOW.read_text(encoding="utf-8"), pending=pending,
                                     pending_files=files)[0])
    assert grouped["PENDING_DELTA"] == {"T-014", "T-027"}
    assert grouped["PENDING_NEW_ID"] == {"T-200"}


def test_cli_writes_report_and_leaves_inputs_alone(worklist_path, tmp_path):
    before = (worklist_path.read_bytes(), V3_NOW.read_bytes())
    code = main(["now_check", "--csv", str(worklist_path), "--now", str(V3_NOW), "--pending", str(PENDING_DIR),
                 "--out-dir", str(tmp_path), "--today", "2026-09-01"])
    assert code == 0
    assert (worklist_path.read_bytes(), V3_NOW.read_bytes()) == before
    report = (tmp_path / REPORT_NAME).read_text(encoding="utf-8")
    assert "## CITED_CLOSED (3)" in report and "section 7 says 20 rows" in report
    with (tmp_path / CSV_NAME).open(newline="", encoding="utf-8") as handle:
        records = list(csv.DictReader(handle))
    assert {record["Check"] for record in records} >= {"CITED_MISSING", "PENDING_NEW_ID"}


def test_cli_missing_pending_path_is_an_error(worklist_path, tmp_path, capsys):
    code = main(["now_check", "--csv", str(worklist_path), "--now", str(V3_NOW),
                 "--pending", str(tmp_path / "nope"), "--out-dir", str(tmp_path)])
    assert code == 1
    assert "pending DELTA path not found" in capsys.readouterr().err


# ------------------------------------------------ review fixes (0.3.0 final) --

def test_ranges_are_strict():
    assert task_id_ranges("- T-001\n- T-020") == set()  # never across lines
    assert task_id_ranges("Scope moved from T-001 to T-020") == set()
    assert task_id_ranges("T-001 - T-030 blocks the lease") == set()  # spaced hyphen is a clause break
    assert task_id_ranges("Chase T-006 — T-020 is waiting") == set()  # em dash likewise
    assert task_id_ranges("T-013–T-016 and T-017 through T-019") == {"T-014", "T-015", "T-018"}


def test_range_members_are_cited_but_never_closed_or_missing(rows):
    text = "# 2. Work\n\n- T-005 to T-017 unchanged.\n"
    grouped = by_check(run_now_check(rows, text)[0])
    assert "CITED_CLOSED" not in grouped  # T-011, T-012, T-013, T-016 sit inside the range
    assert "T-002" in grouped["OPEN_NOT_CITED"] and "T-006" not in grouped["OPEN_NOT_CITED"]


def test_closed_row_described_as_closed_is_not_flagged(rows):
    text = "# 0. Today\n\n- T-011 Done yesterday.\n- T-012 Expired last month.\n- T-013 moved on.\n"
    grouped = by_check(run_now_check(rows, text)[0])
    assert grouped["CITED_CLOSED"] == {"T-013"}


def test_status_word_must_sit_in_the_same_clause(rows):
    text = ("# 2. Work\n\n- T-002 VAT return. Open question on the rate.\n"
            "| T-006 | Server migration: waiting | Blocked |\n- T-001 lease. Done so far: nothing.\n")
    assert "STATUS_MISMATCH" not in by_check(run_now_check(rows, text)[0])


def test_sub_heading_with_a_number_is_not_a_section(rows):
    text = V3_NOW.read_text(encoding="utf-8").replace("## Admin", "## 7 vendors to call back")
    findings, summary = run_now_check(rows, text)
    assert summary["sections_found"] == list(range(9)) and summary["stated_rows"] == 20
    assert "T-002" not in by_check(findings)["OPEN_NOT_CITED"]


def test_row_count_prefers_the_live_worklist_line(rows):
    text = ("# 7. Current pointers\n\n- Private worklist: 5 rows\n- Live Worklist: [LIVE] sheet, 27 rows.\n")
    assert "ROW_COUNT" not in by_check(run_now_check(rows, text)[0])


def test_no_sections_warns(rows):
    _, summary = run_now_check(rows, "just a paragraph mentioning T-001\n")
    assert summary["warnings"] and "no numbered sections" in summary["warnings"][0]


def test_pending_reads_ranges_and_skips_own_reports(tmp_path):
    (tmp_path / "DELTA_x.md").write_text("Archive T-013 to T-016 today.\n", encoding="utf-8")
    (tmp_path / "now_check_report.md").write_text("T-001 T-002\n", encoding="utf-8")
    pending, files = load_pending([tmp_path])
    assert files == ["DELTA_x.md"]
    assert set(pending) == {"T-013", "T-014", "T-015", "T-016"}


def test_google_docs_html_export_gives_the_same_result(rows, tmp_path):
    from pcos_tools.common import html_to_markdown

    html = ("<html><head><style>.c{color:red}</style></head><body>"
            "<h1><span>PCOS_NOW</span></h1><h1><span>2. Current work</span></h1>"
            "<h2><span>Office</span></h2><ul><li><span>T-006 server (Active): waiting</span></li>"
            "<li><span>T-011 claim still open</span></li></ul>"
            "<h1><span>7. Current pointers</span></h1><p><span>Live Worklist: 20 rows &amp; more</span></p>"
            "<table><tr><td><p><span>Lane</span></p></td><td><p><span>State</span></p></td></tr></table>"
            "</body></html>")
    text = html_to_markdown(html)
    assert "# 2. Current work" in text and "## Office" in text and "- T-006 server (Active): waiting" in text
    assert "| Lane | State |" in text and "color:red" not in text and "20 rows & more" in text
    path = tmp_path / "PCOS_NOW.html"
    path.write_text(html, encoding="utf-8")
    code = main(["now_check", "--csv", str(FIXTURES / "worklist_fixture.csv"), "--now", str(path),
                 "--out-dir", str(tmp_path / "out")])
    assert code == 0
    report = (tmp_path / "out" / REPORT_NAME).read_text(encoding="utf-8")
    assert "## STATUS_MISMATCH (1)" in report and "## CITED_CLOSED (1)" in report and "## ROW_COUNT (1)" in report
