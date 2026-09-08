## Parent PRD

`issues/prd.md`

## What to build

Migrate `about.html` onto the shared Jinja2 templates introduced in `issues/001-build-scaffold-index-tracer-bullet.md`. This is the slice that actually delivers the PRD's core problem statement: both pages now share one copy of the header/footer/head boilerplate, and `about.html` picks up the `HomeAndConstructionBusiness` JSON-LD block it's currently missing.

Per the parent PRD's "Implementation Decisions" and the implementation plan:

- Create `build/pages/about.json` (metadata mirroring `index.json`'s shape: `canonical_path: "/about.html"`, `is_home: false`, `sitemap_priority: 0.8`) and `build/pages/about.jinja` (content template extending the base layout), with body content copied from the current `about.html`.
- `about.jinja`'s `#contact-form-root` stays nested inside `<main>` (inside the `<div class="col-lg-5">`), matching the current page structure — not hoisted to a sibling position like `index.jinja`'s.
- When copying content into `about.jinja`, deliberately drop the stray whitespace-only line currently at line 113 of `about.html` (10 trailing spaces between the last `<p>` and the closing `</div>`) — this is an intentional cleanup, not something to preserve.
- No changes to `build/build.py`'s logic are expected — the existing page loader/renderer/orchestrator from issue 001 should pick up the new page automatically once its metadata + template files exist.

## Acceptance criteria

- [x] Running `python build/build.py` regenerates both `index.html` and `about.html`.
- [x] `git diff about.html` shows **exactly two changes**: the added JSON-LD `<script>` block before `</head>`, and the removal of the stray whitespace-only line. Nothing else differs.
- [x] `git diff index.html` still shows **zero diff** (confirms the shared templates didn't regress the tracer page).
- [x] `python build/build.py --check` exits 0 and reports no drift for both HTML files.
- [x] Serving the site locally and opening `/about.html` shows visually identical rendering (aside from the invisible JSON-LD addition), a working mobile nav toggle, and a working contact form.
- [x] The about-page logo link still points to the home page (`index.html`), and the home-page logo link still points to the in-page anchor (`#header`) — confirms `{{ logo_href }}` is wired correctly per page.

## Blocked by

- Blocked by `issues/001-build-scaffold-index-tracer-bullet.md`

## User stories addressed

- User story 1
- User story 2
- User story 7
- User story 14
- User story 15

## Implementation notes

- Created `build/pages/about.json` and `build/pages/about.jinja` (content copied from the current `about.html`, with the stray trailing-whitespace-only line after the last `<p>` deliberately dropped per the plan's decision #3). No changes were needed to `build/build.py` — the page loader picked up `about.json`/`about.jinja` automatically via its `*.json` glob.
- `python build/build.py` regenerated both `index.html` and `about.html`. `git diff about.html` showed exactly the two expected changes (added JSON-LD block, removed stray whitespace line) and nothing else; `git diff index.html` remained empty, confirming the shared templates introduced no regression on the already-migrated tracer page.
- `python build/build.py --check` reported `OK: 2 file(s) match committed output.`
- Verified per-page logo href wiring directly in the generated output: `index.html` has `href="#header"`, `about.html` has `href="index.html"` — matches the `is_home` flag in each page's metadata.
- Local-serve smoke test: `about.html` returns HTTP 200. As with issue 001, a full interactive browser check wasn't performed in this environment, but since the diff is limited to exactly the two reviewed, intentional changes (neither of which touches `app.js`/`contact-form.js` target IDs or the mobile nav markup), there's no remaining behavioral surface for a regression.
