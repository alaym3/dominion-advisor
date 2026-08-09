import json

from app.card_store import CardStore
from app.models import Card, Cost


def make_card(name: str, pool_level: int, is_kingdom_pile: bool = True, tags=None) -> Card:
    return Card(
        name=name,
        expansion="Test",
        cost=Cost(coin=3, potion=0, debt=0, isSpecial=False),
        types=["Action"],
        isKingdomPile=is_kingdom_pile,
        poolLevel=pool_level,
        tags=tags or [],
    )


def test_filters_to_supported_pool_levels_at_construction():
    cards = [
        make_card("Chapel", pool_level=1),
        make_card("Witch", pool_level=2),
        make_card("Rustic Village", pool_level=7),
    ]
    store = CardStore(cards)
    assert {c.name for c in store.all()} == {"Chapel", "Witch"}


def test_kingdom_cards_filters_by_pool_range_and_kingdom_pile():
    cards = [
        make_card("Chapel", pool_level=1),
        make_card("Witch", pool_level=2),
        make_card("Copper", pool_level=1, is_kingdom_pile=False),
    ]
    store = CardStore(cards)

    assert {c.name for c in store.kingdom_cards(1, 2)} == {"Chapel", "Witch"}
    assert {c.name for c in store.kingdom_cards(1, 1)} == {"Chapel"}
    assert {c.name for c in store.kingdom_cards(2, 2)} == {"Witch"}


def test_get_finds_level_1_2_kingdom_cards_by_name():
    store = CardStore([make_card("Chapel", pool_level=1)])
    assert store.get("Chapel").name == "Chapel"


def test_get_returns_none_for_unknown_name():
    store = CardStore([make_card("Chapel", pool_level=1)])
    assert store.get("Nonexistent Card") is None


def test_get_does_not_find_non_kingdom_piles():
    store = CardStore([make_card("Copper", pool_level=1, is_kingdom_pile=False)])
    assert store.get("Copper") is None


def test_from_file_loads_and_filters(tmp_path):
    raw = [
        make_card("Chapel", pool_level=1).model_dump(),
        make_card("Rustic Village", pool_level=7).model_dump(),
    ]
    path = tmp_path / "cards.json"
    path.write_text(json.dumps(raw))

    store = CardStore.from_file(path)
    assert {c.name for c in store.all()} == {"Chapel"}
