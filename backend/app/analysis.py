from typing import List
from typing import Optional

from .models import Card, Observation
from .rule_helpers import Breakpoint, TagThresholdRule, tag_threshold_observation


def analyze_village_density(cards: List[Card]) -> Observation:
    villages = [c for c in cards if "village" in c.tags]
    terminal_draws = [c for c in cards if "terminal-draw" in c.tags]

    village_count = len(villages)
    terminal_count = len(terminal_draws)

    village_names = ", ".join(c.name for c in villages) or "none"
    terminal_names = ", ".join(c.name for c in terminal_draws) or "none"

    if village_count == 0 and terminal_count == 0:
        finding = "No village or terminal-draw effects present"
        detail = "This kingdom has neither dedicated action-support nor big draw cards. Engines will be hard to build here."
    elif village_count >= terminal_count:
        finding = f"Good action support ({village_count} village(s) vs {terminal_count} terminal-draw(s))"
        detail = f"Villages: {village_names}. Terminal-draw cards: {terminal_names}. You likely have enough actions to chain terminal-draw cards without stalling."
    else:
        finding = f"Action-starved ({village_count} village(s) vs {terminal_count} terminal-draw(s))"
        detail = f"Villages: {village_names}. Terminal-draw cards: {terminal_names}. More draw than action support — you may run out of actions before playing everything you want to."

    return Observation(category="engine", finding=finding, detail=detail)


def analyze_curse_pressure(cards: List[Card]) -> Observation:
    cursers = [c for c in cards if "curser" in c.tags]
    curse_cleaners = [c for c in cards if "curse-cleaner" in c.tags]

    curser_count = len(cursers)
    has_curse_cleaner = len(curse_cleaners) > 0

    curser_names = ", ".join(c.name for c in cursers) or "none"
    cleaner_names = ", ".join(c.name for c in curse_cleaners) or "none"

    if curser_count == 0:
        finding = "No curse-granting attacks present"
        detail = "This kingdom has no cards that hand out Curses. No need to rush early purchases to avoid them."
    else:
        severity = "Heavy" if curser_count > 1 else "Some"

        if has_curse_cleaner:
            finding = f"{severity} curse pressure ({curser_count} curse-granting attack(s): {curser_names}) — Curses can be trashed"
            detail = (
                f"{curser_names} can hand out Curses, but this kingdom also has a way to trash them "
                f"({cleaner_names}), so Curses you receive don't have to stick around forever. "
                f"Still worth contesting these cards early, but not an all-or-nothing race."
            )
        else:
            finding = f"{severity} curse pressure ({curser_count} curse-granting attack(s): {curser_names}) — no way to trash Curses"
            detail = (
                f"{curser_names} can hand out Curses, and nothing in this kingdom can trash a Curse once "
                f"you have it. Curses will permanently clog your deck for the rest of the game — this makes "
                f"rushing to buy/play the curser(s) early significantly more urgent than usual."
            )

    return Observation(category="attack", finding=finding, detail=detail)

def analyze_trashing_availability(cards: List[Card]) -> Observation:
    return tag_threshold_observation(cards, TagThresholdRule(
        tag="trasher",
        category="trashing",
        breakpoints=(
            Breakpoint(
                0,
                "No trashing available",
                "This kingdom has no way to trash cards from your deck. You'll be stuck with your starting "
                "Estates and Coppers all game — deck-thinning strategies aren't an option here, so focus on "
                "raw draw/payload instead.",
            ),
            Breakpoint(
                1,
                "Limited trashing available ({names})",
                "{names} is the only trasher in this kingdom. It'll likely be contested early — "
                "getting a copy (or two, if it's cheap enough to double up on) is usually a strong opening.",
            ),
            Breakpoint(
                2,
                "Multiple trashing options available ({count}: {names})",
                "{names} all offer trashing. With this much thinning available, deck-thinning "
                "strategies are very viable here — less pressure to win any single trasher early since "
                "there are backups.",
            ),
        ),
    ))

