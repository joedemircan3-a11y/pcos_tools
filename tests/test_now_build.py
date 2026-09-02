import copy
import json
import re

import pytest

from pcos_tools.common import STATUS_VOCAB, load_vocab, read_worklist
from pcos_tools.cli import main
from pcos_tools.now_build import DRAFT_NAME, active_table, build_now, parse_now, section_body
from pcos_tools.recon_parse import parse_recon

ACTIVE_ORDER = ["T-001", "T-002", "T-003", "T-006", "T-007", "T-021", "T-023", "T-022", "T-004"]
BASE_ROW = {"Title": "x", "Room": "1", "Status": "Active", "Priority": "MED", "Owner": "Joe",
            "Waiting On": "", "Sources": "s", "Next Action": "", "Updated": "2026-08-30",
            "Confidence": "High", "Notes": "", "_row": 2}


@pytest.fixture
def inputs(worklist_path, recon_path, prev_now_path):
    rows = read_worklist(worklist_path)
    recon = parse_recon(recon_path.read_text(encoding="utf-8"), source=recon_path.name)
    return rows, recon, prev_now_path.read_text(encoding="utf-8")


@pytest.fixture
def draft(inputs, today):
    rows, recon, prev = inputs
    text, warnings = build_now(rows, recon, prev, today)
    assert warnings == []
    return text


@pytest.fixture
def parsed(draft):
    return parse_now(draft)


def table_ids(body):
    return [line.split("|")[1].strip() for line in body.splitlines()[2:] if line.startswith("|")]


def make_row(task_id, status, priority, room="1"):
    return dict(BASE_ROW, **{"Task ID": task_id, "Status": status, "Priority": priority, "Room": room})


def test_sections_zero_to_eight_in_order(parsed, draft):
    assert sorted(parsed["sections"]) == list(range(0, 9))
    assert parsed["sections"][0]["heading"] == "## 0. JOE TODAY"
    assert parsed["sections"][7]["heading"] == "## 7. POINTERS AND ROOM SOURCE MAPS"
    assert draft.index("## 0. JOE TODAY") < draft.index("## 1. DECISIONS")
    assert len(re.findall(r"^## \d", draft, flags=re.M)) == 9


def test_section_zero_carried_unchanged(parsed, prev_now_path):
    prev = parse_now(prev_now_path.read_text(encoding="utf-8"))
    assert section_body(parsed, 0) == section_body(prev, 0)
    assert "Call the landlord back before noon" in section_body(parsed, 0)


def test_section_zero_never_created(inputs, today):
    rows, recon, prev = inputs
    without_zero = re.sub(r"## 0\. JOE TODAY\n(?:.*\n)*?(?=## 1\.)", "", prev)
    assert "## 0." not in without_zero
    text, warnings = build_now(rows, recon, without_zero, today)
    assert warnings == []
    assert 0 not in parse_now(text)["sections"]
    assert "JOE TODAY" not in text


def test_active_table_order_and_exclusions(parsed):
    body = section_body(parsed, 2)
    assert table_ids(body) == ACTIVE_ORDER
    for absent in ("T-999", "T-18", "Book dentist", "T-024", "Confirm archive box", "T-025"):
        assert absent not in body


def test_bad_date_rows_are_marked_in_section_2(parsed):
    body = section_body(parsed, 2)
    row = [line for line in body.splitlines() if "| T-021 |" in line][0]
    assert row.endswith("| 31/08/2026 | [BAD DATE] |")
    assert body.count("[BAD DATE]") == 1


def test_aged_days_from_vocab_drives_the_aged_mark(inputs, today, tmp_path):
    rows, recon, prev = inputs
    custom = tmp_path / "vocab.json"
    custom.write_text(json.dumps({
        "status": STATUS_VOCAB, "room": ["1", "2", "3", "4", "10", "13", "PERSONAL"],
        "priority": ["CRITICAL", "HIGH-TODAY", "HIGH", "MED-HIGH", "MED", "LOW", "RECURRING", ""],
        "stale_days": 90, "aged_days": 20}), encoding="utf-8")
    body = section_body(parse_now(build_now(rows, recon, prev, today, vocab=load_vocab(custom))[0]), 3)
    assert "[AGED]" not in body  # T-005 is 17 days old, below the custom 20
    body = section_body(parse_now(build_now(rows, recon, prev, today, vocab=load_vocab(custom), aged_days=10)[0]), 3)
    assert "[AGED]" in [line for line in body.splitlines() if "| T-005 |" in line][0]


