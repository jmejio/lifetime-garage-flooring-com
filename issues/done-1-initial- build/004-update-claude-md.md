## Parent PRD

`issues/prd.md`

## What to build

Update `CLAUDE.md` to document the finished build system, per the PRD's "Update Documents" section and the implementation plan's "CLAUDE.md updates" section. This is the slice that makes the new system discoverable and maintainable by future contributors (human or AI agent) — without it, the rules established by issues 001-003 (never hand-edit generated files, run `--check` before committing) exist only in this issue tracker, not in the document agents actually read every session.

Specifically:

- **Project Overview**: revise the closing sentence to note pages are regenerated from local Jinja2 templates via a build step, with GitHub Pages still serving the committed output as-is, no server-side build.
- **Hosting**: add a bullet clarifying the build step runs locally/on the agent's machine only, GitHub never runs it, Jinja2 is never shipped to the browser, and the "no CI/build pipeline" deploy guarantee is unchanged.
- **Commands**: update the opening line, and document the one-time dependency install (`pip install -r build/requirements.txt`), the build command (`python build/build.py`), and the verification command (`python build/build.py --check`).
- **Architecture**: replace the duplicated-header/footer bullet with a description of the `build/` source layout (templates, per-page metadata + `.jinja` templates, `build.py`'s responsibilities), the never-hand-edit-generated-output rule, the steps for adding a new page, and the domain-change checklist implication (updating `SITE_BASE_URL` in `build.py` in addition to `robots.txt` and `CNAME`).
- Leave the `style.css`/`app.js`/`contact-form.js`/`assets/` bullets as-is — unaffected by this change.

## Acceptance criteria

- [x] `CLAUDE.md`'s Project Overview, Hosting, Commands, and Architecture sections are updated per the plan's exact wording (or a close paraphrase preserving the same content).
- [x] `CLAUDE.md` explicitly states that `index.html`, `about.html`, and `sitemap.xml` are generated output and must never be hand-edited directly.
- [x] `CLAUDE.md` documents the one-time setup, build, and `--check` commands with their exact invocations.
- [x] `CLAUDE.md` documents the two-file pattern (`<slug>.json` + `<slug>.jinja`) for adding a new page, including updating `build/templates/_header.jinja` for a nav entry if needed.
- [x] A fresh read-through of `CLAUDE.md` (as if by a new contributor or agent with no other context) is sufficient to understand which files are hand-authored source vs. generated output, and what command to run after editing a template.

## Blocked by

- Blocked by `issues/001-build-scaffold-index-tracer-bullet.md`
- Blocked by `issues/002-migrate-about-page.md`
- Blocked by `issues/003-sitemap-generation.md`

## User stories addressed

- User story 3
- User story 4
- User story 12

## Implementation notes

- Updated `CLAUDE.md`'s Project Overview, Hosting, Commands, and Architecture sections per the plan, matching the actual implemented file names (`.jinja` extensions, `build/build.py`, `build/requirements.txt`) rather than the plan's original draft wording where they'd diverged.
- The Architecture section's domain-change checklist bullet was written to reflect the real, verified implementation rather than the plan's slightly simplified draft: it now correctly calls out that `build/templates/_jsonld.jinja`'s `image`/`url`/`sameAs` fields are hardcoded (not driven by `SITE_BASE_URL`), in addition to `SITE_BASE_URL` in `build/build.py` and `robots.txt`'s `Sitemap:` line — so a future domain change won't miss that one spot.
- `style.css`/`app.js`/`contact-form.js`/`assets/` bullets were left untouched, as specified.
- `git diff CLAUDE.md` confirmed the change is additive/targeted (16 insertions, 4 deletions) with no unrelated edits.
