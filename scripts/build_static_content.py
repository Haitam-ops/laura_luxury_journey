"""Build one complete frontend content payload for every enabled language."""
from pathlib import Path
import json
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import cms  # noqa: E402


def main():
    database = ROOT / ".local" / "requests.sqlite3"
    output = ROOT / "dist" / "data"
    output.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(database) as connection:
        cms.initialize(connection)
        languages = cms.public_content(connection, "en")["languages"]
        for language in languages:
            if not language.get("enabled"):
                continue
            code = language["code"]
            payload = cms.public_content(connection, code)
            target = output / f"content.{code}.json"
            target.write_text(
                json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
                encoding="utf-8",
            )
            print(f"{code}: {target.name} ({len(payload['trips'])} trips)")

    english = (output / "content.en.json").read_bytes()
    (output / "content.json").write_bytes(english)
    (ROOT / "data" / "content.json").write_bytes(english)
    from prepare_public_assets import main as prepare_public_assets
    prepare_public_assets()
    from build_seo import main as build_seo
    build_seo()


if __name__ == "__main__":
    main()
