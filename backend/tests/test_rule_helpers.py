from app.models import Card, Cost
from app.rule_helpers import Breakpoint, TagThresholdRule, tag_threshold_observation


def make_card(name: str, tags=None) -> Card:
    return Card(
        name=name,
        expansion="Test",
        cost=Cost(coin=3, potion=0, debt=0, isSpecial=False),
        types=["Action"],
        isKingdomPile=True,
        poolLevel=1,
        tags=tags or [],
    )


TWO_WAY_RULE = TagThresholdRule(
    tag="gainer",
    category="acquisition",
    breakpoints=(
        Breakpoint(0, "No gainers", "detail zero"),
        Breakpoint(1, "Gainers present ({count}: {names})", "detail: {names}"),
    ),
)

THREE_WAY_RULE = TagThresholdRule(
    tag="trasher",
    category="trashing",
    breakpoints=(
        Breakpoint(0, "no trashers", "detail zero"),
        Breakpoint(1, "one trasher ({names})", "detail one: {names}"),
        Breakpoint(2, "many trashers ({count}: {names})", "detail many: {names}"),
    ),
)


def test_zero_matches_picks_zero_breakpoint():
    cards = [make_card("Village", tags=["village"])]
    obs = tag_threshold_observation(cards, TWO_WAY_RULE)
    assert obs.category == "acquisition"
    assert obs.finding == "No gainers"
    assert obs.detail == "detail zero"


def test_one_match_two_way_rule_uses_the_same_breakpoint_as_many():
    cards = [make_card("Workshop", tags=["gainer"])]
    obs = tag_threshold_observation(cards, TWO_WAY_RULE)
    assert obs.finding == "Gainers present (1: Workshop)"


def test_three_way_rule_distinguishes_one_from_many():
    one = [make_card("Chapel", tags=["trasher"])]
    many = [make_card("Chapel", tags=["trasher"]), make_card("Moneylender", tags=["trasher"])]

    one_obs = tag_threshold_observation(one, THREE_WAY_RULE)
    many_obs = tag_threshold_observation(many, THREE_WAY_RULE)

    assert one_obs.finding == "one trasher (Chapel)"
    assert many_obs.finding == "many trashers (2: Chapel, Moneylender)"


def test_names_join_and_none_fallback():
    obs = tag_threshold_observation([], THREE_WAY_RULE)
    assert obs.detail == "detail zero"

    cards = [make_card("A", tags=["trasher"]), make_card("B", tags=["trasher"])]
    obs = tag_threshold_observation(cards, THREE_WAY_RULE)
    assert "A, B" in obs.finding


def test_untagged_cards_are_excluded_from_the_count():
    cards = [make_card("Village", tags=["village"]), make_card("Chapel", tags=["trasher"])]
    obs = tag_threshold_observation(cards, THREE_WAY_RULE)
    assert obs.finding == "one trasher (Chapel)"


def test_breakpoints_do_not_need_to_be_passed_in_sorted_order():
    unsorted_rule = TagThresholdRule(
        tag="trasher",
        category="trashing",
        breakpoints=(
            Breakpoint(2, "many", "many detail"),
            Breakpoint(0, "zero", "zero detail"),
            Breakpoint(1, "one", "one detail"),
        ),
    )
    cards = [make_card("Chapel", tags=["trasher"])]
    obs = tag_threshold_observation(cards, unsorted_rule)
    assert obs.finding == "one"
