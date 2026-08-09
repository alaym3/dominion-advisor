from pydantic import BaseModel
from typing import List

class Cost(BaseModel):
    coin: int
    potion: int
    debt: int
    isSpecial: bool


class Card(BaseModel):
    name: str
    expansion: str
    cost: Cost
    types: List[str]
    isKingdomPile: bool
    poolLevel: int
    text: str = ""
    plusCards: int = 0
    plusActions: int = 0
    plusBuys: int = 0
    plusCoins: int = 0
    isAttack: bool = False
    isReaction: bool = False
    trashesOwn: bool = False
    gainsCards: bool = False
    tags: List[str] = []

class KingdomRequest(BaseModel):
    card_names: List[str]


class Observation(BaseModel):
    category: str
    finding: str
    detail: str