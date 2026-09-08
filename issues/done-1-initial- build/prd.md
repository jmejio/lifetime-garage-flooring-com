## Problem Statement

The site has two pages today (`index.html`, `about.html`), and both duplicate the entire `<header>`, `<footer>`, and most of the `<head>` boilerplate (favicons, Bootstrap/Bootstrap Icons CDN links, `style.css`) verbatim. Because there's no templating system, any change to shared content — a phone number, a nav link, a discount message — has to be made by hand in every file. This has already caused drift: `about.html` is missing the `HomeAndConstructionBusiness` JSON-LD structured-data block that `index.html` has. As more pages get added, and as AI agents do most of the day-to-day editing, this duplication becomes the main source of inconsistency across the site.

The site is hosted on GitHub Pages, deployed straight from `main` with no CI/build pipeline — a push is an immediate live deploy. Whatever fixes the duplication problem has to preserve that property: visitors and GitHub Pages must still be served plain, pre-rendered static HTML, with nothing running at deploy time.

## Solution

Introduce a small, local, authoring-time-only build step using Jinja2 templating. Shared header/footer/head markup moves into Jinja2 partials and a base layout; each page becomes a small template plus a metadata file. An agent (or the developer) edits the shared partials or a page's own template, runs one command, and the fully static `index.html`/`about.html`/`sitemap.xml` files that GitHub Pages actually serves get regenerated and committed. The build never runs on GitHub's infrastructure and Jinja2 is never shipped to the browser — it's a developer-machine tool that produces the same kind of static output that's committed today.

This was chosen over several alternatives that were explored and ruled out:
- **Client-side JS injection** (extending the existing `contact-form.js` `innerHTML` pattern to header/footer) — would hide the footer's NAP data and nav links from non-JS crawlers and reintroduce layout shift that recent Core Web Vitals work just fixed.
- **Nuxt.js** — a full Vue app framework for a site with no real client-side interactivity; ships a runtime bundle even in static mode and needs a GitHub Actions build.
- **Eleventy / Astro** — good static site generators, but neither has native GitHub Pages support; both would require a GitHub Actions workflow, turning an instant deploy into a build-then-deploy, and moving the source of truth to uncommitted build artifacts.
- **Hugo / Zola** — same CI trade-off as Eleventy/Astro, plus a new non-Python toolchain.
- **Jekyll** — the one SSG GitHub Pages builds natively, but Ruby isn't installed on the maintainer's machine, and local preview without Ruby breaks the current fast-iteration workflow.
- **Flask as a running app** — wrong category entirely; GitHub Pages can't execute a live Python process.
- **Base44** — a proprietary no-code platform with its own hosting; incompatible with a git-repo-as-source-of-truth model.

**Key technical decisions** (see the full implementation plan for details):
- Jinja2 is installed globally via `pip install -r build/requirements.txt` — no virtualenv, since this is a single-purpose local tool with one pinned dependency and no risk of conflicting with other Python projects on the maintainer's machine.
- Source templates use a `.jinja` extension (`base.jinja`, `_header.jinja`, `_footer.jinja`, `_jsonld.jinja`, `index.jinja`, `about.jinja`), never `.html` — this avoids a same-name collision with the generated `index.html`/`about.html` files at the repo root.
- Line endings must be forced explicitly per output file, not left to platform defaults: the committed `index.html`/`about.html` use CRLF throughout, while `sitemap.xml` uses bare LF throughout (a pre-existing repo inconsistency, verified by inspecting raw bytes — not something this change should "fix"). The build script must reproduce each file's convention explicitly so output is byte-identical regardless of what OS runs the build.
- A stray whitespace-only line already present in `about.html` (an accidental leftover from hand-editing) gets deliberately cleaned up during migration, alongside the intentional addition of the missing JSON-LD block — both are expected, reviewed changes to `about.html`, not signs of a broken template.
- `robots.txt` stays hand-maintained, including its hardcoded `Sitemap:` URL — it's two lines that essentially never change and isn't worth pulling into the build.
- No git pre-commit hook. Enforcement relies on a `CLAUDE.md` rule instructing agents to run a `--check` command before committing anything touching the build sources or a root `*.html` file. This can be revisited if drift is observed in practice.
- A `.gitignore` is added (none exists today) to exclude Python's `__pycache__` bytecode cache, which the build step will otherwise generate.
- No automated test suite is introduced for the build script — consistent with the rest of the repo, which has no test infrastructure. Correctness is verified manually via diffing generated output against committed files and a local server smoke test.

