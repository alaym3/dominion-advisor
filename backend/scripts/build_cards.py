import json
import re
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

FLAT_CARDS_PATH = DATA_DIR / "cards_flat.json"
KLONGMUIR_PATH = DATA_DIR / "raw" / "dominion-cards.json"
MANUAL_PATH = DATA_DIR / "raw" / "manual_cards.json"
OUTPUT_PATH = DATA_DIR / "cards.json"


def parse_plus_value(raw):
    """Extract the leading +N from strings like '+1', '+$1', '-X,+X'. Returns 0 if none found."""
    match = re.search(r'\+\$?(\d+)', raw)
    return int(match.group(1)) if match else 0


def normalize_klongmuir(card):
    return {
        "text": card["text"],
        "plusCards": parse_plus_value(card["cards"]),
        "plusActions": parse_plus_value(card["actionsVillagers"]),
        "plusBuys": parse_plus_value(card["buys"]),
        "plusCoins": parse_plus_value(card["coinsCoffers"]),
        "isAttack": "Attack" in card["types"],
        "isReaction": "Reaction" in card["types"],
        "trashesOwn": bool(card["trashReturn"].strip()),
        "gainsCards": bool(card["gain"].strip()),
        "tags": card.get("categories", []),
    }


def normalize_manual(card):
    # Manual cards are already in our target shape; just strip the name field
    # since that's used as the lookup key, not merged in directly.
    return {k: v for k, v in card.items() if k != "name"}

def apply_tag_overlay(cards, tags_raw):
    tags_by_name = {c["name"]: c["tags"] for c in tags_raw}
    for card in cards:
        if card["name"] in tags_by_name and not card.get("tags"):
            card["tags"] = tags_by_name[card["name"]]
    return cards

def build_final_cards(base_cards, klongmuir_raw, manual_raw):
    klongmuir_by_name = {c["name"]: normalize_klongmuir(c) for c in klongmuir_raw}
    manual_by_name = {c["name"]: normalize_manual(c) for c in manual_raw}

    final = []
    still_missing = []

    for base in base_cards:
        name = base["name"]
        enrichment = manual_by_name.get(name) or klongmuir_by_name.get(name)

        if enrichment is None:
            still_missing.append(name)
            enrichment = {}

        merged = {**base, **enrichment}
        final.append(merged)

    return final, still_missing


def main():
    with open(FLAT_CARDS_PATH) as f:
        base_cards = json.load(f)

    with open(KLONGMUIR_PATH) as f:
        klongmuir_raw = json.load(f)

    with open(MANUAL_PATH) as f:
        manual_raw = json.load(f)

    final_cards, still_missing = build_final_cards(base_cards, klongmuir_raw, manual_raw)
    tags_path = DATA_DIR / "raw" / "card_tags.json"
    if tags_path.exists():
        with open(tags_path) as f:
            tags_raw = json.load(f)
        final_cards = apply_tag_overlay(final_cards, tags_raw)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(final_cards, f, indent=2)

    print(f"Wrote {len(final_cards)} cards to {OUTPUT_PATH}")
    print(f"Cards with no enrichment data found: {len(still_missing)}")
    if still_missing:
        print("\n".join(still_missing))


if __name__ == "__main__":
    main()