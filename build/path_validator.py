"""Path-integrity validator for rendered HTML output.

Flags any href/src attribute value that is not root-relative ("/..."), a
fragment ("#..."), an absolute URL ("http(s)://..."), or a tel:/mailto: link.
This is the regression guard for the root-relative path convention adopted
in issue 001: a page that slips back to a page-relative path (e.g.
"assets/x.jpg" instead of "/assets/x.jpg") would resolve incorrectly once
rendered below the repo root, and this module is what catches that during
`build.py --check`.

Runs standalone (`python build/path_validator.py`) against the fixture
strings below, or importable via `validate`/`validate_outputs` for use from
another script.
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


# --- TEMPORARY fixtures (issue 006) -----------------------------------------
# Prove the validator catches a broken relative path and passes a correct
# root-relative one. Remove this block (see issues/019) once real pages
# exercise the same validation paths.
_FIXTURE_BAD_HTML = '<img src="assets/foo.jpg" alt="broken">'
_FIXTURE_GOOD_HTML = """
<a href="/about.html">About</a>
<a href="#contact">Contact</a>
<a href="https://example.com">External</a>
<a href="tel:+18132134050">Call</a>
<a href="mailto:info@example.com">Email</a>
<img src="/assets/foo.jpg" alt="ok">
"""


def _run_fixture_self_test():
    ok_bad, offenders_bad = validate(_FIXTURE_BAD_HTML)
    assert not ok_bad and offenders_bad == ["assets/foo.jpg"], (
        f"expected the bad fixture to be flagged, got offenders={offenders_bad}"
    )
    ok_good, offenders_good = validate(_FIXTURE_GOOD_HTML)
    assert ok_good and offenders_good == [], (
        f"expected the good fixture to pass clean, got offenders={offenders_good}"
    )
    print("path_validator self-test OK: bad fixture flagged, good fixture passed clean.")
# --- end TEMPORARY fixtures --------------------------------------------------


if __name__ == "__main__":
    _run_fixture_self_test()
