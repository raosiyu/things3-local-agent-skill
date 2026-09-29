# Security Policy

## Design boundary

This project deliberately exposes a small Things 3 capability surface.

Allowed operations:
- Read to-do titles from one explicitly selected list, Project, or Area.
- Create a to-do via the official Things URL Scheme.
- Show an allow-listed built-in list.
- Open Things search.
- Complete exactly one uniquely matched to-do via AppleScript.

Out of scope and intentionally absent:
- SQLite or other direct Things database access.
- Delete / trash operations.
- Backup / restore / database replacement.
- Full-data export.
- Bulk mutation.
- Stored Things URL Scheme authorization tokens.
- Network telemetry or task-data upload by this code.

## macOS permissions

The expected live permission is Automation / Apple Events permission for the process that invokes `osascript` to control Things 3.

Do not grant Accessibility, Full Disk Access, or sudo merely for this skill. If a future version starts requiring one of those, treat that as a security-significant change and review it before upgrading.

## Agent privacy

The local wrapper contains no network client code. However, the host Agent may send tool output or task content to its configured model provider. Limit the scope of reads (for example, use a dedicated `🎮 Reality RPG` Project) and avoid exposing sensitive Things content unnecessarily.

## Reporting

For a public repository, report security issues through GitHub's private vulnerability reporting if enabled. Otherwise open a minimal issue that does not include private task data, credentials, or exploit details.

## Release gate

Before making a release public:

1. Review the current tree and Git history for secrets/private data.
2. Confirm there are no screenshots, logs, databases, runtime data, or task exports.
3. Run the unit tests.
4. Run a secret-pattern scan.
5. Review dependency surface (currently Python standard library only).
6. Confirm no delete/backup/restore/export/database-write capability has been added.
7. Confirm README and security docs match actual behavior.
