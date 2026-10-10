"""Checks for the Retro lane (register P2-30) and the ledger backtest.

They pin what PCOS queue item QC19 fixed: the evening slot moves from EXO to the
retro lane; five questions a card, each with six tap options; the last 90 days
first; nothing asked before the whole thread is read; the EXO skip rule; answers
filed into the Prediction, People, golden-set and Decisions records; and a
backtest that is blind at the cut, capped at 200 threads and never asks Joe.
The general format checks in test_agents_skills.py cover these files too; the
format, key and privacy checks are repeated here for the new files by name.
"""
import re
from pathlib import Path

import pytest

from tests.test_agents_skills import PRIVATE, defined_keys, parse_frontmatter, section

ROOT = Path(__file__).resolve().parent.parent
RETRO_SKILL = ROOT / "skills" / "retro" / "SKILL.md"
RETRO_CARD = ROOT / "agents" / "retro.md"
BACKTEST = ROOT / "skills" / "prediction-ledger" / "references" / "backtest.md"
BACKTEST_CARD = ROOT / "agents" / "ledger-backtest.md"
LEDGER_SKILL = ROOT / "skills" / "prediction-ledger" / "SKILL.md"
EXO_SKILL = ROOT / "skills" / "exo" / "SKILL.md"
EXO_CARD = ROOT / "agents" / "exo.md"
ROUTINES = ROOT / "routines"
NEW_FILES = [RETRO_SKILL, RETRO_CARD, BACKTEST, BACKTEST_CARD,
             ROUTINES / "retro.md", ROUTINES / "ledger-backtest.md"]

TAP_OPTIONS = ["closed as quoted", "closed differently", "dropped", "moved offline",
               "still open", "unrelated"]
# The inputs QC19 names for the skill, plus the records its gate and filing use.
RETRO_INPUTS = ["MAIL_MINING", "PREDICTION", "WORKLIST", "MAIL_SENT", "MAIL_INBOX",
                "MAIL_ROUTED", "PEOPLE", "GOLDEN_SET", "CHANGELOG", "DECISIONS",
                "CORRECTIONS"]
KEY_USE = re.compile(r"\[\[([A-Z0-9_]+)\]\]")


def read(path):
    return path.read_text(encoding="utf-8")


def flat(text):
    """Text with every run of whitespace as one space, so line wrapping never matters."""
    return " ".join(text.split())


def cron(name):
    """(minute, hour, day of week, time zone) of a Routine's trigger or restore line."""
    text = read(ROUTINES / f"{name}.md")
    trigger = re.search(r"^- Trigger: (.*)$", text, re.M).group(1)
    if "cron `" not in trigger:
        trigger = re.search(r"^- Restore: (.*)$", text, re.M).group(1)
    minute, hour, _, _, weekday = re.search(r"cron `([^`]+)`", trigger).group(1).split()
    zone = re.search(r"CRON_TZ=([\w/]+)", trigger)
    return minute, hour, weekday, zone.group(1) if zone else "UTC"


def test_retro_skill_frontmatter():
    fields, body = parse_frontmatter(read(RETRO_SKILL))
    assert fields["name"] == "retro"
    assert fields["metadata"]["register"] == "P2-30"
    assert fields["metadata"]["card"] == "agents/retro.md"
    assert "last 90 days" in fields["description"]
    assert body.startswith("\n# Retro\n")


@pytest.mark.parametrize("path", NEW_FILES, ids=lambda p: str(p.relative_to(ROOT)))
def test_new_files_use_only_defined_keys_and_hold_no_private_identifiers(path):
    text = read(path)
    assert set(KEY_USE.findall(text)) - {"KEY"} <= set(defined_keys())
    for what, find in PRIVATE.items():
        assert not find(text), f"{what} in {path.relative_to(ROOT)}"


def test_retro_skill_names_its_inputs_by_key():
    used = set(KEY_USE.findall(read(RETRO_SKILL)))
    assert set(RETRO_INPUTS) <= used