## User Stories

1. As the site maintainer, I want the header and footer to live in one shared template, so that a phone number or nav change only has to be made in one place instead of every page.
2. As the site maintainer, I want `about.html` to include the same structured-data (JSON-LD) block as `index.html`, so that search engines see consistent business information regardless of which page they crawl.
3. As an AI agent editing this site, I want a clear, documented rule about which files are hand-authored source versus generated output, so that I don't accidentally edit a generated file and have my changes silently overwritten on the next build.
4. As an AI agent editing this site, I want the source template files to be visually distinguishable from the generated output files (even in a file listing or search result), so that I can't confuse `build/pages/index.jinja` (source) with the root `index.html` (output).
5. As the site maintainer, I want a single command that regenerates all pages and the sitemap from their templates, so that publishing a change is still a fast, predictable step.
6. As the site maintainer, I want a verification command that tells me whether the committed HTML/sitemap files are out of sync with their templates, so that I can catch a forgotten rebuild before it goes live.
7. As the site maintainer, I want the generated output to be byte-identical to what's committed today (aside from the one intentional JSON-LD fix and one intentional whitespace cleanup), so that this migration doesn't introduce any unintended visual or SEO regressions.
8. As the site maintainer, I want the build to produce correct output regardless of what operating system runs it, so that line-ending differences between Windows and other environments don't cause spurious diffs later.
9. As the site maintainer, I want to add a new page by creating just two small source files (a metadata file and a content template) rather than copy-pasting an entire HTML document, so that scaling past two pages doesn't multiply the maintenance burden.
10. As the site maintainer, I want adding a new page's nav link to require editing only the shared header partial, so that every existing and future page picks up the nav change automatically on the next build.
11. As the site maintainer, I want this build step to remain purely local/authoring-time, so that GitHub Pages' zero-CI, instant-deploy hosting model is completely unaffected.
12. As the site maintainer, I want the one new Python dependency (Jinja2) documented with an exact one-time install command in `CLAUDE.md`, so that a fresh contributor or agent can get the build working without guesswork.
13. As the site maintainer, I want Python bytecode cache (`__pycache__`) automatically excluded from git, so that build artifacts don't get accidentally committed.
14. As the site maintainer, I want the migration to be reviewable as a small number of clear diffs (template extraction, two intentional `about.html` changes, no changes to `index.html`/`sitemap.xml` content), so that I can confidently verify nothing broke before merging.
15. As a site visitor, I want no visible or functional change to the pages I browse (rendering, mobile nav toggle, contact form), so that this internal refactor has zero impact on my experience.

## Implementation Decisions

- **New `build/` directory** holds all build-time source and tooling, kept fully separate from the repo-root files GitHub Pages serves:
  - `build/requirements.txt` pins Jinja2 as the sole dependency.
  - `build/templates/` holds the shared base layout and partials (base layout, header, footer, JSON-LD block), each using a `.jinja` extension.
  - `build/pages/` holds one metadata file (JSON: title, description, canonical path, OG image, home-page flag, sitemap priority/changefreq) and one content template (`.jinja`, extends the base layout) per page.
  - `build/build.py` is the single build script.
