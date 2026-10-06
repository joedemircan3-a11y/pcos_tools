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
# Every run of that alphabet with both cases and a digit counts as an ID, however
# word-like its pieces look, unless it is one of these public folder and file
# names. A name joins this list only on purpose, in a reviewed change.
PUBLIC_NAMES = {
    "KL_00_PCOS_System_and_AI", "KL_01_Stone_and_Materials", "KL_02_Mosaic_and_Waterjet_Production",
    "KL_03_Pricing", "KL_04_Vendors_and_Terms", "KL_05_Logistics_and_Customs_MX_US_TR",
    "KL_06_Sales_and_CS", "KL_07_Company_and_People", "PCOS_DISPATCH_2026-09-29b",
}
ID_RUN = re.compile(r"(?<![A-Za-z0-9_-])[A-Za-z0-9_-]{12,}(?![A-Za-z0-9_-])")


def find_drive_id(text):
    """Return the first Drive-style ID in text, or None."""
    for match in ID_RUN.finditer(text):
        run = match.group()
        if run not in PUBLIC_NAMES and all(re.search(c, run) for c in ("[a-z]", "[A-Z]", r"\d")):
            return run
    return None


def first_match(pattern):
    """A finder that returns the first match of pattern as text, or None."""
    return lambda text: (found := pattern.search(text)) and found.group()


# Finders for what would publish private PCOS identifiers: Drive-style IDs,
# Notion IDs, UUIDs, e-mail addresses and links to Drive, Docs or Notion objects.
PRIVATE = {
    "Drive-style ID": find_drive_id,
    "Notion ID": first_match(re.compile(r"(?<![0-9a-fA-F])[0-9a-fA-F]{32}(?![0-9a-fA-F])")),
    "UUID": first_match(re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
                                   r"[0-9a-fA-F]{12}")),
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
    "Abc_123D_Def_456E_Ghi_789J_Klm", "Abc_Def_v4_Ghi_Jkl", "KL_02_Mosaic_and_Waterjet_Productio",
])
def test_drive_id_detector_catches_ids_with_url_safe_separators(text):
    assert find_drive_id(text)


@pytest.mark.parametrize("text", [
    *sorted(PUBLIC_NAMES), "PCOS_BUILD_KIT_2026-09-28", "PCOS_AGENT_INPUT_IDS",
    "council-board-review-2", "KL_VENDORS_RAW__INDEX", "[[KL_DOMAINS]]",
])
def test_drive_id_detector_passes_public_names_and_names_without_mixed_case(text):
    assert find_drive_id(text) is None


def test_every_public_name_is_still_used():
    text = "\n".join(p.read_text(encoding="utf-8") for p in public_files())
    assert not {name for name in PUBLIC_NAMES if name not in text}, "drop unused names from PUBLIC_NAMES"


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
    checker_run = " ".join(section(text, "### Checker run: scores a checker version").split())
    assert "raises the defect" in checker_run
    assert "known-good outputs" in checker_run and "passes when the checker gives Accept" in checker_run
    assert "clean half drops fails" in " ".join(section(text, "### Scores").split())
    assert "never added together" in section(text, "### Scores")


def test_prediction_items_match_by_identity_never_by_subject():
    text = (SKILLS / "prediction-ledger" / "SKILL.md").read_text(encoding="utf-8")
    predict = section(text, "## 1. Predict: one row per new item")
    assert "never by subject" in predict and "conversation ID" in predict
    assert "same identity" in predict and "or subject" not in predict


def test_prediction_evidence_matches_the_source_identity():
    skill = (SKILLS / "prediction-ledger" / "SKILL.md").read_text(encoding="utf-8")
    check = " ".join(section(skill, "## 2. Check: rows whose Check date has passed").split())
    card = " ".join((AGENTS / "prediction-ledger.md").read_text(encoding="utf-8").split())
    for text in (check, card):
        assert "thread or subject" not in text and "about the subject" not in text
    assert "Source identity" in check and "unique" in check
    assert "conclusive only while it is still the terminal message" in check
    assert "only nonconclusive evidence" in check and "is set Parked" in check
    assert "counts only while it is terminal" in card


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


