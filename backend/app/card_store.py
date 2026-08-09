import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

from .models import Card

DATA_PATH = Path(__file__).parent.parent / "data" / "cards.json"

# cards.json on disk spans all pool levels the Dominion Online client
# reports (1-10); only 1-2 have been enriched/tagged so far, so the store
# filters down to that scope at load time rather than exposing the rest.
MIN_SUPPORTED_POOL_LEVEL = 1
MAX_SUPPORTED_POOL_LEVEL = 2


class CardStore:
    """Owns the loaded card data and every way the app queries it.
    Loaded once at construction, not per request."""

    def __init__(self, cards: List[Card]):
        self._all_cards = [
            c for c in cards
            if MIN_SUPPORTED_POOL_LEVEL <= c.poolLevel <= MAX_SUPPORTED_POOL_LEVEL
        ]
        self._by_name: Dict[str, Card] = {c.name: c for c in self.kingdom_cards(1, 2)}

    def all(self) -> List[Card]:
        return self._all_cards

    def kingdom_cards(self, min_level: int, max_level: int) -> List[Card]:
        return [
            c for c in self._all_cards
            if c.isKingdomPile and min_level <= c.poolLevel <= max_level
        ]

    def get(self, name: str) -> Optional[Card]:
        """Looks up a card by name among Level 1-2 kingdom cards only —
        matches what /kingdom/analyze accepts."""
        return self._by_name.get(name)

    @classmethod
    def from_file(cls, path: Path = DATA_PATH) -> "CardStore":
        with open(path) as f:
            raw_cards = json.load(f)
        return cls([Card(**c) for c in raw_cards])


@lru_cache
def get_card_store() -> CardStore:
    return CardStore.from_file()
