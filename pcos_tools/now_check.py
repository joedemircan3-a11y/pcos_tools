"""Cross-check PCOS_NOW against the Worklist. Read-only; writes a report.

PCOS_NOW (v3) is hand-written narrative and the Worklist is rebuilt separately,
so the two drift: a row closed in the sheet is still described as live work, a
HIGH row never reaches the state file, the row count in the pointers section
goes stale. This command lists those gaps so the closeout writer fixes them in
one pass. It never edits either file.
"""
from __future__ import annotations

import csv
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from . import __version__
from .common import (
    FINAL_STATUSES,
    PERSONAL_ROOM,
    TASK_ID_FIND_RE,
    WorklistError,
    get_vocab,
    md_table,
    next_free_task_id,
    read_markdown_or_html,
    read_worklist,
    task_id_ranges,
    unescape_md,
)
from .now_build import parse_now
from .pending import load_pending

REPORT_NAME = "now_check_report.md"
CSV_NAME = "now_check.csv"
# Sections that describe live state: 0 today, 1 decisions, 2 current work, 3 waiting/dependencies.
LIVE_SECTIONS = (0, 1, 2, 3)
POINTER_SECTION = 7
OPEN_STATUSES = ("Active", "Needs-Decision", "Blocked", "Waiting")
HIGH_PRIORITIES = ("CRITICAL", "HIGH-TODAY", "HIGH")
# How far after a Task ID a status word still counts as describing that row.
STATUS_WINDOW = 60
ROW_COUNT_RE = re.compile(r"(?<![\d,.])(\d{1,4})\s+rows\b", re.IGNORECASE)
# A status word only describes the ID if it sits in the same clause or table cell.
CLAUSE_END_RE = re.compile(r"[.;!?](?:\s|$)|[|;]")

CHECKS = {
    "CITED_MISSING": "Task ID cited in a live section (0 to 3) but not in the Worklist",
    "CITED_CLOSED": "Task ID cited in a live section but Done, Expired, Superseded or Archived-Auto in the Worklist",
    "STATUS_MISMATCH": "A status word written right after the Task ID differs from the Worklist Status",
    "OPEN_NOT_CITED": "Open HIGH or CRITICAL Worklist row that PCOS_NOW never mentions",
    "ROW_COUNT": "Row count written in section 7 differs from the Worklist",
    "PENDING_DELTA": "Task ID named in an unapplied DELTA (apply before trusting the row)",
    "PENDING_NEW_ID": "Task ID named in an unapplied DELTA but not in the Worklist (a new row, or one kept elsewhere)",
}
CSV_COLUMNS = ["Check", "Task ID", "Worklist Status", "Section", "Detail"]


@dataclass
class CheckFinding:
    check: str
    task_id: str
    status: str
    section: str
    detail: str

    def as_record(self):
        return {"Check": self.check, "Task ID": self.task_id, "Worklist Status": self.status,
                "Section": self.section, "Detail": self.detail}


def _snippet(line, start, end, width=90):
    left = max(0, start - 25)
    text = line[left:max(end, left + width)].strip()
    return ("..." if left else "") + text + ("..." if len(line) > left + width else "")


def _status_words(vocab):
    # Longest first so "Done-Candidate" wins over "Done" and "Active-Low" over "Active".
    words = sorted(vocab.status, key=len, reverse=True)
    return re.compile(r"(?<![\w-])(" + "|".join(re.escape(word) for word in words) + r")(?![\w-])")