def test_brief_keeps_new_messages_in_known_threads():
    prompt = routine_prompt((ROUTINES / "L1-brief.md").read_text(encoding="utf-8"))
    assert "same conversation ID and the same terminal message" in prompt
    assert "Skip items that already have a row with the same conversation ID." not in prompt


def test_brief_backlog_beyond_five_days_is_never_skipped():
    prompt = " ".join(routine_prompt((ROUTINES / "L1-brief.md").read_text(encoding="utf-8")).split())
    assert "at most 5 days." not in prompt and "from the end of the last L1 heartbeat" not in prompt
    assert "window end in the last L1 heartbeat" in prompt
    assert "read the oldest 5 days only and record their end as this run's window end" in prompt
    assert 'the result starts with "window end"' in prompt


def test_render_keeps_every_open_needs_joe_row_on_today():
    prompt = " ".join(routine_prompt((ROUTINES / "L2-render.md").read_text(encoding="utf-8")).split())
    assert "[[INBOX]] (rows since the last render)" not in prompt
    assert "every row whose Status is still Needs Joe, however old" in prompt


def test_github_chair_trusts_only_its_own_final_and_reviews_of_the_current_head():
    prompt = routine_prompt((ROUTINES / "council-github-chair.md").read_text(encoding="utf-8"))
    steps = {line.split(". ", 1)[0]: line for line in prompt.splitlines() if re.match(r"\d+\. ", line)}
    assert "posted by the chair's account" in steps["1"] and "from any other account is ignored" in steps["1"]
    assert "Codex review whose commit is the head" in steps["5"]
    assert "A review of an earlier commit does not count" in steps["5"]
    assert "head reached the pull request less than 2 hours ago" in steps["5"]
    assert "opened less than 2 hours ago" not in steps["5"]
    assert steps["10"].startswith("10. Re-read the pull request's head.")
    assert "write nothing and skip" in steps["10"]
    replay = steps["4"]
    assert replay.index("add any that is missing") < replay.index('post that Final')


def test_github_chair_never_chairs_without_a_review():
    prompt = routine_prompt((ROUTINES / "council-github-chair.md").read_text(encoding="utf-8"))
    fallback = next(line for line in prompt.splitlines() if line.startswith("5. "))
    assert "If exactly one is still missing" in fallback and "If both are missing" in fallback
    assert "never chair" in fallback and "skip" in fallback
    assert "scheduled run goes on to the next pull request" in prompt
    assert 'no "Chair: Final" comment' in prompt


@pytest.mark.parametrize("routine", routines(), ids=lambda p: p.stem)
def test_routine_that_names_the_checker_runs_it(routine):
    text = routine.read_text(encoding="utf-8")
    if "skills/checker/SKILL.md" in header_line(text, "Skills"):
        assert "skills/checker/SKILL.md" in routine_prompt(text), "the header names the checker, but the prompt never loads it"


def test_council_final_checklist_accepts_the_one_review_fallback():
    text = (SKILLS / "checker" / "references" / "checklists.md").read_text(encoding="utf-8")
    council_final = " ".join(section(text, "## council-final").split())
    assert 'Dissent says "Review-N missing"' in council_final


def test_claim_extraction_and_claude_review_use_different_models():
    extract = section((AGENTS / "knowledge-extract.md").read_text(encoding="utf-8"),
                      "## 6. Trigger and owner model")
    review = section((AGENTS / "knowledge-review.md").read_text(encoding="utf-8"),
                     "## 6. Trigger and owner model")
    extract_model = re.search(r"- Model: Claude (\w+)", extract).group(1)
    review_2_model = re.search(r"Review-2 Claude (\w+)", review).group(1)
    assert extract_model != review_2_model


