# Veil Scout: Tech Roadmap & Stack

**Timeline:** 60 days

---

## Recommended Tech Stack

### Smart Contracts (Core)
| Component | Tool | Why |
|-----------|------|-----|
| Language | **Solidity 0.8.x** | Mature ecosystem, most audit tools available |
| Framework | **Foundry (forge + cast)** | Fast compilation, native fuzzing, Solidity-native tests |
| Local chain | **Anvil** (ships with Foundry) | Fork mainnet for integration tests |
| Deployment target | **Base (L2)** or **Arbitrum Sepolia** (testnet) | Low gas, fast finality |
| Math library | **PRBMath v4** (optional) | Only needed if implementing LMSR in V2; MVP can use simpler pool math |

### AI Analyst (Module 3)
| Component | Tool | Why |
|-----------|------|-----|
| LLM API | **Claude API** or **OpenAI GPT-4o** | Project analysis: GitHub, contract, on-chain data, milestone feasibility |
| Agent script | **Python + web3.py** | Lightweight: read project data → LLM analysis → set initial odds on-chain |
| Wallet | **Local private key** (testnet only) | Agent signs transactions to seed initial market odds |
| Data ingestion | **GitHub API + Etherscan API + IPFS gateway** | Fetch project materials for analysis |

### zkID Anti-Sybil (Module 1)
| Component | Tool | Why |
|-----------|------|-----|
| Primary | **Semaphore v4** | Lightweight ZKP group membership — nullifierHash prevents multi-claim per season |
| Fallback | **Worldcoin IDKit** | Plug-and-play Proof of Unique Human if Semaphore too complex |

### Frontend
| Component | Tool | Why |
|-----------|------|-----|
| Framework | **Next.js 14** | SSR + API routes in one project |
| Styling | **TailwindCSS + shadcn/ui** | Fast, modern UI |
| Wallet connection | **RainbowKit + wagmi v2** | Best UX for wallet connect |
| Charts | **Lightweight Charts (TradingView)** | Real-time odds chart per market — high visual impact |
| Contract interaction | **viem** (ships with wagmi) | Type-safe, fast |

### Settlement Oracle (Module 5)
| Component | Tool | Why |
|-----------|------|-----|
| On-chain data | **Etherscan / Blockscout API** | Read contract events for milestone verification |
| GitHub data | **GitHub REST API** | Commit activity, PR merges, deployment status |
| Oracle script | **Python** | Aggregate data sources → determine PASS/FAIL → call `settle()` on-chain |
| Future (V2) | **Chainlink Functions / UMA Optimistic Oracle** | Decentralized settlement for production |

---

## 60-Day Development Roadmap

**Team:** 3 people. Tasks are labeled by skill area — assign based on your strengths.

**Skill labels:**
- **🔗 Contracts** — Solidity, Foundry, on-chain logic. Best for: someone comfortable with smart contract dev.
- **🤖 AI / Backend** — Python, LLM APIs, data ingestion, oracle scripts. Best for: someone comfortable with Python + API integration.
- **🎨 Frontend** — Next.js, React, TailwindCSS, wallet integration. Best for: someone comfortable with web dev + UI.
- **🧮 Design / Math** — Mechanism design, tokenomics, scoring formulas, testing. Best for: someone with strong analytical/math background.
- **👥 All** — Everyone involved.

---

### Phase 1: Core Contracts + Credit System (Days 1–14)

**Goal:** Scout Credit system + simplified prediction market functional on testnet.

| Day | Task | Skill |
|-----|------|-------|
| 1-3 | Set up Foundry project. Implement `ScoutCredits.sol`: non-transferable credit token, per-season mint (gated by zkID nullifier) | 🔗 Contracts |
| 1-3 | Design Scout Credit economics: season allocation size, per-market cap (e.g., max 20%), single-side position rule math | 🧮 Design / Math |
| 4-7 | Implement `Market.sol`: create market, buy YES/NO with credits, enforce single-side rule, state machine (OPEN → TRADING → SETTLING → SETTLED) | 🔗 Contracts |
| 4-7 | Design simplified AMM: constant-product or fixed-ratio pool for MVP. Define buy/sell price curves | 🧮 Design / Math |
| 8-10 | Implement `MarketFactory.sol` (create markets from milestone submissions) + `Settlement.sol` (owner-triggered PASS/FAIL, credit redistribution) | 🔗 Contracts |
| 8-10 | Set up Next.js project skeleton: TailwindCSS + shadcn/ui + RainbowKit + wagmi. Build wallet connect + basic layout | 🎨 Frontend |
| 11-14 | Integration test on Anvil: full lifecycle (create season → mint credits → create market → buy YES/NO → settle → verify balances) | 🔗 Contracts + 🧮 Math |
| 11-14 | Deploy to Arbitrum Sepolia testnet, verify contracts | 🔗 Contracts |

