"""Checks for PCOS queue item QC28: the live rules for text Joe reads, and one clock.

Four live Rules rows bind every lane that writes text Joe reads (item codes with a
plain description, one home per record, the email rules, person names). The card
standard (agents/CARD_TEMPLATE.md) holds them, every card states them in part 4,
every Routine prompt carries them as its TEXT RULES paragraph, and the checker
checks them as common check C5. An output template never shows an item code
without a description slot.

One clock: every Routine runs on the time zone of Joe's Outlook calendar,
America/Mexico_City. A Routine whose schedule names another zone, or none, fails.
"""
import re
from pathlib import Path

import pytest

from tests.test_agents_skills import cards, defined_keys, routine_prompt, routines, section

ROOT = Path(__file__).resolve().parent.parent
AGENTS = ROOT / "agents"
SKILLS = ROOT / "skills"
ROUTINES = ROOT / "routines"
TEMPLATE = AGENTS / "CARD_TEMPLATE.md"
CHECKLISTS = SKILLS / "checker" / "references" / "checklists.md"

# The time zone of Joe's Outlook calendar ("Central Standard Time (Mexico)"), read
# through the Microsoft 365 connector on 2026-10-09 by queue item QC28.
ONE_CLOCK = "America/Mexico_City"

# What every statement of the four rules must name: (a) the description, (b) the
# Drive recorder path, (c) the email rules key, (d) the people key.
RULE_MARKERS = ["plain description", "DRIVE WRITE:", "[[EMAIL_RULES]]", "[[PEOPLE]]"]

# An item code in a template: a capitalised placeholder for a Task ID, SAP code,
# item code, order number, SKU or question ID, or a literal Task or question ID.
ITEM_CODE = re.compile(r"(?<![\w-])(TASK-ID|SAP-CODE|ITEM-CODE|PRODUCT-CODE|ORDER-NUMBER|SKU"
                       r"|QUESTION-ID|T-(?:N{2,}|\d{2,4})|Q-(?:N{3,}|\d{4}))(?![\w-])")
SLOT_AFTER = re.compile(r"\s*\(DESCRIPTION")
SLOT_BEFORE = re.compile(r"DESCRIPTION\s*\($")
FENCE = re.compile(r"^```[^\n]*\n(.*?)^```$", re.M | re.S)
INLINE = re.compile(r"(?<!`)`([^`\n]+)`(?!`)")
ZONE = re.compile(r"\b(?:Africa|America|Antarctica|Asia|Atlantic|Australia|Europe|Etc|Indian|Pacific)"
                  r"/[A-Za-z_]+(?:/[A-Za-z_]+)?")


def read(path):
    return path.read_text(encoding="utf-8")


def flat(text):
    return " ".join(text.split())


def without_change_notes(text):
    """The file without its change note, which records history (old times included)."""
    return re.split(r"^## Change note\s*$", text, maxsplit=1, flags=re.M)[0]


def bare_item_codes(text):
    """Item codes in text that stand without a DESCRIPTION slot next to them."""
    return [match.group() for match in ITEM_CODE.finditer(text)
            if not (SLOT_AFTER.match(text, match.end()) or SLOT_BEFORE.search(text[:match.start()]))]


def templates(path):
    """The output templates of a file: fenced blocks and inline code spans."""
    text = read(path)
    return [*FENCE.findall(text), *INLINE.findall(FENCE.sub("", text))]


def template_files():
    return sorted([*AGENTS.glob("*.md"), *SKILLS.rglob("*.md"), *ROUTINES.glob("*.md")])


def zone_problems(trigger):
    """What is wrong with a Routine's Trigger line under the one clock."""
    problems = []
    if "cron `" in trigger and f"CRON_TZ={ONE_CLOCK}" not in trigger:
        problems.append(f"cron without CRON_TZ={ONE_CLOCK}")
    problems += [f"zone {zone}" for zone in ZONE.findall(trigger) if zone != ONE_CLOCK]
    problems += [f"CRON_TZ={zone}" for zone in re.findall(r"CRON_TZ=(\S+?)[,)\s]", trigger + " ")
                 if zone != ONE_CLOCK]
    if re.search(r"\bUTC\b|\bGMT\b", trigger):
        problems.append("a time in UTC")
    return problems