def test_active_low_ranks_low_even_with_high_priority(parsed):
    body = section_body(parsed, 2)
    order = table_ids(body)
    assert order.index("T-022") > order.index("T-023")  # after the plain LOW row
    assert order.index("T-022") > order.index("T-021")  # after MED
    assert order.index("T-022") < order.index("T-004")  # above RECURRING
    assert "| T-022 | Tidy shared inbox labels | 2 | Active-Low | HIGH |" in body


def test_active_low_takes_low_rank_whatever_its_priority(today):
    rows = [
        make_row("T-101", "Active-Recurring", "RECURRING"),
        make_row("T-102", "Active-Low", "RECURRING"),
        make_row("T-103", "Active-Low", ""),
        make_row("T-104", "Active", ""),
        make_row("T-105", "Active", "LOW"),
        make_row("T-106", "Active-Low", "LOW"),
        make_row("T-107", "Active-Low", "CRITICAL"),
        make_row("T-108", "Active", "MED"),
        make_row("T-109", "Done-Candidate", "CRITICAL"),
        make_row("T-110", "Active-Low", "HIGH", room="PERSONAL"),
    ]
    order = table_ids(active_table(rows, today))
    assert order == ["T-108", "T-105", "T-102", "T-103", "T-106", "T-107", "T-101", "T-104"]


def test_waiting_table_ages_recon_merge_and_personal_exclusion(parsed):
    body = section_body(parsed, 3)
    lines = {line.split("|")[1].strip(): line for line in body.splitlines()[2:]}
    assert "[AGED]" in lines["T-005"] and "[RECON]" in lines["T-005"]
    assert "| 17 |" in lines["T-005"]
    assert "[AGED]" not in lines["T-017"]
    assert "T-019" not in body and "Gym membership" not in body
    assert body.count("RECON s3") == 2
    assert "Selin Aksoy" in body and "Dr. Kaya" in body
    assert "corrected invoice" not in body
    assert table_ids(body)[0] == "T-005"


def test_recon_waiting_item_about_a_personal_task_is_dropped(inputs, today):
    rows, recon, prev = inputs
    recon = copy.deepcopy(recon)
    recon["sections"]["waiting_on_others"]["items"].append({
        "text": "Waiting on Gym for the membership card since 2026-08-20 (T-019)", "level": 0,
        "task_ids": ["T-019"], "dates": [{"raw": "2026-08-20", "iso": "2026-08-20"}],
        "people": [{"name": "Gym", "confidence": "pattern"}]})
    text, _ = build_now(rows, recon, prev, today)
    body = section_body(parse_now(text), 3)
    assert "T-019" not in body and "membership card" not in body
    assert body.count("RECON s3") == 2


def test_stale_block_threshold_and_personal_exclusion(parsed):
    body = section_body(parsed, 6)
    lines = body.splitlines()
    assert [line.split(" - ")[0] for line in lines] == ["- T-014", "- T-026", "- T-015"]
    assert "[ARCHIVE?]" in lines[0] and "[ARCHIVE?]" in lines[1]
    assert "[ARCHIVE?]" not in lines[2]
    assert "T-025" not in body and "holiday photo" not in body
    assert "old stale content" not in body


def test_pointers_verbatim(parsed, prev_now_path):
    prev = parse_now(prev_now_path.read_text(encoding="utf-8"))
    assert section_body(parsed, 7) == section_body(prev, 7)
    assert "Room 1 sources" in section_body(parsed, 7)


def test_sections_4_and_8_unchanged(parsed, prev_now_path):
    prev = parse_now(prev_now_path.read_text(encoding="utf-8"))
    for number in (4, 8):
        assert section_body(parsed, number) == section_body(prev, number)


def test_decisions_appended_from_recon(parsed):
    body = section_body(parsed, 1)
    assert body.startswith("1. Approve lease counter-offer")
    assert "3. [NEW from RECON 2026-09-01] Reply to Ahmet Yilmaz" in body
    assert "5. [NEW from RECON 2026-09-01] Sign the revised lease addendum" in body


def test_candidates_appended_from_recon(parsed):
    body = section_body(parsed, 5)
    assert body.startswith("- Website copy refresh (T-008)")
    assert "- [CANDIDATE from RECON] Invoice follow-ups slip" in body
    assert body.count("[CANDIDATE from RECON]") == 2


def test_rebuild_is_idempotent_for_carried_and_appended_sections(inputs, draft, today):
    rows, recon, _ = inputs
    second, _ = build_now(rows, recon, draft, today)
    first_parsed, second_parsed = parse_now(draft), parse_now(second)
    for number in (0, 1, 4, 5, 7, 8):
        assert section_body(second_parsed, number) == section_body(first_parsed, number)
    assert second.count("<!-- PCOS_NOW draft generated") == 1