**Deliverable:** Working credit-based prediction market on testnet: create season, claim credits (mock zkID), create milestone market, buy YES/NO, settle, credits redistributed.

---

### Phase 2: AI Analyst + zkID + Frontend (Days 15–28)

**Goal:** AI seeds initial odds. zkID prevents multi-claim. Frontend is usable.

| Day | Task | Skill |
|-----|------|-------|
| 15-18 | Build Python AI analyst: ingest project description + GitHub + contract address → LLM analysis → structured JSON output (probability, bullish/bearish reasons) → call `seedMarket()` on-chain | 🤖 AI / Backend |
| 15-18 | Build frontend: season entry page, market browse/list page, basic market card components | 🎨 Frontend |
| 19-22 | Tune AI prompt for milestone feasibility analysis. Add sanity checks (clamp probability to 0.05–0.95). Handle LLM failures gracefully (fallback to 0.50) | 🤖 AI / Backend |
| 19-22 | Build market detail page: odds display, buy YES/NO panel, evidence submission form, AI analysis report card | 🎨 Frontend |
| 23-25 | Integrate Semaphore v4: user joins group → generates proof → contract verifies nullifier → mints credits. (Worldcoin IDKit as fallback if Semaphore is too complex) | 🔗 Contracts + 🤖 Backend |
| 23-25 | Build scout dashboard: credit balance, active positions, virtual PnL, season stats | 🎨 Frontend |
| 26-28 | End-to-end integration test: zkID verify → claim credits → AI seeds market → scout buys YES/NO → positions displayed in UI | 👥 All |

**Deliverable:** Full loop on testnet with frontend — zkID gate → credit claim → AI-seeded market → scout trading.

---

### Phase 3: Settlement + Leaderboard + Polish (Days 29–45)

**Goal:** Milestone settlement works. Leaderboard scores and ranks scouts. Evidence system functional.

| Day | Task | Skill |
|-----|------|-------|
| 29-33 | Build settlement oracle script: read on-chain events + GitHub API → determine PASS/FAIL → call `settle()` on-chain | 🤖 AI / Backend |
| 29-33 | Implement leaderboard logic (contract or off-chain indexer): Scout Score = PnL + accuracy + early discovery + evidence - penalties | 🧮 Design / Math + 🔗 Contracts |
| 34-38 | Implement evidence submission + scoring: scouts submit links/analysis → manual review for MVP (AI-assisted in V2) → bonus score | 🤖 AI / Backend |
| 34-38 | Build leaderboard page: ranking table, scout profiles, accuracy stats. Build settlement countdown + result display | 🎨 Frontend |
| 39-42 | Implement reward distribution: season-end function distributing tokens to top N scouts. Design Alpha Scout SBT metadata | 🔗 Contracts + 🧮 Math |
| 39-42 | Build reward claim page + project submission page (for teams to submit milestones) + AI analysis display per market | 🎨 Frontend |
| 43-45 | Security review: reentrancy, overflow, access control. Test edge cases (all credits on one market, settlement ties, credit non-transferability) | 🔗 Contracts + 👥 All |
| 43-45 | Responsive design, error handling, loading states, mobile layout | 🎨 Frontend |

**Deliverable:** Complete product — zkID entry → AI-seeded markets → scout predictions → milestone settlement → leaderboard ranking → reward distribution.

---

### Phase 4: Demo & Pitch (Days 46–60)

**Goal:** Polished demo with compelling narrative.

