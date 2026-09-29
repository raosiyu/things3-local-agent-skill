# Compatibility

## Hermes Agent

Status: **format-compatible; live Things integration requires target-Mac verification**.

Hermes recognizes `SKILL.md` bundles and replaces `${HERMES_SKILL_DIR}` with the loaded skill directory. This skill uses that feature only as a Hermes convenience; the underlying Python wrapper has no Hermes dependency.

## DeepSeek Harness (DSH)

Status: **filesystem-skill compatible; live Things integration requires target-Mac verification**.

DSH's filesystem skill provider accepts `<name>/SKILL.md` bundles. Required frontmatter fields are `name` and `description`; this skill satisfies them. DSH scans project/user skill roots including `.dsh/skills` and `.agents/skills`.

The DSH runtime does not need `${HERMES_SKILL_DIR}`. It should resolve `scripts/things3.py` relative to the loaded `SKILL.md` path supplied by its skill loader.

## Shared installation

A shared copy under `~/.agents/skills/things3-local` can be discovered by DSH by default. Hermes can also discover it when `~/.agents/skills` is configured in `skills.external_dirs`.

## Things 3

Status: uses the documented Things URL Scheme and AppleScript interfaces only.

No direct database access is implemented.
