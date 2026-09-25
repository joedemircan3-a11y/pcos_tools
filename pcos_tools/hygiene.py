"""Worklist hygiene: read-only checks producing proposed_changes.csv and hygiene_report.md."""
from __future__ import annotations

import csv
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from . import __version__
from .common import (
    AGED_STATUSES,
    CLOSED_STATUSES,
    DONE_CANDIDATE_STATUS,
    STALE_STATUS,
    TASK_ID_RE,
    WorklistError,
    get_vocab,
    md_table,
    next_free_task_id,
    parse_date,
    read_worklist,
    title_similarity,
    title_tokens,
)
from .pending import load_pending

CHECKS = {
    "STALE_ARCHIVE": "Stale-Triage row past the stale threshold; propose Archived-Auto",
    "DONE_PROMOTE": "Done-Candidate row unchanged past the done-candidate threshold; propose Done",
    "AGED_WAITING": "Waiting or Blocked row not updated within the aged threshold",
    "MALFORMED_ID": "Task ID does not match T-### or T-####",
    "DUPLICATE_ID": "Task ID used on more than one row",
    "INVALID_STATUS": "Status outside the vocabulary",
    "INVALID_PRIORITY": "Priority outside the vocabulary",
    "INVALID_ROOM": "Room outside the vocabulary",
    "BAD_DATE": "Updated is empty or not YYYY-MM-DD (age checks skipped for the row)",
    "DUPLICATE_TITLE": "Title duplicates or nearly duplicates an earlier row (skipped when both rows are closed)",
    "EMPTY_SOURCES": "Sources is empty",
    "EMPTY_CONFIDENCE": "Confidence is empty",
}
CHECK_ORDER = {check: index for index, check in enumerate(CHECKS)}
PROPOSED_COLUMNS = ["Task ID", "Title", "Check", "Field", "Current", "Proposed", "Action", "Reason", "Row"]
CHANGES_NAME = "proposed_changes.csv"
# Status proposals the weekly pass may apply on its own; a row named in an
# unapplied DELTA gets HOLD_ACTION instead of set-status.
AUTO_APPLY_CHECKS = ("STALE_ARCHIVE", "DONE_PROMOTE")
HOLD_ACTION = "hold"
REPORT_NAME = "hygiene_report.md"


@dataclass
class Finding:
    check: str
    task_id: str
    title: str
    field: str
    current: str
    proposed: str
    action: str
    reason: str
    row: int

    def as_record(self):
        return {
            "Task ID": self.task_id, "Title": self.title, "Check": self.check,
            "Field": self.field, "Current": self.current, "Proposed": self.proposed,
            "Action": self.action, "Reason": self.reason, "Row": self.row,
        }


@dataclass
class HygieneResult:
    findings: list
    next_id: str
    row_count: int
    today: date
    aged_days: int
    stale_days: int
    dup_threshold: float
    vocab_source: str = ""
    done_candidate_days: int = 7
    pending_files: tuple = ()

    def by_check(self):
        grouped = {check: [] for check in CHECKS}
        for finding in self.findings:
            grouped.setdefault(finding.check, []).append(finding)
        return grouped

    def task_ids(self, check):
        return [finding.task_id for finding in self.findings if finding.check == check]

    def held(self):
        return [finding for finding in self.findings if finding.action == HOLD_ACTION]


