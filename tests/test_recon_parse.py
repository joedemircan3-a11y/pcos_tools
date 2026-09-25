import json

import pytest

from pcos_tools.cli import main
from pcos_tools.recon_parse import SECTION_KEYS, extract_dates, extract_people, parse_recon


@pytest.fixture
def recon(recon_path):
    return parse_recon(recon_path.read_text(encoding="utf-8"), source=recon_path.name)


def test_all_six_sections_found(recon):
    assert [recon["sections"][key]["found"] for key in SECTION_KEYS] == [True] * 6
    assert recon["warnings"] == []
    assert recon["heading_mode"] == "markdown"


def test_item_counts(recon):
    counts = {key: len(recon["sections"][key]["items"]) for key in SECTION_KEYS}
    assert counts == {"coverage": 3, "action_on_joe": 3, "waiting_on_others": 3,
                      "delegable": 2, "patterns": 2, "run_log": 2}


def test_dates(recon):
    waiting = recon["sections"]["waiting_on_others"]["items"]
    assert waiting[0]["dates"] == [{"raw": "2026-08-15", "iso": "2026-08-15"}]
    action = recon["sections"]["action_on_joe"]["items"]
    assert action[1]["dates"][0]["iso"] == "2026-09-05"
    assert recon["as_of"] == "2026-09-01"


def test_people(recon):
    names = {person["name"] for person in recon["people"]}
    assert {"Ahmet Yilmaz", "Fatma Demir", "Mehmet Kaya", "Selin Aksoy", "Dr. Kaya"} <= names
    for noise in ("Gmail", "Calendar", "Coverage", "Sep", "October", "Reply", "Waiting", "Items"):
        assert noise not in names
    ahmet = next(person for person in recon["people"] if person["name"] == "Ahmet Yilmaz")
    assert ahmet["count"] == 2
    assert ahmet["confidence"] == "pattern"


def test_task_ids(recon):
    assert recon["sections"]["waiting_on_others"]["items"][0]["task_ids"] == ["T-005"]
    assert recon["task_ids"] == ["T-005", "T-007"]


def test_coverage_fields(recon):
    fields = recon["sections"]["coverage"]["fields"]
    assert fields["Period"] == "2026-08-25 to 2026-09-01"
    assert recon["sections"]["run_log"]["fields"]["Run"].startswith("RECON-07")


def test_known_people_flag(recon_path):
    parsed = parse_recon(recon_path.read_text(encoding="utf-8"), known_people=["Joe", "ahmet yilmaz"])
    ahmet = next(person for person in parsed["people"] if person["name"].lower() == "ahmet yilmaz")
    assert ahmet["confidence"] == "known"


def test_missing_section_warning():
    text = "## 1. Coverage header\n- Period: 2026-09-01\n## 2. ACTION ON JOE\n- Do a thing\n"
    parsed = parse_recon(text)
    assert parsed["sections"]["action_on_joe"]["items"][0]["text"] == "Do a thing"
    assert parsed["sections"]["delegable"]["found"] is False
    assert any("section 4" in warning for warning in parsed["warnings"])


def test_plain_numbered_headers_without_hashes():
    text = ("1. Coverage header\n- Period: 2026-09-01\n\n2. ACTION ON JOE\n- Call the bank\n\n"
            "3. WAITING ON OTHERS\n- Waiting on Ayse Kaya for the quote\n4. DELEGABLE\n- x\n"
            "5. Patterns\n- y\n6. Run-log footer\n- Run: ok\n")
    parsed = parse_recon(text)
    assert parsed["heading_mode"] == "plain"
    assert all(parsed["sections"][key]["found"] for key in SECTION_KEYS)
    assert parsed["sections"]["waiting_on_others"]["items"][0]["people"][0]["name"] == "Ayse Kaya"


def test_numbered_bullets_are_not_headers():
    text = ("## 2. ACTION ON JOE\n1. First thing\n2. Second thing\n3. Waiting for nothing\n"
            "## 3. WAITING ON OTHERS\n- z\n")
    parsed = parse_recon(text)
    assert [item["text"] for item in parsed["sections"]["action_on_joe"]["items"]] == [
        "First thing", "Second thing", "Waiting for nothing"]
    assert len(parsed["sections"]["waiting_on_others"]["items"]) == 1


def test_extract_dates_formats():
    found = extract_dates("due 2026-09-03, then Sep 5, 2026 and 12 Oct, slash 03/09/2026", 2026)
    assert [d["iso"] for d in found] == ["2026-09-03", "2026-09-05", "2026-10-12", None]
    assert found[-1]["raw"] == "03/09/2026"


