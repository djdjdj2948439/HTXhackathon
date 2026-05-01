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

**Team:** 3 people, each owns one track end-to-end.

| Track | Scope | Tech Involved | Skills Required |
|-------|-------|--------------|-----------------|
| **Track A: Contracts** | All Solidity contracts + tests + deployment | Solidity, Foundry, PRBMath | 🔗 Contracts + 🧮 Math |
| **Track B: AI + Oracle** | AI analyst + settlement oracle + data ingestion + Scout Score design | Python, LLM API, web3.py | 🤖 AI/Backend + 🧮 Math |
| **Track C: Frontend** | All UI pages + wallet interaction + charts | Next.js, React, TailwindCSS, wagmi | 🎨 Frontend |

---

### ⚠️ Day 0: Interface Contract (half day, all 3 together)

**The only hard sync point.** After aligning interfaces, the team can develop fully independently for 4 weeks, with only a 30-minute Sunday sync each week.

#### Interfaces to define:

**1. Contract ABI Draft (produced by Track A, consumed by Track B/C)**

```solidity
// ScoutCredits.sol
function claimCredits(uint256 seasonId, bytes calldata zkProof) external;
function creditBalance(address user, uint256 seasonId) external view returns (uint256);
event CreditsClaimed(address indexed user, uint256 seasonId, uint256 amount);

// MarketFactory.sol
function createMarket(string calldata milestone, uint256 deadline, string calldata dataSource) external returns (uint256 marketId);
event MarketCreated(uint256 indexed marketId, string milestone, uint256 deadline);

// Market.sol
enum Side { YES, NO }
enum Status { OPEN, TRADING, SETTLING, SETTLED }
function buy(uint256 marketId, Side side, uint256 amount) external;
function getPrice(uint256 marketId) external view returns (uint256 yesPrice, uint256 noPrice);
function getPosition(uint256 marketId, address user) external view returns (uint256 yesAmount, uint256 noAmount);
function seedInitialOdds(uint256 marketId, uint256 yesProbability) external; // Called by AI
event Trade(uint256 indexed marketId, address indexed user, Side side, uint256 amount, uint256 newPrice);

// Settlement.sol
function settle(uint256 marketId, bool passed) external; // Called by Oracle
event MarketSettled(uint256 indexed marketId, bool passed);

// Leaderboard.sol
function getScore(address user, uint256 seasonId) external view returns (int256);
function getRanking(uint256 seasonId, uint256 topN) external view returns (address[] memory, int256[] memory);

// RewardVault.sol
function claimReward(uint256 seasonId) external;
event RewardClaimed(address indexed user, uint256 seasonId, uint256 amount);
```

**2. AI Output JSON Schema (produced by Track B, consumed by Track C)**

```json
{
  "marketId": 1,
  "probability": 0.64,
  "confidence": "medium",
  "bullish": ["Demo is live", "Contract deployed on mainnet"],
  "bearish": ["Low active users", "No security audit"],
  "riskFlags": ["possible wash trading"],
  "settleable": true,
  "dataSourcesUsed": ["github", "etherscan"]
}
```

**3. Event List for Frontend (produced by Track A, subscribed by Track C)**

```
CreditsClaimed, MarketCreated, Trade, MarketSettled, RewardClaimed
```

**4. Shared Constants**

```
CREDITS_PER_SEASON = 10000
MAX_CREDIT_PER_MARKET = 2000 (20%)
MIN_PROBABILITY = 0.05
MAX_PROBABILITY = 0.95
```

---

### Independence Strategy: How Each Track Avoids Being Blocked

| Track | Depends On | Unblocking Strategy |
|-------|-----------|---------------------|
| **A: Contracts** | No one | Start immediately |
| **B: AI + Oracle** | Contract ABI + deployed address | First 2 weeks: use local Anvil fork with mock contracts (only need ABI, not full implementation); alternatively, build off-chain parts first (data ingestion + LLM analysis), integrate with Track A after deployment |
| **C: Frontend** | Contract ABI + AI reports | First 2 weeks: use **hardcoded mock data** for all pages; ABI draft available from Day 0; AI reports use mock JSON |

