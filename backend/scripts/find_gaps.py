import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.card_store import MIN_SUPPORTED_POOL_LEVEL, MAX_SUPPORTED_POOL_LEVEL

FLAT_CARDS = BACKEND_DIR / "data" / "cards_flat.json"
KLONGMUIR = BACKEND_DIR / "data" / "raw" / "dominion-cards.json"

with open(FLAT_CARDS) as f:
    our_cards = json.load(f)

with open(KLONGMUIR) as f:
    klongmuir_cards = json.load(f)

klongmuir_names = {c["name"] for c in klongmuir_cards}

level_1_2 = [
    c for c in our_cards
    if MIN_SUPPORTED_POOL_LEVEL <= c["poolLevel"] <= MAX_SUPPORTED_POOL_LEVEL and c["isKingdomPile"]
]

missing = [c["name"] for c in level_1_2 if c["name"] not in klongmuir_names]

print(f"Level 1-2 kingdom cards: {len(level_1_2)}")
print(f"Missing from KLongmuir: {len(missing)}")
print("\n".join(missing))