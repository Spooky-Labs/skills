---
name: workspace
description: Work with files and run shell commands inside your own sandbox — reading, writing and editing files in your session directory, and running bash there.
---

# Workspace

You run inside your own sandbox, and this skill is how you use it. Load it
whenever a task calls for producing files, examining data, or running a
command.

## Tools

- `read_file(file_path, offset?, limit?)` — read a file from your session
  directory or from the read-only `/skills` directory. Long files paginate
  with `offset` and `limit` (lines).
- `write_file(file_path, content)` — write (overwrite) a file in your session
  directory, creating parent directories as needed. Writes are confined to
  your session directory; `/skills` is read-only.
- `edit_file(file_path, old_string, new_string, replace_all?)` — exact string
  replacement. Read the file first; the edit fails if `old_string` is not
  unique unless `replace_all` is true.
- `bash(command)` — run a shell command in your session directory. This is
  where commands run: your own sandbox, the same place your files live, so a
  file you wrote is there for the command and a file the command wrote is
  there for `read_file`. A command times out after 30 seconds, so split long
  work into steps and print what you want to see.
- `list_skills`, `load_skill`, `load_skill_resource` — the skills attached
  to you, their instructions, and the files a skill ships.

## What the sandbox is

- The image is Alpine Linux with `bash`, `git` and the standard Alpine
  utilities. There is no Python. Prefer shell, `awk` and `sed`.
- The network is an allowlist, not the internet. Your sandbox reaches the
  model, your tool servers and the source this skill came from, and nothing
  else. A command that fetches an arbitrary URL is refused; do not build a
  step on it.
- Your session directory is `/tmp/kagent/<session-id>/`. Relative paths
  resolve there; prefer them. Put finished artifacts under `outputs/` so they
  are easy to find.
- The sandbox is snapshotted between turns, so files you wrote are there when
  you come back to the same session. They are not shared with other sessions,
  and anything the user must keep should be shown in your reply as well.