def analyze_payload(cards: List[Card]) -> Observation:
    return tag_threshold_observation(cards, TagThresholdRule(
        tag="payload",
        category="economy",
        breakpoints=(
            Breakpoint(
                0,
                "No dedicated payload cards",
                "This kingdom has no cards specifically built for strong coin production. You'll be leaning "
                "on basic Treasures (and whatever coin your other cards happen to add) to afford Provinces — "
                "worth checking if the kingdom's engine/draw support can make up the difference in card volume instead.",
            ),
            Breakpoint(
                1,
                "One payload card available ({names})",
                "{names} is your main dedicated source of extra coin here. Getting a reliable supply "
                "of it (and enough draw to actually play it most turns) matters more than usual since there's "
                "no backup if it's contested.",
            ),
            Breakpoint(
                2,
                "Multiple payload options available ({count}: {names})",
                "{names} all add strong coin production. This kingdom can support a high-powered "
                "engine or a coin-heavy Big Money variant without much difficulty affording Provinces.",
            ),
        ),
    ))

def analyze_defense(cards: List[Card]) -> Observation:
    attackers = [c for c in cards if c.isAttack]
    defenders = [c for c in cards if c.isReaction]

    attacker_count = len(attackers)
    attacker_names = ", ".join(c.name for c in attackers) or "none"
    defender_names = ", ".join(c.name for c in defenders) or "none"

    if attacker_count == 0:
        finding = "No attacks present"
        detail = "This kingdom has no Attack cards. No need to worry about defense here."
    elif defenders:
        finding = f"Attacks present but defense available ({defender_names})"
        detail = (
            f"This kingdom has attacks ({attacker_names}), but also {defender_names}, which can block them. "
            f"Getting a copy early is worth considering if the attacks are especially punishing."
        )
    else:
        finding = f"Attacks present with no defense ({attacker_names})"
        detail = (
            f"This kingdom has attacks ({attacker_names}) and no reaction card to block them. "
            f"You'll need to play around these attacks directly (e.g. through deck construction or racing) "
            f"rather than relying on a Moat-style counter."
        )

    return Observation(category="attack", finding=finding, detail=detail)

def analyze_discard_attacks(cards: List[Card]) -> Observation:
    return tag_threshold_observation(cards, TagThresholdRule(
        tag="attack-discard",
        category="attack",
        breakpoints=(
            Breakpoint(
                0,
                "No discard attacks present",
                "This kingdom has no cards that force opponents to discard. No need to hedge against hand disruption.",
            ),
            Breakpoint(
                1,
                "Discard attack pressure present ({count}: {names})",
                "{names} force opponents to discard down or lose cards from hand. This punishes greedily "
                "building up a big hand before playing it — consider a leaner, more responsive strategy, "
                "or getting a copy yourself to use offensively too.",
            ),
        ),
    ))

def analyze_topdeck_attacks(cards: List[Card]) -> Observation:
    return tag_threshold_observation(cards, TagThresholdRule(
        tag="attack-topdeck",
        category="attack",
        breakpoints=(
            Breakpoint(
                0,
                "No topdeck-forcing attacks present",
                "This kingdom has no cards that force opponents to bury cards on top of their deck.",
            ),
            Breakpoint(
                1,
                "Topdeck-forcing attack pressure present ({count}: {names})",
                "{names} force opponents to put a card (often a Victory card) on top of their own deck, "
                "wasting their next draw. This particularly punishes hands full of Estates/Victory cards — "
                "worth being mindful of when to buy Victory cards if this attack is active.",
            ),
        ),
    ))

def analyze_alt_vp(cards: List[Card]) -> Observation:
    return tag_threshold_observation(cards, TagThresholdRule(
        tag="alt-vp",
        category="victory",
        breakpoints=(
            Breakpoint(
                0,
                "No alternate VP sources",
                "Victory points come only from the standard Estate/Duchy/Province pile in this kingdom.",
            ),
            Breakpoint(
                1,
                "Alternate VP source(s) present ({count}: {names})",
                "{names} score points outside the standard Victory cards, often rewarding a different "
                "deck shape than a lean engine (e.g. a bigger deck for Gardens-style cards). Worth factoring "
                "into whether heavy trashing is actually the right call this game.",
            ),
        ),
    ))

def analyze_gainers(cards: List[Card]) -> Observation:
    return tag_threshold_observation(cards, TagThresholdRule(
        tag="gainer",
        category="acquisition",
        breakpoints=(
            Breakpoint(
                0,
                "No non-buy gaining available",
                "All card acquisition in this kingdom happens through the normal Buy phase.",
            ),
            Breakpoint(
                1,
                "Non-buy gaining available ({count}: {names})",
                "{names} let you acquire cards outside your normal Buy. This can help you get more cards "
                "per turn than your Buys alone would allow, and matters for pile-control/rushing strategies "
                "since gaining doesn't require spending a Buy.",
            ),
        ),
    ))

