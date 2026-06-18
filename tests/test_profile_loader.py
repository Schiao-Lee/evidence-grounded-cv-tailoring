"""Tests for profile_loader: the zero-dependency YAML parser + pattern builders."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import profile_loader as pl  # noqa: E402

SAMPLE = """
candidate:
  name: "ALEX KOWALSKI"
  phone_digits: "600 100 200"
  email: "alex@example.com"
languages:
  - { name: "English", level: "C1" }
  - { name: "Polish", level: "Native" }
language_exclusions:
  - "Spanish"
education:
  institution: "University of Warsaw"
  degree: "MSc, Data Science & Business Analytics"
"""


def _p():
    # Exercise the built-in fallback parser directly (no PyYAML needed).
    return pl._minimal_yaml(SAMPLE)


def test_minimal_yaml_scalars_and_nested_maps():
    p = _p()
    assert p["candidate"]["name"] == "ALEX KOWALSKI"
    assert p["candidate"]["email"] == "alex@example.com"
    assert p["education"]["institution"] == "University of Warsaw"


def test_inline_flow_maps_and_block_lists():
    p = _p()
    assert {l["name"] for l in p["languages"]} == {"English", "Polish"}
    assert p["language_exclusions"] == ["Spanish"]


def test_language_patterns_match_pdf_text():
    pats = pl.language_patterns(_p())
    assert re.search(pats["English (C1)"], "english (c1)")
    assert re.search(pats["Polish (Native)"], "polish native")


def test_contact_and_education_patterns_match():
    p = _p()
    contact = pl.contact_patterns(p)
    assert any(re.search(v, "reach me at 600-100-200") for v in contact.values())
    edu = pl.education_patterns(p)
    assert any(re.search(v, "university of warsaw") for v in edu.values())


def test_exclusions_passthrough():
    assert pl.language_exclusions(_p()) == ["Spanish"]


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
    print("ALL PASS")
