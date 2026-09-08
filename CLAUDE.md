# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Marketing site for Lifetime Garage Flooring (a Technifloors brand), a residential garage floor coating contractor in Lutz, FL. Static HTML/CSS/JS, no framework, no build system, deployed as-is via GitHub Pages.

## Hosting

**This repo is hosted on GitHub Pages, serving directly from the `main` branch.** There is no staging environment and no CI/build pipeline — a push (or a merge) to `main` is a production deploy of the live public site, typically live within a minute or two. Treat commits to `main` accordingly:

- Don't commit anything you wouldn't want live immediately.
- `CNAME` (containing `www.lifetimegarageflooring.com`) is what maps the custom domain to GitHub Pages — don't remove, rename, or edit it, or the domain mapping breaks.
- There's no `.github/workflows/` — Pages builds straight from the branch, so nothing in Actions needs to pass before it goes live.

## Commands

There is no package manager, build step, linter, or test suite — this is hand-authored static HTML/CSS/JS served directly.

- **Local preview**: serve the repo root with any static file server, e.g. `python -m http.server 8000`, then open `http://localhost:8000/index.html`. Opening the HTML files directly (`file://`) also works since there are no server-side dependencies.
- **Deployment**: none needed — see Hosting above. Pushing to `main` is the deploy.

## Architecture

- Two pages only: `index.html` (home) and `about.html`. There is no templating system — the `<header>` and `<footer>` markup (nav links, phone number, address, social links) is duplicated verbatim in both files. Any change to shared header/footer content must be made by hand in both places.
- `style.css` holds only the overrides layered on top of Bootstrap 5.3.3 and Bootstrap Icons (both loaded from the jsdelivr CDN in `<head>`, not vendored). Layout is otherwise done with Bootstrap utility classes directly in the markup, not custom CSS.
- `app.js`: sets the footer copyright year and closes the mobile nav collapse on link click or outside click.
- `contact-form.js`: a self-contained widget that injects the "Request a Free Quote" form into any `<div id="contact-form-root">` via `innerHTML`, and submits to Web3Forms. The `WEB3FORMS_ACCESS_KEY` constant near the top of the file is a public Web3Forms site key — it's meant to be client-visible, not a secret. The form is two-step: step 1 (name/email/phone) is silently POSTed in the background the moment the visitor advances to step 2, so partial leads aren't lost if they abandon before finishing.
- `assets/` holds all images. Photos are stored as JPEG (re-encoded with Pillow, `optimize=True, progressive=True`, quality ~82); PNG is reserved for logo/mascot artwork that needs transparency. `favicon.ico`, `favicon-16x16.png`, `favicon-32x32.png`, and `apple-touch-icon.png` were generated from `assets/hero-standing.png` (the mascot) — regenerate from that source if the mascot art changes rather than hand-editing the icon files.
- `robots.txt`, `sitemap.xml`, the `<link rel="canonical">`/Open Graph/Twitter meta tags, and the `HomeAndConstructionBusiness` JSON-LD block in `index.html`'s `<head>` all hardcode `https://www.lifetimegarageflooring.com`. If the domain in `CNAME` ever changes, all of these need updating to match.