**Result: All 3 can develop completely independently for 2 weeks after Day 1, with no communication needed until the Week 2 Sunday Sync.**

---

### Phase 1: Foundation (Days 1–14)

#### Track A: Contracts

| Day | Task |
|-----|------|
| 1-2 | Set up Foundry project + project structure. Export ABI JSON files for Track B/C (even if contracts are incomplete, the ABI interface is fixed) |
| 3-5 | Implement `ScoutCredits.sol`: non-transferable credit token, per-season mint. Use mock zkID for now (simple address whitelist) |
| 6-9 | Implement `Market.sol`: buy YES/NO with credits, single-side position rule, per-market credit cap, state machine (OPEN → TRADING → SETTLING → SETTLED). Implement simplified AMM pricing |
| 10-12 | Implement `MarketFactory.sol` (create markets from milestone submissions) + `Settlement.sol` (owner-triggered PASS/FAIL, credit redistribution to winners) |
| 13-14 | Foundry integration tests: create season → claim credits → create market → buy YES/NO → settle → verify balances. Deploy to Arbitrum Sepolia |

**Deliverable A1:** Core contracts deployed on testnet + exported ABI files.

#### Track B: AI + Oracle

| Day | Task |
|-----|------|
| 1-3 | Set up Python project. Build data ingestion layer: GitHub API (commits, PRs, contributors), Etherscan API (contract events, tx count) |
| 4-7 | Build AI analyst core: project data → LLM prompt → structured JSON output (probability + bullish/bearish + confidence). Use Claude or GPT-4o |
| 8-10 | Add sanity checks (clamp 0.05–0.95), LLM failure fallback (default 0.50), structured logging. Design Scout Score formula (PnL + accuracy + early discovery + evidence - penalties) |
| 11-14 | Test with 3-5 sample projects: AI generates reports → verify output quality. Build `seedMarket()` caller script (integrate with Track A after deployment; use local Anvil mock for now) |

**Deliverable B1:** AI analyst capable of generating analysis reports for any project + Scout Score formula document.

#### Track C: Frontend

| Day | Task |
|-----|------|
| 1-3 | Set up Next.js 14 + TailwindCSS + shadcn/ui + RainbowKit + wagmi. Build global layout, wallet connect, nav bar. Create `lib/mockData.ts` with mock data for all pages |
| 4-7 | Build season entry page (zkID verification flow → claim credits). Build market browse page (market cards: project name, odds, deadline, status) |
| 8-10 | Build market detail page: odds display, buy YES/NO panel, position display, AI analysis card (read mock JSON) |
| 11-14 | Build scout dashboard: credit balance, positions across markets, virtual PnL. All pages independently demo-able with mock data |

**Deliverable C1:** All core pages built (with mock data), UI flow independently demo-able.

#### 🔄 Week 2 Sunday Sync (Day 14)

```
Integration tasks:
1. Track C replaces mock data with Track A's exported ABI → verify claim credits + buy YES/NO works in UI
2. Track B's AI analyst connects to Track A's deployed MarketFactory → verify seedMarket() posts on-chain
3. Fix any interface mismatches
Duration: 2-3 hours
```

---

### Phase 2: Feature Complete (Days 15–28)

#### Track A: Contracts

| Day | Task |
|-----|------|
| 15-18 | Integrate Semaphore v4 for real zkID: user joins group → generates proof → contract verifies nullifier → mints credits. (Worldcoin IDKit as fallback) |
| 19-22 | Implement `Leaderboard.sol` (or off-chain indexer): integrate Scout Score formula designed by Track B |
| 23-25 | Implement `RewardVault.sol`: season reward pool, token distribution to top N scouts. Design Alpha Scout SBT metadata + mint function |
| 26-28 | Implement on-chain evidence submission: store evidence hashes per market, track evidence scores per scout |

