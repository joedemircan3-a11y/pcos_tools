"""Shared constants and helpers for pcos_tools.

Standard library only. Nothing in this module writes to disk.

The Status, Priority and Room vocabularies and the stale threshold live in
``vocab.json`` next to this file. ``get_vocab()`` loads it the first time a
command needs it (and caches it); ``get_vocab(path)`` reads an alternative file
for ``--vocab``. Nothing is loaded at import time, so a broken file surfaces as
a normal command error instead of an import traceback. ``VOCAB``,
``STATUS_VOCAB``, ``PRIORITY_VOCAB``, ``ROOM_VOCAB``, ``PRIORITY_ORDER`` and
``DEFAULT_STALE_DAYS`` are available as lazy module attributes.
"""
from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from datetime import date, datetime
from html.parser import HTMLParser
from pathlib import Path

COLUMNS = [
    "Task ID", "Title", "Room", "Status", "Priority", "Owner", "Waiting On",
    "Sources", "Next Action", "Updated", "Confidence", "Notes",
]

VOCAB_PATH = Path(__file__).with_name("vocab.json")
PACKAGED_VOCAB_LABEL = "packaged vocab.json"

# Status groups used by the checks and the PCOS_NOW builder. Every name here
# must also appear in the vocabulary's status list.
ACTIVE_STATUSES = ("Active", "Active-Low", "Active-Recurring", "Needs-Decision", "Blocked")
AGED_STATUSES = ("Waiting", "Blocked")
CLOSED_STATUSES = ("Done", "Done-Candidate", "Expired", "Superseded", "Archived-Auto")
# Closed for good: a row in one of these should no longer be cited as live work.
FINAL_STATUSES = ("Done", "Expired", "Superseded", "Archived-Auto")
ACTIVE_LOW_STATUS = "Active-Low"
DONE_CANDIDATE_STATUS = "Done-Candidate"
STALE_STATUS = "Stale-Triage"
WAITING_STATUS = "Waiting"
PERSONAL_ROOM = "PERSONAL"
# Fallbacks used only when a vocab file omits the key.
DEFAULT_AGED_DAYS = 7
DEFAULT_DONE_CANDIDATE_DAYS = 7

TASK_ID_RE = re.compile(r"^T-\d{3,4}$")
TASK_ID_FIND_RE = re.compile(r"\bT-\d{3,4}\b")
# "T-067 to T-071", "T-067 through T-071", "T-090..T-100", "T-067\u2013T-071" (en dash,
# no spaces): every ID in between is meant. Only spaces or tabs may separate the
# parts, so two IDs on consecutive lines never form a range; a plain hyphen and a
# spaced dash are clause breaks, not ranges; "from T-001 to T-020" is a move.
TASK_ID_RANGE_RE = re.compile(
    r"(?<!from )\bT-(\d{3,4})(?:[ \t]+(?:to|through|thru)[ \t]+|[ \t]*\.\.[ \t]*|\u2013)T-(\d{3,4})\b",
    re.IGNORECASE)
MAX_RANGE_SPAN = 60


def task_id_ranges(text):
    """Task IDs implied by ranges in the text, excluding the two endpoints."""
    implied = set()
    for match in TASK_ID_RANGE_RE.finditer(text):
        first, last = int(match.group(1)), int(match.group(2))
        if 0 < last - first <= MAX_RANGE_SPAN:
            width = len(match.group(1))
            implied.update(f"T-{number:0{width}d}" for number in range(first + 1, last))
    return implied


STOPWORDS = {
    "a", "an", "the", "of", "for", "to", "and", "or", "in", "on", "at", "with",
    "re", "vs", "by", "from", "is", "be", "as", "into", "via", "about",
}

_NON_ALNUM = re.compile(r"[^0-9a-z]+")


class WorklistError(ValueError):
    """Raised when an input file cannot be read or has the wrong shape."""


# ------------------------------------------------------------- vocabulary --

@dataclass(frozen=True)
class Vocab:
    """Allowed values plus the stale threshold, as read from a vocab JSON file."""

    status: tuple
    priority: tuple
    room: tuple
    stale_days: int
    source: str
    aged_days: int = DEFAULT_AGED_DAYS
    done_candidate_days: int = DEFAULT_DONE_CANDIDATE_DAYS

    @property
    def priority_order(self):
        """Non-blank priorities, highest first."""
        return tuple(value for value in self.priority if value)

    def priority_rank(self, priority):
        """Sort key: first listed priority is 0; blank or unknown sorts last."""
        order = self.priority_order
        return order.index(priority) if priority in order else len(order)


def _require_list(data, key, path):
    value = data.get(key)
    if not isinstance(value, list) or not value or not all(isinstance(item, str) for item in value):
        raise WorklistError(f"vocab file {path}: '{key}' must be a non-empty list of strings")
    return tuple(item.strip() for item in value)


