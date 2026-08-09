import { useState } from 'react'
import './App.css'

function App() {
  const [healthResult, setHealthResult] = useState<string | null>(null)
  const [kingdomRandomResult, setKingdomRandomResult] = useState<any[]>([])
  const [kingdomRandomAnalyzedResult, setKingdomRandomAnalyzedResult] = useState<any | null>(null)

  async function checkHealth() {
    const res = await fetch('http://localhost:8001/health')
    const data = await res.json()
    setHealthResult(JSON.stringify(data))
  }

  async function kingdomRandom() {
    const res = await fetch('http://localhost:8001/kingdom/random')
    const data = await res.json()
    setKingdomRandomResult(data)
  }

  async function kingdomRandomAnalyzed() {
    const res = await fetch('http://localhost:8001/kingdom/random/analyzed')
    const data = await res.json()
    setKingdomRandomAnalyzedResult(data)
  }

  return (
    <main id="center">
      <h1>Dominion advisor</h1>

      <section>
        <button type="button" onClick={checkHealth}>
          Call /health
        </button>
        {healthResult && <p>Backend said: {healthResult}</p>}
      </section>

      <section>
        <button type="button" onClick={kingdomRandom}>
          Call /kingdom/random — generate a random kingdom
        </button>
        <ul>
          {kingdomRandomResult.map((card) => (
            <li key={card.name}>{card.name}</li>
          ))}
        </ul>
      </section>

      <section>
        <button type="button" onClick={kingdomRandomAnalyzed}>
          Call /kingdom/random/analyzed — generate and analyze a random kingdom
        </button>
        {kingdomRandomAnalyzedResult && (
          <ul>
            {kingdomRandomAnalyzedResult.cards.map((card) => (
              <li key={card.name}>{card.name}</li>
            ))}
          </ul>
        )}
        {kingdomRandomAnalyzedResult && (
          <ul>
            {kingdomRandomAnalyzedResult.observations.map((obs, i) => (
              <li key={i}>
                <strong>{obs.category}</strong>: {obs.finding} - {obs.detail}
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  )
}

export default App