def test_retro_card_is_five_questions_with_six_tap_options_in_order():
    card = flat(section(read(RETRO_SKILL), "## 5. Build the card"))
    assert "Five items, never more" in card
    positions = [card.find(option) for option in TAP_OPTIONS]
    assert -1 not in positions and positions == sorted(positions)
    assert "Free text or a voice note" in card
    contract = flat(section(read(RETRO_CARD), "## 5. Output contract with evidence labels"))
    positions = [contract.find(option) for option in TAP_OPTIONS]
    assert -1 not in positions and positions == sorted(positions)
    # six options, never seven: the CAL template's own option is the sixth
    assert "lists the first five" in card and "never added a second time" in card
    assert '"Not needed / wrong direction"' in contract and "never added twice" in contract


def test_gaps_come_from_the_last_90_days_first():
    gaps = flat(section(read(RETRO_SKILL), "## 2. Find the gaps"))
    assert "the last 90 days" in gaps
    assert "step back 90 days at a time" in gaps
    order = section(read(RETRO_SKILL), "## 3. Order")
    keys = ["Recency", "Open value", "Pattern class"]
    assert [order.find(k) for k in keys] == sorted(order.find(k) for k in keys)


def test_nothing_is_asked_before_the_whole_thread_and_later_replies_are_read():
    gate = flat(section(read(RETRO_SKILL), "## 4. Gate before any question"))
    assert "never ask what the record already answers" in gate
    assert "full thread chain" in gate and "every later reply" in gate
    assert "do not ask" in gate


def test_skip_rule_is_the_exo_rule():
    exo = flat(section(read(EXO_SKILL), "## 4. Skip rule"))
    retro = flat(section(read(RETRO_SKILL), "## 7. Skip rule (as EXO)"))
    for rule in ("2 skips: reshape", "3 skips: park and ask once"):
        assert rule in exo and rule in retro
    assert "Nothing closes on silence" in retro


def test_answers_are_filed_without_touching_the_mail():
    filing = flat(section(read(RETRO_SKILL), "## 6. File the answers"))
    for key in ("PREDICTION", "PEOPLE", "CORRECTIONS", "GOLDEN_SET", "DECISIONS"):
        assert f"[[{key}]]" in filing
    assert "create one if none" in filing
    assert "Never overwrite, move, delete or answer the mail" in filing
    # golden-set candidates go through weekly-evolve, never straight into the set
    assert "never writes the golden set directly" in filing


def test_the_evening_slot_moved_from_exo_to_retro():
    assert cron("retro") == ("53", "18", "*", "America/Mexico_City")
    minute, hour, weekday, zone = cron("exo")
    assert (hour, weekday, zone) == ("7", "*", "America/Mexico_City")
    for path in (EXO_CARD, EXO_SKILL):
        assert "07:00, 13:00 and 19:00" not in read(path)


def test_what_happened_questions_ride_on_the_evening_card():
    ask = flat(section(read(LEDGER_SKILL), "## 3. Ask only when blind"))
    assert "evening card of the retro lane" in ask and "EXO card" not in ask
    exo_prompt = read(ROUTINES / "exo.md")
    assert "counted inside the 4 items" not in exo_prompt
    assert "evening card of the retro lane" in flat(read(ROUTINES / "prediction-ledger.md"))


def test_backtest_is_blind_capped_and_never_asks_joe():
    text = flat(read(BACKTEST))
    assert "Stop at 200 threads per run" in text
    assert "the last 90 days" in text
    assert "only the messages up to and" in text
    assert "Ask Joe anything" in section(read(BACKTEST), "## Never")
    # class rows are measurements: they never enter the live mean
    assert "never enter the live mean" in text
    calibrate = section(read(LEDGER_SKILL), "## 5. Calibrate: weekly, Sunday, before the weekly-evolve lane")
    assert "never average" in flat(calibrate)


