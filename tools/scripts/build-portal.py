#!/usr/bin/env python3
import os, re, json, datetime, yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
ATOMS = DOCS / "atoms"
BOOKS = [DOCS / "textbooks", DOCS / "monographs"]
GENERATED = DOCS / "_generated"
HUBS = ["learn","build","govern","apply","research","tools"]
LANE_LIMIT = 7

FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)

def read_md_frontmatter(path: Path):
    txt = path.read_text(encoding="utf-8")
    m = FM_RE.match(txt)
    if not m:
        return None, txt
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except Exception as e:
        fm = None
    body = txt[m.end():]
    return fm, body

def iter_atom_files():
    for p in ATOMS.rglob("*.md"):
        yield p
    for root in BOOKS:
        if root.exists():
            for p in root.rglob("index.md"):
                yield p

def parse_date(s):
    try:
        return datetime.datetime.fromisoformat(str(s))
    except Exception:
        return None

def normalize_item(path: Path, fm: dict):
    if not fm: return None
    hub = str(fm.get("hub","")).lower()
    if hub not in HUBS: return None
    lanes = fm.get("lanes") or []
    if isinstance(lanes, str): lanes = [lanes]
    added = parse_date(fm.get("added"))
    return {
        "title": fm.get("title","Untitled"),
        "kind": fm.get("kind","note"),
        "hub": hub,
        "lanes": [str(x).lower() for x in lanes],
        "audience": fm.get("audience"),
        "tags": fm.get("tags") or [],
        "added": fm.get("added"),
        "added_dt": added.isoformat() if added else None,
        "starter": bool(fm.get("starter", False)),
        "summary": (fm.get("summary") or "").strip().splitlines()[0:1],
        "path": str(path.relative_to(DOCS)).replace("\\","/"),
    }

def collect_items():
    items = []
    for p in iter_atom_files():
        fm, _ = read_md_frontmatter(p)
        item = normalize_item(p, fm)
        if item: items.append(item)
    return items

def write_generated_index(items):
    GENERATED.mkdir(parents=True, exist_ok=True)
    out = GENERATED / "index.json"
    
    # Create a custom JSON encoder to handle date objects
    class DateTimeEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (datetime.date, datetime.datetime)):
                return obj.isoformat()
            return super().default(obj)
    
    with out.open("w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, cls=DateTimeEncoder)
    print(f"[portal] wrote {out}")

def filter_hub(items, hub):
    return [x for x in items if x["hub"] == hub]

def latest(items, days=3, limit=6):
    now = datetime.datetime.now()
    cutoff = now - datetime.timedelta(days=days)
    dated = []
    for x in items:
        try:
            dt = datetime.datetime.fromisoformat(x["added"])
            if dt >= cutoff: dated.append((dt, x))
        except Exception:
            continue
    dated.sort(key=lambda t: t[0], reverse=True)
    return [x for _, x in dated[:limit]]

def top_starters(items, limit=6):
    return [x for x in items if x["starter"]][:limit]

def lanes_for_hub(items, hub):
    # frequency count
    freq = {}
    for x in items:
        for lane in x["lanes"]:
            freq[lane] = freq.get(lane, 0) + 1
    # pick top LANE_LIMIT lanes
    return [k for k,_ in sorted(freq.items(), key=lambda kv: kv[1], reverse=True)[:LANE_LIMIT]]

def render_list(items):
    out = []
    for x in items:
        out.append(f"- [{x['title']}](/{x['path']}) — {x['summary'][0] if x['summary'] else ''}")
    return "\n".join(out) if out else "_(none yet)_"

def replace_block(md, name, new_content):
    start = f"<!-- START:{name} -->"
    end   = f"<!-- END:{name} -->"
    if start not in md or end not in md:
        # insert at end if markers missing
        return md + f"\n\n{start}\n{new_content}\n{end}\n"
    return re.sub(
        rf"{re.escape(start)}.*?{re.escape(end)}",
        f"{start}\n{new_content}\n{end}",
        md,
        flags=re.S
    )

def update_hub(hub, items):
    hub_md = DOCS / "hubs" / hub / "README.md"
    if not hub_md.exists():
        return
    md = hub_md.read_text(encoding="utf-8")

    hub_items = filter_hub(items, hub)
    starters = top_starters(hub_items)
    today = latest(hub_items)

    # Lanes
    chosen_lanes = lanes_for_hub(hub_items, hub)
    lane_blocks = []
    for lane in chosen_lanes:
        lane_items = [x for x in hub_items if lane in x["lanes"]]
        lane_items = sorted(
            lane_items, key=lambda x: x.get("added_dt") or "", reverse=True
        )[:5]
        lane_blocks.append(f"### {lane.title()}\n{render_list(lane_items)}")
    lanes_md = "\n\n".join(lane_blocks) if lane_blocks else "_(no lanes yet)_"

    md = replace_block(md, "START-HERE", render_list(starters))
    md = replace_block(md, "TODAY", render_list(today))
    md = replace_block(md, "LANES", lanes_md)
    hub_md.write_text(md, encoding="utf-8")
    print(f"[portal] updated {hub_md}")

def main():
    items = collect_items()
    write_generated_index(items)
    for hub in HUBS:
        update_hub(hub, items)
    print("[portal] done")

if __name__ == "__main__":
    main()
