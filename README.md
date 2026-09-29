# Things 3 Local Agent Skill

A small, auditable macOS Agent Skill for safely working with **Things 3**.

It is designed for **Hermes Agent**, **DeepSeek Harness (DSH)**, and other Agent Skills-compatible runtimes that can call a local CLI.

## Why this exists

Many Things integrations read the app's SQLite database directly or expose broad MCP toolsets. This project intentionally takes the narrower route:

- **Create / show / search** → Cultured Code's official Things URL Scheme.
- **Read / complete** → Cultured Code's official AppleScript interface.
- **No direct Things database access.**
- **No delete / trash / backup / restore / export operations.**
- **No stored Things auth token.**
- **No network client code.**
- **No third-party Python dependencies.**

Official Things references:
- URL Scheme: https://culturedcode.com/things/support/articles/2803573/
- AppleScript commands: https://culturedcode.com/things/support/articles/4562654/

## Requirements

- macOS.
- Things 3 installed.
- Python 3.
- A host Agent with a local terminal/shell tool.

Live access is macOS-only. The test suite and URL dry-runs are cross-platform.

## Supported hosts

### Hermes Agent

Hermes supports directory-based skills with `SKILL.md` and exposes `${HERMES_SKILL_DIR}` when loading a skill.

Recommended install:

```bash
mkdir -p ~/.hermes/skills/productivity
cp -R things3-local ~/.hermes/skills/productivity/things3-local
```

### DeepSeek Harness (DSH)

DSH's filesystem skill provider supports `<name>/SKILL.md` bundles under scanned roots including:

- `<project>/.dsh/skills`
- `<project>/.agents/skills`
- `~/.dsh/skills`
- `~/.agents/skills`

Recommended install:

```bash
mkdir -p ~/.dsh/skills
cp -R things3-local ~/.dsh/skills/things3-local
```

### One shared install for Hermes + DSH

DSH scans `~/.agents/skills` by default. Hermes can also scan external skill directories when `~/.agents/skills` is added to `skills.external_dirs`.

```bash
mkdir -p ~/.agents/skills
cp -R things3-local ~/.agents/skills/things3-local
```

Then configure Hermes to include the shared directory:

```yaml
skills:
  external_dirs:
    - ~/.agents/skills
```

This lets both runtimes use one copy of the skill.

## First test

From the installed skill directory:

```bash
python3 scripts/things3.py --version
python3 scripts/things3.py doctor
python3 scripts/things3.py add --title "Things Skill Test" --when today --dry-run
```

The dry-run prints a `things:///add?...` URL and does not modify Things.

On the target Mac, the first AppleScript operation may trigger a macOS **Automation / Apple Events** permission prompt for the process controlling Things. This skill does not require Accessibility, Full Disk Access, or sudo.

## Reality RPG example

A safe structure is:

```text
Area: 个人成长            (optional)
└── Project: 🎮 Reality RPG
    ├── DAILY BASE
    ├── MAIN QUEST
    ├── SIDE QUEST
    ├── WEEKLY BOSS
    └── ACHIEVEMENTS
```

Read only that Project by default:

```bash
python3 scripts/things3.py read --source project --name "🎮 Reality RPG" --json
```

Create a task:

```bash
python3 scripts/things3.py add \
  --title "🎯 今日主线：推进当前项目" \
  --when "today@10:30" \
  --list "🎮 Reality RPG" \
  --heading "DAILY BASE"
```

Complete exactly one matching task:

```bash
python3 scripts/things3.py complete \
  --source project \
  --name "🎮 Reality RPG" \
  --title "💪 运动 / 快走"
```

## Security model

See [SECURITY.md](SECURITY.md) and [docs/THREAT-MODEL.md](docs/THREAT-MODEL.md).

The most important privacy caveat: **the skill itself sends no network requests, but an Agent using a cloud model may place task titles/content into the model context.** Keep sensitive Things content out of Agent-visible scopes unless you are comfortable sharing it with that model provider under its applicable privacy terms.

## Tests

No external dependencies are required:

```bash
python3 -m unittest discover -s tests -v
```

## Status

Version: **0.2.0**

Static tests and non-mutating dry-runs are included. A real macOS + Things 3 Apple Events integration test must be performed on the target machine before claiming full live compatibility.

## License

MIT. This project is independent and is not affiliated with or endorsed by Cultured Code, Hermes Agent, DeepSeek, or OpenAI.
