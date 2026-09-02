"""Command line entry point: python -m pcos_tools <command>."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date

from . import __version__
from .common import DEFAULT_AGED_DAYS, WorklistError
from .hygiene import hygiene_command
from .now_build import now_build_command
from .recon_parse import recon_parse_command


def iso_date(text):
    try:
        return date.fromisoformat(text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"expected YYYY-MM-DD, got {text!r}") from exc


def _int_at_least(minimum):
    def convert(text):
        try:
            value = int(text)
        except ValueError as exc:
            raise argparse.ArgumentTypeError(f"expected a whole number of days, got {text!r}") from exc
        if value < minimum:
            raise argparse.ArgumentTypeError(f"expected at least {minimum}, got {value}")
        return value
    return convert


positive_int = _int_at_least(1)
non_negative_int = _int_at_least(0)


def _add_vocab_flags(parser):
    # Static help text on purpose: building the parser must never read vocab.json.
    parser.add_argument("--vocab", default=None,
                        help="alternative vocab JSON (default: the packaged pcos_tools/vocab.json)")
    parser.add_argument("--stale-days", type=positive_int, default=None,
                        help="Stale-Triage age in days, 1 or more; overrides stale_days from the vocab file "
                             "(packaged file: pcos_tools/vocab.json)")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="python -m pcos_tools",
        description="Draft-only helpers for the PCOS worklist. Inputs are never modified.",
    )
    parser.add_argument("--version", action="version", version=f"pcos_tools {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)

    hygiene = commands.add_parser(
        "hygiene", help="check a Worklist CSV; write proposed_changes.csv and hygiene_report.md")
    hygiene.add_argument("worklist", help="path to the Worklist CSV export")
    hygiene.add_argument("--out-dir", default=".", help="directory for the two output files (default: current)")
    hygiene.add_argument("--today", type=iso_date, default=None, help="reference date YYYY-MM-DD (default: today)")
    hygiene.add_argument("--aged-days", type=non_negative_int, default=DEFAULT_AGED_DAYS,
                         help=f"Waiting/Blocked age threshold in days (default {DEFAULT_AGED_DAYS})")
    _add_vocab_flags(hygiene)
    hygiene.add_argument("--dup-threshold", type=float, default=0.8,
                         help="title token overlap that counts as duplicate (default 0.8)")
    hygiene.add_argument("--skip-closed", action="store_true",
                         help="do not flag empty Sources/Confidence on Done, Expired, Superseded, Archived-Auto rows")
    hygiene.add_argument("--pandas", action="store_true", help="read the CSV with pandas (optional dependency)")
    hygiene.set_defaults(func=hygiene_command)

    recon = commands.add_parser("recon_parse", aliases=["recon-parse"], help="parse a RECON markdown into JSON")
    recon.add_argument("recon", help="path to the RECON markdown")
    recon.add_argument("--out", default=None,
                       help="output JSON path (default: RECON path with .json; '-' for stdout)")
    recon.add_argument("--people", default=None, help="comma-separated known names to match with high confidence")
    recon.add_argument("--year", type=int, default=None,
                       help="year for dates written without one (default: first ISO date in the file, else this year)")
    recon.set_defaults(func=recon_parse_command)

    now = commands.add_parser("now_build", aliases=["now-build"],
                              help="write PCOS_NOW_draft.md from CSV + RECON + previous PCOS_NOW")
    now.add_argument("--csv", required=True, help="Worklist CSV")
    now.add_argument("--recon", required=True, help="RECON JSON from recon_parse (a RECON .md is parsed on the fly)")
    now.add_argument("--prev", required=True, help="previous PCOS_NOW markdown")
    now.add_argument("--out-dir", default=".", help="directory for PCOS_NOW_draft.md (default: current)")
    now.add_argument("--today", type=iso_date, default=None, help="reference date YYYY-MM-DD (default: today)")
    now.add_argument("--aged-days", type=non_negative_int, default=DEFAULT_AGED_DAYS,
                     help=f"days before a waiting item gets the [AGED] mark (default {DEFAULT_AGED_DAYS})")
    _add_vocab_flags(now)
    now.add_argument("--people", default=None, help="comma-separated known names (only used when --recon is a .md)")
    now.add_argument("--pandas", action="store_true", help="read the CSV with pandas (optional dependency)")
    now.set_defaults(func=now_build_command)
    return parser


def configure_streams():
    """Never crash on non-ASCII output: UTF-8 when piped, escaped when on a console."""
    for stream in (sys.stdout, sys.stderr):
        if not hasattr(stream, "reconfigure"):
            continue
        try:
            if stream.isatty():
                stream.reconfigure(errors="backslashreplace")
            else:
                stream.reconfigure(encoding="utf-8", errors="backslashreplace")
        except (ValueError, OSError):  # pragma: no cover - exotic streams
            pass


def main(argv=None):
    configure_streams()
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args) or 0)
    except UnicodeDecodeError as exc:
        print(f"error: an input file is not UTF-8 text ({exc.reason} at byte {exc.start}); "
              "re-save it as UTF-8", file=sys.stderr)
        return 1
    except (WorklistError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