def test_council_chair_writes_only_after_a_checker_accept():
    prompt = routine_prompt((ROUTINES / "council-board-chair.md").read_text(encoding="utf-8"))
    check = next(line for line in prompt.splitlines() if line.startswith("5. Run the checker"))
    assert "only after an Accept" in check and "keeps its Status" in check
    assert "Needs Joe stays reserved" in check


def test_github_chair_checks_the_final_before_posting():
    prompt = routine_prompt((ROUTINES / "council-github-chair.md").read_text(encoding="utf-8"))
    check = next(line for line in prompt.splitlines() if "job type council-final" in line)
    assert "only after an Accept" in check and "post nothing" in check


def test_health_stale_kernel_check_is_scoped_to_the_last_day():
    prompt = routine_prompt((ROUTINES / "L3-health.md").read_text(encoding="utf-8"))
    stale = next(line for line in prompt.splitlines() if "Stale kernel:" in line)
    assert "last 24 hours" in stale


def test_extract_and_review_2_routines_run_different_models():
    def model(name):
        line = header_line((ROUTINES / name).read_text(encoding="utf-8"), "Model")
        return re.match(r"Claude (\w+)", line).group(1)
    assert model("knowledge-extract.md") != model("knowledge-review-2.md")


def test_extracted_claims_keep_the_evidence_label_apart_from_status():
    contract = " ".join(section((AGENTS / "knowledge-extract.md").read_text(encoding="utf-8"),
                                "## 5. Output contract with evidence labels").split())
    assert "every extracted claim is Candidate" not in contract
    assert "separate from Status" in contract and "labeled Confirmed" in contract


def test_blind_row_blocked_by_another_rows_subject_is_parked():
    ask = " ".join(section((SKILLS / "prediction-ledger" / "SKILL.md").read_text(encoding="utf-8"),
                           "## 3. Ask only when blind").split())
    assert "through another row" in ask and "It is set Parked" in ask


def test_intake_stop_list_asks_stay_needs_joe():
    gate = " ".join(section((SKILLS / "intake-email" / "SKILL.md").read_text(encoding="utf-8"),
                            "## 6. Send gate").split())
    assert "Needs Joe when the sender is not on the allowlist" in gate
    assert "a stop-list ask" in gate and "only when condition 1 alone failed" in gate


def test_prediction_checklist_reads_the_conversation_and_takes_the_terminal_message():
    text = (SKILLS / "checker" / "references" / "checklists.md").read_text(encoding="utf-8")
    prediction = " ".join(section(text, "## prediction").split())
    assert "lookup order" not in prediction
    assert "Joe's sent mail, thread replies" not in prediction
    assert "read together" in prediction and "terminal message" in prediction
    assert "counts only while no later reply follows it" in prediction


def test_handled_offline_answer_is_scored_only_when_every_guess_is_settled():
    ask = " ".join(section((SKILLS / "prediction-ledger" / "SKILL.md").read_text(encoding="utf-8"),
                           "## 3. Ask only when blind").split())
    answer_a = ask[ask.index('- A: Actual "handled offline"'):ask.index("- B:")]
    assert "Status Scored" not in answer_a
    assert "Owner, Route, Candidate output and every assumption" in answer_a
    assert "set Status Parked with Actual kept" in answer_a
    contract = " ".join(section((AGENTS / "prediction-ledger.md").read_text(encoding="utf-8"),
                                "## 5. Output contract with evidence labels").split())
    assert '"handled offline"' in contract and "never scored on part of its checks" in contract


def test_knowledge_checklist_accepts_inferred_claims_labeled_candidate():
    text = (SKILLS / "checker" / "references" / "checklists.md").read_text(encoding="utf-8")
    claim = " ".join(section(text, "## knowledge-claim").split())
    assert "and the source states the claim." not in claim
    assert "a claim that needs inference is labeled Candidate" in claim
    assert "an inferred claim labeled Confirmed" in claim
    extract = " ".join((AGENTS / "knowledge-extract.md").read_text(encoding="utf-8").split())
    assert "a claim that needs inference from the source is labeled Candidate" in extract


