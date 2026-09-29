# Changelog

## 0.2.0 - 2026-09-29

- Generalized the project from a Hermes-only skill to an Agent Skill compatible with Hermes and DSH filesystem skills.
- Added shared-install guidance for `~/.agents/skills`.
- Kept the core wrapper host-independent.
- Added `--version`.
- Added security policy, threat model, compatibility notes, tests, and public-release guidance.
- Preserved the narrow capability boundary: no direct Things database access, delete, backup, restore, export, network client, or stored auth token.

## 0.1.1

- Hardened URL percent encoding.
- Documented Hermes skill-directory resolution.
- Scoped Reality RPG reads to its dedicated Project by default.
