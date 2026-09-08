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
| Site-wide layout, `<head>` tags | `build/templates/base.jinja` |
| Colors, spacing, custom styling | `style.css` |
| Contact form behavior | `contact-form.js` |
| Images/photos | `assets/` |

## Update existing content

1. Edit the relevant file(s) from the table above.
2. Run `python build/build.py`.
3. Preview locally (see above), check it looks right.
4. Commit **both** the source file(s) and the regenerated `*.html`/`sitemap.xml`/`robots.txt` together.

## Create a new page

1. Add `build/pages/<slug>.json`:
   ```json
   {
     "title": "Page Title | Lifetime Garage Flooring",
     "description": "One or two sentences for search results, ~150-160 chars.",
     "canonical_path": "/<slug>.html",
     "og_image": "https://www.lifetimegarageflooring.com/assets/<some-image>.jpg",
     "is_home": false,
     "sitemap_priority": 0.8,
     "sitemap_changefreq": "monthly"
   }
   ```
2. Add `build/pages/<slug>.jinja`:
   ```jinja
   {% extends "base.jinja" %}
   {% block content %}
   <!-- page markup using Bootstrap utility classes -->
   {% endblock %}
   ```
3. Add a nav `<li>` for it in `build/templates/_header.jinja` (if it should appear in navigation).
4. Run `python build/build.py` — this generates `<slug>.html` and adds the page to `sitemap.xml` automatically.
5. Commit everything under `build/` plus the new `<slug>.html` and updated `sitemap.xml`.

## Delete a page

1. Delete `build/pages/<slug>.json` and `build/pages/<slug>.jinja`.
2. Remove its nav `<li>` from `build/templates/_header.jinja` if present.
3. Delete the generated `<slug>.html` from the repo root.
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

Exits non-zero with a diff if generated output is stale or was hand-edited. Fix by rerunning `python build/build.py` (without `--check`) and committing the result.

**Reminder:** this repo deploys straight from `main` via GitHub Pages — a commit to `main` is live within a minute or two. There's no staging.
