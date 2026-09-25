"""Parse a RECON markdown file into JSON: sections, items, dates and named people."""
from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

from . import __version__
from .common import TASK_ID_FIND_RE, WorklistError, fence_flags, read_text_file

SECTION_SPECS = [
    (1, "coverage", "Coverage header", ("coverage",)),
    (2, "action_on_joe", "ACTION ON JOE", ("action",)),
    (3, "waiting_on_others", "WAITING ON OTHERS", ("waiting",)),
    (4, "delegable", "DELEGABLE", ("delegab", "delegat")),
    (5, "patterns", "Patterns", ("pattern",)),
    (6, "run_log", "Run-log footer", ("run-log", "run log", "runlog", "footer")),
]
SECTION_BY_NUMBER = {number: (key, title, keywords) for number, key, title, keywords in SECTION_SPECS}
SECTION_KEYS = [key for _, key, _, _ in SECTION_SPECS]

# RECON runbook 01-EM-02 v1.4 (Sep 2026) writes a different layout:
# "## COVERAGE DISCLOSURE", "## SECTION 1 — NEW TASK CANDIDATES", ... "## RUN LOG",
# with items as "**3.1**" or "**2.1 — title**" followed by "- **Field:** value"
# bullets. Keywords are matched in this order against the heading text.
V14_SPECS = [
    ("coverage", "COVERAGE DISCLOSURE", ("coverage",)),
    ("new_task_candidates", "NEW TASK CANDIDATES", ("new task",)),
    ("task_updates", "UPDATES TO EXISTING TASKS", ("updates to existing", "update")),
    ("action_on_joe", "FOLLOW-UPS REQUIRING OPERATOR ACTION", ("follow-up", "follow up", "operator action")),
    ("sensitive", "SENSITIVE / LEADERSHIP-WATCH", ("sensitive", "leadership")),
    ("ignore", "IGNORE / NO-ACTION", ("ignore", "no-action", "no action")),
    ("run_log", "RUN LOG", ("run log", "run-log")),
]
V14_KEYS = [key for key, _, _ in V14_SPECS]
V14_SECTION_RE = re.compile(r"^\s{0,3}#{1,6}\s+SECTION\s+\d+\s*[\u2014\u2013\-:.]", re.IGNORECASE)
V14_ITEM_RE = re.compile(r"^\s{0,3}\*\*(\d+\.\d+)\s*(.*?)\*\*\s*(.*)$")
V14_FIELD_RE = re.compile(r"^\s*[-*+]\s+\*\*([^*]{1,60}?)(?::\*\*|\*\*\s*:)\s*(.*)$")
V14_TABLE_KV_RE = re.compile(r"^\s*\|\s*\**([^|*]{1,60}?)\**\s*\|\s*(.+?)\s*\|?\s*$")
# When an item header has no text of its own, its label comes from the first of these fields.
V14_LABEL_FIELDS = ("Title", "What is needed", "What changed", "Subject (verbatim)", "Contact")

HASH_HEADER_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$")
NUMBERED_TITLE_RE = re.compile(r"^(\d)\s*[.):\-]\s*(.+)$")
PLAIN_HEADER_RE = re.compile(r"^\s{0,3}[*_]{0,2}\s*(\d)\s*[.):\-]\s*(.+?)\s*[*_]{0,2}\s*$")
BULLET_RE = re.compile(r"^(\s*)(?:[-*+•]|\d{1,3}[.)])\s+(.*\S)\s*$")
CHECKBOX_RE = re.compile(r"^\[([ xX])\]\s*")
RULE_RE = re.compile(r"^\s*[-*_]{3,}\s*$")
KV_RE = re.compile(r"^\**([A-Za-z][A-Za-z0-9 _/\-]{0,40}?)\**\s*:\s*(.+?)\s*$")

MONTH_PATTERN = (r"jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|"
                 r"aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?")
MONTH_INDEX = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
               "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}
