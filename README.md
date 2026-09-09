# Content Manual

How to Create, Read, Update, and Delete pages and content on this site. See [CLAUDE.md](CLAUDE.md) for full architecture details — this is the quick task-oriented version.

**Golden rule:** never hand-edit `index.html`, `about.html`, `sitemap.xml`, or `robots.txt`. They're generated. Edit the source under `build/`, then run the build.

## One-time setup

```
pip install -r build/requirements.txt
```

## Live preview while editing

```
python build/watch.py
```

Rebuilds automatically whenever you save a `.jinja`/`.json` file under `build/`. Pair it with VS Code's Live Server extension (right-click `index.html` → "Open with Live Server") so the browser refreshes on its own. Or just rebuild manually and refresh:

```
python build/build.py
```

---

## Read: find where content lives

| You want to change... | Edit this file |
|---|---|
| Page text/sections | `build/pages/<slug>.jinja` |
| Page title, meta description, OG image, sitemap priority | `build/pages/<slug>.json` |
| Header nav links / logo | `build/templates/_header.jinja` |
| Footer content | `build/templates/_footer.jinja` |
| Business info (name, address, phone, hours) for search engines | `build/templates/_jsonld.jinja` |
| Site-wide layout, `<head>` tags, `extra_schema` block | `build/templates/base.jinja` |
| Reusable content sections (benefits grid, process steps, FAQ, testimonial, CTA band, related links) | `build/templates/_components.jinja` |
| Breadcrumb trail + `BreadcrumbList` schema | `build/templates/_breadcrumbs.jinja` |
| Colors, spacing, custom styling | `style.css` |
| Contact form behavior | `contact-form.js` |
| Images/photos | `assets/` |

## Update existing content

1. Edit the relevant file(s) from the table above.
2. Run `python build/build.py`.
3. Preview locally (see above), check it looks right.
4. Commit **both** the source file(s) and the regenerated `*.html`/`sitemap.xml`/`robots.txt` together.

## Create a new page

1. Decide the page's `canonical_path` — flat for a top-level page (`/about.html`) or nested for a category page (`/services/pressure-washing/`, `/locations/brandon/`, `/resources/<slug>/`). Nested paths must end in `/`; `build.py` derives the output file's path from this field (`"/services/pressure-washing/"` → `services/pressure-washing/index.html`), not from the source filename.
2. Pick a flat source slug that mirrors the URL without colliding with the generated output, e.g. `canonical_path: "/services/pressure-washing/"` → source files `services-pressure-washing.json` / `.jinja`.
3. Add `build/pages/<slug>.json`:
   ```json
   {
     "title": "Page Title | Lifetime Garage Flooring",
     "description": "One or two sentences for search results, ~150-160 chars.",
     "canonical_path": "/services/pressure-washing/",
     "og_image": "https://www.lifetimegarageflooring.com/assets/<some-image>.jpg",
     "is_home": false,
     "sitemap_priority": 0.8,
     "sitemap_changefreq": "monthly",
     "page_type": "service",
     "primary_keyword": "pressure washing Tampa Bay",
     "secondary_keywords": ["driveway pressure washing"],
     "schema_type": "Service",
     "breadcrumbs": null,
     "related_services": [],
     "related_locations": []
   }
   ```
   `page_type` (`service` / `location` / `resource` / `project` / `static`) determines which nav dropdown and index page, if any, auto-lists this page — see "Where pages get listed automatically" below. Leave `breadcrumbs: null` to auto-derive Home → … → Page Title from `canonical_path` segments, or supply an explicit `[{"label", "path"}, ...]` list if the auto-derived trail would point at an intermediate URL that doesn't actually exist (e.g. there's no `/services/` index, so service pages point their middle crumb at `/index.html#services` instead — copy the pattern from an existing `build/pages/services-*.json`).
4. Add `build/pages/<slug>.jinja`, composing the body from the shared macro library rather than hand-rolled markup:
   ```jinja
   {% extends "base.jinja" %}
   {% import "_components.jinja" as components %}
   {% block extra_schema %}
   <script type="application/ld+json">
   { "@context": "https://schema.org", "@type": "Service", "...": "..." }
   </script>
   {% endblock %}
   {% block content %}
     <main id="top">
       <!-- intro -->
       {{ components.benefits_grid([{"icon": "bi-shield-check", "title": "...", "text": "..."}]) }}
       {{ components.faq_accordion([{"question": "...", "answer": "..."}]) }}
       {{ components.cta_band("Ready to Get Started?", "#contact") }}
       {{ components.related_links("Explore Our Services", [{"href": "/services/...", "label": "..."}]) }}
     </main>
     <div id="contact-form-root"></div>
   {% endblock %}
   ```
   **Every `href`/`src` on the page must be root-relative** (`/assets/...`, `/services/...`, `#contact`), never relative to the current page — pages can render several directories deep, and a page-relative link would resolve against the wrong directory. `build/build.py --check` runs a path-integrity validator that rejects any that aren't.