def test_extract_people_handles_turkish_and_accented_names():
    people = extract_people("Waiting on Ayşe Çelik for the quote; ping İbrahim Öztürk and Ahmet Yılmaz; "
                            "cc @Gülşah about the café")
    names = {p["name"] for p in people}
    assert {"Ayşe Çelik", "İbrahim Öztürk", "Ahmet Yılmaz", "Gülşah"} <= names
    assert "café" not in names and "Ahmet" not in names


def test_extract_people_confidence():
    people = extract_people("Ping @selin and ask Mehmet Kaya; Fatma Demir agreed", known_people=["Fatma Demir"])
    by_name = {p["name"]: p["confidence"] for p in people}
    assert by_name["selin"] == "mention"
    assert by_name["Mehmet Kaya"] == "pattern"
    assert by_name["Fatma Demir"] == "known"


def test_cli_writes_json(recon_path, tmp_path):
    out = tmp_path / "recon.json"
    assert main(["recon_parse", str(recon_path), "--out", str(out)]) == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["source"] == recon_path.name
    assert len(data["sections"]["action_on_joe"]["items"]) == 3


# ------------------------------------------------------ v0.3.0: runbook v1.4 --

def test_runbook_v14_layout():
    from .conftest import FIXTURES

    text = (FIXTURES / "RECON_v14_sample.md").read_text(encoding="utf-8")
    parsed = parse_recon(text, source="RECON_v14_sample.md")
    assert parsed["layout"] == "runbook-v1.4"
    sections = parsed["sections"]
    assert all(section["found"] for section in sections.values())
    assert [len(sections[key]["items"]) for key in sections] == [0, 1, 1, 1, 1, 0, 0]
    new = sections["new_task_candidates"]["items"][0]
    assert new["ref"] == "1.1" and new["text"] == "Parking permit renewal for the office garage"
    assert new["fields"]["Urgency"] == "MED"
    update = sections["task_updates"]["items"][0]
    assert update["text"].startswith("T-005 (Invoice from Ahmet Yilmaz)") and update["task_ids"] == ["T-005"]
    assert {d["iso"] for d in update["dates"]} == {"2026-09-03"}
    follow = sections["action_on_joe"]["items"][0]
    assert follow["text"].startswith("An answer on the CRM vendor") and follow["task_ids"] == ["T-007"]
    assert sections["sensitive"]["items"][0]["task_ids"] == ["T-001"]
    assert sections["coverage"]["fields"]["Channel used"] == "Connector, read-only."
    assert parsed["as_of"] == "2026-09-01"  # from the ISO timestamps in the coverage table
    assert parsed["task_ids"] == ["T-001", "T-005", "T-007"]
    assert parsed["warnings"] == []


def test_legacy_layout_is_unchanged(recon_path):
    parsed = parse_recon(recon_path.read_text(encoding="utf-8"))
    assert parsed["layout"] == "legacy"
    assert list(parsed["sections"]) == SECTION_KEYS


def test_v14_recon_feeds_legacy_now_build_decisions(worklist_path, prev_now_path, today):
    from pcos_tools.common import read_worklist
    from pcos_tools.now_build import build_now
    from .conftest import FIXTURES

    recon = parse_recon((FIXTURES / "RECON_v14_sample.md").read_text(encoding="utf-8"))
    text, _ = build_now(read_worklist(worklist_path), recon, prev_now_path.read_text(encoding="utf-8"), today)
    assert "[NEW from RECON 2026-09-01] An answer on the CRM vendor (T-007)" in text
    assert "Parking permit" not in text  # candidates are not decisions


def test_legacy_file_with_section_word_headings_stays_legacy(recon_path):
    text = recon_path.read_text(encoding="utf-8")
    for number in range(1, 7):
        text = text.replace(f"## {number}. ", f"## Section {number}: ")
    parsed = parse_recon(text)
    assert parsed["layout"] == "legacy"
    assert len(parsed["sections"]["action_on_joe"]["items"]) == 3


def test_v14_sub_heading_does_not_switch_section():
    from .conftest import FIXTURES

    text = (FIXTURES / "RECON_v14_sample.md").read_text(encoding="utf-8")
    text = text.replace("- **Suggested next action:** Chase", "### Follow-up context\n- **Suggested next action:** Chase")
    parsed = parse_recon(text)
    assert len(parsed["sections"]["task_updates"]["items"]) == 1
    assert len(parsed["sections"]["action_on_joe"]["items"]) == 1
    assert "Item" not in parsed["sections"]["coverage"]["fields"]  # table header row skipped
