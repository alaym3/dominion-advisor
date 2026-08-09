from scripts.build_cards import validate_cards


def make_raw_card(name, pool_level=1, is_kingdom_pile=True, tags=None, **overrides):
    card = {
        "name": name,
        "expansion": "Test",
        "cost": {"coin": 3, "potion": 0, "debt": 0, "isSpecial": False},
        "types": ["Action"],
        "isKingdomPile": is_kingdom_pile,
        "poolLevel": pool_level,
        "tags": tags if tags is not None else [],
    }
    card.update(overrides)
    return card


def test_valid_level_1_2_kingdom_card_with_tags_passes():
    cards = [make_raw_card("Chapel", pool_level=1, tags=["trasher"])]
    assert validate_cards(cards, still_missing=[]) == []


def test_untagged_level_1_2_kingdom_card_fails():
    cards = [make_raw_card("Chapel", pool_level=1, tags=[])]
    violations = validate_cards(cards, still_missing=[])
    assert len(violations) == 1
    assert "Chapel" in violations[0]
    assert "no tags" in violations[0]


def test_untagged_level_3_plus_card_is_not_flagged():
    cards = [make_raw_card("Rustic Village", pool_level=7, tags=[])]
    assert validate_cards(cards, still_missing=[]) == []


def test_untagged_non_kingdom_pile_is_not_flagged():
    cards = [make_raw_card("Copper", pool_level=1, is_kingdom_pile=False, tags=[])]
    assert validate_cards(cards, still_missing=[]) == []


def test_still_missing_level_1_2_kingdom_card_fails():
    cards = [make_raw_card("Chapel", pool_level=1, tags=["trasher"])]
    violations = validate_cards(cards, still_missing=["Chapel"])
    assert len(violations) == 1
    assert "no enrichment data" in violations[0]


def test_still_missing_level_3_plus_card_is_not_flagged():
    cards = [make_raw_card("Rustic Village", pool_level=7, tags=[])]
    violations = validate_cards(cards, still_missing=["Rustic Village"])
    assert violations == []


def test_malformed_card_fails_schema_validation():
    cards = [make_raw_card("Chapel", pool_level=1, cost="not a cost object")]
    violations = validate_cards(cards, still_missing=[])
    assert len(violations) == 1
    assert "failed schema validation" in violations[0]


def test_malformed_card_short_circuits_further_checks_for_that_card():
    # Missing tags too, but the schema failure should be the only violation
    # reported — no point double-reporting a card that doesn't even parse.
    cards = [make_raw_card("Chapel", pool_level=1, cost="not a cost object", tags=[])]
    violations = validate_cards(cards, still_missing=["Chapel"])
    assert len(violations) == 1
