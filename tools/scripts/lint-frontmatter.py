#!/usr/bin/env python3
import sys, os, re, yaml

REQUIRED_FOR_BOOKS = [
    "title","kind","status","audience","hub","canonical_repo","summary","citation"
]

# Citation must contain these strings
CITATION_REQUIRED_TEXTS = ["rolodexter/ai Portal", "github.com/rolodexter/ai"]
VALID_KINDS = {"textbook","monograph"}
BOOK_ROOTS = ("docs/textbooks", "docs/monographs")
TARGET_FILENAMES = ("index.md",)
ATOMS_ROOT = "docs/atoms"

def is_book_page(path):
    norm_path = path.replace("\\","/")
    if not os.path.basename(norm_path) in TARGET_FILENAMES:
        return False
    for root in BOOK_ROOTS:
        if norm_path.startswith(root):
            return True
    return False
    
def is_atom_page(path):
    return path.replace("\\","/").startswith(ATOMS_ROOT) and not path.endswith("_BOOK.md") and not path.endswith("_PAPER.md")

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
        # Skip files that aren't books or atoms
        if not (is_book_page(path) or is_atom_page(path)):
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
            
        # Check citation field contains required text
        citation = fm.get("citation", "")
        for required_text in CITATION_REQUIRED_TEXTS:
            if required_text not in citation:
                print(f"[lint] {path} citation does not contain '{required_text}'")
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