def run_now_check(rows, now_text, vocab=None, pending=None, pending_files=()):
    """Return (findings, summary). Pure: never touches the file system."""
    vocab = vocab or get_vocab()
    by_id = {}
    for row in rows:
        by_id.setdefault(row["Task ID"], row)
    parsed = parse_now(now_text)
    sections = parsed["sections"]
    status_re = _status_words(vocab)
    plain = unescape_md(now_text)
    findings, cited_live = [], {}
    cited_anywhere = set(TASK_ID_FIND_RE.findall(plain)) | task_id_ranges(plain)
    seen = set()

    def add(check, task_id, section, detail):
        key = (check, task_id, section)
        if key in seen:
            return
        seen.add(key)
        status = by_id[task_id]["Status"] if task_id in by_id else ""
        findings.append(CheckFinding(check, task_id, status, section, detail))

    for number in LIVE_SECTIONS:
        section = sections.get(number)
        if not section:
            continue
        label = f"{number} {unescape_md(section['title']).strip()}".strip()
        for raw in section["lines"]:
            line = unescape_md(raw)
            matches = list(TASK_ID_FIND_RE.finditer(line))
            for index, match in enumerate(matches):
                task_id = match.group(0)
                cited_live.setdefault(task_id, label)
                if task_id not in by_id:
                    add("CITED_MISSING", task_id, label, _snippet(line, match.start(), match.end()))
                    continue
                row = by_id[task_id]
                stop = matches[index + 1].start() if index + 1 < len(matches) else len(line)
                window = line[match.end():min(stop, match.end() + STATUS_WINDOW)]
                clause_end = CLAUSE_END_RE.search(window)
                if clause_end:
                    window = window[:clause_end.start()]
                word = status_re.search(window)
                if row["Status"] in FINAL_STATUSES and not (word and word.group(1) == row["Status"]):
                    add("CITED_CLOSED", task_id, label,
                        f"Worklist says {row['Status']}; PCOS_NOW: {_snippet(line, match.start(), match.end())}")
                if word and word.group(1) != row["Status"]:
                    add("STATUS_MISMATCH", task_id, label,
                        f"PCOS_NOW says {word.group(1)}, Worklist says {row['Status']}: "
                        f"{_snippet(line, match.start(), match.end())}")
            # IDs inside a range ("T-067 to T-071 unchanged") count as cited, which keeps
            # them out of OPEN_NOT_CITED. A range naturally spans gaps and closed rows,
            # so its members are never reported as missing or closed.
            for task_id in task_id_ranges(line):
                cited_live.setdefault(task_id, label)

    for row in rows:
        if (row["Status"] in OPEN_STATUSES and row["Priority"] in HIGH_PRIORITIES
                and row["Room"] != PERSONAL_ROOM and row["Task ID"] not in cited_anywhere):
            add("OPEN_NOT_CITED", row["Task ID"], "-",
                f"{row['Priority']} {row['Status']}: {row['Title']} (next: {row['Next Action'] or 'none'})")

    stated_counts = []
    pointer = sections.get(POINTER_SECTION)
    if pointer:
        lines = [unescape_md(raw) for raw in pointer["lines"]]
        live = [line for line in lines if "live worklist" in line.lower()]
        for line in live or [line for line in lines if "worklist" in line.lower()]:
            stated_counts += [int(found) for found in ROW_COUNT_RE.findall(line)]
    if stated_counts and stated_counts[0] != len(rows):
        add("ROW_COUNT", "", str(POINTER_SECTION),
            f"section 7 says {stated_counts[0]} rows; the Worklist has {len(rows)}")

    for task_id, names in sorted((pending or {}).items()):
        if task_id in by_id:
            add("PENDING_DELTA", task_id, "inbox", ", ".join(names))
        else:
            add("PENDING_NEW_ID", task_id, "inbox", ", ".join(names))

    order = {check: index for index, check in enumerate(CHECKS)}
    findings.sort(key=lambda finding: (order[finding.check], finding.task_id))
    warnings = []
    if not sections:
        warnings.append("no numbered sections found in PCOS_NOW (expected '# 0. ...' to '# 8. ...'); "
                        "only OPEN_NOT_CITED and PENDING checks ran")
    elif not any(number in sections for number in LIVE_SECTIONS):
        warnings.append("PCOS_NOW has none of the live sections 0 to 3")
    summary = {
        "warnings": warnings,
        "rows": len(rows),
        "sections_found": sorted(sections),
        "cited_live": len(cited_live),
        "next_id": next_free_task_id(rows),
        "pending_files": list(pending_files),
        "stated_rows": stated_counts[0] if stated_counts else None,
    }
    return findings, summary