def analyze_topdeck_combo(cards: List[Card]) -> Optional[Observation]:
    consumers = [c for c in cards if "topdeck-consumer" in c.tags]

    if not consumers:
        return None

    placers = [c for c in cards if "topdeck-place" in c.tags]
    consumer_names = ", ".join(c.name for c in consumers)

    if placers:
        placer_names = ", ".join(c.name for c in placers)
        finding = f"Topdeck combo available ({consumer_names} + {placer_names})"
        detail = (
            f"{consumer_names} checks the top card of your deck and acts on it — and this kingdom has "
            f"{placer_names}, which can deliberately place a known card on top first. Setting up a good "
            f"card for {consumer_names} to find is a real strategy here, not just a lucky reveal."
        )
    else:
        finding = f"Topdeck-consumer present with no setup support ({consumer_names})"
        detail = (
            f"{consumer_names} checks the top card of your deck and acts on it, but nothing in this "
            f"kingdom lets you deliberately place a card there first. It'll mostly be hitting whatever's "
            f"randomly on top — weaker and swingier than when it has setup support."
        )

    return Observation(category="combo", finding=finding, detail=detail)

def analyze_doubler_combo(cards: List[Card]) -> Optional[Observation]:
    doublers = [c for c in cards if "doubler" in c.tags]

    if not doublers:
        return None

    doubler_names = ", ".join(c.name for c in doublers)
    cursers = [c for c in cards if c not in doublers and "curser" in c.tags]
    strong_targets = [
        c for c in cards
        if c not in doublers
        and c not in cursers
        and ("terminal-draw" in c.tags or "payload" in c.tags)
    ]

    parts = []

    if cursers:
        curser_names = ", ".join(c.name for c in cursers)
        parts.append(
            f"{curser_names} hands out Curses — doubling a curse-attack is a well-known nasty combo, "
            f"and can single-handedly decide a curse race if you land it consistently."
        )

    if strong_targets:
        target_names = ", ".join(c.name for c in strong_targets)
        parts.append(
            f"{target_names} are strong candidates to double for extra draw or coin."
        )

    if not parts:
        finding = f"Doubler present with no strong targets ({doubler_names})"
        detail = (
            f"{doubler_names} lets you replay an Action card, but this kingdom doesn't have a standout "
            f"terminal-draw, payload, or curse-attack card worth doubling. It may still have niche uses, "
            f"but it's not an obvious centerpiece here."
        )
    else:
        finding = f"Doubler combo potential ({doubler_names})"
        detail = f"{doubler_names} lets you replay an Action card. " + " ".join(parts)

    return Observation(category="combo", finding=finding, detail=detail)

def analyze_engine_speed(cards: List[Card]) -> Optional[Observation]:
    villages = [c for c in cards if "village" in c.tags]

    if not villages:
        return None  # already covered by analyze_village_density's "no villages" case

    cheapest_village = min(v.cost.coin for v in villages)
    cheapest_village_card = min(villages, key=lambda v: v.cost.coin)
    village_names = ", ".join(v.name for v in villages)

    if cheapest_village <= 3:
        finding = f"Cheap village support available ({cheapest_village_card.name} at ${cheapest_village})"
        detail = (
            f"Village support here ({village_names}) includes a copy costing ${cheapest_village} or less. "
            f"That's affordable early — you can likely get your engine's action-support piece by turn 3-4 "
            f"without delaying your economy much."
        )
    else:
        finding = f"Village support is expensive (cheapest is {cheapest_village_card.name} at ${cheapest_village})"
        detail = (
            f"Village support here ({village_names}) doesn't come cheap — the least expensive option is "
            f"${cheapest_village}. Your engine will likely take longer to get moving, since you'll need "
            f"a few turns of economy-building before you can even start assembling it."
        )

    return Observation(category="engine", finding=finding, detail=detail)

