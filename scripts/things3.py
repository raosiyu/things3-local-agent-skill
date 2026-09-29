#!/usr/bin/env python3
"""Safety-scoped Things 3 bridge for Agent Skills on macOS.

Supported hosts include Hermes Agent, DeepSeek Harness (DSH), and other
Agent Skills-compatible runtimes that can invoke a local CLI.

Security boundary:
- Create/show/search via Cultured Code's documented Things URL Scheme.
- Read/complete via Cultured Code's documented AppleScript interface.
- No direct Things database access.
- No delete/trash/backup/restore/export operations.
- No network client code or third-party Python dependencies.
- No Things auth-token storage.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from urllib.parse import quote, urlencode

VERSION = "0.2.0"

BUILTIN_SHOW_IDS = {
    "inbox",
    "today",
    "anytime",
    "upcoming",
    "someday",
    "logbook",
    "tomorrow",
    "deadlines",
    "repeating",
    "all-projects",
    "logged-projects",
}

READ_SCRIPT = r'''
on replaceText(findText, replaceWith, sourceText)
    set AppleScript's text item delimiters to findText
    set parts to text items of sourceText
    set AppleScript's text item delimiters to replaceWith
    set sourceText to parts as text
    set AppleScript's text item delimiters to ""
    return sourceText
end replaceText

on cleanTitle(v)
    set s to v as text
    set s to my replaceText(return, " ", s)
    set s to my replaceText(linefeed, " ", s)
    return s
end cleanTitle

on run argv
    set sourceKind to item 1 of argv
    set sourceName to item 2 of argv

    tell application "Things3"
        if sourceKind is "list" then
            set itemsFound to to dos of list sourceName
        else if sourceKind is "project" then
            set itemsFound to to dos of project sourceName
        else if sourceKind is "area" then
            set itemsFound to to dos of area sourceName
        else
            error "Unsupported source kind: " & sourceKind number 64
        end if

        set outputText to ""
        repeat with t in itemsFound
            set outputText to outputText & my cleanTitle(name of t) & linefeed
        end repeat
        return outputText
    end tell
end run
'''

COMPLETE_SCRIPT = r'''
on run argv
    set sourceKind to item 1 of argv
    set sourceName to item 2 of argv
    set targetTitle to item 3 of argv

    tell application "Things3"
        if sourceKind is "list" then
            set itemsFound to to dos of list sourceName
        else if sourceKind is "project" then
            set itemsFound to to dos of project sourceName
        else if sourceKind is "area" then
            set itemsFound to to dos of area sourceName
        else
            error "Unsupported source kind: " & sourceKind number 64
        end if

        set matchCount to 0
        set matchedItem to missing value
        repeat with t in itemsFound
            if (name of t as text) is targetTitle then
                set matchCount to matchCount + 1
                set matchedItem to t
            end if
        end repeat

        if matchCount is 0 then
            return "NOT_FOUND"
        else if matchCount is greater than 1 then
            return "AMBIGUOUS:" & (matchCount as text)
        else
            set status of matchedItem to completed
            return "COMPLETED:" & targetTitle
        end if
    end tell
end run
'''

VERSION_SCRIPT = r'''
tell application "Things3"
    return version
end tell
'''


class ThingsError(RuntimeError):
    """Expected operational failure."""


def require_macos() -> None:
    if sys.platform != "darwin":
        raise ThingsError("Live Things operations require macOS.")


def run_process(cmd: list[str], *, input_text: str | None = None) -> str:
    proc = subprocess.run(
        cmd,
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()
        raise ThingsError(detail or f"Command failed: {cmd[0]}")
    return proc.stdout.strip()


def run_osascript(script_text: str, args: list[str] | None = None) -> str:
    require_macos()
    if not shutil.which("osascript"):
        raise ThingsError("osascript was not found.")
    cmd = ["osascript", "-"]
    if args:
        cmd.extend(args)
    return run_process(cmd, input_text=script_text)


def open_things_url(url: str, dry_run: bool = False) -> str:
    if dry_run:
        return url
    require_macos()
    if not shutil.which("open"):
        raise ThingsError("macOS 'open' command was not found.")
    run_process(["open", url])
    return "OK"


def build_url(command: str, params: dict[str, str | bool]) -> str:
    encoded = urlencode(
        {
            key: ("true" if value is True else "false" if value is False else value)
            for key, value in params.items()
        },
        quote_via=quote,
    )
    return f"things:///{command}" + (f"?{encoded}" if encoded else "")


def cmd_doctor(_: argparse.Namespace) -> int:
    result = {
        "version": VERSION,
        "platform": sys.platform,
        "macos": sys.platform == "darwin",
        "osascript": bool(shutil.which("osascript")),
        "open": bool(shutil.which("open")),
        "things_version": None,
        "live_check": "not_run",
    }
    if sys.platform == "darwin" and shutil.which("osascript"):
        try:
            result["things_version"] = run_osascript(VERSION_SCRIPT)
            result["live_check"] = "pass"
        except ThingsError as exc:
            result["live_check"] = "fail"
            result["error"] = str(exc)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["live_check"] in {"pass", "not_run"} else 2


def cmd_read(args: argparse.Namespace) -> int:
    out = run_osascript(READ_SCRIPT, [args.source, args.name])
    titles = [line for line in out.splitlines() if line.strip()]
    payload = {
        "source": args.source,
        "name": args.name,
        "count": len(titles),
        "titles": titles,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("\n".join(titles))
    return 0


def validate_text(label: str, value: str | None, max_len: int) -> None:
    if value is not None and len(value) > max_len:
        raise ThingsError(
            f"{label} exceeds Things' documented limit of {max_len} characters."
        )


def cmd_add(args: argparse.Namespace) -> int:
    validate_text("title", args.title, 4000)
    validate_text("notes", args.notes, 10000)
    params: dict[str, str | bool] = {"title": args.title}
    for key in ("notes", "when", "deadline", "tags", "list", "heading"):
        value = getattr(args, key)
        if value is not None:
            params[key] = value
    if args.reveal:
        params["reveal"] = True
    print(open_things_url(build_url("add", params), args.dry_run))
    return 0


def cmd_complete(args: argparse.Namespace) -> int:
    out = run_osascript(COMPLETE_SCRIPT, [args.source, args.name, args.title])
    print(out)
    if out.startswith("COMPLETED:"):
        return 0
    if out == "NOT_FOUND":
        return 3
    if out.startswith("AMBIGUOUS:"):
        return 4
    return 2


def cmd_show(args: argparse.Namespace) -> int:
    show_id = args.list_id.lower()
    if show_id not in BUILTIN_SHOW_IDS:
        raise ThingsError(
            f"Unsupported built-in list id '{args.list_id}'. Allowed: "
            f"{', '.join(sorted(BUILTIN_SHOW_IDS))}"
        )
    print(open_things_url(build_url("show", {"id": show_id}), args.dry_run))
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    validate_text("query", args.query, 4000)
    print(open_things_url(build_url("search", {"query": args.query}), args.dry_run))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="things3.py",
        description="Safety-scoped Things 3 bridge for Agent Skills.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    sub = parser.add_subparsers(dest="command", required=True)

    doctor = sub.add_parser(
        "doctor", help="Check local prerequisites and Things availability."
    )
    doctor.set_defaults(func=cmd_doctor)

    read = sub.add_parser("read", help="Read to-do titles from a Things source.")
    read.add_argument("--source", choices=("list", "project", "area"), required=True)
    read.add_argument("--name", required=True, help="Visible list/project/area name.")
    read.add_argument("--json", action="store_true")
    read.set_defaults(func=cmd_read)

    add = sub.add_parser("add", help="Create a new to-do via Things URL Scheme.")
    add.add_argument("--title", required=True)
    add.add_argument("--notes")
    add.add_argument("--when")
    add.add_argument("--deadline")
    add.add_argument("--tags")
    add.add_argument("--list")
    add.add_argument("--heading")
    add.add_argument("--reveal", action="store_true")
    add.add_argument(
        "--dry-run", action="store_true", help="Print URL without opening Things."
    )
    add.set_defaults(func=cmd_add)

    complete = sub.add_parser(
        "complete",
        help="Complete exactly one exact-title match in a list/project/area.",
    )
    complete.add_argument(
        "--source", choices=("list", "project", "area"), required=True
    )
    complete.add_argument("--name", required=True)
    complete.add_argument("--title", required=True)
    complete.set_defaults(func=cmd_complete)

    show = sub.add_parser("show", help="Open a supported built-in Things list.")
    show.add_argument("list_id")
    show.add_argument("--dry-run", action="store_true")
    show.set_defaults(func=cmd_show)

    search = sub.add_parser("search", help="Open Things search.")
    search.add_argument("query")
    search.add_argument("--dry-run", action="store_true")
    search.set_defaults(func=cmd_search)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        return args.func(args)
    except ThingsError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
