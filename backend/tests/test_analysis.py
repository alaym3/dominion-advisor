from app.analysis import (
    compute_kingdom_facts,
    analyze_village_density,
    analyze_engine_speed,
    analyze_bigmoney_viability,
    analyze_archetype_summary,
)
from app.models import Card, Cost


def make_card(name: str, cost: int = 3, tags=None) -> Card:
    return Card(
        name=name,
        expansion="Test",
        cost=Cost(coin=cost, potion=0, debt=0, isSpecial=False),
        types=["Action"],
        isKingdomPile=True,
        poolLevel=1,
        tags=tags or [],
    )


# --- compute_kingdom_facts ---

def test_facts_separates_villages_and_terminal_draws():
    cards = [
        make_card("Village", tags=["village"]),
        make_card("Smithy", tags=["terminal-draw"]),
        make_card("Copper", tags=[]),
    ]
    facts = compute_kingdom_facts(cards)
    assert [c.name for c in facts.villages] == ["Village"]
    assert [c.name for c in facts.terminal_draws] == ["Smithy"]


def test_engine_favored_true_when_villages_outnumber_terminal_draws():
    cards = [make_card("Village", tags=["village"]), make_card("Smithy", tags=["terminal-draw"])]
    assert compute_kingdom_facts(cards).engine_favored is True


def test_engine_favored_false_with_no_villages():
    cards = [make_card("Smithy", tags=["terminal-draw"])]
    assert compute_kingdom_facts(cards).engine_favored is False


def test_engine_favored_false_when_terminal_draws_outnumber_villages():
    cards = [
        make_card("Village", tags=["village"]),
        make_card("Smithy1", tags=["terminal-draw"]),
        make_card("Smithy2", tags=["terminal-draw"]),
    ]
    assert compute_kingdom_facts(cards).engine_favored is False


def test_cheap_village_true_if_any_village_costs_3_or_less():
    cards = [make_card("Village", cost=3, tags=["village"]), make_card("Festival", cost=5, tags=["village"])]
    assert compute_kingdom_facts(cards).cheap_village is True


def test_cheap_village_false_if_all_villages_cost_more_than_3():
    cards = [make_card("Festival", cost=5, tags=["village"])]
    assert compute_kingdom_facts(cards).cheap_village is False


def test_cheap_village_false_with_no_villages():
    assert compute_kingdom_facts([]).cheap_village is False


# --- analyze_village_density (now takes only facts) ---

def test_village_density_no_villages_or_terminal_draws():
    facts = compute_kingdom_facts([])
    obs = analyze_village_density(facts)
    assert obs.finding == "No village or terminal-draw effects present"


def test_village_density_engine_favored():
    cards = [make_card("Village", tags=["village"]), make_card("Smithy", tags=["terminal-draw"])]
    obs = analyze_village_density(compute_kingdom_facts(cards))
    assert "Good action support" in obs.finding


def test_village_density_action_starved():
    cards = [make_card("Smithy", tags=["terminal-draw"])]
    obs = analyze_village_density(compute_kingdom_facts(cards))
    assert "Action-starved" in obs.finding


# --- analyze_engine_speed (now takes only facts) ---

def test_engine_speed_none_without_villages():
    assert analyze_engine_speed(compute_kingdom_facts([])) is None


def test_engine_speed_cheap():
    cards = [make_card("Village", cost=3, tags=["village"])]
    obs = analyze_engine_speed(compute_kingdom_facts(cards))
    assert "Cheap village support" in obs.finding


def test_engine_speed_expensive():
    cards = [make_card("Festival", cost=5, tags=["village"])]
    obs = analyze_engine_speed(compute_kingdom_facts(cards))
    assert "expensive" in obs.finding


# --- analyze_bigmoney_viability (still takes cards + facts) ---

def test_bigmoney_none_when_engine_favored():
    cards = [make_card("Village", tags=["village"]), make_card("Smithy", tags=["terminal-draw"])]
    facts = compute_kingdom_facts(cards)
    assert analyze_bigmoney_viability(cards, facts) is None


def test_bigmoney_strong_fallback_with_two_payload_cards():
    cards = [make_card("Bank", tags=["payload"]), make_card("Mint", tags=["payload"])]
    facts = compute_kingdom_facts(cards)
    obs = analyze_bigmoney_viability(cards, facts)
    assert "strong fallback" in obs.finding


def test_bigmoney_no_support():
    cards = [make_card("Copper", tags=[])]
    facts = compute_kingdom_facts(cards)
    obs = analyze_bigmoney_viability(cards, facts)
    assert obs.finding == "Neither engine nor strong Big Money is well-supported"


# --- analyze_archetype_summary (still takes cards + facts) ---

def test_archetype_curse_race_takes_priority():
    cards = [
        make_card("Witch", tags=["curser"]),
        make_card("Mountebank", tags=["curser"]),
        make_card("Village", tags=["village"]),
        make_card("Smithy", tags=["terminal-draw"]),
    ]
    facts = compute_kingdom_facts(cards)
    obs = analyze_archetype_summary(cards, facts)
    assert obs.finding == "Curse race — prioritize the curser(s) early"


def test_archetype_engine_favored_and_cheap():
    cards = [make_card("Village", cost=3, tags=["village"])]
    facts = compute_kingdom_facts(cards)
    obs = analyze_archetype_summary(cards, facts)
    assert obs.finding == "Engine-favored — build toward multiple actions per turn"


def test_archetype_engine_favored_but_expensive():
    cards = [make_card("Festival", cost=5, tags=["village"])]
    facts = compute_kingdom_facts(cards)
    obs = analyze_archetype_summary(cards, facts)
    assert obs.finding == "Engine possible but slow to assemble"


def test_archetype_bigmoney_fallback():
    cards = [make_card("Bank", tags=["payload"])]
    facts = compute_kingdom_facts(cards)
    obs = analyze_archetype_summary(cards, facts)
    assert obs.finding == "Big Money+X is likely your best approach"


def test_archetype_no_dominant_strategy():
    cards = [make_card("Copper", tags=[])]
    facts = compute_kingdom_facts(cards)
    obs = analyze_archetype_summary(cards, facts)
    assert obs.finding == "No dominant strategy — grindy kingdom"
