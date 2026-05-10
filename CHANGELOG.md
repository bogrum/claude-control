# Changelog

All notable changes to claude-control are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] — 2026-05-10

### Added
- **Rich preview pane** — click any skill card name to open a rendered markdown preview with headings, code blocks, tables, and a file listing
- `GET /api/{kind}/{name}/preview` endpoint
- Markdown rendering via marked.js + DOMPurify (sanitized, no script execution)
- Esc-to-close on all modals

## [1.0.0] — 2026-05-10

### Added
- Local FastAPI dashboard for managing `~/.claude/` skills, plugins, agents, commands
- Toggle skills on / name-only / off (writes to `settings.local.json`)
- Inline edit modal for SKILL.md (frontmatter + body)
- Tag sidebar with click-to-filter
- Bulk import from marketplace repos (e.g. `anthropics/skills`)
- SKILL.md validator (frontmatter required-field + naming checks)
- Stats bar (per-kind counts and sizes)
- ZIP upload with Zip Slip protection
- `git clone` support with strict URL validation
- Cross-platform desktop installers
  - Linux: `install.sh` → `.desktop` entry + GNOME app database
  - macOS: `install-macos.sh` → `.app` bundle in `~/Applications/`
  - Windows: `install.ps1` → Start Menu shortcut
- Cross-platform launcher (`launcher.py`) with PID/port file management and idempotent re-launch
- Optional `pywebview` integration for native-window mode
- 19 pytest tests covering scan, toggle, edit, validate, delete, upload, and security paths
- GitHub Actions CI matrix on Python 3.10 / 3.11 / 3.12
- Pre-push secret scanner (`scripts/preflight.sh`)
- systemd unit for always-on home-server use

### Security
- Loopback-only bind by default (127.0.0.1)
- Path traversal blocked via `Path.resolve()` containment checks
- Zip Slip blocked at upload time
- No `shell=True` anywhere; subprocess calls use fixed argument lists
- 180-second timeout on all subprocess calls
- `git clone` URL validated against strict regex

[1.0.0]: https://github.com/YOUR_USER/claude-control/releases/tag/v1.0.0
