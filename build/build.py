import json, sys, difflib
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

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


def load_pages():
    for json_path in sorted((BUILD / "pages").glob("*.json")):  # deterministic order
        slug = json_path.stem
        meta = json.loads(json_path.read_text())
        yield slug, meta


def render_page(slug, meta):
    template = env.get_template(f"{slug}.jinja")
    logo_href = "#header" if meta["is_home"] else "index.html"
    canonical_url = SITE_BASE_URL + meta["canonical_path"]
    rendered = template.render(
        title=meta["title"], description=meta["description"],
        canonical_url=canonical_url, og_image=meta["og_image"],
        logo_href=logo_href,
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


def main():
    pages = list(load_pages())
    outputs = {f"{slug}.html": render_page(slug, meta) for slug, meta in pages}
    outputs["sitemap.xml"] = build_sitemap(pages)
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
            target.write_bytes(content.encode("utf-8"))
            print(f"wrote {filename}")
    if check:
        sys.exit(1) if drift else print(f"OK: {len(outputs)} file(s) match committed output.")


if __name__ == "__main__":
    main()