def load_vocab(path=None):
    """Read a vocab JSON file (default: the packaged vocab.json). Not cached."""
    path = Path(path) if path else VOCAB_PATH
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError as exc:
        raise WorklistError(f"vocab file not found: {path}") from exc
    except OSError as exc:
        raise WorklistError(f"vocab file {path} cannot be read: {exc.strerror or exc}") from exc
    except UnicodeDecodeError as exc:
        raise WorklistError(f"vocab file {path} is not UTF-8 text ({exc.reason})") from exc
    except json.JSONDecodeError as exc:
        raise WorklistError(f"vocab file {path} is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise WorklistError(f"vocab file {path}: top level must be a JSON object")
    status = _require_list(data, "status", path)
    priority = _require_list(data, "priority", path)
    room = _require_list(data, "room", path)
    def days(key, default, minimum):
        value = data.get(key, default)
        if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
            raise WorklistError(f"vocab file {path}: '{key}' must be an integer of at least {minimum}")
        return value

    stale_days = days("stale_days", None, 1)
    aged_days = days("aged_days", DEFAULT_AGED_DAYS, 0)
    done_candidate_days = days("done_candidate_days", DEFAULT_DONE_CANDIDATE_DAYS, 1)
    source = PACKAGED_VOCAB_LABEL if path == VOCAB_PATH else str(path)
    return Vocab(status, priority, room, stale_days, source, aged_days, done_candidate_days)


_PACKAGED_VOCAB = None


def get_vocab(path=None):
    """Vocab for ``path`` (uncached) or the packaged vocab.json (loaded once)."""
    global _PACKAGED_VOCAB
    if path:
        return load_vocab(path)
    if _PACKAGED_VOCAB is None:
        _PACKAGED_VOCAB = load_vocab()
    return _PACKAGED_VOCAB


_LAZY_ATTRS = {
    "VOCAB": lambda vocab: vocab,
    "STATUS_VOCAB": lambda vocab: list(vocab.status),
    "PRIORITY_VOCAB": lambda vocab: list(vocab.priority),
    "ROOM_VOCAB": lambda vocab: list(vocab.room),
    "PRIORITY_ORDER": lambda vocab: list(vocab.priority_order),
    "DEFAULT_STALE_DAYS": lambda vocab: vocab.stale_days,
    "AGED_DAYS": lambda vocab: vocab.aged_days,
    "DONE_CANDIDATE_DAYS": lambda vocab: vocab.done_candidate_days,
}


def __getattr__(name):
    """Lazy module attributes derived from the packaged vocabulary."""
    if name in _LAZY_ATTRS:
        return _LAZY_ATTRS[name](get_vocab())
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def priority_rank(priority, vocab=None):
    """Sort key for a priority value under the given (or packaged) vocabulary."""
    return (vocab or get_vocab()).priority_rank(priority)


def room_sort_key(room):
    return (0, int(room)) if room.isdigit() else (1, room)


# ------------------------------------------------------------------ dates --

def parse_date(value):
    """Return a date for a YYYY-MM-DD string (or a date), else None."""
    if isinstance(value, date):
        return value
    text = "" if value is None else str(value).strip()
    if not text:
        return None
    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        return None


def age_days(today, value):
    """Whole days between today and a YYYY-MM-DD value; None if unparseable."""
    parsed = parse_date(value)
    if parsed is None:
        return None
    return (today - parsed).days


# --------------------------------------------------------------- worklist --

def read_text_file(path, what="input file"):
    """Read a UTF-8 (BOM tolerated) text file with clean errors."""
    path = Path(path)
    if not path.is_file():
        raise WorklistError(f"{what} not found: {path}")
    try:
        return path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        raise WorklistError(
            f"{what} {path} is not UTF-8 text ({exc.reason} at byte {exc.start}); re-save it as UTF-8"
        ) from exc
    except OSError as exc:
        raise WorklistError(f"{what} {path} cannot be read: {exc.strerror or exc}") from exc


FENCE_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")


def fence_flags(lines):
    """True for every line that is a code fence or sits inside one."""
    flags, in_fence = [], False
    for line in lines:
        if FENCE_RE.match(line):
            in_fence = not in_fence
            flags.append(True)
        else:
            flags.append(in_fence)
    return flags


def _read_with_csv(path):
    try:
        with path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            fieldnames = [name.strip() for name in (reader.fieldnames or [])]
            reader.fieldnames = fieldnames
            return fieldnames, list(reader)
    except UnicodeDecodeError as exc:
        raise WorklistError(
            f"worklist {path} is not UTF-8 text ({exc.reason} at byte {exc.start}); "
            "re-export it as CSV UTF-8"
        ) from exc
    except OSError as exc:
        raise WorklistError(f"worklist {path} cannot be read: {exc.strerror or exc}") from exc


def _read_with_pandas(path):
    try:
        import pandas as pd  # optional dependency, only behind --pandas
    except ImportError as exc:  # pragma: no cover - depends on environment
        raise WorklistError(
            "--pandas was requested but pandas is not installed (pip install pandas)"
        ) from exc
    frame = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    frame.columns = [str(column).strip() for column in frame.columns]
    return list(frame.columns), frame.to_dict(orient="records")


def read_worklist(path, use_pandas=False):
    """Read the Worklist CSV into a list of dicts keyed by COLUMNS.

    Every cell is stripped. Each row also carries ``_row``: its row number in
    the file, counting the header as row 1. The file is opened read-only.
    """
    path = Path(path)
    if not path.is_file():
        raise WorklistError(f"worklist not found: {path}")
    fieldnames, records = _read_with_pandas(path) if use_pandas else _read_with_csv(path)
    missing = [column for column in COLUMNS if column not in fieldnames]
    if missing:
        raise WorklistError(
            "worklist header is missing columns: " + ", ".join(missing)
            + "; found: " + ", ".join(fieldnames)
        )
    rows = []
    for number, record in enumerate(records, start=2):
        row = {}
        for column in COLUMNS:
            value = record.get(column)
            row[column] = "" if value is None else str(value).strip()
        row["_row"] = number
        rows.append(row)
    return rows


# ----------------------------------------------------------------- titles --

def normalize_title(text):
    """Lowercase, strip punctuation, collapse whitespace."""
    return _NON_ALNUM.sub(" ", (text or "").lower()).strip()


def title_tokens(text):
    """Token set of a title with stopwords removed (kept if nothing else remains)."""
    tokens = normalize_title(text).split()
    kept = [token for token in tokens if token not in STOPWORDS]
    return set(kept or tokens)


def title_similarity(tokens_a, tokens_b):
    """Sorensen-Dice overlap of two token sets, 0.0 to 1.0."""
    if not tokens_a or not tokens_b:
        return 0.0
    return 2.0 * len(tokens_a & tokens_b) / (len(tokens_a) + len(tokens_b))


def next_free_task_id(rows):
    """Highest well-formed Task ID plus one, zero-padded to three digits."""
    numbers = [int(row["Task ID"][2:]) for row in rows if TASK_ID_RE.match(row["Task ID"])]
    return f"T-{max(numbers, default=0) + 1:03d}"


# --------------------------------------------------------------- markdown --

# Google Docs escapes Markdown punctuation when a Doc is downloaded as .md
# ("# 0\. Joe today", "PCOS\_NOW", "\[LIVE\]", "\$45"). Undo it before matching.
MD_ESCAPE_RE = re.compile(r"\\([\\`*_{}\[\]()#+\-.!|<>~=:$])")


def unescape_md(text):
    """Remove the backslash escapes Google Docs adds to exported Markdown."""
    return MD_ESCAPE_RE.sub(r"\1", text)


class _HtmlToMarkdown(HTMLParser):
    """Just enough HTML to Markdown for a Google Docs HTML export: headings,
    paragraphs, list items and table rows become lines; everything else is text."""

    BLOCKS = {"p", "div", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "br", "table", "ul", "ol"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lines, self.buffer, self.cells, self.prefix, self.skip = [], [], None, "", 0

    def _flush(self):
        text = " ".join("".join(self.buffer).split())
        self.buffer = []
        if text:
            self.lines.append(self.prefix + text)
        self.prefix = ""

    def handle_starttag(self, tag, attrs):
        if tag in ("style", "script", "head", "title"):
            self.skip += 1
        elif tag == "tr":
            self._flush()
            self.cells = []
        elif tag in ("td", "th") and self.cells is not None:
            self.buffer = []
        elif tag in self.BLOCKS and self.cells is None:
            self._flush()
            if len(tag) == 2 and tag[0] == "h" and tag[1].isdigit():
                self.prefix = "#" * int(tag[1]) + " "
            elif tag == "li":
                self.prefix = "- "

    def handle_endtag(self, tag):
        if tag in ("style", "script", "head", "title"):
            self.skip = max(0, self.skip - 1)
        elif tag in ("td", "th") and self.cells is not None:
            self.cells.append(" ".join("".join(self.buffer).split()))
            self.buffer = []
        elif tag == "tr" and self.cells is not None:
            self.lines.append("| " + " | ".join(self.cells) + " |")
            self.cells = None
        elif tag in self.BLOCKS and self.cells is None:
            self._flush()

    def handle_data(self, data):
        if not self.skip:
            self.buffer.append(data)


def html_to_markdown(html):
    """Convert a Google Docs HTML export into Markdown-like lines (headings keep their level)."""
    parser = _HtmlToMarkdown()
    parser.feed(html)
    parser.close()
    parser._flush()
    return "\n".join(parser.lines) + "\n"


def read_markdown_or_html(path, what="input file"):
    """Read a Markdown file, or an .html/.htm export converted to Markdown lines."""
    text = read_text_file(path, what)
    if Path(path).suffix.lower() in (".html", ".htm"):
        return html_to_markdown(text)
    return text


def md_cell(value):
    text = "" if value is None else str(value)
    return text.replace("\r", " ").replace("\n", " ").replace("|", "\\|").strip()


def md_table(headers, rows):
    lines = [
        "| " + " | ".join(md_cell(header) for header in headers) + " |",
        "|" + "|".join(" --- " for _ in headers) + "|",
    ]
    for row in rows:
        lines.append("| " + " | ".join(md_cell(cell) for cell in row) + " |")
    return "\n".join(lines)