5. If `page_type` is `service` or `location`, the page is automatically picked up by the header/footer Services/Locations dropdowns and columns — no manual nav edit needed. For other types, link to it manually from a relevant existing page (and/or the header/footer) so it isn't orphaned.
6. Run `python build/build.py`.
7. Run `python build/build.py --check` to confirm the generated output matches what you're about to commit and that the path validator passes.
8. Commit everything under `build/` plus the newly generated `.html` file(s) and updated `sitemap.xml`.

### Where pages get listed automatically

`build.py` passes every page's metadata into every template as a `pages` lookup dict. Three index pages, plus the header/footer nav, use it to render their entries by filtering on `page_type` — so adding a page of the right type is enough; no index-template or nav edits required:

| `page_type` | Auto-listed in |
|---|---|
| `service` | Header/footer Services dropdown & column |
| `location` | Header/footer Locations dropdown & column, `/locations/` index |
| `resource` | `/resources/` index |
| `project` | `/projects/` index (see "Create a new project" below) |

## Create a new project

Project pages need real details from the business owner before they're authored — location, square footage, service performed, a problem/solution narrative, real before/after photos, and a real testimonial. Don't write one speculatively or with placeholder claims; ask first if any of that is missing. (A generated gray placeholder image, `assets/placeholder-project-photo.jpg`, is fine to use temporarily if real photos aren't ready yet — mark the spot with a `<!-- TODO -->` comment so it's easy to find and swap out later.)

1. Pick a descriptive slug: `/projects/<descriptive-title>/`, e.g. `/projects/hotel-flake-epoxy-st-petersburg/`.
2. Add `build/pages/projects-<slug>.json` with `page_type: "project"`, `schema_type` (e.g. `"Article"`), and the project-specific fields the `/projects/` index card renders directly: `location`, `service`, `square_footage`, `scope_summary`.
3. Add `build/pages/projects-<slug>.jinja`, composing from the macro library, including the real testimonial via `{{ components.testimonial_quote(text, author) }}` and real (or clearly `TODO`-marked placeholder) before/after photos.
4. Run `python build/build.py` — the `/projects/` index picks up the new project automatically via the `pages` lookup dict; **no index-template changes are needed**.
5. Link the new project from its related service/location pages via `{{ components.related_links(...) }}` where relevant, so it's reachable from more than just the index.
6. Run `python build/build.py --check` before committing.

## Delete a page

1. Delete `build/pages/<slug>.json` and `build/pages/<slug>.jinja`.
2. If it was `page_type: service`/`location`, it disappears from nav/index pages automatically. Otherwise, remove any manual links to it (nav `<li>` in `build/templates/_header.jinja`/`_footer.jinja`, or `related_links` entries on other pages).
3. Delete the generated `.html` file (and its directory, for a nested page) from the repo.
4. Run `python build/build.py` to drop it from `sitemap.xml`.
5. Commit the deletions together.

## Images

- Photos: JPEG, re-encoded with Pillow (`optimize=True, progressive=True`, quality ~82).
- Logo/mascot artwork needing transparency: PNG.
- Favicons are generated from `assets/hero-standing.png` — regenerate from that source if the mascot changes, don't hand-edit the `.ico`/`.png` icon files.

## Before every commit

```
python build/build.py --check
```

This single command is the whole pre-commit gate — it does two checks in one pass:

1. **Drift check**: rebuilds every page in memory and diffs it against the committed output. Exits non-zero with a diff if generated output is stale or was hand-edited. Fix by rerunning `python build/build.py` (without `--check`) and committing the result.
2. **Path-integrity validator** (`build/path_validator.py`): scans every rendered page for any `href`/`src` that isn't root-relative (`/...`), a fragment (`#...`), absolute (`http(s)://...`), or `tel:`/`mailto:`. Exits non-zero with the offending page and path(s) if any internal link would break once rendered at its nested URL. Fix by changing the offending `href`/`src` to be root-relative, then rerun `--check`.

**Reminder:** this repo deploys straight from `main` via GitHub Pages — a commit to `main` is live within a minute or two. There's no staging.
