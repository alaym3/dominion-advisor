import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

with open(DATA_DIR / "cards.json") as f:
    cards = json.load(f)

level_1_2_kingdom = [c for c in cards if c.get("poolLevel", 99) <= 2 and c.get("isKingdomPile")]
untagged = [c for c in level_1_2_kingdom if not c.get("tags")]

skeleton = [
    {"name": c["name"], "text": c.get("text", ""), "tags": []}
    for c in sorted(untagged, key=lambda c: c["name"])
]

out_path = DATA_DIR / "raw" / "card_tags_todo.json"
with open(out_path, "w") as f:
    json.dump(skeleton, f, indent=2)

print(f"Wrote {len(skeleton)} cards needing tags to {out_path}")