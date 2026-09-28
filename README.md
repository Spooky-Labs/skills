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

- `trading` — trading the agent's own brokerage account within the
  brokerage's rules, and how the agent's sandbox works.

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
      - trading
```

Every source is immutable: the platform pins one **full commit id** of
this repository, bakes that commit into the agent runtime image, and its
catalog reads the same commit, so an agent's template declares exactly the
package its sandbox already holds and nothing is fetched when the agent
starts. Publishing a change is therefore two steps:

1. A pull request merges here.
2. The platform pins the new commit (`platform-api/runtime/kagent/skills.env`),
   which rebuilds the runtime image and rolls it out. Agents created after
   that carry the new commit; agents already running keep the content they
   started with.

The skill directories are what `plugins[].skills` selects by name, and the
`name` in each `SKILL.md` front matter must equal its directory name
([Agent Skills specification](https://agentskills.io/specification)). The
`check` workflow refuses a pull request that breaks either rule, so a
mistake never becomes a skill the runtime silently skips.

## Writing a skill

A skill is a directory under `skills/` holding a `SKILL.md` with YAML
front matter (`name`, `description`) and the instructions the agent follows
once it has chosen the skill by that description. Reference files go
beside it. The agent has file tools only: it reads, writes and edits files
in its session directory and reads a skill's files, and it has no shell, so
a skill must not ship scripts or depend on running commands or fetching the
internet.
