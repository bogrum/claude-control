# Architecture

claude-control is intentionally small. The whole app fits in five core files plus tests.

## Files

```
app/
├── main.py            ~440 lines · all routes + filesystem helpers in one file
├── templates/
│   └── index.html     single page, ~110 lines
└── static/
    ├── style.css      ~490 lines · editorial dark theme
    └── app.js         ~340 lines · vanilla JS, no framework

tests/
├── conftest.py        path fixup
└── test_main.py       19 tests, runs in ~1s

launcher.py            background server lifecycle (start/stop/reuse)
install.sh             registers .desktop entry + icon
scripts/preflight.sh   pre-push secret scanner
```

## Request flow

```
Browser (localhost:8765)
        │
        │  GET /                     → renders index.html (Jinja2)
        │  GET /api/health           → {"ok": true, ...}
        │  GET /api/assets           → all skills/plugins/agents/commands
        │  GET /api/stats            → counts, sizes, all_tags
        │  POST /api/skills/{n}/state → writes settings.local.json
        │  GET /api/{k}/{n}/file     → frontmatter + body
        │  PUT /api/{k}/{n}/file     → atomic write
        │  GET /api/{k}/{n}/validate → lint issues
        │  DELETE /api/{k}/{n}       → rm -rf
        │  POST /api/{k}/upload      → unzip safely
        │  POST /api/{k}/clone       → git clone --depth 1
        │  POST /api/{k}/bulk-import → clone + copy each subfolder
        ▼
~/.claude/
├── skills/
├── plugins/
├── agents/
├── commands/
└── settings.local.json   ← skillOverrides written here
```

## What it doesn't do

- Run skills (use Claude Code's `/skills` for that)
- Authenticate users (binds to loopback only)
- Watch the filesystem (UI re-fetches `/api/assets` on every action)
- Cache anything (each request hits disk; the dirs are small)
- Manage plugin enable/disable (use `/plugin` in Claude Code; this app shows them read-only)

## Why FastAPI + vanilla JS?

- **No build step.** Clone, install, run.
- **Small dep tree.** 5 deps total, easy to audit.
- **Self-explanatory routes.** Each route maps directly to a file operation.
- **Easy to fork.** Anyone with basic Python can read all of `main.py` in under ten minutes.

## Module-level globals & testability

`CLAUDE_HOME` and `SETTINGS_FILE` are read at import time from environment variables, but the helper functions access them via `sys.modules[__name__]` indirection. This means tests can `monkeypatch.setattr(main, "CLAUDE_HOME", tmp_path)` and the routes will pick it up without needing a reimport.

## Extending

Common extension points and where to touch them:

| Add this | Where |
|---|---|
| A new asset kind | `ASSET_KINDS` dict in `main.py` + tab in `index.html` |
| A new toggle for plugins | New POST route + corresponding button in `app.js` |
| Tag autocomplete | Pull from `/api/stats` `all_tags` into a `<datalist>` |
| Diff view | New GET route running `git diff` inside the asset folder |
| Markdown preview | Add `marked.js` + a preview pane to the edit modal |

## Test strategy

- **Unit-level**: each route hit through FastAPI's `TestClient` against a `tmp_path` claude home.
- **No filesystem mocks** — tests work on real temp dirs, which is fast enough (whole suite < 1s) and catches real bugs (path resolution, atomic writes, zip extraction).
- **Security tests**: zip slip, path traversal, URL validation each have explicit cases.
- **Frontmatter roundtrip**: write → read → assert preserved.
