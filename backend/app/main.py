import random
from fastapi import Depends, FastAPI, HTTPException
from typing import List
from .card_store import CardStore, get_card_store
from .models import Card, KingdomRequest
from .analysis import analyze_kingdom

app = FastAPI()


@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/cards", response_model=List[Card])
def get_cards(store: CardStore = Depends(get_card_store)):
    return store.kingdom_cards(1, 2)

@app.get("/kingdom/random", response_model=List[Card])
def get_random_kingdom(store: CardStore = Depends(get_card_store)):
    return random.sample(store.kingdom_cards(1, 2), 10)

def _sample_and_analyze(store: CardStore, min_level: int, max_level: int):
    kingdom = random.sample(store.kingdom_cards(min_level, max_level), 10)
    observations = analyze_kingdom(kingdom)
    return {
        "cards": kingdom,
        "card_names": [c.name for c in kingdom],
        "observations": observations,
    }

@app.get("/kingdom/random/analyzed")
def get_random_kingdom_analyzed(store: CardStore = Depends(get_card_store)):
    return _sample_and_analyze(store, 1, 2)

@app.get("/kingdom/random/pool1/analyzed")
def get_random_kingdom_pool1_analyzed(store: CardStore = Depends(get_card_store)):
    return _sample_and_analyze(store, 1, 1)

@app.get("/kingdom/random/pool2/analyzed")
def get_random_kingdom_pool2_analyzed(store: CardStore = Depends(get_card_store)):
    return _sample_and_analyze(store, 2, 2)


@app.post("/kingdom/analyze")
def analyze_specific_kingdom(request: KingdomRequest, store: CardStore = Depends(get_card_store)):
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
        card = store.get(name)
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