def analyze_bigmoney_viability(cards: List[Card]) -> Optional[Observation]:
    villages = [c for c in cards if "village" in c.tags]
    terminal_draws = [c for c in cards if "terminal-draw" in c.tags]
    payload_cards = [c for c in cards if "payload" in c.tags]

    engine_favored = len(villages) > 0 and len(villages) >= len(terminal_draws)

    if engine_favored:
        # Already well-covered by analyze_village_density's positive case — no new info to add.
        return None

    payload_count = len(payload_cards)
    payload_names = ", ".join(c.name for c in payload_cards) or "none"

    if payload_count >= 2:
        finding = f"Big Money+X likely a strong fallback ({payload_count} payload cards: {payload_names})"
        detail = (
            f"Engine-building looks difficult here (limited village support), but {payload_names} give "
            f"you real coin production to lean on. A Big Money strategy — mostly buying Treasures and "
            f"Provinces, supplemented by {payload_names} — is likely competitive with, or better than, "
            f"forcing an engine on this board."
        )
    elif payload_count == 1:
        finding = f"Big Money+X is a modest fallback ({payload_names})"
        detail = (
            f"Engine-building looks difficult here (limited village support), and {payload_names} is your "
            f"only dedicated payload. Big Money is still probably your best bet, but without much extra "
            f"coin production, expect a slower, grindier game."
        )
    else:
        finding = "Neither engine nor strong Big Money is well-supported"
        detail = (
            "This kingdom has limited village support for an engine AND no dedicated payload cards for "
            "Big Money. Expect a slow, grindy game either way — look at whatever secondary tools "
            "(trashing, gaining, alt-VP) might tip the balance instead."
        )

    return Observation(category="strategy", finding=finding, detail=detail)

def analyze_archetype_summary(cards: List[Card]) -> Observation:
    villages = [c for c in cards if "village" in c.tags]
    terminal_draws = [c for c in cards if "terminal-draw" in c.tags]
    payload_cards = [c for c in cards if "payload" in c.tags]
    cursers = [c for c in cards if "curser" in c.tags]
    curse_cleaners = [c for c in cards if "curse-cleaner" in c.tags]
    doublers = [c for c in cards if "doubler" in c.tags]
    topdeck_consumers = [c for c in cards if "topdeck-consumer" in c.tags]
    topdeck_placers = [c for c in cards if "topdeck-place" in c.tags]

    engine_favored = len(villages) > 0 and len(villages) >= len(terminal_draws)
    cheap_village = any(v.cost.coin <= 3 for v in villages) if villages else False

    reasoning = []

    if len(cursers) >= 2 and not curse_cleaners:
        headline = "Curse race — prioritize the curser(s) early"
        reasoning.append(
            f"{len(cursers)} curse-granting attacks with no way to trash them means falling behind "
            f"on Curses is very costly here."
        )
    elif engine_favored and cheap_village:
        headline = "Engine-favored — build toward multiple actions per turn"
        reasoning.append("Village support is both sufficient and cheap, making an engine a realistic goal.")
    elif engine_favored:
        headline = "Engine possible but slow to assemble"
        reasoning.append("Village support exists but is expensive, so expect a slower ramp-up.")
    elif payload_cards:
        headline = "Big Money+X is likely your best approach"
        reasoning.append(
            "Limited village support makes an engine risky, but dedicated payload cards make a "
            "Treasure-heavy strategy solid."
        )
    else:
        headline = "No dominant strategy — grindy kingdom"
        reasoning.append(
            "Neither engine-building nor Big Money has strong support here; lean on secondary "
            "tools instead."
        )

    if doublers and (cursers or payload_cards):
        reasoning.append(
            f"Also worth noting: {', '.join(c.name for c in doublers)} pairs well with strong "
            f"targets here for extra value."
        )
    if topdeck_consumers and topdeck_placers:
        reasoning.append(
            f"There's also a topdeck combo available ({', '.join(c.name for c in topdeck_consumers)} "
            f"+ {', '.join(c.name for c in topdeck_placers)})."
        )

    return Observation(category="summary", finding=headline, detail=" ".join(reasoning))

def analyze_kingdom(cards: List[Card]) -> List[Observation]:
    """Runs all analysis rules against a kingdom and collects the results."""
    rules = [
        analyze_village_density,
        analyze_curse_pressure,
        analyze_trashing_availability,
        analyze_payload,
        analyze_defense,
        analyze_discard_attacks,
        analyze_topdeck_attacks,
        analyze_alt_vp,
        analyze_gainers,
        analyze_topdeck_combo,
        analyze_doubler_combo,
        analyze_engine_speed,
        analyze_bigmoney_viability,
        analyze_archetype_summary,
    ]
    results = [rule(cards) for rule in rules]
    return [r for r in results if r is not None]