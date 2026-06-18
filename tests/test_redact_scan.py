"""Tests for the redaction scanner."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import redact_scan as rs  # noqa: E402


def test_example_emails_are_safe_but_real_ones_are_not():
    assert rs.is_safe_email("someone@example.com")
    assert rs.is_safe_email("a@sub.example.org")
    assert not rs.is_safe_email("someone@gmail.com")


def test_detects_real_email_and_phone():
    d = Path(tempfile.mkdtemp())
    f = d / "leak.txt"
    f.write_text("contact jane@realcorp.com or 555-123-4567\n")
    kinds = {kind for kind, _, _ in rs.scan_file(f, [])}
    assert "email" in kinds
    assert "phone" in kinds


def test_clean_file_has_no_hits():
    d = Path(tempfile.mkdtemp())
    f = d / "ok.txt"
    f.write_text("plain text; demo email someone@example.com is fine\n")
    assert rs.scan_file(f, []) == []


def test_deny_term_is_flagged():
    d = Path(tempfile.mkdtemp())
    f = d / "doc.txt"
    f.write_text("written by J. Smith\n")
    kinds = {kind for kind, _, _ in rs.scan_file(f, ["J. Smith"])}
    assert "deny-term" in kinds


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
    print("ALL PASS")
