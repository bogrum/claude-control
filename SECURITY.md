# Security

## Threat model

claude-control is a **local-only** tool. The threat model assumes:

- **Trusted user.** The user running the server is the same person using the browser.
- **Untrusted everything else.** No other process, no other person on the network, no external service.

If those assumptions hold, claude-control is safe to run. If they don't, see "What you must NOT do" below.

---

## Default protections

| Risk                         | Mitigation                                                              |
|------------------------------|-------------------------------------------------------------------------|
| Network-exposed by accident  | Binds to `127.0.0.1` by default; warning printed if you override        |
| Path traversal via filename  | All paths resolved with `Path.resolve()` and checked against base dir   |
| Zip Slip on uploads          | Each ZIP entry is resolved before extraction; unsafe paths rejected     |
| Arbitrary command injection  | No `shell=True` anywhere; `git clone` uses fixed-arg list + URL regex   |
| Long-running git commands    | 120 s timeout                                                           |
| Settings file corruption     | JSON parsed with `try/except`; falls back to `{}` on parse failure      |

## What you must NOT do

1. **Do not bind to `0.0.0.0` or your LAN IP** without putting an authenticated reverse proxy in front.
2. **Do not run claude-control as `root`.** Run as your normal user; the only files it should ever touch are inside `$CLAUDE_HOME`.
3. **Do not commit your `~/.claude/` contents** to a public repo via this tool. The "delete" button removes from disk; it does not push anywhere — but be aware that some skills may contain hard-coded secrets you wrote yourself.
4. **Do not install untrusted skills.** Skills can contain executable code that Claude Code will run. Inspect any third-party skill before enabling it. The same applies here: this dashboard helps you manage skills, but it can't tell you whether a skill is malicious.

---

## Pre-publication checklist (before pushing to GitHub)

If you fork or contribute, run through this list before `git push`:

### Files

- [ ] No `.env`, `settings.local.json`, or `.claude/` directory committed (verify with `git status`)
- [ ] `.gitignore` includes the patterns in this repo's `.gitignore`
- [ ] No API keys, tokens, or passwords in commit history (`git log -p | grep -iE 'api[_-]?key|secret|token|password'`)
- [ ] No personal hostnames, internal IPs, or company-internal paths in code or docs
- [ ] No real client/patient data in any test fixture
- [ ] `LICENSE` file present

### Code

- [ ] All `subprocess` calls use a list, never a string with `shell=True`
- [ ] All file path inputs run through `_safe_join()` before use
- [ ] No `eval()`, `exec()`, or `pickle.load()` on user input
- [ ] CORS is not enabled (this is a localhost app)

### Repository settings (GitHub)

- [ ] Enable **Secret scanning** (Settings → Code security)
- [ ] Enable **Push protection** to block pushes that contain secrets
- [ ] Enable **Dependabot alerts** for the Python deps
- [ ] Add a `SECURITY.md` (this file) so reporters know how to reach you

---

## Reporting a vulnerability

Please open a [GitHub Security Advisory](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability) on this repo rather than a public issue. If that's not available, email the maintainer listed in `pyproject.toml` / `package.json`.

We aim to respond within 7 days.
