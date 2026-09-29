# Threat Model

## Assets to protect

- Things 3 task data.
- Integrity of the Things database.
- macOS permissions granted to the host Agent.
- User privacy when an Agent uses a remote/cloud model.

## Trust boundaries

1. **Host Agent → local wrapper**
   - The Agent chooses commands and arguments.
   - The wrapper allow-lists operations and rejects unsupported source types/list IDs.

2. **Local wrapper → Things URL Scheme**
   - Used only for create/show/search.
   - Existing-item URL update operations requiring an auth token are not implemented.

3. **Local wrapper → Apple Events / Things AppleScript**
   - Used for read and exact completion.
   - User-controlled values are passed as `osascript` argv, not interpolated into AppleScript source.

4. **Agent context → model provider**
   - Task data returned by the wrapper may enter the Agent/model context.
   - This is outside the wrapper's network boundary and must be managed by host configuration and data minimization.

## Key abuse cases and mitigations

### Accidental destructive mutation
Mitigation: no delete, trash, restore, backup replacement, bulk mutation, or direct DB writes exist in the CLI.

### Completing the wrong task
Mitigation: completion requires an exact title match within an explicitly selected source and fails when zero or multiple matches exist.

### AppleScript injection
Mitigation: source/project/title values are supplied to `osascript` as argv; they are not concatenated into executable AppleScript source.

### Arbitrary local command execution
Mitigation: the Skill instructs hosts to invoke only the bundled wrapper and not arbitrary `osascript` commands. The wrapper itself does not use `shell=True`, `eval`, or `exec`.

### Excessive data disclosure
Mitigation: workflows should scope reads to a dedicated Project, such as `🎮 Reality RPG`, rather than global Today/Inbox unless explicitly requested.

### Database corruption
Mitigation: no SQLite or direct Things database path is used anywhere in the implementation.