def test_missing_sections_get_default_headings(inputs, today):
    rows, recon, _ = inputs
    text, warnings = build_now(rows, recon, "# PCOS_NOW\n\n## 1. DECISIONS\n1. Only one\n", today)
    assert len(warnings) == 7
    parsed = parse_now(text)
    assert sorted(parsed["sections"]) == list(range(1, 9))
    assert parsed["sections"][3]["heading"] == "## 3. WAITING ON OTHERS"
    assert parsed["sections"][6]["heading"] == "## 6. STALE BLOCK"
    assert parsed["sections"][8]["heading"] == "## 8. SYSTEM STATUS"
    assert "## 0" not in text


def test_sections_located_by_leading_number_only(inputs, today):
    rows, recon, _ = inputs
    prev = ("# NOW\n\n## 0 Today\n- x\n\n## 1) Whatever\n1. keep\n\n## 2 - Doing\nold\n\n"
            "## 3: Waiting stuff\nold\n\n## 4. Deltas\n- d\n\n## 5 Ideas\n- i\n\n## 6\nold\n\n"
            "## 7 Links\n- p\n\n## 8 Status\n- s\n")
    text, warnings = build_now(rows, recon, prev, today)
    assert warnings == []
    parsed = parse_now(text)
    assert parsed["sections"][0]["heading"] == "## 0 Today"
    assert parsed["sections"][6]["heading"] == "## 6"
    assert section_body(parsed, 7) == "- p"
    assert section_body(parsed, 4) == "- d"
    assert "1. keep" in section_body(parsed, 1)
    assert table_ids(section_body(parsed, 2)) == ACTIVE_ORDER


def test_lookalike_lines_are_not_section_headings():
    text = ("## 10 things\n- a\n## 2026-08-25 report\n- b\n## 1. Real\n- c\n#2 option is cheaper\n"
            "### 2.1 Sub-point\n- d\n#7 is not a heading either\n")
    parsed = parse_now(text)
    assert sorted(parsed["sections"]) == [1]
    assert section_body(parsed, 1) == "- c\n#2 option is cheaper\n### 2.1 Sub-point\n- d\n#7 is not a heading either"


def test_headings_without_a_space_after_the_number_are_found():
    parsed = parse_now("## 0.JOE TODAY\n- t\n## 1.DECISIONS\n- a\n## 2)ACTIVE\n- b\n## 3:WAITING\n- c\n## 6-STALE\n- d\n")
    assert sorted(parsed["sections"]) == [0, 1, 2, 3, 6]
    assert parsed["sections"][1]["title"] == "DECISIONS"
    bold = parse_now("**1.DECISIONS**\n- a\n**2.ACTIVE**\n- b\n**6**\n- c\n")
    assert sorted(bold["sections"]) == [1, 2, 6] and bold["style"] == "bold"


def test_headings_inside_code_fences_are_ignored(inputs, today):
    rows, recon, _ = inputs
    prev = ("# NOW\n\n## 0. JOE TODAY\nExample of the format:\n```\n## 2. ACTIVE\n| a |\n```\n- real line\n\n"
            "## 1. DECISIONS\n1. keep\n\n## 2. ACTIVE\nold\n\n## 3. WAITING ON OTHERS\nold\n\n## 4. DELTAS\n- d\n\n"
            "## 5. CANDIDATES\n- i\n\n## 6. STALE BLOCK\nold\n\n## 7. POINTERS\n- p\n\n## 8. STATUS\n- s\n")
    text, warnings = build_now(rows, recon, prev, today)
    assert warnings == []
    parsed = parse_now(text)
    assert section_body(parsed, 0) == "Example of the format:\n```\n## 2. ACTIVE\n| a |\n```\n- real line"
    assert text.count("\n## 2. ACTIVE\n") == 2  # one inside the fence, one real heading
    assert table_ids(section_body(parsed, 2)) == ACTIVE_ORDER


def test_empty_recon_items_are_never_appended(inputs, today):
    rows, _, prev = inputs
    recon = parse_recon("# RECON 2026-09-01\n\n## 2. ACTION ON JOE\n- [ ]\n- Reply to Ahmet\n- ???\n\n"
                        "## 5. Patterns\n- [x]\n- ...\n- Real pattern\n")
    first, _ = build_now(rows, recon, prev, today)
    second, _ = build_now(rows, recon, first, today)
    for number in (1, 5):
        assert section_body(parse_now(first), number) == section_body(parse_now(second), number)
    body1, body5 = section_body(parse_now(first), 1), section_body(parse_now(first), 5)
    assert body1.count("[NEW from RECON") == 1 and "Reply to Ahmet" in body1
    assert body5.count("[CANDIDATE from RECON]") == 1 and "Real pattern" in body5