**Deliverable A2:** Full contract suite: credits + markets + zkID + leaderboard + rewards + evidence.

#### Track B: AI + Oracle

| Day | Task |
|-----|------|
| 15-18 | Build settlement oracle: read on-chain events + GitHub API at deadline → aggregate data → determine PASS/FAIL → call `settle()` on-chain |
| 19-22 | Build multi-source verifier: support contract event counting, unique wallet filtering, GitHub commit/PR verification. Handle edge cases (data source down → retry / manual flag) |
| 23-25 | Build evidence scoring helper: AI reads submitted evidence links → assess quality/relevance → output score suggestion (manual confirm for MVP) |
| 26-28 | End-to-end test: project deadline arrives → oracle aggregates data → settles market → credit redistribution triggers |

**Deliverable B2:** Settlement oracle with auto-settle capability + AI evidence scorer.

#### Track C: Frontend

| Day | Task |
|-----|------|
| 15-18 | Replace all mock data with real contract calls. Add tx confirmation flows (loading → success → error) |
| 19-22 | Build evidence submission page: upload links/screenshots/analysis per market. Build AI analysis report display (structured bullish/bearish card) |
| 23-25 | Build leaderboard page: ranking table, scout profiles (accuracy %, PnL, early alpha calls, specialty tags). Build settlement countdown + result display |
| 26-28 | Build project submission page (for teams to submit milestones) + reward claim page. Polish all pages |

**Deliverable C2:** Fully functional frontend, all pages connected to live contracts.

#### 🔄 Week 4 Sunday Sync (Day 28)

```
Full pipeline integration test:
zkID verify → claim credits → AI seeds market → scout trades
→ evidence submitted → deadline → oracle settles → leaderboard updates → rewards claimable

If this flow runs end-to-end = Feature Complete ✅
Duration: half day
```

---

### Phase 3: Polish + Security (Days 29–42)

All 3 return to collaborative mode, working by expertise.

| Day | Task | Who |
|-----|------|-----|
| 29-31 | Contract security audit: reentrancy, overflow, access control. Fuzz test credit non-transferability, single-side enforcement, settlement edge cases | Track A lead |
| 29-31 | AI prompt hardening: adversarial testing (feed garbage projects, test edge inputs). Oracle retry/failure handling | Track B lead |
| 29-31 | Responsive design, error handling, loading states, mobile layout | Track C lead |
| 32-35 | Fix integration bugs from Week 4 sync. Stress test with 10+ markets and 20+ scout addresses | All |
| 36-38 | Seed demo data: create 3-5 realistic project markets (strong / weak / suspicious mix). Generate AI reports for each | All |
| 39-42 | UX polish: onboarding flow, tooltips, empty states, transaction feedback. Final contract audit pass | Track C + Track A |

**Deliverable:** Production-quality MVP. All flows smooth, edge cases handled, demo data seeded.

---

### Phase 4: Demo & Pitch (Days 43–60)

| Day | Task | Who |
|-----|------|-----|
| 43-46 | Script demo walkthrough: AI analysis → scout trading → evidence → settlement → leaderboard. Practice screen flow | All |
| 47-50 | Build pitch deck: problem (project discovery is broken) → solution (Scout-to-Earn) → live demo → architecture → zkID + AI roles → flywheel → HTX ecosystem fit | All (one person leads deck design) |
| 51-53 | Write mechanism design section: Scout Score formula derivation, credit economics, anti-gaming analysis (single-side + credit cap + zkID) | Track B lead |
| 54-55 | Record demo video as backup. Prepare local Anvil fallback for live demo | Track C + Track A |
| 56-58 | Rehearse pitch (target: 5 min pitch + 3 min demo + 2 min Q&A). Prep Q&A: "how is this different from voting?", "what if AI is wrong?", "how do you prevent collusion?" | All |
| 59-60 | Final bug fixes, re-deploy clean version, last rehearsal | All |

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
