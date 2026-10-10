"""Checks for queue item QX35: the temporary Claude usage diet."""
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ROUTINES = ROOT / "routines"
AGENTS = ROOT / "agents"
ONE_CLOCK = "America/Mexico_City"

PAUSED = {
    "L3-health": "cron `30 7 * * *`",
    "prediction-ledger": "cron `45 7 * * 1-5`",
    "ledger-backtest": "cron `0 7 * * 0`",
    "council-board-draft": "cron `0 8 * * *`",
    "council-board-review-2": "cron `30 9 * * *`",
    "council-board-chair": "cron `0 10 * * *`",
    "council-github-chair": "cron `0 */2 * * *`",
}

NOT_INSTALLED = {"intake-email", "knowledge-extract", "knowledge-review-2"}


def read(path):
    return path.read_text(encoding="utf-8")


def field(name, key):
    text = read(ROUTINES / f"{name}.md")
    return re.search(rf"^- {re.escape(key)}: (.*)$", text, re.M).group(1)


def cron(name):
    trigger = field(name, "Trigger")
    return re.search(r"cron `([^`]+)`", trigger).group(1)


def test_kept_lane_schedules_are_exact():
    assert cron("L1-brief") == "30 6 * * 1-5"
    assert cron("exo") == "0 7 * * *"
    assert cron("retro") == "53 18 * * *"
    assert cron("commitments") == "40 12 * * 1-5"
    for name in ("L1-brief", "exo", "retro", "commitments"):
        assert f"CRON_TZ={ONE_CLOCK}" in field(name, "Trigger")
        assert "usage diet" in field(name, "Status")


def test_commitments_backfill_is_manual_only():
    trigger = field("commitments-backfill", "Trigger")
    assert "once by hand" in trigger
    assert "cron `" not in trigger
    assert "One-time manual run only" in field("commitments-backfill", "Status")


def test_paused_routines_have_no_trigger_and_keep_the_restore_schedule():
    for name, old_cron in PAUSED.items():
        assert field(name, "Status") == "Paused 2026-10-10 (usage diet)"
        assert field(name, "Trigger") == "none while paused"
        restore = field(name, "Restore")
        assert old_cron in restore
        assert f"CRON_TZ={ONE_CLOCK}" in restore


def test_uninstalled_lanes_stay_off_with_restore_lines():
    for name in NOT_INSTALLED:
        assert field(name, "Status") == "Not installed; stay off 2026-10-10 (usage diet)"
        assert field(name, "Trigger").startswith("none;")
        assert "cron `" in field(name, "Restore")
        assert f"CRON_TZ={ONE_CLOCK}" in field(name, "Restore")


def test_non_repo_lanes_are_recorded_in_the_index():
    index = read(ROUTINES / "_INDEX.md")
    cal = next(line for line in index.splitlines() if line.startswith("| L5 CAL |"))
    hub = next(line for line in index.splitlines() if line.startswith("| PCOS hub sync |"))
    recorder = next(line for line in index.splitlines()
                    if line.startswith("| Drive recorder (Claude side) |"))
    assert "paused 2026-10-10" in cal and "Restore: daily 07:00" in cal
    assert "paused 2026-10-10" in hub and "Restore: daily 06:00" in hub
    assert "daily 20:10 only" in recorder


def test_cards_state_the_reduced_or_paused_lane_schedule():
    exo = read(AGENTS / "exo.md")
    commitments = read(AGENTS / "commitments.md")
    retro = read(AGENTS / "retro.md")
    assert "Trigger: 07:00, America/Mexico_City" in exo
    assert "13:00 run is off" in exo
    assert "Trigger: weekdays at 12:40 America/Mexico_City" in commitments
    assert "06:40 and 18:40 runs" in commitments
    assert "Routine fires at 18:53" in retro
    for name in ("council-board", "council-github", "prediction-ledger",
                 "ledger-backtest"):
        assert "paused 2026-10-10" in read(AGENTS / f"{name}.md").lower()


def test_active_l4_skips_prediction_calibration_while_prediction_is_paused():
    l4 = read(ROUTINES / "L4-weekly.md")
    assert "Calibration: paused 2026-10-10 (usage diet)" in l4
    assert "Do not read [[PREDICTION]]" in l4
    assert "follow that section" in l4 and "Restore:" in l4
    prediction = read(AGENTS / "prediction-ledger.md")
    assert "L4 explicitly skips" in prediction
    assert "does not read Prediction rows" in prediction
