#!/usr/bin/env python3
import sys, os, re, yaml

REQUIRED_FOR_BOOKS = [
    "title","kind","status","audience","hub","canonical_repo","summary"
]
VALID_KINDS = {"textbook","monograph"}
BOOK_ROOTS = ("docs/textbooks", "docs/monographs")
TARGET_FILENAMES = ("index.md",)

def is_book_page(path):
    if not path.replace("\\","/").endswith(TARGET_FILENAMES):
        return False
    return path.replace("\\","/").startswith(BOOK_ROOTS)

def extract_frontmatter(md):
    m = re.match(r"^---\n(.*?)\n---\n", md, flags=re.S)
    if not m:
        return None
    try:
        return yaml.safe_load(m.group(1)) or {}
    except Exception as e:
        print(f"[lint] YAML parse error: {e}")
        return None

def walk_md_files(root):
    for base, _, files in os.walk(root):
        for f in files:
            if f.endswith(".md"):
                yield os.path.join(base, f)

def main():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..",".."))
    repo = root
    failures = 0
    for path in walk_md_files(repo):
        if not is_book_page(path):
            continue
        with open(path, "r", encoding="utf-8") as fh:
            txt = fh.read()
        fm = extract_frontmatter(txt)
        if fm is None:
            print(f"[lint] Missing frontmatter: {path}")
            failures += 1
            continue
        missing = [k for k in REQUIRED_FOR_BOOKS if k not in fm or fm[k] in ("", None, [])]
        if missing:
            print(f"[lint] {path} missing keys: {missing}")
            failures += 1
        if fm.get("kind") not in VALID_KINDS:
            print(f"[lint] {path} invalid kind: {fm.get('kind')}")
            failures += 1
        # discourage long bodies (map-only)
        body = re.sub(r"^---\n.*?\n---\n", "", txt, flags=re.S).strip()
        if len(body.split()) > 1000:
            print(f"[lint] {path} body too long (>1000 words) — maps only.")
            failures += 1
    if failures:
        print(f"[lint] FAILED with {failures} issue(s).")
        sys.exit(1)
    print("[lint] OK")
    return 0

if __name__ == "__main__":
    sys.exit(main())