def trigger_line(path):
    return re.search(r"^- Trigger: (.*)$", read(path), re.M).group(1)


# --- the four live rules -------------------------------------------------------------

def test_card_standard_holds_the_four_live_rules_with_their_sources():
    rules = section(read(TEMPLATE), "## Live rules for text Joe reads")
    rows = re.findall(r"^\| \(([a-d])\) ([^|]+) \| ([^|]+) \| ([^|]+) \|$", rules, re.M)
    assert [row[0] for row in rows] == ["a", "b", "c", "d"]
    for marker in RULE_MARKERS:
        assert marker in flat(rules), f"the card standard does not name {marker}"
    assert all(re.search(r"20\d\d-\d\d-\d\d", source) for *_, source in rows), "a rule has no dated source"
    assert "TASK-ID (DESCRIPTION)" in rules
    inherited = section(read(TEMPLATE), "## Rules every card inherits")
    assert "live rules for text Joe reads" in inherited and ONE_CLOCK in inherited


def test_the_email_rules_key_is_defined():
    assert "EMAIL_RULES" in defined_keys()


@pytest.mark.parametrize("card", cards(), ids=lambda p: p.stem)
def test_every_card_states_the_live_text_rules_in_part_4(card):
    part = flat(section(read(card), "## 4. Rules and kernel version"))
    assert "Live text rules" in part, "part 4 has no Live text rules line"
    for marker in RULE_MARKERS:
        assert marker in part, f"the Live text rules line does not name {marker}"


@pytest.mark.parametrize("routine", routines(), ids=lambda p: p.stem)
def test_every_routine_prompt_carries_the_text_rules(routine):
    prompt = routine_prompt(read(routine))
    paragraph = next((line for line in prompt.splitlines() if line.startswith("TEXT RULES")), None)
    assert paragraph, "the prompt has no TEXT RULES paragraph"
    for marker in RULE_MARKERS:
        assert marker in paragraph, f"TEXT RULES does not name {marker}"


def test_checker_checks_the_live_text_rules_on_every_output_joe_reads():
    common = flat(read(CHECKLISTS).split("## mail-draft")[0])
    assert "C5 Live text rules" in common
    for marker in RULE_MARKERS:
        assert marker in common, f"check C5 does not name {marker}"
    assert "a code alone is a FAIL" in common
    card = flat(section(read(CHECKLISTS), "## question-card"))
    assert "a bare code is a FAIL" in card
    assert "[[EMAIL_RULES]]" in flat(section(read(CHECKLISTS), "## mail-draft"))


def test_today_shows_codes_with_their_description_and_keeps_one_mirror_file():
    prompt = flat(routine_prompt(read(ROUTINES / "L2-render.md")))
    assert "TASK-ID (DESCRIPTION), never the code alone" in prompt
    assert "as new files" not in prompt and "[SUPERSEDED]" not in prompt
    assert "keeps its link" in prompt and '"DRIVE WRITE:" row in [[INBOX]]' in prompt
    assert "Drive recorder lane" in read(ROUTINES / "L2-render.md").split("## Prompt")[0]
    # a later render names each existing mirror by its own key, and counts what it queued
    assert "[[NOW_MIRROR]]" in prompt and "[[KERNEL_MIRROR]]" in prompt
    assert {"NOW_MIRROR", "KERNEL_MIRROR"} <= set(defined_keys())
    assert "rows changed (0)" not in prompt and 'per "DRIVE WRITE:" row filed' in prompt
    assert "never create the mirror again" in prompt


