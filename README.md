# Spooky Labs skills

The know-how a Spooky Labs agent picks up, published as one
[Agent Plugins](https://agent-plugins.org) package. This repository is the
single source of truth for what an agent is told: the platform points every
agent at a commit of it, the website and the docs link here, and nothing in
it is secret.

```
plugin.json                 the package manifest (Agent Plugins 1.0.0)
skills/<name>/SKILL.md      one Agent Skill per directory
```

- `workspace` — working with files and running shell commands inside the
  agent's own sandbox.
- `trading` — trading the agent's own brokerage account within the
  brokerage's rules.

## How the platform uses it

An agent runs on [kagent](https://kagent.dev) 1.x, whose AgentTemplate
attaches this package with `spec.plugins`:

```yaml
plugins:
  - source:
      git:
        url: https://github.com/Spooky-Labs/skills
        commit: <full commit id>
    skills:
      - workspace
```

Every source is immutable: the platform pins the **full commit id** of
`main` that its catalog last read, and the agent's sandbox fetches that
commit when the agent starts. Publishing a change is therefore two steps
that happen on their own:

1. A pull request merges here.
2. The platform's catalog re-reads `main` within ten minutes. Agents created
   after that carry the new commit; agents already running keep the content
   they started with, until they are re-saved.

The skill directories are what `plugins[].skills` selects by name, and the
`name` in each `SKILL.md` front matter must equal its directory name
([Agent Skills specification](https://agentskills.io/specification)). The
`check` workflow refuses a pull request that breaks either rule, so a
mistake never becomes a skill the runtime silently skips.

## Writing a skill

A skill is a directory under `skills/` holding a `SKILL.md` with YAML
front matter (`name`, `description`) and the instructions the agent follows
once it has chosen the skill by that description. Scripts and reference
files go beside it; the agent's sandbox is Alpine Linux with `bash` and
`git`, without Python, and it reaches only the hosts the platform allows, so
a skill must not depend on fetching the internet.
