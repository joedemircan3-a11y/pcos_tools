"""Format checks for the agent cards (agents/), skills (skills/), Routine prompts
(routines/) and the pull request template (.github/).

They keep every card on the six-part template, every skill in the Agent Skills
format, every Routine prompt paste-ready, every source key defined, and keep
private identifiers out of this public repository.
"""
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
AGENTS = ROOT / "agents"
SKILLS = ROOT / "skills"
ROUTINES = ROOT / "routines"
PR_TEMPLATE = ROOT / ".github" / "pull_request_template.md"

PARTS = [
    "## 1. Mission",
    "## 2. Inputs by ID",
    "## 3. Tools allowed",
    "## 4. Rules and kernel version",
    "## 5. Output contract with evidence labels",
    "## 6. Trigger and owner model",
]
HEADER_FIELDS = ["Version", "Status", "Register", "Lane ID", "Skills", "Date"]
PLANNED_LANES = [
    "prediction-ledger", "exo", "checker", "council-board", "council-github",
    "intake-email", "weekly-evolve", "knowledge-extract", "knowledge-review",
    "knowledge-chair",
]
SKILLS_WRITTEN = ["checker", "prediction-ledger", "exo", "council-board", "intake-email", "weekly-evolve"]
LABELS = ["Confirmed", "Candidate", "Needs Source Check", "Needs Thread Check",
          "Needs Joe Approval", "Blocked"]
NOT_CARDS = {"CARD_TEMPLATE.md", "INPUTS.md", "_INDEX.md"}
ROUTINE_FIELDS = ["Status", "Lane", "Trigger", "Repository", "Connectors", "Model", "Card",
                  "Skills", "Needs first"]
CHECKLIST = ["Six-part card present", "Sources by ID", "Evidence labels", "No pricing commitment",
             "No external send"]

KEY_USE = re.compile(r"\[\[([A-Z0-9_]+)\]\]")
PLACEHOLDER_KEY = "KEY"  # the template and the skills explain the syntax as [[KEY]]
KEY_DEF = re.compile(r"^\| `([A-Z0-9_]+)` \|", re.M)
LINK = re.compile(r"\]\(([^)\s]+)\)")
SKILL_NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
KEY_ROW = re.compile(r"^\| `([A-Z0-9_]+)` \| [^|\n]* \| ([^|\n]*) \|", re.M)
GROUP_ROW = re.compile(r"^\| `([A-Z0-9_]+)` \| ([^|\n]*) \|", re.M)
PLURAL_OBJECT = re.compile(r"\b(folders|files|databases|pages|views|sheets)\b")
SET_KEYS = {"MAIL_ROUTED"}  # Outlook folders named in one list; see the top of INPUTS.md

# Drive IDs are opaque runs of the URL-safe alphabet: letters, digits, "-" and "_".
# A run of that alphabet with both cases and a digit is an ID unless every piece
# between the separators reads as a word, a number, a short code or a timestamp
# (KL_02_Mosaic_and_Waterjet_Production, PCOS_DISPATCH_2026-09-29b, QC18, v4).
ID_RUN = re.compile(r"(?<![A-Za-z0-9_-])[A-Za-z0-9_-]{12,}(?![A-Za-z0-9_-])")
WORDISH = re.compile(r"[A-Z]*[a-z]*|(?:[A-Z]{0,4}|[a-z]{0,4})\d+[a-z]{0,2}|\d+[A-Z]{1,4}"
                     r"|\d{8}T\d{4,6}Z?")


def find_drive_id(text):
    """Return the first Drive-style ID in text, or None."""
    for match in ID_RUN.finditer(text):
        run = match.group()
        if not all(re.search(c, run) for c in ("[a-z]", "[A-Z]", r"\d")):
            continue
        if not all(WORDISH.fullmatch(piece) for piece in re.split("[-_]", run)):
            return run
    return None


def first_match(pattern):
    """A finder that returns the first match of pattern as text, or None."""
    return lambda text: (found := pattern.search(text)) and found.group()


