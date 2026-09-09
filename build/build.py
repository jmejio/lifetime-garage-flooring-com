import json, sys, difflib
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from path_validator import validate_outputs

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
SITE_BASE_URL = "https://www.lifetimegarageflooring.com"

# Line endings are forced explicitly per output file so the build produces
# byte-identical output regardless of what OS runs it. The committed
# index.html/about.html use CRLF throughout, while sitemap.xml uses bare LF
# throughout — a pre-existing repo inconsistency, preserved rather than fixed.
HTML_NEWLINE = "\r\n"
SITEMAP_NEWLINE = "\n"

env = Environment(
    loader=FileSystemLoader([str(BUILD / "pages"), str(BUILD / "templates")]),
    autoescape=select_autoescape(["html"]),
    trim_blocks=True,
    lstrip_blocks=True,
    keep_trailing_newline=True,
)


# build/pages/<slug>.json schema:
#   title, description, canonical_path, og_image, is_home,
#   sitemap_priority, sitemap_changefreq  (original fields)
#   page_type          "home" | "service" | "location" | "resource" | "project" | "static"
#   primary_keyword    str   — reasoned SEO target, not measured search-volume data
#   secondary_keywords list[str]
#   schema_type        str | null — extra_schema JSON-LD @type for this page (e.g. "Service",
#                       "LocalBusiness", "Article"), or null when the page adds no extra schema
#                       beyond the sitewide HomeAndConstructionBusiness block
#   breadcrumbs        list[{"label": str, "path": str}] | null — null means derive from
#                       canonical_path segments instead of listing explicitly
#   related_services   list[str] — slugs into build/pages/
#   related_locations  list[str] — slugs into build/pages/
# Project pages (page_type: "project") additionally carry: location, service,
# square_footage, scope_summary.
def load_pages():
    for json_path in sorted((BUILD / "pages").glob("*.json")):  # deterministic order
        slug = json_path.stem
        meta = json.loads(json_path.read_text())
        yield slug, meta


def build_pages_lookup(pages):
    return {
        slug: {
            "title": meta["title"], "canonical_path": meta["canonical_path"],
            "page_type": meta["page_type"], "description": meta["description"],
        }
        for slug, meta in pages
    }


def _display_title(title):
    # Page titles are "<Page Name> | Lifetime Garage Flooring"; breadcrumbs
    # only want the page-specific half.
    return title.split(" | ")[0]


def compute_breadcrumbs(meta, pages):
    if meta.get("breadcrumbs") is not None:
        return meta["breadcrumbs"]
    if meta["canonical_path"] == "/":
        return []
    segments = [s for s in meta["canonical_path"].split("/") if s]
    by_path = {p["canonical_path"]: p["title"] for p in pages.values()}
    trail = [{"label": "Home", "path": "/"}]
    running = ""
    for seg in segments[:-1]:
        running += "/" + seg
        title = by_path.get(running) or by_path.get(running + "/")
        label = _display_title(title) if title else seg.replace("-", " ").title()
        trail.append({"label": label, "path": running + "/"})
    trail.append({"label": _display_title(meta["title"]), "path": meta["canonical_path"]})
    return trail


def output_path_for(canonical_path):
    if canonical_path == "/":
        return "index.html"
    path = canonical_path.lstrip("/")
    if path.endswith("/"):
        return path + "index.html"
    return path


def render_page(slug, meta, pages):
    template = env.get_template(f"{slug}.jinja")
    logo_href = "#header" if meta["is_home"] else "/index.html"
    canonical_url = SITE_BASE_URL + meta["canonical_path"]
    rendered = template.render(
        title=meta["title"], description=meta["description"],
        canonical_url=canonical_url, og_image=meta["og_image"],
        logo_href=logo_href, site_base_url=SITE_BASE_URL,
        pages=pages, breadcrumb_trail=compute_breadcrumbs(meta, pages),
    )
    # Jinja always renders with \n; convert to this output's real line ending.
    return rendered.replace("\n", HTML_NEWLINE)


def build_sitemap(pages):
    ordered = sorted(pages, key=lambda p: (-p[1]["sitemap_priority"], p[0]))
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for slug, meta in ordered:
        loc = SITE_BASE_URL + meta["canonical_path"]
        lines += ["  <url>", f"    <loc>{loc}</loc>",
                  f"    <changefreq>{meta['sitemap_changefreq']}</changefreq>",
                  f"    <priority>{meta['sitemap_priority']}</priority>", "  </url>"]
    lines.append("</urlset>")
    return SITEMAP_NEWLINE.join(lines) + SITEMAP_NEWLINE


def build_robots():
    lines = ["User-agent: *", "Allow: /", "", f"Sitemap: {SITE_BASE_URL}/sitemap.xml"]
    return SITEMAP_NEWLINE.join(lines) + SITEMAP_NEWLINE


def main():
    pages = list(load_pages())
    pages_lookup = build_pages_lookup(pages)
    outputs = {output_path_for(meta["canonical_path"]): render_page(slug, meta, pages_lookup) for slug, meta in pages}
    outputs["sitemap.xml"] = build_sitemap(pages)
    outputs["robots.txt"] = build_robots()
    check = "--check" in sys.argv
    drift = False
    for filename, content in outputs.items():
        target = ROOT / filename
        existing = target.read_bytes().decode("utf-8") if target.exists() else ""
        if check:
            if existing != content:
                drift = True
                print("".join(difflib.unified_diff(
                    existing.splitlines(keepends=True), content.splitlines(keepends=True),
                    fromfile=f"committed/{filename}", tofile=f"generated/{filename}")))
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content.encode("utf-8"))
            print(f"wrote {filename}")
    if check:
        path_failures = validate_outputs(outputs)
        for filename, offenders in path_failures.items():
            drift = True
            print(f"PATH INTEGRITY: {filename} has non-root-relative internal path(s): {offenders}")
        if drift:
            sys.exit(1)
        print(f"OK: {len(outputs)} file(s) match committed output.")


if __name__ == "__main__":
    main()
