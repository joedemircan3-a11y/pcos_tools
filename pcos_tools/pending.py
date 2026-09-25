"""Read unapplied DELTA files and report which Task IDs they name.

A DELTA sitting in _PCOS_INBOX is not an applied change, but it can carry new
evidence about a row (a Done-Candidate that got new work, a Stale-Triage row
that came back to life). Automatic status proposals for those rows wait until
the DELTA is applied.
"""
from __future__ import annotations

from pathlib import Path

from .common import TASK_ID_FIND_RE, WorklistError, read_text_file, task_id_ranges, unescape_md

PENDING_SUFFIXES = (".md", ".txt", ".markdown")
# Reports this package writes; never read back as DELTAs if --out-dir is the inbox folder.
OWN_OUTPUTS = {"hygiene_report.md", "now_check_report.md", "PCOS_NOW_draft.md"}


def _expand(paths):
    files = []
    for raw in paths or ():
        path = Path(raw)
        if path.is_dir():
            files.extend(sorted(child for child in path.iterdir()
                                if child.is_file() and child.suffix.lower() in PENDING_SUFFIXES
                                and child.name not in OWN_OUTPUTS))
        elif path.is_file():
            files.append(path)
        else:
            raise WorklistError(f"pending DELTA path not found: {path}")
    return files


def load_pending(paths):
    """Return (mentions, files): Task ID -> sorted file names, and the files read.

    Directories are expanded to their .md / .txt files (not recursive).
    """
    mentions, files = {}, _expand(paths)
    for path in files:
        text = unescape_md(read_text_file(path, "pending DELTA"))
        for task_id in set(TASK_ID_FIND_RE.findall(text)) | task_id_ranges(text):
            mentions.setdefault(task_id, set()).add(path.name)
    return {task_id: sorted(names) for task_id, names in mentions.items()}, [path.name for path in files]