- **Module boundaries within `build.py`** (confirmed with the developer):
  - *Page loader*: reads all page metadata files and returns them in a deterministic order; pure filesystem read, no rendering logic.
  - *Page renderer*: given one page's slug and metadata, returns the fully rendered HTML as a string with the correct line ending already applied. This is the deep module — callers never see the Jinja2 environment configuration, autoescaping behavior, or newline handling; the interface (metadata in, string out) is stable even if the templates grow more complex.
  - *Sitemap builder*: given all pages' metadata, returns the `sitemap.xml` content as a string (same shape as the renderer — data in, string out — but for XML output with its own line-ending convention).
  - *Build orchestrator*: the thin entry point that loads pages, invokes the renderer/sitemap builder, and either writes the results to disk or diffs them against what's already committed, depending on a `--check` flag.
- **Drift detection**: the build script supports a `--check` mode that regenerates output in memory and diffs it against the committed files, exiting non-zero if anything differs, without ever writing to disk in that mode.
- **Logo link behavior**: the header partial's logo link target is the one real variable difference between pages today (an in-page anchor on the home page, a link to the home page everywhere else) and is driven by the page's home-page flag.
- **JSON-LD scope change**: including the structured-data block on every page (not just the homepage) is an intentional, reviewed side effect of the migration — its content legitimately applies to every page under standard local-business schema practice.
- **No enforcement mechanism beyond documentation**: this migration does not add a git hook or CI check. It relies on `CLAUDE.md` instructing whoever edits the site (human or agent) to run the verification command before committing changes to build sources or generated root HTML files.
- **`robots.txt` remains fully hand-maintained**, outside the build's scope, including its hardcoded sitemap URL.

## Update Documents

- Update `CLAUDE.md`:
  - Revise the Project Overview to note that pages are regenerated from local Jinja2 templates via a build step, with GitHub Pages still serving the committed output as-is.
  - Add a Hosting bullet clarifying the build step runs locally/on the agent's machine only, never on GitHub, and doesn't change the no-CI deploy guarantee.
  - Update Commands to document the one-time dependency install, the build command, and the verification (`--check`) command.
  - Replace the Architecture section's duplicated-header/footer description with a description of the new `build/` source layout, the never-hand-edit-generated-output rule, and the steps for adding a new page.
  - Note that `robots.txt` remains hand-maintained and call out the domain-change checklist implication (updating the build's base-URL constant in addition to `robots.txt` if the domain ever changes).

## Testing Decisions

No automated tests are introduced as part of this change. This repo has no existing test infrastructure (`CLAUDE.md` explicitly documents "no test suite"), and introducing one — even a small one scoped to two pure functions — was considered and deliberately deferred in favor of consistency with the rest of the codebase's hand-verified, no-build-pipeline conventions.

Correctness is instead verified manually for this migration and for any future page additions:
- Diffing generated output against committed files after running the build, confirming only the expected, reviewed changes appear.
- Running the verification (`--check`) command and confirming it reports no drift.
- Serving the site locally and manually confirming visual rendering, mobile nav collapse, and contact form behavior are unaffected on both existing pages.

If test coverage is wanted in the future, the page renderer and sitemap builder are the natural candidates — both are pure, deterministic functions (metadata in, string out) with no filesystem or environment dependencies once their input is supplied.

## Out of Scope

- Adding a git pre-commit hook or any CI enforcement of the verification command.
- Templating or otherwise folding `robots.txt` into the build.
- Any URL structure changes (e.g., extensionless paths) — canonical paths and file names are unchanged.
- Adding new pages beyond the two that exist today (`index.html`, `about.html`) — this PRD only covers migrating the existing pages onto the new system; adding a third page is a follow-up task the new system is designed to make cheap, not something this PRD implements.
- Any changes to `style.css`, `app.js`, `contact-form.js`, or `assets/` — none of these are affected by this migration.
- Introducing automated tests or a test framework.
- Changing the site's hosting, domain, or deploy process in any way.

## Further Notes

- This is a one-time migration plus a small piece of ongoing tooling, not a recurring feature — there are no temporary test files or scaffolding created as part of this work that would need later cleanup.
- The full technical implementation plan (exact file contents, the build script, and the precise migration/verification steps) has already been designed and reviewed separately; this PRD captures the product-level problem, solution, and decisions for that plan.
