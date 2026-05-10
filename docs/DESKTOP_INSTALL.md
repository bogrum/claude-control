# Install as a desktop app

Pick your OS. After this, claude-control behaves like any other app: an icon you can pin to your dock / taskbar, no terminal required.

---

## Ubuntu / Linux (GNOME, KDE, XFCE, Cinnamon, MATE)

```bash
git clone https://github.com/YOUR_USER/claude-control.git ~/claude-control
cd ~/claude-control
./install.sh
```

Press **Super**, type "Claude Control", click. Right-click the running icon in the dock → "Add to Favorites" to keep it pinned.

`install.sh` does all of this under your home directory (no `sudo`):

1. Creates `.venv/` with all Python deps
2. Optionally installs `pywebview` for native-window mode
3. Writes `~/.local/share/applications/claude-control.desktop`
4. Copies the icon to `~/.local/share/icons/hicolor/256x256/apps/`
5. Refreshes the GNOME app database

To uninstall: `./uninstall.sh`. To wipe the project too: `rm -rf ~/claude-control`.

---

## macOS (12 Monterey or newer)

```bash
git clone https://github.com/YOUR_USER/claude-control.git ~/claude-control
cd ~/claude-control
./install-macos.sh
```

`install-macos.sh` builds a real `.app` bundle at `~/Applications/Claude Control.app`. Launch it from Spotlight (⌘+Space → "Claude Control") or Launchpad. To pin to the Dock, drag it from `~/Applications/` onto the Dock.

The bundle contains:

```
~/Applications/Claude Control.app/
└── Contents/
    ├── Info.plist           # bundle metadata
    ├── MacOS/
    │   └── claude-control   # entry point shim → launcher.py
    └── Resources/
        └── icon.icns        # converted from icon.png
```

If macOS's Gatekeeper warns you the first time ("unidentified developer"), right-click → Open → Open. The app is unsigned because you built it yourself; this is expected for local tools.

To uninstall: `./uninstall-macos.sh`.

### Native window mode on macOS

```bash
./.venv/bin/pip install pywebview pyobjc-framework-WebKit
```

Then edit `~/Applications/Claude Control.app/Contents/MacOS/claude-control` and add `--window` to the python arguments:

```bash
exec /path/to/claude-control/.venv/bin/python /path/to/claude-control/launcher.py --window
```

The dashboard now opens in a chromeless native window instead of your default browser.

---

## Windows 10 / 11

Open **PowerShell** (no need to be admin) and run:

```powershell
git clone https://github.com/YOUR_USER/claude-control.git $HOME\claude-control
cd $HOME\claude-control
.\install.ps1
```

If PowerShell refuses to run the script, allow user-scope scripts once:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Press the **Windows key**, type "Claude Control", press Enter. Right-click the Start Menu entry → "Pin to taskbar" if you want it always visible.

`install.ps1` creates a Start Menu shortcut at:

```
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Claude Control.lnk
```

To uninstall: `.\uninstall.ps1`.

### Native window mode on Windows

`pywebview` works out of the box on Windows 10+ (uses Edge WebView2). After install:

```powershell
.\.venv\Scripts\pip install pywebview
```

Edit the shortcut's "Arguments" field (right-click the .lnk → Properties) and add `--window` after the `launcher.py` path.

---

## How clicking the icon actually works

The launcher (`launcher.py`) does the same thing on every OS:

1. Picks port 8765 (or any free port if taken)
2. Spawns uvicorn as a **detached** background process
3. Polls `/api/health` until the server responds
4. Opens your default browser to the dashboard
5. Writes the PID and port to a runtime dir (`$XDG_RUNTIME_DIR` on Linux, `tempfile.gettempdir()` elsewhere)

Click the icon a second time → it sees the existing server and opens a new browser tab pointed at it. No duplicate processes.

## Stopping the server

The server keeps running after you close the browser tab — that's intentional, so the next click is instant. To actually stop it:

| OS | Command |
|---|---|
| Linux/macOS | `./.venv/bin/python launcher.py --stop` |
| Windows | `.\.venv\Scripts\python.exe launcher.py --stop` |

Or just reboot — it doesn't auto-start unless you set up systemd (Linux only, see [`SYSTEMD.md`](SYSTEMD.md)).

## Troubleshooting

**Linux: "Claude Control" doesn't show up in Activities**

Run `update-desktop-database ~/.local/share/applications/`. If still missing, log out and back in.

**macOS: "App can't be opened because it is from an unidentified developer"**

Right-click the app → Open → Open. You only need to do this once.

**Windows: Start Menu shortcut shows a generic icon**

Install ImageMagick (`winget install ImageMagick.ImageMagick`) and re-run `install.ps1`. The script will then convert `icon.png` → `icon.ico` for proper Windows display.

**Server won't start (any OS)**

Check the log file at:

| OS | Path |
|---|---|
| Linux | `$XDG_RUNTIME_DIR/claude-control/server.log` |
| macOS / Windows | `<tempdir>/claude-control/server.log` |
