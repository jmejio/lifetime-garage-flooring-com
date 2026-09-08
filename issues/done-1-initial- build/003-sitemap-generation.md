## Parent PRD

`issues/prd.md`

## What to build

Add sitemap generation to the build system. Per the PRD's confirmed module breakdown, this is a separate, pure "sitemap builder" module (page metadata in, `sitemap.xml` string out) alongside the existing page renderer — not folded into the HTML-rendering logic.

Per the parent PRD's "Implementation Decisions" and the implementation plan:

- Implement the sitemap-builder module in `build/build.py`: given all pages' metadata (loaded via the existing page loader from `issues/001-build-scaffold-index-tracer-bullet.md`), produce the `sitemap.xml` content as a string, ordered by `sitemap_priority` descending then slug ascending (reproduces today's index-then-about order).
- `sitemap.xml` uses a **different line-ending convention than the HTML outputs**: bare LF, not CRLF (verified against the currently-committed file — an existing repo inconsistency, not something to "fix"). The sitemap builder must apply this explicitly, independent of whatever convention the page renderer uses.
- Wire `sitemap.xml` into the orchestrator's existing write/`--check` loop alongside the HTML outputs.
- `SITE_BASE_URL` should be defined once in `build.py` and reused for both canonical/OG URLs (already used by the page renderer) and sitemap `<loc>` entries — this is the single-source-of-truth benefit called out in the PRD for a future domain change.

## Acceptance criteria

- [x] Running `python build/build.py` regenerates `sitemap.xml` at the repo root, in addition to `index.html` and `about.html`.
- [x] `git diff sitemap.xml` shows **zero diff** — output matches today's file exactly, including its bare-LF line endings and priority-descending ordering (index before about).
- [x] `python build/build.py --check` exits 0 and reports no drift across all three output files (`index.html`, `about.html`, `sitemap.xml`).
- [x] Deliberately changing a page's `sitemap_priority` or `sitemap_changefreq` in its `.json` file and rebuilding correctly updates the corresponding `<priority>`/`<changefreq>` value in the regenerated `sitemap.xml` (manual spot-check, then revert the test change).

## Blocked by

- Blocked by `issues/001-build-scaffold-index-tracer-bullet.md`
- Blocked by `issues/002-migrate-about-page.md`

## User stories addressed

- User story 7
- User story 8
- User story 9
- User story 10

## Implementation notes

- Added `build_sitemap(pages)` to `build/build.py`: sorts pages by `(-sitemap_priority, slug)` (matches the plan), emits the same XML structure as the current committed `sitemap.xml`, and joins lines with a dedicated `SITEMAP_NEWLINE = "\n"` constant — distinct from `HTML_NEWLINE = "\r\n"` used by the page renderer, since the two output types have different pre-existing line-ending conventions in this repo.
- Wired `outputs["sitemap.xml"] = build_sitemap(pages)` into the existing orchestrator loop in `main()`; no other orchestrator changes were needed since it already iterates generically over an `outputs` dict.
- `python build/build.py` regenerated all three files. `git diff sitemap.xml` and `git diff index.html` were both empty; `about.html` still showed only the two changes from issue 002. `python build/build.py --check` reported `OK: 3 file(s) match committed output.`
- Spot-check: temporarily set `about.json`'s `sitemap_priority` to `0.5` and `sitemap_changefreq` to `"yearly"`, rebuilt, and confirmed `sitemap.xml`'s about-page `<url>` entry updated accordingly. Reverted both fields back to `0.8`/`"monthly"` and rebuilt; `--check` confirmed a clean match again afterward.
- `str(1.0) == "1.0"` and `str(0.8) == "0.8"` in Python, so no special float formatting was needed to match the committed file's `<priority>` values.