def run_hygiene(rows, today=None, aged_days=None, stale_days=None, dup_threshold=0.8,
                skip_closed=False, vocab=None, done_candidate_days=None, pending=None, pending_files=()):
    """Run every check over the rows. Pure: never touches the file system.

    ``aged_days``, ``stale_days`` and ``done_candidate_days`` default to the
    vocabulary's values; ``vocab`` defaults to the packaged vocab.json.
    ``pending`` maps Task ID -> DELTA file names (see pending.load_pending);
    STALE_ARCHIVE and DONE_PROMOTE proposals for those rows are put on hold.
    """
    vocab = vocab or get_vocab()
    today = today or date.today()
    if aged_days is None:
        aged_days = vocab.aged_days
    if stale_days is None:
        stale_days = vocab.stale_days
    if done_candidate_days is None:
        done_candidate_days = vocab.done_candidate_days
    findings = []
    seen_ids = {}

    def flag(row, check, field, current, proposed, action, reason):
        findings.append(Finding(check, row["Task ID"], row["Title"], field, current,
                                proposed, action, reason, row["_row"]))

    for row in rows:
        task_id = row["Task ID"]
        if not TASK_ID_RE.match(task_id):
            flag(row, "MALFORMED_ID", "Task ID", task_id, "", "fix-id",
                 "expected T- followed by 3 or 4 digits")
        elif task_id in seen_ids:
            flag(row, "DUPLICATE_ID", "Task ID", task_id, "", "review",
                 f"also used on row {seen_ids[task_id]}")
        else:
            seen_ids[task_id] = row["_row"]

        if row["Status"] not in vocab.status:
            flag(row, "INVALID_STATUS", "Status", row["Status"], "", "fix-value",
                 "allowed: " + ", ".join(vocab.status))
        if row["Priority"] not in vocab.priority:
            allowed = ", ".join(vocab.priority_order)
            if "" in vocab.priority:
                allowed += ", or blank"
            flag(row, "INVALID_PRIORITY", "Priority", row["Priority"], "", "fix-value", "allowed: " + allowed)
        if row["Room"] not in vocab.room:
            flag(row, "INVALID_ROOM", "Room", row["Room"], "", "fix-value",
                 "allowed: " + ", ".join(vocab.room))

        updated = parse_date(row["Updated"])
        age = None
        if updated is None:
            flag(row, "BAD_DATE", "Updated", row["Updated"], "", "fix-date",
                 "empty or not YYYY-MM-DD")
        else:
            age = (today - updated).days

        if row["Status"] in AGED_STATUSES and age is not None and age >= aged_days:
            waiting_on = row["Waiting On"] or "(Waiting On is empty)"
            flag(row, "AGED_WAITING", "Updated", row["Updated"], "", "chase-or-close",
                 f"{row['Status']} for {age} days (threshold {aged_days}); waiting on {waiting_on}")

        if not (skip_closed and row["Status"] in CLOSED_STATUSES):
            if not row["Sources"]:
                flag(row, "EMPTY_SOURCES", "Sources", "", "", "fill", "no source recorded")
            if not row["Confidence"]:
                flag(row, "EMPTY_CONFIDENCE", "Confidence", "", "", "fill", "no confidence recorded")

        if row["Status"] == STALE_STATUS and age is not None and age >= stale_days:
            flag(row, "STALE_ARCHIVE", "Status", STALE_STATUS, "Archived-Auto", "set-status",
                 f"{STALE_STATUS} for {age} days (threshold {stale_days})")

        if row["Status"] == DONE_CANDIDATE_STATUS and age is not None and age >= done_candidate_days:
            flag(row, "DONE_PROMOTE", "Status", DONE_CANDIDATE_STATUS, "Done", "set-status",
                 f"{DONE_CANDIDATE_STATUS} for {age} days with no change (threshold {done_candidate_days})")

    token_sets = [title_tokens(row["Title"]) for row in rows]
    for later in range(len(rows)):
        for earlier in range(later):
            other = rows[earlier]
            if rows[later]["Status"] in CLOSED_STATUSES and other["Status"] in CLOSED_STATUSES:
                continue  # two closed rows with the same title are history, not a duplicate
            score = title_similarity(token_sets[later], token_sets[earlier])
            if score >= dup_threshold:
                flag(rows[later], "DUPLICATE_TITLE", "Title", rows[later]["Title"], "",
                     "merge-or-rename",
                     f"overlap {score:.2f} with {other['Task ID']} '{other['Title']}' "
                     f"[{other['Status']}] on row {other['_row']}")

    for finding in findings:
        if finding.check in AUTO_APPLY_CHECKS and pending and finding.task_id in pending:
            finding.action = HOLD_ACTION
            finding.reason += (f"; HOLD: named in unapplied DELTA {', '.join(pending[finding.task_id])}; "
                               "apply that DELTA first, then re-run")

    findings.sort(key=lambda finding: (finding.row, CHECK_ORDER[finding.check]))
    return HygieneResult(findings, next_free_task_id(rows), len(rows), today,
                         aged_days, stale_days, dup_threshold, vocab.source, done_candidate_days,
                         tuple(pending_files))