def render_report(findings, summary, csv_name, now_name, today):
    grouped = {check: [f for f in findings if f.check == check] for check in CHECKS}
    missing = [number for number in range(9) if number not in summary["sections_found"]]
    lines = [
        f"# PCOS_NOW cross-check - {now_name} vs {csv_name}",
        "",
        f"- Generated by pcos_tools now_check v{__version__} on {today.isoformat()}",
        f"- Worklist rows: {summary['rows']}; next free Task ID: **{summary['next_id']}**",
        f"- PCOS_NOW sections found: {', '.join(map(str, summary['sections_found'])) or 'none'}"
        + (f" (missing: {', '.join(map(str, missing))})" if missing else ""),
        f"- Task IDs cited in live sections 0 to 3: {summary['cited_live']}",
        f"- Pending DELTAs read: {len(summary['pending_files'])}"
        + (f" ({', '.join(summary['pending_files'])})" if summary["pending_files"] else ""),
        f"- Findings: {len(findings)}",
        *[f"- WARNING: {warning}" for warning in summary["warnings"]],
        "",
        "> READ ONLY. Neither file was modified. The closeout writer resolves each line from the "
        "sources: fix PCOS_NOW, fix the Worklist row, or leave it and say why. Tool output is advisory; "
        "a live read of the source wins.",
        "",
        "## Summary",
        "",
        md_table(["Check", "Count", "Meaning"],
                 [[check, len(grouped[check]), meaning] for check, meaning in CHECKS.items()]),
        "",
    ]
    for check, meaning in CHECKS.items():
        items = grouped[check]
        if not items:
            continue
        lines += [f"## {check} ({len(items)})", "", meaning + ".", "",
                  md_table(["Task ID", "Worklist Status", "Section", "Detail"],
                           [[f.task_id, f.status, f.section, f.detail] for f in items]), ""]
    return "\n".join(lines)


def now_check_command(args):
    today = args.today or date.today()
    vocab = get_vocab(args.vocab)
    csv_path, now_path = Path(args.csv), Path(args.now)
    rows = read_worklist(csv_path, use_pandas=args.pandas)
    now_text = read_markdown_or_html(now_path, "PCOS_NOW")
    pending, pending_files = load_pending(args.pending)
    findings, summary = run_now_check(rows, now_text, vocab=vocab, pending=pending,
                                      pending_files=pending_files)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path, table_path = out_dir / REPORT_NAME, out_dir / CSV_NAME
    for target in (report_path, table_path):
        for source in (csv_path, now_path):
            if target.resolve() == source.resolve():
                raise WorklistError(f"refusing to overwrite an input file: {source}; choose another --out-dir")
    with table_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for finding in findings:
            writer.writerow(finding.as_record())
    report_path.write_text(render_report(findings, summary, csv_path.name, now_path.name, today),
                           encoding="utf-8", newline="\n")
    counts = {}
    for finding in findings:
        counts[finding.check] = counts.get(finding.check, 0) + 1
    for warning in summary["warnings"]:
        print(f"warning: {warning}", file=sys.stderr)
    if args.pending and not pending_files:
        print("warning: --pending was given but no .md, .markdown or .txt DELTA file was found", file=sys.stderr)
    print(f"now_check: {summary['rows']} rows, {summary['cited_live']} IDs cited in sections 0-3, "
          f"{len(findings)} findings, next free Task ID {summary['next_id']}")
    for check in CHECKS:
        if counts.get(check):
            print(f"  {check}: {counts[check]}")
    print(f"wrote {table_path}")
    print(f"wrote {report_path}")
    return 0