def test_backtest_runs_on_sunday_before_l4():
    minute, hour, weekday, zone = cron("ledger-backtest")
    l4_minute, l4_hour, l4_weekday, l4_zone = cron("L4-weekly")
    assert weekday == l4_weekday == "0" and zone == l4_zone == "America/Mexico_City"
    assert int(hour) < int(l4_hour)


def test_a_class_item_files_and_counts_every_identity():
    skill = read(RETRO_SKILL)
    assert "every identity it covers" in flat(section(skill, "## 5. Build the card"))
    filing = flat(section(skill, "## 6. File the answers"))
    assert "Prediction rows, one per identity" in filing and "For every identity" in filing
    skips = flat(section(skill, "## 7. Skip rule (as EXO)"))
    assert "counted per identity" in skips and "for each identity" in skips


def test_a_row_without_a_prediction_is_settled_without_a_score():
    score = flat(section(read(LEDGER_SKILL), "## 4. Score"))
    assert "has no check to score" in score and "leave Score empty" in score
    filing = flat(section(read(RETRO_SKILL), "## 6. File the answers"))
    assert "without a Score" in filing


def test_backtest_rebuilds_the_owner_map_at_the_cut():
    method = flat(section(read(BACKTEST), "## 2. Predict blind"))
    assert "the owner map as it stood at the cut" in method
    assert "undo every change dated after the cut" in method
    assert "skip the thread" in method
    assert "leave the Owner check out" not in method


def test_prior_questions_and_rows_match_by_identity_never_by_subject():
    gaps = flat(section(read(RETRO_SKILL), "## 2. Find the gaps"))
    assert "Match by identity (the conversation ID or Task ID), never by subject" in gaps
    assert "identity is already in the Source of a [[PREDICTION]] row" in gaps
    gate = flat(section(read(RETRO_SKILL), "## 4. Gate before any question"))
    assert "concerns the same ask" in gate
    # a gate catch is filed like an answer, so the ledger can match it later
    assert "Source = the identity" in gate


def test_filing_never_invents_a_channel_and_always_sets_a_status():
    filing = flat(section(read(RETRO_SKILL), "## 6. File the answers"))
    assert "the channel Joe tapped" not in filing and "never a guessed channel" in filing
    free_text = filing[filing.index("free text or voice only"):filing.index("3. People.")]
    assert "Status Parked" in free_text


def test_backtest_checker_sample_fits_the_run():
    for path in (BACKTEST, BACKTEST_CARD, ROUTINES / "ledger-backtest.md"):
        assert "min(10, threads scored" in flat(read(path))


def test_no_subject_based_veto_remains():
    never = flat(section(read(RETRO_SKILL), "## Never"))
    assert "a subject that has a [[PREDICTION]] row" not in never
    assert "identity is in the Source of a [[PREDICTION]] row" in never
    checklist = flat(section(read(ROOT / "skills" / "checker" / "references" / "checklists.md"),
                             "## question-card"))
    assert "the subject has no [[PREDICTION]] row" not in checklist
    assert "never by subject" in checklist


def test_the_last_chance_item_is_shown_before_any_row_parks_it():
    skips = flat(section(read(RETRO_SKILL), "## 7. Skip rule (as EXO)"))
    assert skips.index("Keep this open, or let it go?") < skips.index("Status Parked")
    assert "before any row is written" in skips


def test_backtest_undoes_owner_changes_newest_first():
    method = flat(section(read(BACKTEST), "## 2. Predict blind"))
    assert "undo every change dated after the cut, newest first" in method


def test_a_thread_and_its_worklist_row_are_one_gap():
    gaps = flat(section(read(RETRO_SKILL), "## 2. Find the gaps"))
    assert "are one gap with both identities" in gaps
    assert "excluded when either identity is" in gaps


def test_worklist_only_gaps_have_their_own_wording_and_outcome():
    card = flat(section(read(RETRO_SKILL), "## 5. Build the card"))
    assert "A gap with no thread (a Worklist row alone) sums up the row instead" in card
    filing = flat(section(read(RETRO_SKILL), "## 6. File the answers"))
    assert "done as the row's Next Action planned" in filing


