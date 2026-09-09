"""Path-integrity validator for rendered HTML output.

Flags any href/src attribute value that is not root-relative ("/..."), a
fragment ("#..."), an absolute URL ("http(s)://..."), or a tel:/mailto: link.
This is the regression guard for the root-relative path convention adopted
in issue 001: a page that slips back to a page-relative path (e.g.
"assets/x.jpg" instead of "/assets/x.jpg") would resolve incorrectly once
rendered below the repo root, and this module is what catches that during
`build.py --check`.

Importable via `validate`/`validate_outputs` — pass any HTML string to
`validate()` to check it in isolation, independent of the full build.
"""
import re

ATTR_RE = re.compile(r'\b(?:href|src)\s*=\s*"([^"]*)"')


def is_allowed_path(path):
    return (
        path.startswith("/")
        or path.startswith("#")
        or path.startswith("http://")
        or path.startswith("https://")
        or path.startswith("tel:")
        or path.startswith("mailto:")
    )


def find_offending_paths(html):
    """Return the href/src values in `html` that fail the root-relative rule."""
    return [path for path in ATTR_RE.findall(html) if not is_allowed_path(path)]


def validate(html):
    """Validate a single rendered HTML string. Returns (ok, offending_paths)."""
    offenders = find_offending_paths(html)
    return not offenders, offenders


def validate_outputs(outputs):
    """Validate a {filename: html_content} mapping, e.g. build.py's rendered outputs.

    Returns {filename: [offending_paths]} for files with at least one offense.
    """
    failures = {}
    for filename, content in outputs.items():
        if not filename.endswith(".html"):
            continue
        ok, offenders = validate(content)
        if not ok:
            failures[filename] = offenders
    return failures