# Also matches the date part of an ISO timestamp ("2026-09-23T16:08Z").
ISO_RE = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})(?:\b|(?=T\d))")
DMY_RE = re.compile(rf"\b(\d{{1,2}})(?:st|nd|rd|th)?\s+({MONTH_PATTERN})\b\.?,?(?:\s+(\d{{4}}))?",
                    re.IGNORECASE)
MDY_RE = re.compile(rf"\b({MONTH_PATTERN})\b\.?\s+(\d{{1,2}})(?:st|nd|rd|th)?\b(?:,?\s+(\d{{4}}))?",
                    re.IGNORECASE)
SLASH_RE = re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{2,4})\b")

# Latin letters including Latin-1 and Latin Extended-A (Turkish, German, French,
# Spanish, Polish ...), split by case so "Ayşe Çelik" and "Yılmaz" are names.
_UPPER = "A-ZÀ-ÖØ-Þ" + "".join(chr(code) for code in range(0x100, 0x180) if chr(code).isupper())
_LOWER = "a-zß-öø-ÿ" + "".join(chr(code) for code in range(0x100, 0x180) if chr(code).islower())
NAME_WORD = rf"[{_UPPER}][{_LOWER}]+(?:[-'][{_UPPER}][{_LOWER}]+)?"
HONORIFIC = r"(?:Dr|Mr|Mrs|Ms|Mx|Prof|Sir)\.?"
HONORIFICS = {"Dr", "Mr", "Mrs", "Ms", "Mx", "Prof", "Sir"}
NAME_SEQ = rf"(?:{HONORIFIC}\s+)?{NAME_WORD}(?:\s+{NAME_WORD}){{0,2}}"
TRIGGERS = (r"waiting on|waiting for|wait on|delegate to|assigned to|from|with|ask|asked|call|"
            r"called|email|emailed|ping|pinged|chase|chased|per|via|by|to|cc|for|owner")
PATTERN_RE = re.compile(rf"\b(?i:{TRIGGERS})\s+({NAME_SEQ})\b")
MENTION_RE = re.compile(r"@([^\W\d_][\w.\-]*)")
GENERIC_RE = re.compile(rf"(?<![{_UPPER}{_LOWER}@]){NAME_SEQ}\b")
SENTENCE_END_RE = re.compile(r"[.;!?]\s*$")
CONFIDENCE_RANK = {"heuristic": 1, "pattern": 2, "mention": 3, "known": 4}

NAME_STOPLIST = set("""
January February March April May June July August September October November December
Jan Feb Mar Apr Jun Jul Aug Sep Sept Oct Nov Dec
Monday Tuesday Wednesday Thursday Friday Saturday Sunday Mon Tue Wed Thu Fri Sat Sun
Today Tomorrow Yesterday Tonight Week Month Year Quarter Morning Afternoon Evening
Coverage Header Action Actions Waiting Others Delegable Delegate Pattern Patterns Run Log Footer
Recon Codex Worklist Room Task Tasks Owner Status Priority Sources Source Notes Note Next Updated
Confidence Period Items Item Summary Decision Decisions Candidate Candidates Stale Pointers Active
Blocked Done Open Backlog Expired Superseded Archived Auto Personal Critical High Med Low Recurring
Urgent Needs
The This That These Those There Here When Where Which Who What Why How If Then And But Or Not No Yes
Also Still After Before Since Until Per Via Re
Reply Send Sent Call Ask Check Confirm Book Pay Sign Decide Follow Up Chase Ping Email Schedule Cancel
Renew Submit Fix Compile Consolidate Draft Review Update Prepare Finish Start Close Write Read Set Get
Move Add Remove Buy Order Plan Wait Chased Pinged Promised Requested Approve Approved Pick Choose
One Two Three Four Five Six Seven Eight Nine Ten New Old Ok Okay
Gmail Calendar WhatsApp Drive Slack Outlook Teams Zoom Docs Sheets Google Microsoft Claude Chrome Notion
Invoice Contract Lease Vendor Report Sheet Conference Travel Team Office Meeting Deadline Due Migration
""".split())