def test_reshaped_exo_steps_keep_a_row_out_of_retro():
    gaps = flat(section(read(RETRO_SKILL), "## 2. Find the gaps"))
    assert "no Queued, Shown or Reshaped step" in gaps


def test_the_checker_checks_every_identity_of_a_gap():
    checklist = flat(section(read(ROOT / "skills" / "checker" / "references" / "checklists.md"),
                             "## question-card"))
    assert "any identity the gap carries" in checklist


def test_settled_worklist_gaps_reach_the_closeout_owner():
    filing = flat(section(read(RETRO_SKILL), "## 6. File the answers"))
    assert "When a Worklist row covers the gap and the answer settles it" in filing
    assert "never changes a Worklist row itself" in filing


def test_the_checker_accepts_a_gap_with_no_thread():
    checklist = flat(section(read(ROOT / "skills" / "checker" / "references" / "checklists.md"),
                             "## question-card"))
    assert "for a gap with no thread, the Worklist row" in checklist
    assert "for a Worklist row alone, the row and the sources it names were read" in checklist


def test_gap_level_records_are_filed_once_and_handoffs_cover_every_settlement():
    skill = read(RETRO_SKILL)
    gate = flat(section(skill, "## 4. Gate before any question"))
    assert "When a Worklist row covers the gap, also file one [[INBOX]] row" in gate
    filing = flat(section(skill, "## 6. File the answers"))
    assert "filed once per gap, never once per identity" in filing
    skips = flat(section(skill, "## 7. Skip rule (as EXO)"))
    assert "An explicit keep is also filed as \"still open\" is" in skips


def test_closed_worklist_statuses_are_never_retro_gaps():
    from pcos_tools.common import CLOSED_STATUSES
    gaps = flat(section(read(RETRO_SKILL), "## 2. Find the gaps"))
    waiting = gaps[gaps.index("Rows of [[WORKLIST]]"):gaps.index("identified by Task ID")]
    for status in CLOSED_STATUSES:
        assert status not in waiting
    closure = gaps[gaps.index("no closure evidence"):gaps.index("[[MAIL_MINING]] sharpens")]
    for status in CLOSED_STATUSES:
        assert status in closure
    assert "no Done on its Worklist row" not in closure


def test_ledger_answers_that_settle_a_worklist_task_reach_the_closeout_owner():
    ask = flat(section(read(LEDGER_SKILL), "## 3. Ask only when blind"))
    handled = ask[ask.index("- A: Actual"):ask.index("- B: Status Parked")]
    assert "if the subject is a Worklist task, file one [[INBOX]] row" in handled
    assert "Scored or Parked" in handled
    assert "The subject is a Worklist task when the row names a Task ID" in ask
    # an item reached through an Inbox row or DELTA line has that row as Source
    assert "in the Inbox row or DELTA line its Source points to" in ask
    filing = flat(section(read(RETRO_SKILL), "## 6. File the answers"))
    assert "every answer that settles it (handled offline or dropped)" in filing
    assert "this lane files no second one" in filing
    checklist = flat(section(read(ROOT / "skills" / "checker" / "references" / "checklists.md"),
                             "## prediction"))
    assert "settles a Worklist task (handled offline or dropped" in checklist


def test_the_backtest_sample_is_checked_by_its_own_scoring_rule():
    checklists = read(ROOT / "skills" / "checker" / "references" / "checklists.md")
    backtest = flat(section(checklists, "## prediction-backtest"))
    assert "not the live rule of skill section 4" in backtest
    assert "Candidate output 1 when the output type matches what happened" in backtest
    assert "only the assumptions the outcome settles are scored" in backtest
    for path in (BACKTEST, ROUTINES / "ledger-backtest.md"):
        text = flat(read(path))
        assert "job type prediction-backtest" in text
        assert "job type prediction)" not in text
    assert "prediction-backtest checklist" in flat(read(BACKTEST_CARD))

