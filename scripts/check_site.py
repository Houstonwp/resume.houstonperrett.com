#!/usr/bin/env python3
"""Offline checks for the production output. Run after hugo --gc --minify."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
import re
import sys
import tomllib
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "public"
CONFIG = tomllib.loads((ROOT / "config.toml").read_text())
BASE = CONFIG["baseURL"]

class Document(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.tags = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

    def attrs(self, tag):
        return [attrs for name, attrs in self.tags if name == tag]

    def meta(self, key):
        return [attrs.get("content", "") for attrs in self.attrs("meta")
                if attrs.get("name", attrs.get("property")) == key]

    def canonical(self):
        return [attrs.get("href") for attrs in self.attrs("link")
                if "canonical" in attrs.get("rel", "").split()]


def local_exists(url, page_url=BASE):
    parsed = urlsplit(urljoin(page_url, url))
    if parsed.scheme not in ("http", "https") or parsed.netloc != urlsplit(BASE).netloc:
        return True  # Network-dependent links are outside this offline smoke check.
    path = PUBLIC / unquote(parsed.path).lstrip("/")
    return path.is_file() or (path / "index.html").is_file()

assert PUBLIC.is_dir(), f"Build directory missing: {PUBLIC}"
html_files = list(PUBLIC.rglob("*.html"))
assert html_files, "No HTML output"
for path in html_files:
    text = path.read_text()
    doc = Document(text)
    page_url = urljoin(BASE, path.relative_to(PUBLIC).as_posix())
    for tag, attrs in doc.tags:
        # Check generated internal navigation, CSS, images, scripts and feed links.
        attr = "src" if tag in ("img", "script", "source") else "href" if tag in ("a", "link") else None
        if attr and attrs.get(attr):
            assert local_exists(attrs[attr], page_url), f"{path}: missing {attrs[attr]}"

home_text = (PUBLIC / "index.html").read_text()
home = Document(home_text)
assert home.canonical() == [BASE], home.canonical()
assert home.attrs("html")[0].get("lang", "").startswith("en")
assert home.meta("viewport") and "width=device-width" in home.meta("viewport")[0]
assert any("charset" in attrs for attrs in home.attrs("meta"))

assert BASE == "https://resume.houstonp.com/"
assert home.meta("description") == [CONFIG["params"]["description"]]
for typo in ("transctions", "accomodate", "Softwares", "five presentation at"):
    assert typo not in home_text, f"Uncorrected typo: {typo}"
for correction in ("transactions", "accommodate", "Software", "five presentations", "Present"):
    assert correction in home_text, f"Missing correction: {correction}"
assert "Work Experience" in home_text and "Education" in home_text
assert home_text.index("Work Experience") < home_text.index("Education")
assert "2024" in home_text and "$50 million" in home_text, "Retain substantive resume content"
assert any("responsive" in a.get("href", "") for a in home.attrs("link"))
print(f"PASS: {len(html_files)} HTML file(s), local links/assets, resume metadata, proofreading, theme order")
