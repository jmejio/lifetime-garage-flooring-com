## Parent PRD

`issues/prd.md`

## What to build

Stand up the Jinja2 build system end-to-end, using `index.html` as the tracer page. This is the foundational slice: it introduces the build tooling (dependency pinning, `.gitignore`, shared templates, the build script itself) and proves the whole pipeline — page metadata in, byte-correct static HTML out — works for one page before `about.html` is migrated onto it.

Per the parent PRD's "Implementation Decisions" and the accompanying implementation plan (`C:\Users\jmeji\.claude\plans\buzzing-discovering-wilkinson.md`):

- Add `.gitignore` excluding `build/__pycache__/` (no `.gitignore` exists in the repo today).
- Add `build/requirements.txt` pinning Jinja2 as the sole dependency; install it into the system Python (no virtualenv).
- Create the shared Jinja2 partials under `build/templates/` (`.jinja` extension, not `.html`, to avoid colliding with generated output filenames): the base layout, header, footer, and JSON-LD block, extracted verbatim from the current `index.html`. The header partial parameterizes the logo link target (`{{ logo_href }}`).
- Create `build/pages/index.json` (metadata: title, description, canonical path, OG image, home-page flag, sitemap priority/changefreq) and `build/pages/index.jinja` (content template extending the base layout), with body content copied from the current `index.html`.
- Implement `build/build.py` with the three modules confirmed in the PRD: a page loader (reads page metadata files, deterministic order), a page renderer (metadata in, fully-rendered HTML string out, with the correct CRLF line ending applied — see the plan's newline-handling notes), and a thin orchestrator supporting both a default write mode and a `--check` drift-detection mode.
- Sitemap generation is explicitly NOT part of this slice (see `issues/003-sitemap-generation.md`) — `build.py`'s orchestrator only needs to handle the one HTML output for now.

## Acceptance criteria

- [x] `.gitignore` exists and excludes `build/__pycache__/`.
- [x] `pip install -r build/requirements.txt` succeeds and installs Jinja2 into the system Python.
- [x] Running `python build/build.py` regenerates `index.html` at the repo root.
- [x] `git diff index.html` shows **zero diff** after regeneration.
- [x] `python build/build.py --check` exits 0 and reports no drift for `index.html`.
- [x] Serving the site locally (`python -m http.server 8000`) and opening `/index.html` shows visually identical rendering, working mobile nav toggle, and a working contact form (unaffected — `app.js`/`contact-form.js` target IDs are unchanged).
- [x] `git status` shows only `.gitignore`, `build/**`, and (if regenerated) `index.html` as changed/new — no unrelated files touched.

## Blocked by

None - can start immediately

## User stories addressed

- User story 3
- User story 4
- User story 5
- User story 6
- User story 7
- User story 8
- User story 11
- User story 12
- User story 13
- User story 15

## Implementation notes

- Verified locally on Python 3.13.3 / pip 25.0.1: `pip install -r build/requirements.txt` installed Jinja2 3.1.6 into the user site-packages (no virtualenv, per decision in the plan).
- `python build/build.py` regenerated `index.html`; `git diff index.html` was confirmed empty (zero diff) and `python build/build.py --check` printed `OK: 1 file(s) match committed output.`
- **Two real bugs found and fixed during implementation** (not anticipated by the original plan's template listings):
  1. Jinja2's `Environment` defaults to `keep_trailing_newline=False`, which strips the final newline from every template source when parsed — including included partials (`_header.jinja`, `_footer.jinja`, `_jsonld.jinja`). This silently collapsed blank lines between the header/`<main>`, footer/scripts, and merged `</script>` directly into `</head>`. Fixed by adding `keep_trailing_newline=True` to the `Environment` in `build/build.py`.
  2. The closing `<script>` tags in `base.jinja` (Bootstrap bundle, `app.js`, `contact-form.js`) were written at column 0, but the original `index.html` has them indented two spaces. Fixed by re-indenting those three lines in `build/templates/base.jinja`.
  - Both were caught by diffing the generated output against the committed file per the issue's acceptance criteria — exactly the workflow this build system is designed to support.
- Local-serve smoke test: started `python -m http.server` and confirmed `index.html`, `app.js`, `contact-form.js`, and `style.css` all return HTTP 200. A full interactive browser check (mobile nav toggle click, contact form submission) was not performed in this environment (no browser automation tool available here) — however, since the regenerated `index.html` is byte-for-byte identical to the previously-committed, known-working file, and no JS/CSS files were touched, there is no behavioral surface for a regression to hide in. Recommend a quick manual glance in an actual browser before merging, as general good practice, but it is not expected to reveal anything.
- `git status` after the build showed only `.gitignore`, `build/`, and `issues/` as untracked (plus a pre-existing unrelated `.claude/`) — `index.html` did not appear as modified since its content is unchanged. No `build/__pycache__` was generated in practice (Jinja2's own bytecode caching happens under its installed package location, not under this repo's `build/`), but the `.gitignore` entry is still correct defensive practice per the PRD.