def test_recon_line_naming_both_a_personal_and_a_work_task_marks_the_work_row(inputs, today):
    rows, recon, prev = inputs
    recon = copy.deepcopy(recon)
    recon["sections"]["waiting_on_others"]["items"] = [{
        "text": "Chased Ahmet Yilmaz for T-005 and the gym for T-019 on 2026-08-30", "level": 0,
        "task_ids": ["T-005", "T-019"], "dates": [], "people": []}]
    body = section_body(parse_now(build_now(rows, recon, prev, today)[0]), 3)
    assert "[RECON]" in [line for line in body.splitlines() if "| T-005 |" in line][0]
    assert "T-019" not in body and "RECON s3" not in body


def test_bold_numbered_headings_are_supported_and_kept(inputs, today):
    rows, recon, _ = inputs
    prev = ("# NOW\n\n**0. JOE TODAY**\n- morning\n\n**1. DECISIONS**\n1. keep\n\n**2. ACTIVE**\nold\n\n"
            "**3. WAITING ON OTHERS**\nold\n\n**4. DELTAS**\n- d\n\n**5. CANDIDATES**\n- i\n\n"
            "**7. POINTERS AND ROOM SOURCE MAPS**\n- p\n\n**8. SYSTEM STATUS**\n- s\n")
    text, warnings = build_now(rows, recon, prev, today)
    assert warnings == ["section 6 missing in previous PCOS_NOW; default heading used"]
    parsed = parse_now(text)
    assert parsed["style"] == "bold"
    assert sorted(parsed["sections"]) == list(range(0, 9))
    assert parsed["sections"][0]["heading"] == "**0. JOE TODAY**"
    assert parsed["sections"][6]["heading"] == "**6. STALE BLOCK**"
    assert section_body(parsed, 7) == "- p"
    assert "## " not in text.split("-->", 1)[1].replace("# NOW", "")
    second, warnings_again = build_now(rows, recon, text, today)
    assert warnings_again == []
    assert section_body(parse_now(second), 7) == "- p"
    assert section_body(parse_now(second), 0) == "- morning"


def test_custom_vocab_and_stale_days_change_the_archive_mark(inputs, today, tmp_path):
    rows, recon, prev = inputs
    custom = tmp_path / "vocab.json"
    custom.write_text(json.dumps({
        "status": STATUS_VOCAB, "room": ["1", "2", "3", "4", "10", "13", "PERSONAL"],
        "priority": ["CRITICAL", "HIGH-TODAY", "HIGH", "MED-HIGH", "MED", "LOW", "RECURRING", ""],
        "stale_days": 200}), encoding="utf-8")
    text, _ = build_now(rows, recon, prev, today, vocab=load_vocab(custom))
    assert "[ARCHIVE?]" not in section_body(parse_now(text), 6)
    text, _ = build_now(rows, recon, prev, today, vocab=load_vocab(custom), stale_days=100)
    assert section_body(parse_now(text), 6).count("[ARCHIVE?]") == 2


def test_cli_with_markdown_recon(worklist_path, recon_path, prev_now_path, tmp_path):
    code = main(["now_build", "--csv", str(worklist_path), "--recon", str(recon_path),
                 "--prev", str(prev_now_path), "--out-dir", str(tmp_path), "--today", "2026-09-01",
                 "--stale-days", "120"])
    assert code == 0
    text = (tmp_path / DRAFT_NAME).read_text(encoding="utf-8")
    assert len(re.findall(r"^## \d\. ", text, flags=re.M)) == 9
    assert section_body(parse_now(text), 6).count("[ARCHIVE?]") == 1  # only T-014 at 120 days
    assert prev_now_path.read_text(encoding="utf-8").startswith("# PCOS_NOW")


def test_cli_with_trimmed_recon_json(worklist_path, prev_now_path, tmp_path):
    recon = tmp_path / "recon.json"
    recon.write_text(json.dumps({"sections": {"waiting_on_others": {"items": [
        {"text": "Waiting on Ayse Kaya for the quote (T-005)"}]}}}), encoding="utf-8")
    assert main(["now_build", "--csv", str(worklist_path), "--recon", str(recon), "--prev", str(prev_now_path),
                 "--out-dir", str(tmp_path), "--today", "2026-09-01"]) == 0
    body = section_body(parse_now((tmp_path / DRAFT_NAME).read_text(encoding="utf-8")), 3)
    assert "[RECON]" in body and "RECON s3" not in body  # T-005 merged, nothing else appended
