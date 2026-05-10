"""Tests for claude-control. Run: pytest"""
from __future__ import annotations

import io
import zipfile

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def claude_home(tmp_path, monkeypatch):
    """Point the app at a fresh tmp dir for the duration of the test."""
    home = tmp_path / "claude_home"
    home.mkdir()
    for sub in ("skills", "plugins", "agents", "commands"):
        (home / sub).mkdir()
    monkeypatch.setenv("CLAUDE_HOME", str(home))

    # Mutate the module's module-level constants in place.
    from app import main
    monkeypatch.setattr(main, "CLAUDE_HOME", home.resolve())
    monkeypatch.setattr(main, "SETTINGS_FILE", home.resolve() / "settings.local.json")
    return home


@pytest.fixture
def client(claude_home):
    from app.main import app
    return TestClient(app)


@pytest.fixture
def example_skill(claude_home):
    """Create a sample skill folder."""
    skill_dir = claude_home / "skills" / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: my-skill\n"
        "description: A test skill for the unit suite covering basic behavior.\n"
        "tags:\n"
        "  - testing\n"
        "  - bioinformatics\n"
        "---\n\n"
        "# Body\n\nThis is the skill body.\n"
    )
    return skill_dir


# --- Health & listing ------------------------------------------------------

def test_health(client, claude_home):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["claude_home"] == str(claude_home.resolve())


def test_list_assets_empty(client):
    r = client.get("/api/assets")
    assert r.status_code == 200
    body = r.json()
    assert body == {"skills": [], "plugins": [], "agents": [], "commands": []}


def test_list_assets_with_skill(client, example_skill):
    r = client.get("/api/assets")
    skills = r.json()["skills"]
    assert len(skills) == 1
    s = skills[0]
    assert s["name"] == "my-skill"
    assert "test skill" in s["description"]
    assert set(s["tags"]) == {"testing", "bioinformatics"}
    assert s["state"] == "on"
    assert s["editable"] is True


def test_stats(client, example_skill):
    r = client.get("/api/stats")
    body = r.json()
    assert body["skills"]["total"] == 1
    assert body["skills"]["enabled"] == 1
    assert "bioinformatics" in body["all_tags"]


# --- Toggle ----------------------------------------------------------------

def test_toggle_off_and_on(client, example_skill, claude_home):
    r = client.post("/api/skills/my-skill/state", data={"state": "off"})
    assert r.status_code == 200
    settings = (claude_home / "settings.local.json").read_text()
    assert "off" in settings

    # Toggle back on -> entry should disappear from overrides
    r = client.post("/api/skills/my-skill/state", data={"state": "on"})
    assert r.status_code == 200
    settings = (claude_home / "settings.local.json").read_text()
    assert "my-skill" not in settings


def test_toggle_invalid_state(client, example_skill):
    r = client.post("/api/skills/my-skill/state", data={"state": "garbage"})
    assert r.status_code == 400


# --- File read/write ------------------------------------------------------

def test_read_file(client, example_skill):
    r = client.get("/api/skills/my-skill/file")
    body = r.json()
    assert body["frontmatter"]["name"] == "my-skill"
    assert "skill body" in body["body"].lower()


def test_write_file_roundtrip(client, example_skill):
    edit = {
        "frontmatter": {
            "name": "my-skill",
            "description": "Updated description for the test skill, now slightly longer.",
            "tags": ["clinical"],
        },
        "body": "# Updated\n\nNew body content.\n",
    }
    r = client.put("/api/skills/my-skill/file", json=edit)
    assert r.status_code == 200

    # Read back
    r = client.get("/api/skills/my-skill/file")
    body = r.json()
    assert body["frontmatter"]["tags"] == ["clinical"]
    assert "Updated" in body["body"]


# --- Validation -----------------------------------------------------------

def test_validate_clean(client, example_skill):
    r = client.get("/api/skills/my-skill/validate")
    body = r.json()
    assert body["ok"] is True
    # No errors, may have folder-name info if the folder name matches name (it does)
    assert all(i["level"] != "error" for i in body["issues"])


