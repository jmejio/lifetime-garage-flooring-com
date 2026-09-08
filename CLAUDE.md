# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Marketing site for Lifetime Garage Flooring (a Technifloors brand), a residential garage floor coating contractor in Lutz, FL. Static HTML/CSS/JS, no framework. Pages are regenerated from local Jinja2 templates by a small Python build step before committing (see Commands/Architecture below); GitHub Pages still serves the committed output as-is, with no server-side build.

## Hosting

**This repo is hosted on GitHub Pages, serving directly from the `main` branch.** There is no staging environment and no CI/build pipeline — a push (or a merge) to `main` is a production deploy of the live public site, typically live within a minute or two. Treat commits to `main` accordingly:

- Don't commit anything you wouldn't want live immediately.
- `CNAME` (containing `www.lifetimegarageflooring.com`) is what maps the custom domain to GitHub Pages — don't remove, rename, or edit it, or the domain mapping breaks.
- `.nojekyll` (empty file at the repo root) tells GitHub Pages to skip Jekyll and serve the repo as plain static files — don't remove it. Without it, GitHub Pages runs every push through Jekyll, which converts markdown files (including this one) into themed HTML pages and fails the entire deploy if any file contains text Jekyll's Liquid templating misreads as its own syntax (this happened in practice: prose describing Jinja2's `{% block %}` tag in this file's Architecture section crashed the Jekyll build with "Unknown tag 'block'"). Keep it in the repo permanently, and be aware that `{{ }}`/`{% %}` in any committed file's prose — not just code — is a landmine unless `.nojekyll` is present.
- There's no `.github/workflows/` — Pages builds straight from the branch, so nothing in Actions needs to pass before it goes live.
- A local build step (`python build/build.py`) regenerates the static `*.html` files and `sitemap.xml` from Jinja2 templates under `build/templates/` and `build/pages/` before you commit. This runs on your machine (or the agent's) only — GitHub never runs it, and Jinja2 is never shipped to the browser. The committed `*.html` files are still plain static output, and the "no CI/build pipeline" guarantee above is unchanged: nothing runs at deploy time, only ahead of a commit.

## Commands

There is no build/lint/test *pipeline*; there is one local Python dependency (Jinja2) used only by the page build step below.

- **Local preview**: serve the repo root with any static file server, e.g. `python -m http.server 8000`, then open `http://localhost:8000/index.html`. Opening the HTML files directly (`file://`) also works since there are no server-side dependencies.
- **One-time setup**: `pip install -r build/requirements.txt` (installs Jinja2 into your system Python — no virtualenv needed for this single-dependency tool).
- **Build pages**: `python build/build.py` — regenerates all committed `*.html` files and `sitemap.xml` from `build/templates/` + `build/pages/`. Run after editing anything under `build/`, then commit both the source changes and the regenerated output together.
- **Verify generated output is in sync**: `python build/build.py --check` — rebuilds in memory and diffs against the committed output; exits non-zero with a diff if anything is stale or was hand-edited. Run before committing any change touching `build/` or a root `*.html` file.
- **Deployment**: none needed — see Hosting above. Pushing to `main` is the deploy.

## Architecture

- Two pages only: `index.html` (home) and `about.html`. Pages are generated from local Jinja2 templates, not hand-duplicated. Source of truth lives under `build/`:
  - `build/templates/base.jinja` — the shared layout: head boilerplate, per-page `{{ title }}`/`{{ description }}`/`{{ canonical_url }}`/`{{ og_image }}` variables, and a `{% block content %}` each page overrides.
  - `build/templates/_header.jinja` / `_footer.jinja` — shared header/footer partials, included via `{% include %}`. The header has one variable, `{{ logo_href }}` (`#header` on the home page, `index.html` everywhere else); the footer is fully static.
  - `build/templates/_jsonld.jinja` — the `HomeAndConstructionBusiness` JSON-LD block, included on every page.
  - `build/pages/<slug>.json` — per-page metadata: `title`, `description`, `canonical_path`, `og_image`, `is_home`, `sitemap_priority`, `sitemap_changefreq`.
  - `build/pages/<slug>.jinja` — the actual Jinja2 template for that page (`{% extends "base.jinja" %}` + a `content` block). Source files use a `.jinja` extension specifically so they never share a name with the generated `<slug>.html` file at the repo root.
  - `build/build.py` — reads the above with Jinja2 and writes the root `<slug>.html` files and `sitemap.xml`, forcing the correct line endings per file (`*.html` is CRLF, `sitemap.xml` is bare LF — an existing repo inconsistency this build preserves rather than "fixes"); supports `--check` for drift detection. Its one dependency (Jinja2) is pinned in `build/requirements.txt`.
  - **Never hand-edit `index.html`, `about.html`, any other root-level `*.html` file, or `sitemap.xml` directly** — they are generated output. Edit `build/templates/` or `build/pages/`, run `python build/build.py`, then commit both together.
  - To add a new page: create `build/pages/<slug>.json` and `build/pages/<slug>.jinja`, add a nav `<li>` to `build/templates/_header.jinja` if needed, run the build, commit source + generated output together.
- `style.css` holds only the overrides layered on top of Bootstrap 5.3.3 and Bootstrap Icons (both loaded from the jsdelivr CDN in `<head>`, not vendored). Layout is otherwise done with Bootstrap utility classes directly in the markup, not custom CSS.
- `app.js`: sets the footer copyright year and closes the mobile nav collapse on link click or outside click.
- `contact-form.js`: a self-contained widget that injects the "Request a Free Quote" form into any `<div id="contact-form-root">` via `innerHTML`, and submits to Web3Forms. The `WEB3FORMS_ACCESS_KEY` constant near the top of the file is a public Web3Forms site key — it's meant to be client-visible, not a secret. The form is two-step: step 1 (name/email/phone) is silently POSTed in the background the moment the visitor advances to step 2, so partial leads aren't lost if they abandon before finishing.
- `assets/` holds all images. Photos are stored as JPEG (re-encoded with Pillow, `optimize=True, progressive=True`, quality ~82); PNG is reserved for logo/mascot artwork that needs transparency. `favicon.ico`, `favicon-16x16.png`, `favicon-32x32.png`, and `apple-touch-icon.png` were generated from `assets/hero-standing.png` (the mascot) — regenerate from that source if the mascot art changes rather than hand-editing the icon files.
- `robots.txt` remains fully hand-maintained (outside the build), including its hardcoded `Sitemap:` URL. If the domain in `CNAME` ever changes: update `SITE_BASE_URL` in `build/build.py` (drives the canonical/OG/sitemap URLs for every page from one place), update the hardcoded URLs inside `build/templates/_jsonld.jinja` (its `image`/`url`/`sameAs` fields aren't templated), update `robots.txt`'s `Sitemap:` line, then rerun `python build/build.py` and commit the regenerated output.