# ---------------------------------------------------------------- headers --

def _resolve_title(title, current_number, allow_sequential):
    title = title.strip().strip("*_").strip()
    match = NUMBERED_TITLE_RE.match(title)
    if match:
        number, rest = int(match.group(1)), match.group(2).strip().strip("*_").strip()
        if number not in SECTION_BY_NUMBER:
            return None
        if any(keyword in rest.lower() for keyword in SECTION_BY_NUMBER[number][2]):
            return number, rest
        if allow_sequential and number == (current_number or 0) + 1:
            return number, rest
        return None
    lowered = title.lower()
    for number, _key, _canonical, keywords in SECTION_SPECS:
        if any(keyword in lowered for keyword in keywords):
            return number, title
    return None


def _is_section_heading(line):
    match = HASH_HEADER_RE.match(line)
    return bool(match and _resolve_title(match.group(1), None, allow_sequential=False))


def _detect_header(line, heading_mode, current_number):
    hash_match = HASH_HEADER_RE.match(line)
    if hash_match:
        return _resolve_title(hash_match.group(1), current_number, allow_sequential=True)
    if heading_mode:
        return None
    plain_match = PLAIN_HEADER_RE.match(line)
    if not plain_match:
        return None
    number = int(plain_match.group(1))
    rest = plain_match.group(2).strip().strip("*_").strip()
    if number not in SECTION_BY_NUMBER or number <= (current_number or 0):
        return None
    if any(keyword in rest.lower() for keyword in SECTION_BY_NUMBER[number][2]):
        return number, rest
    return None


# ------------------------------------------------------------------ dates --

def _make_iso(year, month, day):
    try:
        return date(year, month, day).isoformat()
    except ValueError:
        return None


def extract_dates(text, default_year):
    """Find dates in free text. Returns [{"raw": ..., "iso": ... or None}] in text order."""
    found = []

    def add(start, end, raw, iso):
        for other_start, other_end, _, _ in found:
            if start < other_end and end > other_start:
                return
        found.append((start, end, raw, iso))

    for match in ISO_RE.finditer(text):
        add(match.start(), match.end(), match.group(0),
            _make_iso(int(match.group(1)), int(match.group(2)), int(match.group(3))))
    for match in DMY_RE.finditer(text):
        month = MONTH_INDEX[match.group(2)[:3].lower()]
        year = int(match.group(3)) if match.group(3) else default_year
        add(match.start(), match.end(), match.group(0).strip(), _make_iso(year, month, int(match.group(1))))
    for match in MDY_RE.finditer(text):
        month = MONTH_INDEX[match.group(1)[:3].lower()]
        year = int(match.group(3)) if match.group(3) else default_year
        add(match.start(), match.end(), match.group(0).strip(), _make_iso(year, month, int(match.group(2))))
    for match in SLASH_RE.finditer(text):
        add(match.start(), match.end(), match.group(0), None)  # day/month order ambiguous
    found.sort()
    return [{"raw": raw, "iso": iso} for _, _, raw, iso in found]


# ----------------------------------------------------------------- people --

def _clean_name(candidate):
    words = candidate.replace("_", " ").split()
    while words and words[0].rstrip(".") in NAME_STOPLIST:
        words.pop(0)
    while words and words[-1].rstrip(".") in NAME_STOPLIST:
        words.pop()
    if not words or (len(words) == 1 and words[0].rstrip(".") in HONORIFICS):
        return ""
    return " ".join(words)