def test_the_drive_recorder_that_applies_drive_write_rows_is_listed():
    index = read(ROUTINES / "_INDEX.md")
    row = next((line for line in index.splitlines() if line.startswith("| Drive recorder (Claude side) |")), None)
    assert row, "routines/_INDEX.md does not list the Drive recorder lane"
    assert '"DRIVE WRITE:"' in row and "Applied" in row and "reads it back" in row


# --- item codes in output templates ---------------------------------------------------

@pytest.mark.parametrize("path", template_files(), ids=lambda p: str(p.relative_to(ROOT)))
def test_no_output_template_shows_an_item_code_without_a_description_slot(path):
    for template in templates(path):
        assert not bare_item_codes(template), (
            f"{path.relative_to(ROOT)}: item code without a description slot "
            f"{bare_item_codes(template)} in: {template.strip()[:120]}")


@pytest.mark.parametrize("text", [
    "Item: TASK-ID | owner | due", "T-057 overdue with the owner", "SAP-CODE, quantity, unit",
    "Q-0096 A | note", "row ORDER-NUMBER then T-NNN (DESCRIPTION)", "SKU only",
])
def test_bare_item_code_detector_catches_codes_alone(text):
    assert bare_item_codes(text)


@pytest.mark.parametrize("text", [
    "Item: TASK-ID (DESCRIPTION) | owner", "DESCRIPTION (SAP-CODE), quantity with unit",
    "T-NNN (DESCRIPTION) and ORDER-NUMBER (DESCRIPTION)", "never mint a Task ID",
    "council-board-review-2", "TASK-IDS", "MY-SKU-LIST",
])
def test_bare_item_code_detector_passes_codes_with_a_slot_and_plain_words(text):
    assert not bare_item_codes(text)


# --- one clock ------------------------------------------------------------------------

@pytest.mark.parametrize("routine", routines(), ids=lambda p: p.stem)
def test_every_routine_runs_on_the_one_clock(routine):
    trigger = trigger_line(routine)
    assert "cron `" in trigger
    assert not zone_problems(trigger), f"{routine.stem}: {zone_problems(trigger)}"


@pytest.mark.parametrize("card", cards(), ids=lambda p: p.stem)
def test_every_card_trigger_names_only_the_one_clock(card):
    part = section(read(card), "## 6. Trigger and owner model")
    trigger = re.search(r"^- Trigger: (.*?)(?=^- |\Z)", part, re.M | re.S).group(1)
    problems = [p for p in zone_problems(trigger) if not p.startswith("cron without")]
    assert not problems, f"{card.stem}: {problems}"


@pytest.mark.parametrize("path", template_files(), ids=lambda p: str(p.relative_to(ROOT)))
def test_no_card_skill_or_routine_names_another_time_zone(path):
    others = {zone for zone in ZONE.findall(without_change_notes(read(path))) if zone != ONE_CLOCK}
    assert not others, f"{path.relative_to(ROOT)} names {sorted(others)}"


def test_routines_index_states_the_one_clock():
    index = flat(read(ROUTINES / "_INDEX.md"))
    assert f"One clock: every Routine runs on {ONE_CLOCK}" in index
    assert not re.search(r"\bUTC\b|Matamoros", index)


@pytest.mark.parametrize("trigger", [
    "cron `0 7,13 * * *`, CRON_TZ=America/Matamoros (07:00 and 13:00 daily)",
    "cron `0 15 * * 0` (Sunday 15:00 UTC)",
    "cron `0 */2 * * *` (every 2 hours)",
    f"cron `0 9 * * 0`, CRON_TZ={ONE_CLOCK} (Sunday 09:00, card at 19:00 Europe/Istanbul)",
])
def test_clock_check_catches_another_zone_or_none(trigger):
    assert zone_problems(trigger)


def test_clock_check_passes_the_one_clock():
    assert not zone_problems(f"cron `40 6,12,18 * * 1-5`, CRON_TZ={ONE_CLOCK} (weekdays 06:40)")