def test_github_council_row_is_bound_by_the_pull_request_link_not_the_title():
    card = " ".join((AGENTS / "council-github.md").read_text(encoding="utf-8").split())
    inputs = card[card.index("- L1:"):card.index("- L2:")]
    assert "matched by the Task title" not in inputs
    assert "Draft field holds the pull request's link" in inputs
    assert "never picked by its title" in inputs and "more than one, means Blocked" in inputs
    assert "writes the pull request's link into the Council row's Draft field" in card


def test_council_final_author_check_covers_the_github_council():
    text = (SKILLS / "checker" / "references" / "checklists.md").read_text(encoding="utf-8")
    council_final = " ".join(section(text, "## council-final").split())
    assert "6. The reviewers worked from the Reviewer view (Author hidden)." not in council_final
    assert "Board council: they worked from the Reviewer view" in council_final
    assert "GitHub council: the pull request names no author model" in council_final
    assert "No author model is named." in (AGENTS / "council-github.md").read_text(encoding="utf-8")


def test_pricing_result_carries_exactly_one_evidence_label():
    text = (SKILLS / "checker" / "references" / "checklists.md").read_text(encoding="utf-8")
    pricing = " ".join(section(text, "## pricing-prep").split())
    assert "labeled Candidate and Needs Joe Approval" not in pricing
    assert "exactly one evidence label, Needs Joe Approval" in pricing
    assert "never as a second label" in pricing
    assert "exactly one label" in (AGENTS / "CARD_TEMPLATE.md").read_text(encoding="utf-8")


def test_delta_checklist_reopens_the_cited_sources():
    text = (SKILLS / "checker" / "references" / "checklists.md").read_text(encoding="utf-8")
    delta = " ".join(section(text, "## delta").split())
    assert "Required: the sources each line cites" in delta
    assert "reopened in this run" in delta and "what changed is what the source shows" in delta
    assert "that no source shows, fails" in delta


@pytest.mark.parametrize("text", [
    "ABCDEF1234567890ABCDEF1234567890", "abcdef1234567890abcdef1234567890",
    "ABCDEF12-3456-7890-ABCD-EF1234567890", "abcdef12-3456-7890-abcd-ef1234567890",
])
def test_privacy_guard_catches_hex_ids_in_either_case(text):
    assert any(find(text) for find in PRIVATE.values())


def test_github_chair_feeds_the_pr_reviews_to_the_checker_and_writes_the_row_first():
    prompt = routine_prompt((ROUTINES / "council-github-chair.md").read_text(encoding="utf-8"))
    check = next(line for line in prompt.splitlines() if "job type council-final" in line)
    assert "the reviews the pull request has" in check and "one-review fallback" in check
    assert prompt.index("Update the [[COUNCIL]] row") < prompt.index('"Chair: Final" with Final')
    assert "head commit on the Final's first line equals" in prompt


def test_github_chair_trusts_only_owner_pull_requests_bound_to_their_row():
    prompt = routine_prompt((ROUTINES / "council-github-chair.md").read_text(encoding="utf-8"))
    lines = prompt.splitlines()
    first = next(line for line in lines if line.startswith("1. "))
    assert "repository owner's account" in first and "not a fork" in first
    assert "[[" not in first, "the GitHub-only filter must not touch keyed objects"
    load = prompt.index("\nLOAD\n")
    assert all(prompt.index(key) > load for key in ("[[COUNCIL]]", "[[INBOX]]")), "load keys first"
    assert "Draft field" in next(line for line in lines if line.startswith("3. "))


def test_github_chair_finds_the_council_row_by_link_never_by_title():
    prompt = routine_prompt((ROUTINES / "council-github-chair.md").read_text(encoding="utf-8"))
    step_3 = next(line for line in prompt.splitlines() if line.startswith("3. "))
    assert 'row named after "Council row:"' not in step_3
    assert "search the Draft field for the pull request's link" in step_3
    assert "Never pick a row by its Task title" in step_3
    assert "exactly one row holds the link" in step_3 and "more than one bound row" in step_3