def extract_people(text, known_people=()):
    """Named people in free text, best confidence first.

    confidence: known (matched --people list) > mention (@name) > pattern
    (after a trigger such as "waiting on", "from", "to") > heuristic
    (capitalised word run that is not a stop word).
    """
    found = {}

    def add(name, confidence, clean=True):
        name = _clean_name(name) if clean else name.strip()
        if not name:
            return
        key = name.lower()
        if key not in found or CONFIDENCE_RANK[found[key][1]] < CONFIDENCE_RANK[confidence]:
            found[key] = (name, confidence)

    for person in known_people:
        if person and re.search(r"(?<!\w)" + re.escape(person) + r"(?!\w)", text, re.IGNORECASE):
            add(person, "known", clean=False)
    for match in MENTION_RE.finditer(text):
        add(match.group(1), "mention")
    for match in PATTERN_RE.finditer(text):
        add(match.group(1), "pattern")
    for match in GENERIC_RE.finditer(text):
        prefix = text[:match.start()]
        at_start = not prefix.strip() or bool(SENTENCE_END_RE.search(prefix))
        name = _clean_name(match.group(0))
        if not name or (at_start and len(name.split()) < 2):
            continue
        add(name, "heuristic")
    ordered = sorted(found.values(), key=lambda pair: (-CONFIDENCE_RANK[pair[1]], pair[0]))
    return [{"name": name, "confidence": confidence} for name, confidence in ordered]


# ------------------------------------------------------------------ parse --

def _new_sections():
    return {
        key: {"number": number, "key": key, "title": canonical, "found": False,
              "heading_line": None, "items": [], "notes": [], "fields": {}}
        for number, key, canonical, _ in SECTION_SPECS
    }


# Keywords that only the v1.4 section titles use; a legacy file with "## Section 2: ACTION ON JOE"
# headings stays legacy.
V14_ONLY_KEYWORDS = ("new task", "updates to existing", "follow-up", "follow up", "sensitive", "no-action", "ignore")


def is_v14_layout(lines, fenced):
    for line, in_fence in zip(lines, fenced):
        if not in_fence and V14_SECTION_RE.match(line):
            if any(keyword in line.lower() for keyword in V14_ONLY_KEYWORDS):
                return True
    return False


def _v14_section_key(title):
    lowered = title.lower()
    for key, _canonical, keywords in V14_SPECS:
        if any(keyword in lowered for keyword in keywords):
            return key
    return None


def _item_extras(item, default_year, known_people):
    full = " ".join([item["text"]] + list(item.get("fields", {}).values()) + item.get("detail", []))
    item["dates"] = extract_dates(full, default_year)
    item["people"] = extract_people(full, known_people)
    item["task_ids"] = sorted(set(TASK_ID_FIND_RE.findall(full)))


