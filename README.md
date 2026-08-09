# Dominion Advisor — API Reference

## Running the app

From the project root:
```bash
docker compose up --build
```

- Backend (FastAPI): http://localhost:8001
- Frontend (Vite/React): http://localhost:5173
- Interactive API docs (Swagger UI, auto-generated): http://localhost:8001/docs

To restart just the backend after changing Python code that isn't picked up
by `--reload` (e.g. after rebuilding `cards.json`):
```bash
docker compose restart app
```

To view logs:
```bash
docker compose logs -f app
```

## Frontend

A minimal UI at http://localhost:5173, calling the backend directly (CORS
enabled for this origin — see `backend/app/main.py`). Three buttons:

- **Call /health** — shows the raw health-check response
- **Call /kingdom/random** — draws 10 cards, shows their names
- **Call /kingdom/random/analyzed** — draws 10 cards and shows both the
  cards and the rule engine's observations

Not built yet: a pool-level selector (Level 1 / Level 2 / both — currently
always hits the combined Level 1-2 endpoint), and a manual 10-card picker
for `POST /kingdom/analyze`.

## Rebuilding the card data

If you've edited any of `manual_cards.json`, `card_tags.json`, or the raw
Dominion Online extract, regenerate `cards.json` before testing:
```bash
cd backend
python3 scripts/build_cards.py
```
Then restart the backend container (see above) — `cards.json` is only loaded
at startup, not watched for changes.

---

## Endpoints

### `GET /health`
Basic liveness check.

```bash
curl http://localhost:8001/health
```
```json
{"status": "ok"}
```

---

### `GET /cards`
Returns all 78 Level 1-2 kingdom cards with full data (cost, types, text,
numeric effects, tags).

```bash
curl -s http://localhost:8001/cards | python3 -m json.tool
```

Just the count, as a sanity check:
```bash
curl -s http://localhost:8001/cards | python3 -c "import json,sys; print(len(json.load(sys.stdin)))"
```
Should print `78`.

---

### `GET /kingdom/random`
Draws 10 random, unique cards from the Level 1-2 kingdom pool. No analysis,
just the cards.

```bash
curl -s http://localhost:8001/kingdom/random | python3 -c "import json,sys; data=json.load(sys.stdin); print([c['name'] for c in data])"
```

---

### `GET /kingdom/random/analyzed`
Draws 10 random cards AND runs the full rule engine against them. Returns
card names, full card data, and a list of observations (each with a
category, a short finding, and a plain-English explanation).

```bash
curl -s http://localhost:8001/kingdom/random/analyzed | python3 -m json.tool
```

Response shape:
```json
{
  "card_names": ["Witch", "Village", "..."],
  "cards": [ /* full card objects */ ],
  "observations": [
    {
      "category": "engine",
      "finding": "Action-starved (1 village(s) vs 3 terminal-draw(s))",
      "detail": "..."
    }
  ]
}
```

---

### `GET /kingdom/random/pool1/analyzed`
Same as above, restricted to Card Pool Level 1 cards only.

```bash
curl -s http://localhost:8001/kingdom/random/pool1/analyzed | python3 -m json.tool
```

---

### `GET /kingdom/random/pool2/analyzed`
Same as above, restricted to Card Pool Level 2 cards only.

```bash
curl -s http://localhost:8001/kingdom/random/pool2/analyzed | python3 -m json.tool
```

---

### `POST /kingdom/analyze`
Same analysis as above, but for a kingdom YOU choose — useful for testing
specific rule logic or edge cases rather than waiting on a random draw.

Body: `{"card_names": [...exactly 10 names...]}`

```bash
curl -s -X POST http://localhost:8001/kingdom/analyze \
  -H "Content-Type: application/json" \
  -d '{"card_names": ["Witch", "Village", "Moat", "Chapel", "Smithy", "Throne Room", "Market", "Militia", "Bureaucrat", "Gardens"]}' \
  | python3 -m json.tool
```

