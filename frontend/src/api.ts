export interface Cost {
  coin: number
  potion: number
  debt: number
  isSpecial: boolean
}

export interface Card {
  name: string
  expansion: string
  cost: Cost
  types: string[]
  isKingdomPile: boolean
  poolLevel: number
  text: string
  plusCards: number
  plusActions: number
  plusBuys: number
  plusCoins: number
  isAttack: boolean
  isReaction: boolean
  trashesOwn: boolean
  gainsCards: boolean
  tags: string[]
}

export interface Observation {
  category: string
  finding: string
  detail: string
}

export interface AnalyzedKingdom {
  cards: Card[]
  card_names: string[]
  observations: Observation[]
}

// Local dev only — the backend is reachable directly on its Docker Compose
// host port; see CORS setup in backend/app/main.py.
const API_BASE = 'http://localhost:8001'

export type Pool = '1-2' | '1' | '2'

const ENDPOINT_BY_POOL: Record<Pool, string> = {
  '1-2': '/kingdom/random/analyzed',
  '1': '/kingdom/random/pool1/analyzed',
  '2': '/kingdom/random/pool2/analyzed',
}

export async function drawAnalyzedKingdom(pool: Pool): Promise<AnalyzedKingdom> {
  const res = await fetch(`${API_BASE}${ENDPOINT_BY_POOL[pool]}`)
  if (!res.ok) {
    throw new Error(`Request failed: ${res.status} ${res.statusText}`)
  }
  return res.json()
}
