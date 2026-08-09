import random
from fastapi import FastAPI, HTTPException
from typing import List
import json
from pathlib import Path
from .models import Card, Cost, KingdomRequest, Observation
from .analysis import analyze_kingdom

app = FastAPI()


## loading only card pool level 1-2 kingdom cards for now, since that's all we need for the advisor
DATA_PATH = Path(__file__).parent.parent / "data" / "cards.json"

with open(DATA_PATH) as f:
    _raw_cards = json.load(f)

ALL_CARDS: List[Card] = [Card(**c) for c in _raw_cards]

LEVEL_1_2_KINGDOM_CARDS: List[Card] = [
    c for c in ALL_CARDS if c.poolLevel <= 2 and c.isKingdomPile
]

LEVEL_1_KINGDOM_CARDS: List[Card] = [
    c for c in ALL_CARDS if c.poolLevel == 1 and c.isKingdomPile
]

LEVEL_2_KINGDOM_CARDS: List[Card] = [
    c for c in ALL_CARDS if c.poolLevel == 2 and c.isKingdomPile
]

CARDS_BY_NAME = {c.name: c for c in LEVEL_1_2_KINGDOM_CARDS}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/cards", response_model=List[Card])
def get_cards():
    return LEVEL_1_2_KINGDOM_CARDS

@app.get("/kingdom/random", response_model=List[Card])
def get_random_kingdom():
    return random.sample(LEVEL_1_2_KINGDOM_CARDS, 10)

@app.get("/kingdom/random/analyzed")
def get_random_kingdom_analyzed():
    kingdom = random.sample(LEVEL_1_2_KINGDOM_CARDS, 10)
    observations = analyze_kingdom(kingdom)
    return {
        "cards": kingdom,
        "card_names": [c.name for c in kingdom],
        "observations": observations,
    }

@app.get("/kingdom/random/pool1/analyzed")
def get_random_kingdom_analyzed():
    kingdom = random.sample(LEVEL_1_KINGDOM_CARDS, 10)
    observations = analyze_kingdom(kingdom)
    return {
        "cards": kingdom,
        "card_names": [c.name for c in kingdom],
        "observations": observations,
    }

@app.get("/kingdom/random/pool2/analyzed")
def get_random_kingdom_analyzed():
    kingdom = random.sample(LEVEL_2_KINGDOM_CARDS, 10)
    observations = analyze_kingdom(kingdom)
    return {
        "cards": kingdom,
        "card_names": [c.name for c in kingdom],
        "observations": observations,
    }


@app.post("/kingdom/analyze")
def analyze_specific_kingdom(request: KingdomRequest):
    if len(request.card_names) != 10:
        raise HTTPException(
            status_code=400,
            detail=f"Expected exactly 10 card names, got {len(request.card_names)}."
        )

    duplicates = {name for name in request.card_names if request.card_names.count(name) > 1}
    if duplicates:
        raise HTTPException(
            status_code=400,
            detail=f"Duplicate card name(s) not allowed in a kingdom: {', '.join(sorted(duplicates))}."
        )

    kingdom = []
    unknown_names = []

    for name in request.card_names:
        card = CARDS_BY_NAME.get(name)
        if card is None:
            unknown_names.append(name)
        else:
            kingdom.append(card)

    if unknown_names:
        raise HTTPException(
            status_code=400,
            detail=f"Unrecognized card name(s): {', '.join(unknown_names)}. "
                   f"Check spelling and make sure they're Level 1-2 kingdom cards."
        )

    observations = analyze_kingdom(kingdom)
    return {
        "cards": kingdom,
        "card_names": [c.name for c in kingdom],
        "observations": observations,
    }