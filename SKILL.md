---
name: things3-local
description: Safely read and manage Things 3 on macOS through Cultured Code's official URL Scheme and AppleScript interfaces. Designed for Hermes Agent, DeepSeek Harness (DSH), and compatible Agent Skills runtimes; no direct database access, deletion, backup/restore, export, or stored auth token.
version: 0.2.0
license: MIT
platforms: [macos]
metadata:
  hermes:
    tags: [things3, productivity, todo, macos, automation]
    category: productivity
    requires_toolsets: [terminal]
---

# Things 3 Local

Use this skill when the user asks to inspect, create, show, search, or complete Things 3 tasks on the local Mac.

## Host compatibility

This bundle is intended to work with:

- Hermes Agent.
- DeepSeek Harness (DSH) filesystem skills.
- Other Agent Skills-compatible hosts that expose a local terminal/shell tool.

### Resolve the bundled CLI safely

Do **not** assume the current working directory is the skill directory.

- **Hermes:** when `${HERMES_SKILL_DIR}` has been expanded by Hermes, use:
  `python3 ${HERMES_SKILL_DIR}/scripts/things3.py ...`
- **DSH / other Agent Skills hosts:** use the absolute directory of this loaded `SKILL.md` supplied by the host's skill loader, append `/scripts/things3.py`, and invoke that exact file.
- Never search arbitrary user directories for another `things3.py` and never execute a similarly named script outside this skill bundle.

## Safety contract

Allowed:
- Read to-do titles from one explicitly selected Things built-in list, Project, or Area.
- Create a new to-do through Things' official URL Scheme.
- Show an allow-listed Things built-in list.
- Open Things search.
- Mark one exact, uniquely matched to-do as completed.

Not allowed:
- Delete to-dos, projects, areas, tags, or trash.
- Directly read or write the Things SQLite database.
- Backup, restore, replace, or export the Things database.
- Store or request a Things URL Scheme `auth-token`.
- Execute arbitrary AppleScript supplied by the user.
- Bulk-complete ambiguous task names.
- Grant Full Disk Access, Accessibility, or sudo privileges for this skill.

Use only the bundled `scripts/things3.py` wrapper. Do not bypass it with ad-hoc `osascript`, database queries, or destructive Things commands.

## First-use check

Run the bundled CLI with:

```bash
python3 <SKILL_DIR>/scripts/things3.py doctor
```

For Hermes, `<SKILL_DIR>` is `${HERMES_SKILL_DIR}` after template substitution. For DSH, resolve `<SKILL_DIR>` from the loaded skill file location.

On first AppleScript read/write, macOS may ask whether the process running the agent/terminal may control Things. This is an Automation / Apple Events permission. Do not request Accessibility or Full Disk Access.

## Read tasks

For Reality RPG, default to its dedicated Project only:

```bash
python3 <SKILL_DIR>/scripts/things3.py read \
  --source project \
  --name "🎮 Reality RPG" \
  --json
```

Only read a built-in list, another Project, or an Area when the user explicitly requests it.

Built-in list names used through AppleScript must match the language visible in Things, so a dedicated Project is safer for automation than a localized built-in list name.

## Create a task

```bash
python3 <SKILL_DIR>/scripts/things3.py add \
  --title "🎯 今日主线：推进当前项目" \
  --when "today@10:30" \
  --list "🎮 Reality RPG" \
  --heading "DAILY BASE"
```

Optional flags: `--notes`, `--when`, `--deadline`, `--tags`, `--list`, `--heading`, `--reveal`, `--dry-run`.

Prefer ISO dates (`YYYY-MM-DD`) or Things keywords such as `today` and `tomorrow`. Natural-language dates in Things URLs are interpreted in English.

Before creating a recurring/daily task, read the target Project first and avoid duplicates.

## Complete a task

```bash
python3 <SKILL_DIR>/scripts/things3.py complete \
  --source project \
  --name "🎮 Reality RPG" \
  --title "💪 运动 / 快走"
```

Completion succeeds only when exactly one item has that exact title. On `NOT_FOUND` or `AMBIGUOUS`, do not guess.

Never mark a task completed merely because it seems likely to be done. Complete it only after the user explicitly confirms completion or a deterministic workflow result proves it.

## Show / Search

```bash
python3 <SKILL_DIR>/scripts/things3.py show today
python3 <SKILL_DIR>/scripts/things3.py search "Reality RPG"
```

## Reality RPG policy

1. Things is the task source of truth.
2. Prefer one Project named `🎮 Reality RPG`.
3. Use headings inside that Project: `DAILY BASE`, `MAIN QUEST`, `SIDE QUEST`, `WEEKLY BOSS`, `ACHIEVEMENTS`.
4. Daily mandatory items remain at three: `🎯 今日主线`, `💪 运动 / 快走`, `📝 日终复盘`.
5. Read before creating to avoid duplicates.
6. Scheduling notifications belongs to the host agent's scheduler/automation layer, not this skill.
7. Do not broaden permissions for convenience.
8. Default to reading only the `🎮 Reality RPG` Project. Access unrelated Things data only when the user explicitly asks.

## Verification

After a create:
1. Re-read the target Project.
2. Confirm the new title appears exactly once.

After completion:
1. Require a `COMPLETED:` result.
2. Re-read the source and verify the expected state.

For any state-changing operation, report what changed in one concise sentence.
