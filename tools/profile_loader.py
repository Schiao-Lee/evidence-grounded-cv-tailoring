#!/usr/bin/env python3
"""
profile_loader.py — load profile.yaml and build the personal QA patterns.

This is the single place that turns YOUR facts (profile.yaml) into the
regexes the QA gate uses. No personal data lives in qa_one_job.py anymore.

Uses PyYAML if installed; otherwise falls back to a small built-in parser that
handles the simple profile.yaml schema (so the kit runs with zero dependencies).
For full YAML in your own files: pip install pyyaml
"""

import re
import sys
from pathlib import Path

try:
    import yaml
    _HAVE_YAML = True
except ImportError:  # zero-dependency fallback
    yaml = None
    _HAVE_YAML = False


def _strip_comment(s: str) -> str:
    """Drop a trailing # comment that is not inside quotes."""
    out, quote = [], None
    for ch in s:
        if quote:
            out.append(ch)
            if ch == quote:
                quote = None
        elif ch in ('"', "'"):
            quote = ch
            out.append(ch)
        elif ch == "#":
            break
        else:
            out.append(ch)
    return "".join(out)


def _unquote(v: str) -> str:
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in ('"', "'"):
        return v[1:-1]
    return v


def _minimal_yaml(text: str) -> dict:
    """Parse the controlled profile.yaml schema: top-level keys -> scalars,
    nested 2-space maps, block lists of scalars, and inline {k: v, ...} maps."""
    root, cur_key, cur_val = {}, None, None
    for raw in text.splitlines():
        line = _strip_comment(raw).rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        stripped = line.strip()
        if indent == 0:
            key, _, rest = stripped.partition(":")
            key, rest = key.strip(), rest.strip()
            if rest:
                root[key] = _unquote(rest)
                cur_key, cur_val = None, None
            else:
                cur_key, cur_val = key, None
        elif stripped.startswith("- "):
            item = stripped[2:].strip()
            if not isinstance(cur_val, list):
                cur_val = root[cur_key] = []
            if item.startswith("{") and item.endswith("}"):
                d = {}
                for pair in item[1:-1].split(","):
                    if ":" in pair:
                        k, _, v = pair.partition(":")
                        d[k.strip()] = _unquote(v)
                cur_val.append(d)
            else:
                cur_val.append(_unquote(item))
        else:
            k, _, v = stripped.partition(":")
            if not isinstance(cur_val, dict):
                cur_val = root[cur_key] = {}
            cur_val[k.strip()] = _unquote(v)
    return root


def find_kit_root(start: Path = None) -> Path:
    """Walk up from `start` until we find profile.yaml (preferred) or the kit
    markers, so tools work no matter which subfolder they run from."""
    start = (start or Path(__file__)).resolve()
    for d in [start, *start.parents]:
        if (d / "profile.yaml").is_file():
            return d
        if (d / "profile.example.yaml").is_file() or (d / "CLAUDE.md").is_file():
            return d
    return Path.cwd()


def load_profile(path: Path = None) -> dict:
    """Load profile.yaml; fall back to profile.example.yaml with a warning."""
    if path is None:
        root = find_kit_root()
        path = root / "profile.yaml"
        if not path.is_file():
            example = root / "profile.example.yaml"
            if example.is_file():
                print(
                    f"NOTE: {path.name} not found — using {example.name}. "
                    "Copy it to profile.yaml and fill in your own facts.",
                    file=sys.stderr,
                )
                path = example
    if not Path(path).is_file():
        raise FileNotFoundError(f"profile not found: {path}")
    text = Path(path).read_text(encoding="utf-8")
    if _HAVE_YAML:
        return yaml.safe_load(text) or {}
    return _minimal_yaml(text)


# --- pattern builders (mirror the old hardcoded dicts, now data-driven) -------

def _loose(text: str) -> str:
    """Tokens joined so spaces/&/punctuation between words don't matter."""
    tokens = re.findall(r"[a-z0-9+]+", text.lower())
    return r"[\s&,\.]*".join(re.escape(t) for t in tokens)


def language_patterns(profile: dict) -> dict:
    out = {}
    for lang in profile.get("languages", []):
        name, level = lang.get("name", ""), lang.get("level", "")
        label = f"{name} ({level})" if level else name
        pat = _loose(name)
        if level:
            pat += r"\s*\(?\s*" + re.escape(level.lower()) + r"\s*\)?"
        out[label] = pat
    return out


def contact_patterns(profile: dict) -> dict:
    c = profile.get("candidate", {})
    out = {}
    digits = re.findall(r"\d+", c.get("phone_digits", "") or c.get("phone_display", ""))
    if digits:
        out[f"phone ({c.get('phone_display', ' '.join(digits))})"] = r"[\s\-]*".join(digits)
    email = c.get("email", "")
    if email:
        out[f"email ({email})"] = re.escape(email.lower()).replace(r"\.", r"\.")
    return out


def education_patterns(profile: dict) -> dict:
    e = profile.get("education", {})
    out = {}
    inst = e.get("institution", "")
    if inst:
        out[f"institution: {inst}"] = _loose(inst)
    degree = e.get("degree", "")
    if degree:
        # match the field-of-study (after the first comma) if present, else whole
        field = degree.split(",", 1)[1] if "," in degree else degree
        out[f"degree: {field.strip()}"] = _loose(field)
    return out


def education_entry_pattern(profile: dict) -> str:
    inst = profile.get("education", {}).get("institution", "")
    return r"\\entry\{" + re.escape(inst) + r"\}" if inst else ""


def language_exclusions(profile: dict) -> list:
    return list(profile.get("language_exclusions", []) or [])


if __name__ == "__main__":
    # Quick self-check: print the patterns that would be enforced.
    p = load_profile()
    print("languages:", language_patterns(p))
    print("contact:  ", contact_patterns(p))
    print("education:", education_patterns(p))
    print("entry:    ", education_entry_pattern(p))
    print("excluded: ", language_exclusions(p))
