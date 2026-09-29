# Official integration boundaries

This skill intentionally follows documented Cultured Code interfaces.

## Things URL Scheme

https://culturedcode.com/things/support/articles/2803573/

Used for:
- `add`
- `show`
- `search`

The documented URL Scheme requires an authorization token for commands that modify existing Things data. This project does not implement those URL update commands and does not store/request the token.

## Things AppleScript

https://culturedcode.com/things/support/articles/4562654/

Used for:
- Reading `to dos` from a built-in list, Project, or Area.
- Setting one exact matched to-do's status to `completed`.

## Agent Skill hosts

Hermes creating skills:
https://hermes-agent.nousresearch.com/docs/developer-guide/creating-skills

Hermes external skill directories:
https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/skills.md

DeepSeek Harness filesystem skills:
https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/skill/skill-filesystem/README.md
