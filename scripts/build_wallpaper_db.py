import json
import os
import sys
import zipfile
from pathlib import Path
from hashlib import sha1

REPO_RAW_BASE = os.environ.get("REPO_RAW_BASE", "").rstrip("/")

def file_hash_for_id(path: Path) -> str:
    return sha1(str(path).encode("utf-8")).hexdigest()[:12]

def build_db(source_dir: str, output_zip: str):
    source = Path(source_dir)
    if not source.exists():
        raise FileNotFoundError(f"Source folder not found: {source_dir}")

    db = {
        "db_id": f"wallpapers_{source.name}",
        "db_name": f"{source.name} Wallpapers",
        "db_url": "",
        "files": []
    }

    for file_path in sorted(source.rglob("*")):
        if not file_path.is_file():
            continue

        rel_path = file_path.relative_to(source).as_posix()
        raw_url = f"{REPO_RAW_BASE}/{source.name}/{rel_path}"

        db["files"].append({
            "id": file_hash_for_id(file_path),
            "url": raw_url,
            "path": f"/media/fat/wallpapers/{Path(rel_path).name}",
            "tags": ["wallpaper"],
            "description": f"{source.name} wallpaper: {rel_path}"
        })

    output_zip_path = Path(output_zip)
    output_zip_path.parent.mkdir(parents=True, exist_ok=True)

    json_name = "db.json"
    with zipfile.ZipFile(output_zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(json_name, json.dumps(db, indent=2))

    print(f"Built {output_zip_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python build_wallpaper_db.py <source_dir> <output_zip>")
        sys.exit(1)

    build_db(sys.argv[1], sys.argv[2])