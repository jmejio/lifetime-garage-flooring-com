"""Dev convenience only: rebuilds the site whenever a file under build/ changes.

Not part of the deploy — GitHub Pages never runs this. Pair it with a
static/live-reload server (e.g. the VS Code Live Server extension) pointed
at the repo root: this script keeps index.html/about.html/sitemap.xml/
robots.txt in sync with your template edits, and the live-reload server
picks up those regenerated files and refreshes the browser.

Usage: python build/watch.py

To use it:

Run python build/watch.py in a terminal — it rebuilds immediately, then watches.
Start Live Server on the repo root 
(right-click index.html → "Open with Live Server", or your usual command) 
so the browser auto-reloads on file changes.
Edit any .jinja or .json file under build/ and save 
— the watcher rebuilds the root HTML, Live Server sees it change, browser refreshes.

"""
import subprocess
import sys
import time
from pathlib import Path

WATCH_DIR = Path(__file__).resolve().parent
BUILD_SCRIPT = WATCH_DIR / "build.py"
POLL_SECONDS = 0.5


def snapshot():
    return {
        p: p.stat().st_mtime
        for p in WATCH_DIR.rglob("*")
        if p.suffix in (".jinja", ".json")
    }


def main():
    print(f"Watching {WATCH_DIR} for .jinja/.json changes (Ctrl+C to stop)...")
    subprocess.run([sys.executable, str(BUILD_SCRIPT)])
    last = snapshot()
    try:
        while True:
            time.sleep(POLL_SECONDS)
            current = snapshot()
            if current != last:
                print("Change detected, rebuilding...")
                subprocess.run([sys.executable, str(BUILD_SCRIPT)])
                current = snapshot()  # pick up files build.py itself may not touch
            last = current
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
