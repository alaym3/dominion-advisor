import json
from pathlib import Path

FLAT_CARDS = Path(__file__).parent.parent / "data" / "cards_flat.json"
KLONGMUIR = Path(__file__).parent.parent / "data" / "raw" / "dominion-cards.json"

with open(FLAT_CARDS) as f:
    our_cards = json.load(f)

with open(KLONGMUIR) as f:
    klongmuir_cards = json.load(f)

klongmuir_names = {c["name"] for c in klongmuir_cards}

level_1_2 = [c for c in our_cards if c["poolLevel"] <= 2 and c["isKingdomPile"]]

missing = [c["name"] for c in level_1_2 if c["name"] not in klongmuir_names]

print(f"Level 1-2 kingdom cards: {len(level_1_2)}")
print(f"Missing from KLongmuir: {len(missing)}")
print("\n".join(missing))