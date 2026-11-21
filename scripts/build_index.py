"""Build reels.json and the table in README.md from every <folder>/reel.json.

    python scripts/build_index.py          # rewrite reels.json and README.md
    python scripts/build_index.py --check  # fail if they are out of date (CI)

labs.stacklor.com can read reels.json to show "Watch the reel" and
"Get the code" links next to each simulation.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO_URL = "https://github.com/amalsam/stacklor-reels/tree/main"
LABS_URL = "https://labs.stacklor.com"
REQUIRED = ["title", "date", "summary", "language"]
FOLDER_RE = re.compile(r"^\d{4}-\d{2}-[a-z0-9]+(-[a-z0-9]+)*$")
START, END = "<!-- reels:start -->", "<!-- reels:end -->"


def load_reels():
    reels, errors = [], []
    for meta in sorted(ROOT.glob("*/reel.json")):
        folder = meta.parent.name
        if folder.startswith("_"):
            continue
        if not FOLDER_RE.match(folder):
            errors.append(f"{folder}: folder must look like YYYY-MM-short-name")
        try:
            data = json.loads(meta.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            errors.append(f"{folder}/reel.json: {e}")
            continue
        for key in REQUIRED:
            if not data.get(key):
                errors.append(f"{folder}/reel.json: missing '{key}'")
        if not (meta.parent / "README.md").exists():
            errors.append(f"{folder}: missing README.md")
        reels.append({
            "folder": folder,
            "code": f"{REPO_URL}/{folder}",
            "title": data.get("title", ""),
            "date": data.get("date", ""),
            "summary": data.get("summary", ""),
            "language": data.get("language", ""),
            "tags": data.get("tags", []),
            "instagram": data.get("instagram"),
            "youtube": data.get("youtube"),
            "labs": data.get("labs", []),
        })
    reels.sort(key=lambda r: r["folder"], reverse=True)  # newest first
    return reels, errors


def table(reels):
    rows = ["| Date | Reel | Language | Watch | Play in browser |", "| --- | --- | --- | --- | --- |"]
    for r in reels:
        watch = " · ".join(
            f"[{name}]({url})" for name, url in (("IG", r["instagram"]), ("YT", r["youtube"])) if url
        ) or "–"
        labs = ", ".join(f"[{s}]({LABS_URL}/{s}/)" for s in r["labs"]) or "–"
        rows.append(f"| {r['date']} | [{r['title']}]({r['folder']}/) | {r['language']} | {watch} | {labs} |")
    return "\n".join(rows)


def main():
    check = "--check" in sys.argv
    reels, errors = load_reels()
    if errors:
        print("\n".join(errors))
        sys.exit(1)

    index = json.dumps(reels, indent=2, ensure_ascii=False) + "\n"
    readme_path = ROOT / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    new_readme = re.sub(
        re.escape(START) + r".*?" + re.escape(END),
        f"{START}\n{table(reels)}\n{END}",
        readme,
        flags=re.S,
    )
    index_path = ROOT / "reels.json"
    old_index = index_path.read_text(encoding="utf-8") if index_path.exists() else ""

    if check:
        if old_index != index or new_readme != readme:
            print("reels.json or README.md is out of date. Run: python scripts/build_index.py")
            sys.exit(1)
        print(f"OK: {len(reels)} reels")
        return
    index_path.write_text(index, encoding="utf-8")
    readme_path.write_text(new_readme, encoding="utf-8")
    print(f"Wrote {len(reels)} reels")


if __name__ == "__main__":
    main()