| Day | Task | Skill |
|-----|------|-------|
| 46-50 | Prepare demo scenario: seed 3-5 project markets (mix of strong/weak/suspicious). Script walkthrough showing AI analysis → scout trading → settlement → leaderboard | 👥 All |
| 46-50 | Build pitch deck: problem → solution → live demo → architecture → zkID + AI roles → flywheel → HTX ecosystem fit | 🧮 Design / Math |
| 51-55 | Write mechanism design section: Scout Score formula, credit economics, anti-gaming analysis (single-side rule + credit cap + zkID) | 🧮 Design / Math |
| 51-55 | Record demo video as backup. Prepare local Anvil fallback for live demo | 🎨 Frontend + 🔗 Contracts |
| 56-60 | Rehearse pitch (5 min pitch + 3 min demo + 2 min Q&A). Prep Q&A: "how is this different from voting?", "what if AI is wrong?", "how do you prevent collusion?" | 👥 All |
| 56-60 | Final bug fixes, seed demo data, deploy clean version for demo day | 👥 All |

**Deliverable:** Pitch-ready project with live demo, backup video, and clear "Scout-to-Earn for project discovery" narrative.

---

## Critical Path & Risk Mitigation

| Risk | Probability | Mitigation |
|------|------------|------------|
| Semaphore v4 integration complexity | Medium | Worldcoin IDKit as plug-and-play fallback; worst case, use simple address-based identity + rate limiting for demo |
| AI analyst gives nonsensical probabilities | Medium | Hardcode fallback (default 0.5 if LLM fails), sanity clamp (0.05–0.95), display AI confidence level |
| Non-transferable credit token edge cases | Medium | Thoroughly test: can't transfer, can't approve, can't be flash-loaned. Use custom implementation, not standard ERC-20 |
| Settlement oracle data unreliable | Medium | Support multiple data sources per market. For demo, use pre-seeded verifiable data |
| Scout Score gaming (all-in on one market) | Low | Per-market credit cap (max 20%). Risk penalty in score formula for excessive concentration |
| Demo day live chain issues | Medium | Pre-record video demo as backup, deploy to local Anvil as second fallback |

---

## File Structure (Suggested)

```
veil-scout/
├── contracts/                  # Foundry project
│   ├── src/
│   │   ├── ScoutCredits.sol   # Non-transferable credit token (soulbound)
│   │   ├── Season.sol         # Season lifecycle + zkID nullifier registry
│   │   ├── Market.sol         # YES/NO market: buy, sell, position tracking
│   │   ├── MarketFactory.sol  # Create markets from project milestones
│   │   ├── Settlement.sol     # Oracle-triggered PASS/FAIL + credit redistribution
│   │   ├── Leaderboard.sol    # Scout Score computation + ranking (or off-chain indexer)
│   │   └── RewardVault.sol    # Season reward pool + token distribution
│   ├── test/
│   │   ├── ScoutCredits.t.sol # Non-transferability, mint gating, season limits
│   │   ├── Market.t.sol       # Single-side rule, credit cap, state machine
│   │   └── Integration.t.sol  # Full season lifecycle
│   └── foundry.toml
├── ai-analyst/                 # Python AI analyst
│   ├── analyst.py             # Main: watch new projects → analyze → seed odds
│   ├── llm.py                 # LLM API wrapper (project data → probability + report)
│   ├── data_ingestion.py      # Fetch GitHub / Etherscan / IPFS data
│   └── requirements.txt
├── oracle/                     # Settlement oracle
│   ├── verifier.py            # Aggregate data sources → PASS/FAIL
│   ├── sources/               # Data source adapters (etherscan, github, custom API)
│   └── settler.py             # Post result on-chain
├── frontend/                   # Next.js app
│   ├── app/
│   │   ├── page.tsx           # Landing: "Scout-to-Earn: Discover Real Builders"
│   │   ├── season/            # Season entry + zkID verification
│   │   ├── markets/           # Browse all project milestone markets
│   │   ├── market/[id]/       # Market detail: odds chart, trade panel, AI report, evidence
│   │   ├── submit/            # Project team: submit milestone for market creation
│   │   ├── leaderboard/       # Scout rankings, scores, profiles
│   │   └── dashboard/         # Scout: credit balance, positions, PnL, rewards
│   ├── components/
│   ├── lib/
│   │   ├── contracts.ts       # ABI + addresses
│   │   └── wagmi.ts           # Wallet config
│   └── package.json
└── docs/
    ├── The Oracle of Truth.md  # Project design doc (Veil Scout)
    └── tech-roadmap.md         # This file
```