Validation:
- Returns `400` if you don't send exactly 10 names.
- Returns `400` listing any unrecognized name(s) — check spelling, and note
  this only accepts Level 1-2 kingdom cards (not Level 3+, not non-kingdom
  cards like Events/Landmarks).

#### Known-good test kingdom (regression test)
This exact kingdom is useful for re-checking the curse-pressure rule
specifically, since it has both a curser (Witch) and a curse-cleaner
(Chapel) — expected output: "Curses can be trashed."
```
Witch, Village, Moat, Chapel, Smithy, Throne Room, Market, Militia, Bureaucrat, Gardens
```

---

## Current rule engine coverage (backend/app/analysis.py)

| Rule | Category | Checks |
|---|---|---|
| `analyze_village_density` | engine | village vs terminal-draw ratio |
| `analyze_curse_pressure` | attack | curser count + curse-cleaner availability |
| `analyze_trashing_availability` | trashing | general trasher count |
| `analyze_payload` | economy | payload tag count |
| `analyze_defense` | attack | attack cards vs reaction cards |
| `analyze_discard_attacks` | attack | attack-discard tag |
| `analyze_topdeck_attacks` | attack | attack-topdeck tag |
| `analyze_alt_vp` | victory | alt-vp tag |
| `analyze_gainers` | acquisition | gainer tag |
| `analyze_topdeck_combo` | combo | topdeck-consumer (e.g. Vassal) paired with topdeck-place support |
| `analyze_doubler_combo` | combo | doubler tag paired with curser/terminal-draw/payload targets |
| `analyze_engine_speed` | engine | cheapest available village cost |
| `analyze_bigmoney_viability` | strategy | payload count as a Big Money fallback when engine isn't favored |
| `analyze_archetype_summary` | summary | headline recommendation synthesized from every other observation |

The six single-tag threshold rules (`discard_attacks`, `topdeck_attacks`,
`alt_vp`, `gainers`, `trashing_availability`, `payload`) are implemented as
declarative config — see `backend/app/rule_helpers.py`'s `TagThresholdRule` —
rather than one bespoke function apiece.

## Running tests

```bash
docker compose run --rm app python -m pytest tests -v
```

## Rebuilding your own card data

This repo ships the full pipeline needed to fork it, edit tags, and
regenerate `cards.json` yourself:

- `backend/data/raw/dominion-cards.json` — base card data from
  [KLongmuir/dominion-card-data](https://github.com/KLongmuir/dominion-card-data)
  (MIT License, © 2022 Kevin Longmuir — see "Third-party data" below)
- `backend/data/raw/manual_cards.json` / `backend/data/raw/card_tags.json` —
  hand-transcribed cards and tag overrides
- `backend/data/cards_flat.json` — the static Level 1-2 card/pool-level list
- `backend/scripts/build_cards.py` — merges the above into `cards.json`
- `backend/scripts/generate_tag_skeleton.py` — scans `cards.json` for
  untagged Level 1-2 kingdom cards and writes a todo skeleton to
  `backend/data/raw/card_tags_todo.json`. Fill in the `tags` field for each
  entry, then rename the file to `card_tags.json` before rebuilding — the
  overlay is skipped silently if the filename doesn't match exactly.
- `backend/scripts/find_gaps.py` — lists Level 1-2 kingdom cards missing from
  the KLongmuir dataset (i.e. cards that need a `manual_cards.json` entry)

To rebuild after editing tags or manual card data:
```bash
cd backend
python3 scripts/build_cards.py
docker compose restart app   # cards.json only loads at startup
```

Not included in this repo: the one-time bootstrap that produced
`cards_flat.json` in the first place (extracting `CardPoolLevels` from the
Dominion Online client and flattening it).

## Third-party data

`backend/data/raw/dominion-cards.json` is from
[KLongmuir/dominion-card-data](https://github.com/KLongmuir/dominion-card-data),
used under the MIT License.

All other card text in this repo is paraphrased by hand, not copied from any
wiki or client source.