# Finders for what would publish private PCOS identifiers: Drive-style IDs,
# Notion IDs, UUIDs, e-mail addresses and links to Drive, Docs or Notion objects.
PRIVATE = {
    "Drive-style ID": find_drive_id,
    "Notion ID": first_match(re.compile(r"(?<![0-9a-f])[0-9a-f]{32}(?![0-9a-f])")),
    "UUID": first_match(re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")),
    "e-mail address": first_match(re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)+")),
    "Drive or Notion link": first_match(re.compile(r"(docs|drive)\.google\.com|notion\.(so|site|com)")),
}


def cards():
    return sorted(p for p in AGENTS.glob("*.md") if p.name not in NOT_CARDS)


def skill_files():
    return sorted(SKILLS.glob("*/SKILL.md"))


def routines():
    return sorted(p for p in ROUTINES.glob("*.md") if p.name != "_INDEX.md")


def public_files():
    return sorted([*(p for folder in (AGENTS, SKILLS, ROUTINES) for p in folder.rglob("*.md")),
                   PR_TEMPLATE])


def defined_keys():
    return KEY_DEF.findall((AGENTS / "INPUTS.md").read_text(encoding="utf-8"))


def section(text, heading):
    """The body of the markdown section whose heading line is exactly heading."""
    match = re.search(rf"^{re.escape(heading)}\n(.*?)(?=^#{{1,3}} |\Z)", text, re.M | re.S)
    assert match, f"section {heading!r} missing"
    return match.group(1)


def parse_frontmatter(text):
    """Split SKILL.md into (fields, body). Handles the flat keys plus one level of nesting used here."""
    assert text.startswith("---\n"), "SKILL.md must start with a --- frontmatter line"
    end = text.index("\n---\n", 4)
    fields, parent = {}, None
    for line in text[4:end].splitlines():
        if not line.strip():
            continue
        key, _, value = line.strip().partition(":")
        value = value.strip().strip('"')
        if line[0] in " \t":
            fields[parent][key] = value
        elif value:
            fields[key] = value
        else:
            fields[key], parent = {}, key
    return fields, text[end + 5:]


def test_every_planned_lane_has_a_card():
    assert sorted(p.stem for p in cards()) == sorted(PLANNED_LANES)


@pytest.mark.parametrize("card", cards(), ids=lambda p: p.stem)
def test_card_header_and_six_parts_in_order(card):
    text = card.read_text(encoding="utf-8")
    assert text.startswith(f"# Card: {card.stem}\n")
    for field in HEADER_FIELDS:
        assert re.search(rf"^- {field}: \S", text, re.M), f"header line {field} missing"
    positions = [text.find(f"\n{part}\n") for part in PARTS]
    assert -1 not in positions, f"missing part: {PARTS[positions.index(-1)]}"
    assert positions == sorted(positions)
    assert all(text.count(f"\n{part}\n") == 1 for part in PARTS)
    contract = text[positions[4]:positions[5]]
    assert "Evidence labels" in contract
    assert "Never:" in text[positions[0]:positions[1]]
    assert "Not allowed:" in text[positions[2]:positions[3]]


def test_template_shows_the_same_six_parts_and_all_labels():
    text = (AGENTS / "CARD_TEMPLATE.md").read_text(encoding="utf-8")
    for part in PARTS:
        assert f"\n{part}\n" in text
    for label in LABELS:
        assert f"| {label} |" in text


def test_input_keys_are_unique_and_every_used_key_is_defined():
    keys = defined_keys()
    assert len(keys) == len(set(keys)), "a key is defined twice in INPUTS.md"
    for path in public_files():
        unknown = set(KEY_USE.findall(path.read_text(encoding="utf-8"))) - set(keys) - {PLACEHOLDER_KEY}
        assert not unknown, f"{path.relative_to(ROOT)} uses undefined keys {sorted(unknown)}"


def test_every_written_skill_is_present():
    assert sorted(p.parent.name for p in skill_files()) == sorted(SKILLS_WRITTEN)


@pytest.mark.parametrize("skill", skill_files(), ids=lambda p: p.parent.name)
def test_skill_frontmatter_follows_the_agent_skills_format(skill):
    fields, body = parse_frontmatter(skill.read_text(encoding="utf-8"))
    name, description = fields["name"], fields["description"]
    assert SKILL_NAME.match(name) and len(name) <= 64
    assert name == skill.parent.name
    assert 1 <= len(description) <= 1024
    # plain YAML scalars may not contain these; keep descriptions unquoted and safe
    assert ": " not in description and " #" not in description
    assert len(fields.get("compatibility", "")) <= 500
    assert fields["metadata"]["version"] and fields["metadata"]["status"]
    assert (ROOT / fields["metadata"]["card"]).is_file()
    assert body.strip() and len(body.splitlines()) < 500


def test_skill_frontmatter_is_valid_yaml():
    yaml = pytest.importorskip("yaml")
    for skill in skill_files():
        text = skill.read_text(encoding="utf-8")
        data = yaml.safe_load(text[4:text.index("\n---\n", 4)])
        assert data["name"] == skill.parent.name and isinstance(data["metadata"], dict)


@pytest.mark.parametrize("path", public_files(), ids=lambda p: str(p.relative_to(ROOT)))
def test_relative_links_resolve(path):
    for target in LINK.findall(path.read_text(encoding="utf-8")):
        if not target.startswith(("http://", "https://", "#")):
            assert (path.parent / target.split("#")[0]).exists(), f"broken link {target}"


@pytest.mark.parametrize("path", public_files(), ids=lambda p: str(p.relative_to(ROOT)))
def test_no_private_identifiers_in_the_public_repository(path):
    text = path.read_text(encoding="utf-8")
    for what, find in PRIVATE.items():
        found = find(text)
        assert not found, f"{what} in {path.relative_to(ROOT)}: {found}"


@pytest.mark.parametrize("text", [
    "1Abc_defghijklmnop", "1abc_Defghijklmnop", "id 0AbC1dEf2GhI3jKl4Mn.",
    "(1aB9-xYz_Q2w3e4R5t6y7U8i9o0P1a)", "1-_xQ09Kp_Lm3NoPqRsTuVwXy",
])
def test_drive_id_detector_catches_ids_with_url_safe_separators(text):
    assert find_drive_id(text)


@pytest.mark.parametrize("text", [
    "KL_02_Mosaic_and_Waterjet_Production", "KL_05_Logistics_and_Customs_MX_US_TR",
    "PCOS_DISPATCH_2026-09-29b", "PCOS_BUILD_KIT_2026-09-28", "PCOS_AGENT_INPUT_IDS",
    "CLAIM_QC18_CLAUDE_code_20261006T021249Z.md", "council-board-review-2", "KL_VENDORS_RAW__INDEX",
])
def test_drive_id_detector_passes_file_and_key_names(text):
    assert find_drive_id(text) is None


def test_each_key_names_one_object_and_groups_list_keys():
    text = (AGENTS / "INPUTS.md").read_text(encoding="utf-8")
    groups = dict(GROUP_ROW.findall(section(text, "## Groups")))
    keys = {key: system for key, system in KEY_ROW.findall(text) if key not in groups}
    for key, system in keys.items():
        if key not in SET_KEYS:
            assert not PLURAL_OBJECT.search(system), f"{key} names more than one object: {system}"
    for group, members in groups.items():
        listed = re.findall(r"`([A-Z0-9_]+)`", members)
        assert listed, f"group {group} lists no keys"
        assert all(m in keys for m in listed), f"group {group} lists a key that is not defined"


def test_golden_set_lane_run_scores_the_output_and_the_checker_is_scored_apart():
    text = (SKILLS / "checker" / "SKILL.md").read_text(encoding="utf-8")
    lane_run = " ".join(section(text, "### Lane run: scores a lane version").split())
    assert "satisfies Joe's correction" in lane_run
    assert "checker raises" not in lane_run
    assert "raises the defect" in section(text, "### Checker run: scores a checker version")
    assert "never added together" in section(text, "### Scores")


def test_prediction_items_match_by_identity_never_by_subject():
    text = (SKILLS / "prediction-ledger" / "SKILL.md").read_text(encoding="utf-8")
    predict = section(text, "## 1. Predict: one row per new item")
    assert "never by subject" in predict and "conversation ID" in predict
    assert "same identity" in predict and "or subject" not in predict


def test_parked_prediction_rows_are_never_asked_again():
    text = (SKILLS / "prediction-ledger" / "SKILL.md").read_text(encoding="utf-8")
    ask = section(text, "## 3. Ask only when blind")
    assert "A Parked row is never asked again." in ask
    assert "asked again only if" not in ask and "7 days later" not in ask
    assert "Parked row" in section(text, "## 5. Calibrate: weekly, Sunday, before the weekly-evolve lane")


def test_every_knowledge_review_verdict_has_a_chair_status():
    review = (AGENTS / "knowledge-review.md").read_text(encoding="utf-8")
    mission = section((AGENTS / "knowledge-chair.md").read_text(encoding="utf-8"), "## 1. Mission")
    for verdict, status in [("supported", "Confirmed"), ("contradicted", "Contradicted"),
                            ("stale", "Stale"), ("duplicate", "Duplicate")]:
        assert verdict in review and status in mission, f"no chair status for verdict {verdict}"


def test_indexes_list_every_card_and_skill():
    agents_index = (AGENTS / "_INDEX.md").read_text(encoding="utf-8")
    for path in [*cards(), AGENTS / "CARD_TEMPLATE.md", AGENTS / "INPUTS.md"]:
        assert f"| agents/{path.name} |" in agents_index
    skills_index = (SKILLS / "_INDEX.md").read_text(encoding="utf-8")
    for skill in skill_files():
        assert f"| skills/{skill.parent.name}/ |" in skills_index


@pytest.mark.parametrize("routine", routines(), ids=lambda p: p.stem)
def test_routine_header_and_paste_ready_prompt(routine):
    text = routine.read_text(encoding="utf-8")
    assert text.startswith(f"# Routine: {routine.stem}\n")
    for field in ROUTINE_FIELDS:
        assert re.search(rf"^- {field}: \S", text, re.M), f"header line {field} missing"
    block = re.search(r"^```text\n(.*?)^```$", text, re.M | re.S)
    assert block, "the prompt must sit in one ```text block"
    lines = block.group(1).splitlines()
    assert lines[0] == "BEGIN" and lines[-1] == "END"
    prompt = block.group(1)
    assert "kernel" in prompt and "[[LANES]]" in prompt, "load the kernel and write a heartbeat"
    assert "never" in prompt.lower()


def test_routines_index_lists_every_routine():
    index = (ROUTINES / "_INDEX.md").read_text(encoding="utf-8")
    for routine in routines():
        assert f"| routines/{routine.name} |" in index


def test_pull_request_template_has_the_review_checklist():
    text = PR_TEMPLATE.read_text(encoding="utf-8")
    for item in CHECKLIST:
        assert f"- [ ] **{item}.**" in text


# The anonymous Review-2 works from the reviewer prompt and the Reviewer view
# only: the council-board card names the drafting model, so it never loads it.
ANONYMOUS_REVIEWERS = {"council-board-review-2"}


def routine_prompt(text):
    return re.search(r"^```text\n(.*?)^```$", text, re.M | re.S).group(1)


def header_line(text, field):
    return re.search(rf"^- {field}: (.*)$", text, re.M).group(1)


@pytest.mark.parametrize("routine", routines(), ids=lambda p: p.stem)
def test_routine_prompt_loads_the_cards_in_its_header(routine):
    text = routine.read_text(encoding="utf-8")
    cards = re.findall(r"agents/[\w.-]+\.md", header_line(text, "Card"))
    assert cards, "the Card line names no card file"
    if routine.stem not in ANONYMOUS_REVIEWERS:
        prompt = routine_prompt(text)
        for card in cards:
            assert card in prompt, f"the prompt never reads {card}"


@pytest.mark.parametrize("routine", routines(), ids=lambda p: p.stem)
def test_routine_has_a_schedule_so_a_waiting_run_is_picked_up(routine):
    assert "cron `" in header_line(routine.read_text(encoding="utf-8"), "Trigger")


@pytest.mark.parametrize("routine", routines(), ids=lambda p: p.stem)
def test_routine_prompt_steps_are_numbered_in_order(routine):
    steps = re.findall(r"^(\d+)\. ", routine_prompt(routine.read_text(encoding="utf-8")), re.M)
    assert [int(n) for n in steps] == list(range(1, len(steps) + 1))


def test_council_chair_finalizes_reviewed_2_rows_only_with_both_reviews():
    prompt = routine_prompt((ROUTINES / "council-board-chair.md").read_text(encoding="utf-8"))
    queue = next(line for line in prompt.splitlines() if line.startswith("3. Queue:"))
    assert "Status Reviewed-2 and both Review-1 and Review-2 written" in queue