def test_validate_missing_description(client, claude_home):
    skill_dir = claude_home / "skills" / "broken"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\nname: broken\n---\n\nbody"
    )
    r = client.get("/api/skills/broken/validate")
    body = r.json()
    assert body["ok"] is False
    assert any("description" in i["message"].lower() for i in body["issues"])


def test_validate_no_frontmatter(client, claude_home):
    skill_dir = claude_home / "skills" / "noformat"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("just text, no frontmatter")
    r = client.get("/api/skills/noformat/validate")
    body = r.json()
    assert body["ok"] is False


# --- Delete ---------------------------------------------------------------

def test_delete(client, example_skill, claude_home):
    r = client.delete("/api/skills/my-skill")
    assert r.status_code == 200
    assert not (claude_home / "skills" / "my-skill").exists()


def test_delete_path_traversal_blocked(client):
    r = client.delete("/api/skills/..%2F..%2Fetc%2Fpasswd")
    # FastAPI normalizes URLs, so this becomes /api/skills/../../etc/passwd
    # which the safe_join should refuse
    assert r.status_code in (400, 404)


# --- Upload (Zip Slip) ----------------------------------------------------

def _make_zip(members: dict[str, str]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, content in members.items():
            zf.writestr(name, content)
    return buf.getvalue()


def test_upload_safe_zip(client, claude_home):
    z = _make_zip({"my-zip-skill/SKILL.md": "---\nname: x\ndescription: ok\n---\nbody"})
    r = client.post(
        "/api/skills/upload",
        files={"file": ("safe.zip", z, "application/zip")},
    )
    assert r.status_code == 200
    assert (claude_home / "skills" / "my-zip-skill" / "SKILL.md").exists()


def test_upload_zip_slip_blocked(client, claude_home):
    z = _make_zip({"../../../tmp/escape.txt": "pwned"})
    r = client.post(
        "/api/skills/upload",
        files={"file": ("evil.zip", z, "application/zip")},
    )
    assert r.status_code == 400
    assert "unsafe path" in r.json()["detail"].lower()


def test_upload_rejects_non_zip(client):
    r = client.post(
        "/api/skills/upload",
        files={"file": ("not-a-zip.txt", b"hello", "text/plain")},
    )
    assert r.status_code == 400


# --- Clone URL validation -------------------------------------------------

def test_clone_invalid_url(client):
    r = client.post("/api/skills/clone", data={"url": "javascript:alert(1)"})
    assert r.status_code == 400


def test_clone_invalid_url_no_dot_git(client):
    r = client.post("/api/skills/clone", data={"url": "https://github.com/user/repo"})
    assert r.status_code == 400


# --- Tags & filtering -----------------------------------------------------

def test_tags_aggregated_in_stats(client, claude_home):
    for n, tag in [("a", "x"), ("b", "y"), ("c", "x")]:
        d = claude_home / "skills" / n
        d.mkdir()
        (d / "SKILL.md").write_text(
            f"---\nname: {n}\ndescription: skill description text here\ntags: [{tag}]\n---\nbody"
        )
    r = client.get("/api/stats")
    assert set(r.json()["all_tags"]) == {"x", "y"}


# --- Preview ---------------------------------------------------------------

def test_preview_returns_body_and_files(client, claude_home, example_skill):
    # Add a script file alongside SKILL.md
    (example_skill / "helper.py").write_text("# helper\n")
    r = client.get("/api/skills/my-skill/preview")
    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "my-skill"
    assert "skill body" in body["body"].lower()
    assert set(body["tags"]) == {"testing", "bioinformatics"}
    file_paths = [f["path"] for f in body["files"]]
    assert "SKILL.md" in file_paths
    assert "helper.py" in file_paths


def test_preview_404(client):
    r = client.get("/api/skills/does-not-exist/preview")
    assert r.status_code == 404
