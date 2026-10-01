"""Format checks for the agent cards (agents/) and skills (skills/).

They keep every card on the six-part template, every skill in the Agent Skills
format, every source key defined, and keep private identifiers out of this
public repository.
"""
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
AGENTS = ROOT / "agents"
SKILLS = ROOT / "skills"

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

KEY_USE = re.compile(r"\[\[([A-Z0-9_]+)\]\]")
PLACEHOLDER_KEY = "KEY"  # the template and the skills explain the syntax as [[KEY]]
KEY_DEF = re.compile(r"^\| `([A-Z0-9_]+)` \|", re.M)
LINK = re.compile(r"\]\(([^)\s]+)\)")
SKILL_NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
# Patterns that would publish private PCOS identifiers: Drive-style IDs (a long
# run of letters and digits with both cases and a digit), Notion IDs, UUIDs,
# e-mail addresses and links to Drive, Docs or Notion objects.
PRIVATE = {
    "Drive-style ID": re.compile(
        r"(?<![A-Za-z0-9])(?=[A-Za-z0-9]*[a-z])(?=[A-Za-z0-9]*[A-Z])(?=[A-Za-z0-9]*\d)"
        r"[A-Za-z0-9]{12,}(?![A-Za-z0-9])"),
    "Notion ID": re.compile(r"(?<![0-9a-f])[0-9a-f]{32}(?![0-9a-f])"),
    "UUID": re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"),
    "e-mail address": re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)+"),
    "Drive or Notion link": re.compile(r"(docs|drive)\.google\.com|notion\.(so|site|com)"),
}


def cards():
    return sorted(p for p in AGENTS.glob("*.md") if p.name not in NOT_CARDS)


def skill_files():
    return sorted(SKILLS.glob("*/SKILL.md"))


def public_files():
    return sorted(p for folder in (AGENTS, SKILLS) for p in folder.rglob("*.md"))


def defined_keys():
    return KEY_DEF.findall((AGENTS / "INPUTS.md").read_text(encoding="utf-8"))


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
    for what, pattern in PRIVATE.items():
        found = pattern.search(text)
        assert not found, f"{what} in {path.relative_to(ROOT)}: {found.group()}"


def test_indexes_list_every_card_and_skill():
    agents_index = (AGENTS / "_INDEX.md").read_text(encoding="utf-8")
    for path in [*cards(), AGENTS / "CARD_TEMPLATE.md", AGENTS / "INPUTS.md"]:
        assert f"| agents/{path.name} |" in agents_index
    skills_index = (SKILLS / "_INDEX.md").read_text(encoding="utf-8")
    for skill in skill_files():
        assert f"| skills/{skill.parent.name}/ |" in skills_index
