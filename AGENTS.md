# AGENTS.md

## Project purpose

Maintain a small, auditable Agent Skill that gives local macOS agents narrowly scoped Things 3 access through documented Cultured Code interfaces.

## Non-negotiable security constraints

- Never add direct SQLite/Things database access.
- Never add delete/trash, backup, restore, database replacement, or full export operations without an explicit major-version security review.
- Never store or log a Things URL Scheme auth token.
- Do not add network telemetry or task-data upload.
- Do not request Accessibility, Full Disk Access, or sudo for normal operation.
- Pass user data to AppleScript via argv; do not interpolate it into executable AppleScript source.
- Keep state-changing operations exact, scoped, and fail-closed.

## Development workflow

1. Read `README.md`, `SECURITY.md`, and `docs/THREAT-MODEL.md`.
2. Plan the smallest change.
3. Run `python3 -m unittest discover -s tests -v`.
4. Run the static secret/security checks described in `SECURITY.md`.
5. Review `git diff` before commit.
6. One coherent work package per commit.
7. Before a public release, perform the public release security gate in `SECURITY.md`.

## Compatibility

Preserve plain Agent Skills `SKILL.md` compatibility for Hermes and DSH. Avoid host-specific dependencies in `scripts/things3.py`.