def parse_recon_v14(text, lines, fenced, source, default_year, known_people):
    """Parse the runbook v1.4 layout (see V14_SPECS)."""
    sections = {key: {"key": key, "title": canonical, "found": False, "heading_line": None,
                      "items": [], "notes": [], "fields": {}}
                for key, canonical, _ in V14_SPECS}
    preamble, warnings, current, item = [], [], None, None
    for lineno, raw in enumerate(lines, start=1):
        stripped = raw.strip()
        if fenced[lineno - 1]:
            if current is None:
                preamble.append(raw.rstrip())
            elif stripped:
                (item["detail"] if item else current["notes"]).append(stripped)
            continue
        heading = HASH_HEADER_RE.match(raw)
        if heading:
            # Only the numbered SECTION headings, COVERAGE and RUN LOG switch sections;
            # a sub-heading such as "### Follow-up context" stays inside the current one.
            key = _v14_section_key(heading.group(1))
            if key and not (V14_SECTION_RE.match(raw) or key in ("coverage", "run_log")):
                key = None
            if key:
                section = sections[key]
                if section["found"]:
                    warnings.append(f"line {lineno}: {section['title']} appears again; items merged")
                else:
                    section["found"], section["title"], section["heading_line"] = True, heading.group(1), lineno
                current, item = section, None
                continue
        if not stripped or RULE_RE.match(raw):
            continue
        if current is None:
            preamble.append(stripped.lstrip("#").strip())
            continue
        head = V14_ITEM_RE.match(raw)
        if head:
            label = head.group(2).strip().lstrip("\u2014\u2013-: ").strip()
            tail = head.group(3).strip().lstrip("\u2014\u2013-: ").strip()
            item = {"ref": head.group(1), "text": " ".join(part for part in (label, tail) if part),
                    "level": 0, "line": lineno, "fields": {}, "detail": []}
            current["items"].append(item)
            continue
        field = V14_FIELD_RE.match(raw)
        if field and item is not None:
            item["fields"].setdefault(field.group(1).strip(), field.group(2).strip())
            continue
        table = V14_TABLE_KV_RE.match(raw)
        next_line = lines[lineno] if lineno < len(lines) else ""
        is_header_row = bool(re.match(r"^\s*\|[\s:|-]+\|?\s*$", next_line))
        if table and not is_header_row and not set(table.group(1).strip()) <= set("-: "):
            current["fields"].setdefault(table.group(1).strip(), table.group(2).strip())
            continue
        if item is not None:
            item["detail"].append(stripped)
        else:
            current["notes"].append(stripped)

    all_dates, people, task_ids = [], {}, set()
    for key in V14_KEYS:
        section = sections[key]
        for index, entry in enumerate(section["items"]):
            entry["index"] = index
            if not entry["text"]:
                entry["text"] = next((entry["fields"][name] for name in V14_LABEL_FIELDS
                                      if entry["fields"].get(name)), "")
            _item_extras(entry, default_year, known_people)
            for found in entry["dates"]:
                all_dates.append({"iso": found["iso"], "raw": found["raw"], "section": key, "item": index})
            for person in entry["people"]:
                record = people.setdefault(person["name"].lower(), {
                    "name": person["name"], "count": 0, "sections": [], "confidence": person["confidence"]})
                record["count"] += 1
                if key not in record["sections"]:
                    record["sections"].append(key)
                if CONFIDENCE_RANK[person["confidence"]] > CONFIDENCE_RANK[record["confidence"]]:
                    record["confidence"] = person["confidence"]
            task_ids.update(entry["task_ids"])
        if not section["found"]:
            warnings.append(f"{section['title']} not found")

    coverage_text = " ".join(list(sections["coverage"]["fields"].values()) + sections["coverage"]["notes"])
    coverage_isos = [found["iso"] for found in extract_dates(coverage_text, default_year) if found["iso"]]
    return {
        "tool": f"pcos_tools recon_parse {__version__}",
        "source": source,
        "layout": "runbook-v1.4",
        "parsed_at": date.today().isoformat(),
        "as_of": max(coverage_isos) if coverage_isos else None,
        "default_year": default_year,
        "heading_mode": "markdown",
        "preamble": preamble,
        "sections": sections,
        "dates": all_dates,
        "people": sorted(people.values(), key=lambda entry: (-entry["count"], entry["name"])),
        "task_ids": sorted(task_ids),
        "warnings": warnings,
    }