def write_proposed_changes(result, path):
    path = Path(path)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=PROPOSED_COLUMNS)
        writer.writeheader()
        for finding in result.findings:
            writer.writerow(finding.as_record())
        writer.writerow({
            "Task ID": "", "Title": "", "Check": "NEXT_FREE_ID", "Field": "Task ID",
            "Current": "", "Proposed": result.next_id, "Action": "info",
            "Reason": "next unused Task ID (highest valid ID plus one)", "Row": "",
        })


def render_report(result, source_name):
    grouped = result.by_check()
    lines = [
        f"# Hygiene report - {source_name}",
        "",
        f"- Generated by pcos_tools hygiene v{__version__} on {date.today().isoformat()}; "
        f"ages computed against {result.today.isoformat()}",
        f"- Rows read: {result.row_count}",
        f"- Findings: {len(result.findings)}",
        f"- Next free Task ID: **{result.next_id}**",
        f"- Thresholds: aged >= {result.aged_days} days, stale >= {result.stale_days} days, "
        f"done-candidate >= {result.done_candidate_days} days, "
        f"duplicate title overlap >= {result.dup_threshold:.2f}",
        f"- Vocabulary: {result.vocab_source or 'packaged vocab.json'}",
        f"- Pending DELTAs read: {len(result.pending_files)}"
        + (f" ({', '.join(result.pending_files)}); proposals on hold: {len(result.held())}"
           if result.pending_files else " (nothing held)"),
        "",
        "> DRAFT ONLY. The input worklist was not modified. The weekly AI pass applies STALE_ARCHIVE "
        "and DONE_PROMOTE rows whose Action is set-status; rows with Action hold wait until the named "
        "DELTA is applied. A human reviews the rest of proposed_changes.csv.",
        "",
        "## Summary",
        "",
        md_table(["Check", "Count", "Meaning"],
                 [[check, len(grouped.get(check, [])), meaning] for check, meaning in CHECKS.items()]),
        "",
    ]
    for check, meaning in CHECKS.items():
        items = grouped.get(check, [])
        if not items:
            continue
        lines += [
            f"## {check} ({len(items)})",
            "",
            meaning + ".",
            "",
            md_table(["Task ID", "Title", "Field", "Current", "Proposed", "Action", "Reason", "Row"],
                     [[f.task_id, f.title, f.field, f.current, f.proposed, f.action, f.reason, f.row]
                      for f in items]),
            "",
        ]
    lines += [
        "## Next free Task ID",
        "",
        f"`{result.next_id}` (highest well-formed Task ID plus one; gaps are not reused).",
        "",
    ]
    return "\n".join(lines)


def hygiene_command(args):
    today = args.today or date.today()
    vocab = get_vocab(args.vocab)
    source = Path(args.worklist)
    rows = read_worklist(source, use_pandas=args.pandas)
    pending, pending_files = load_pending(getattr(args, "pending", None))
    if getattr(args, "pending", None) and not pending_files:
        print("warning: --pending was given but no .md, .markdown or .txt DELTA file was found", file=sys.stderr)
    result = run_hygiene(rows, today=today, aged_days=args.aged_days, stale_days=args.stale_days,
                         dup_threshold=args.dup_threshold, skip_closed=args.skip_closed, vocab=vocab,
                         done_candidate_days=args.done_candidate_days, pending=pending,
                         pending_files=pending_files)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    changes_path = out_dir / CHANGES_NAME
    report_path = out_dir / REPORT_NAME
    for target in (changes_path, report_path):
        if target.resolve() == source.resolve():
            raise WorklistError(f"refusing to overwrite the input file: {source}")
    write_proposed_changes(result, changes_path)
    report_path.write_text(render_report(result, source.name), encoding="utf-8", newline="\n")
    grouped = result.by_check()
    print(f"hygiene: {len(rows)} rows, {len(result.findings)} findings, "
          f"next free Task ID {result.next_id} (aged >= {result.aged_days} d, stale >= {result.stale_days} d, "
          f"done-candidate >= {result.done_candidate_days} d, vocab {vocab.source})")
    for check in CHECKS:
        if grouped.get(check):
            print(f"  {check}: {len(grouped[check])}")
    if result.pending_files:
        print(f"  pending DELTAs read: {len(result.pending_files)}; proposals on hold: {len(result.held())}")
    print(f"wrote {changes_path}")
    print(f"wrote {report_path}")
    return 0
