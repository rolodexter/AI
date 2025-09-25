import os, sys, argparse, pathlib

EXCLUDES = {'.git', 'node_modules', '.venv', '.tox', '.cache', '.pytest_cache', '.DS_Store'}

def tag(name):
    ext = pathlib.Path(name).suffix.lower()
    if name.lower() == 'license' or name.lower().startswith('license'):
        return '(license)'
    if ext in ('.md',): return '(md)'
    if ext in ('.py',): return '(py)'
    if ext in ('.yml', '.yaml'): return '(yml)'
    if ext in ('.json',): return '(json)'
    if ext in ('.js', '.mjs', '.cjs'): return '(js)'
    if ext in ('.ps1',): return '(ps1)'
    if ext in ('.txt',): return '(txt)'
    return ''

def is_excluded(p: pathlib.Path):
    parts = set(p.parts)
    return any(x in EXCLUDES for x in parts)

def build_tree(root: pathlib.Path):
    # Build a nested dict {name: subtree or None for files}
    def helper(p: pathlib.Path):
      if p.is_dir():
          if p.name in EXCLUDES: return None
          entries = []
          for child in sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
              if is_excluded(child): continue
              node = helper(child)
              if node is not None:
                  entries.append((child.name, node))
          return entries
      else:
          return None
    return (root.name, helper(root))

def render_tree(node, prefix=""):
    name, children = node
    lines = [f"{name}/"]
    def rec(children, prefix):
        last_idx = len(children) - 1
        for i, (name, subtree) in enumerate(children):
            connector = "└── " if i == last_idx else "├── "
            if subtree is None:
                lines.append(f"{prefix}{connector}{name} {tag(name)}".rstrip())
            else:
                lines.append(f"{prefix}{connector}{name}/")
                new_prefix = f"{prefix}{'    ' if i == last_idx else '│   '}"
                rec(subtree, new_prefix)
    if children: rec(children, "")
    return "\n".join(lines)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Repo root")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    node = build_tree(root)
    # Handle Windows encoding issues
    try:
        print(render_tree(node))
    except UnicodeEncodeError:
        # Use sys.stdout.buffer to write UTF-8 bytes
        sys.stdout.buffer.write(render_tree(node).encode('utf-8'))