def parse_recon(text, source="", default_year=None, known_people=()):
    """Parse RECON markdown text into a JSON-serialisable dict.

    Two layouts: the original six numbered sections (Coverage, ACTION ON JOE,
    WAITING ON OTHERS, DELEGABLE, Patterns, Run-log) and runbook v1.4
    ("SECTION n — ..." headings, see V14_SPECS). ``layout`` in the result says which.
    """
    lines = text.splitlines()
    if default_year is None:
        first_iso = ISO_RE.search(text)
        default_year = int(first_iso.group(1)) if first_iso else date.today().year
    fenced = fence_flags(lines)
    if is_v14_layout(lines, fenced):
        return parse_recon_v14(text, lines, fenced, source, default_year, known_people)
    heading_mode = any(not in_fence and _is_section_heading(line) for line, in_fence in zip(lines, fenced))
    sections = _new_sections()
    preamble, warnings = [], []
    current = None

    for lineno, raw in enumerate(lines, start=1):
        in_fence = fenced[lineno - 1]
        if in_fence:  # code fences are kept as plain notes, never headers or bullets
            stripped = raw.rstrip()
            if current is None:
                preamble.append(stripped)
            elif stripped:
                current["notes"].append(stripped)
            continue
        header = _detect_header(raw, heading_mode, current["number"] if current else None)
        if header:
            number, title = header
            section = sections[SECTION_BY_NUMBER[number][0]]
            if section["found"]:
                warnings.append(f"line {lineno}: section {number} appears again; "
                                "items merged into the first occurrence")
            else:
                section["found"], section["title"], section["heading_line"] = True, title, lineno
            current = section
            continue
        stripped = raw.strip()
        if not stripped or RULE_RE.match(raw):
            continue
        if current is None:
            preamble.append(stripped.lstrip("#").strip())
            continue
        bullet = BULLET_RE.match(raw)
        if bullet:
            indent = len(bullet.group(1).replace("\t", "    "))
            body = bullet.group(2).strip()
            item = {"text": body, "level": min(indent // 2, 3), "line": lineno}
            box = CHECKBOX_RE.match(body)
            if box:
                item["done"] = box.group(1).lower() == "x"
                item["text"] = body[box.end():].strip()
            current["items"].append(item)
            continue
        if stripped.startswith("#"):
            stripped = stripped.lstrip("#").strip()
        if current["items"] and raw[:1] in (" ", "\t"):
            current["items"][-1]["text"] += " " + stripped
        else:
            current["notes"].append(stripped)

    all_dates, people, task_ids = [], {}, set()
    for key in SECTION_KEYS:
        section = sections[key]
        for index, item in enumerate(section["items"]):
            item["index"] = index
            item["dates"] = extract_dates(item["text"], default_year)
            item["people"] = extract_people(item["text"], known_people)
            item["task_ids"] = sorted(set(TASK_ID_FIND_RE.findall(item["text"])))
            for found in item["dates"]:
                all_dates.append({"iso": found["iso"], "raw": found["raw"], "section": key, "item": index})
            for person in item["people"]:
                entry = people.setdefault(person["name"].lower(), {
                    "name": person["name"], "count": 0, "sections": [], "confidence": person["confidence"]})
                entry["count"] += 1
                if key not in entry["sections"]:
                    entry["sections"].append(key)
                if CONFIDENCE_RANK[person["confidence"]] > CONFIDENCE_RANK[entry["confidence"]]:
                    entry["confidence"] = person["confidence"]
            task_ids.update(item["task_ids"])
        if key in ("coverage", "run_log"):
            for text_line in [item["text"] for item in section["items"]] + section["notes"]:
                pair = KV_RE.match(text_line)
                if pair:
                    section["fields"].setdefault(pair.group(1).strip(), pair.group(2).strip())
        if not section["found"]:
            warnings.append(f"section {section['number']} ({section['title']}) not found")

    coverage_isos = [found["iso"] for found in all_dates if found["section"] == "coverage" and found["iso"]]
    if not coverage_isos:
        coverage_isos = [found["iso"] for note in sections["coverage"]["notes"]
                         for found in extract_dates(note, default_year) if found["iso"]]
    if not coverage_isos:
        coverage_isos = [found["iso"] for line in preamble
                         for found in extract_dates(line, default_year) if found["iso"]]

    return {
        "tool": f"pcos_tools recon_parse {__version__}",
        "source": source,
        "layout": "legacy",
        "parsed_at": date.today().isoformat(),
        "as_of": max(coverage_isos) if coverage_isos else None,
        "default_year": default_year,
        "heading_mode": "markdown" if heading_mode else "plain",
        "preamble": preamble,
        "sections": sections,
        "dates": all_dates,
        "people": sorted(people.values(), key=lambda entry: (-entry["count"], entry["name"])),
        "task_ids": sorted(task_ids),
        "warnings": warnings,
    }


def validate_recon(data, source="RECON JSON"):
    """Check that a hand-supplied RECON JSON has the shape recon_parse writes.

    Missing per-item keys (level, dates, people, task_ids) are filled with
    empty defaults so a trimmed file still works; anything else is an error.
    """
    if not isinstance(data, dict) or not isinstance(data.get("sections"), dict):
        raise WorklistError(f"{source} is not a recon_parse JSON file (no 'sections' object)")
    for key, section in data["sections"].items():
        if not isinstance(section, dict) or not isinstance(section.get("items", []), list):
            raise WorklistError(f"{source}: section {key!r} must be an object with an 'items' list")
        for index, item in enumerate(section.setdefault("items", [])):
            where = f"{source}: section {key!r} item {index}"
            if not isinstance(item, dict) or not isinstance(item.get("text"), str):
                raise WorklistError(f"{where} has no 'text' string")
            level = item.setdefault("level", 0)
            if isinstance(level, bool) or not isinstance(level, int):
                raise WorklistError(f"{where}: 'level' must be an integer")
            for list_key in ("dates", "people", "task_ids"):
                if item.get(list_key) is None:
                    item[list_key] = []
                elif not isinstance(item[list_key], list):
                    raise WorklistError(f"{where}: '{list_key}' must be a list")
            if not item["task_ids"]:
                item["task_ids"] = sorted(set(TASK_ID_FIND_RE.findall(item["text"])))
            if not all(isinstance(found, dict) and isinstance(found.get("iso"), (str, type(None)))
                       for found in item["dates"]):
                raise WorklistError(f"{where}: 'dates' must be a list of objects with an 'iso' string or null")
            if not all(isinstance(person, dict) and isinstance(person.get("name"), str)
                       for person in item["people"]):
                raise WorklistError(f"{where}: 'people' must be a list of objects with a 'name' string")
            if not all(isinstance(task_id, str) for task_id in item["task_ids"]):
                raise WorklistError(f"{where}: 'task_ids' must be a list of strings")
    return data


def load_recon(path, default_year=None, known_people=()):
    """Load a RECON as a dict from either a parsed .json or a raw .md file."""
    path = Path(path)
    if not path.is_file():
        raise WorklistError(f"RECON file not found: {path}")
    try:
        text = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        raise WorklistError(f"RECON file {path} is not UTF-8 text ({exc.reason} at byte {exc.start})") from exc
    if path.suffix.lower() == ".json":
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise WorklistError(f"RECON JSON {path} is not valid JSON: {exc}") from exc
        return validate_recon(data, str(path))
    return parse_recon(text, source=path.name, default_year=default_year, known_people=known_people)


def split_people(value):
    return [name.strip() for name in (value or "").split(",") if name.strip()]


def recon_parse_command(args):
    path = Path(args.recon)
    result = parse_recon(read_text_file(path, "RECON file"), source=path.name,
                         default_year=args.year, known_people=split_people(args.people))
    payload = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.out == "-":
        sys.stdout.write(payload)
    else:
        out_path = Path(args.out) if args.out else path.with_suffix(".json")
        if out_path.resolve() == path.resolve():
            raise WorklistError("refusing to overwrite the RECON input; choose another --out")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(payload, encoding="utf-8", newline="\n")
        counts = ", ".join(f"{key}={len(section['items'])}" for key, section in result["sections"].items())
        print(f"recon_parse ({result['layout']}): {counts}; dates={len(result['dates'])}; "
              f"people={len(result['people'])}; as_of={result['as_of']}")
        print(f"wrote {out_path}")
    for warning in result["warnings"]:
        print(f"warning: {warning}", file=sys.stderr)
    return 0
