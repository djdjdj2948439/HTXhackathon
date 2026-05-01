# Veil Scout

> Predict with credits. Prove uniqueness with zkID. Earn by discovering real builders.

**Timeline:** 60-day development cycle (AI x Web3 Hackathon)

---

# 1. Problem

HTX hackathons, AI x Web3 ecosystems, DAOs, and incubators all face the same problem:

> **Lots of projects, but no reliable way to tell who can actually deliver vs. who is just packaging.**

Traditional evaluation methods — pitch decks, demos, team backgrounds, storytelling, KOL endorsements, short-window judge scoring, community hype — are all easily gamed and prone to misjudgment.

Some projects look polished but have no real execution capability. Some look rough, have unknown teams, but are technically solid and can actually deliver.

**Veil Scout solves this:**

> **How do you use market incentives to let the smartest people in the community discover which projects have real execution power?**

---

# 2. Core Positioning

This is **NOT** a Polymarket clone. It does not predict:

```
Will Iran and the US go to war?
Will BTC hit $200k?
Will some token get listed?
```

Veil Scout predicts:

```
Will this AI Agent complete 500 verified on-chain operations?
Will this project reach 1,000 active wallets in 30 days?
Will this smart contract pass a security audit?
Will this team complete the HTX-designated milestone?
Will this builder pass an anonymous backend challenge?
```

It is a **project-discovery prediction market**, not an entertainment prediction market.

More precisely:

> **Scout-to-Earn Prediction Network** — using prediction market mechanics for project due diligence, with token incentives rewarding accurate judgment.

---

# 3. Credits, Not Real Money

Users do not wager USDC/USDT on YES/NO outcomes. They use a platform-internal point system:

**Scout Credits:**
- Non-transferable
- Non-withdrawable
- Fixed allocation per season (e.g., 10,000 per user per season)
- Can only be used in prediction markets

### How It Works

A market is created:

```
Will AgentPay complete 1,000 verified AI-agent payments within 30 days?
```

- User thinks it will → buys YES with Scout Credits
- User thinks it won't → buys NO with Scout Credits

At deadline, the milestone is verified against on-chain/verifiable data:
- PASS → YES wins
- FAIL → NO wins

Correct predictions → gain Scout Credits + Scout Score.
Wrong predictions → lose credits.

### End-of-Season Rewards

Top performers on the leaderboard receive:

```
Token rewards (from season reward pool)
Alpha Scout SBT (on-chain reputation badge)
Ecosystem whitelists
HTX / B.AI / DAO privileges
Higher credit allocations in future seasons
```

This is not **Bet-to-Earn**. It is **Scout-to-Earn**.

---

# 4. Why Users Participate

Five motivation layers:

### 4.1 Leaderboard Competition

Limited initial credits force strategic allocation:
- Which projects do I believe in most?
- Which do I doubt most?
- How much do I concentrate vs. diversify?

Correct calls → score rises. Wrong calls → score falls. Ranked by Scout Score.

### 4.2 Token Rewards

Season reward pool distribution example:

```
Season Reward Pool: 100,000 tokens
Top 1:              15%
Top 2-10:           35%
Top 11-50:          30%
Evidence contributors: 20%
```

### 4.3 Alpha Scout Reputation

Accurate scouts build verifiable on-chain reputation:

```
Scout_0x7a3f
Accuracy: 78%
Virtual PnL: +42,000
Early Alpha Calls: 6
Evidence Score: 91
Specialty: AI Agent / Wallet / DeFi infra
```

Benefits: higher reward weight, lower fees, early market access, project whitelists, DAO review weight, ecosystem researcher badge.

### 4.4 Influence on Resource Allocation

If market results and leaderboard rankings influence:
- Project visibility and grant ranking
- Incubation candidacy and mentor support
- Demo day recommendations
- Post-hackathon investment watchlists

...then scouts are not playing a game — they are participating in ecosystem curation.

### 4.5 Proving Alpha

Many Web3 users want to prove:

```
I found the good project before everyone else.
I understood the risk better than the AI.
I spotted the flaw before the market did.
```

Veil Scout turns this instinct into **verifiable, on-chain reputation**.

---

# 5. zkID: Anti-Sybil Core

Once leaderboard rankings carry token rewards, the attack is obvious:

```
1 person → 100 wallets → 100 × 10,000 Scout Credits
→ hedge across markets → farm leaderboard → extract tokens
```

Wallet addresses alone cannot prevent this because **one person can have infinite wallets**.

### Solution: zkID Anti-Sybil Gate

Before claiming Scout Credits, users must prove:

> **"I am a unique, qualified participant — but I do not reveal my real identity."**

Anonymous, but not infinitely cloneable.

### Two enforcement points:

**1. Credit Allocation Gating**

```
1 zkID = 1 season allocation
```

Same real person, same season → only one credit claim, regardless of how many wallets they control.

**2. Leaderboard Identity**

Leaderboard scores are tied to zkID-derived anonymous identities (`Scout_0x7a3f`), not wallet addresses. Users can switch wallets but cannot duplicate their leaderboard identity.

### How It Works: nullifierHash

The `nullifierHash` is an anonymous fingerprint unique to each person per season:

```
Season = "HTX Genesis Scout Season 1"
User generates zkID proof → nullifierHash = 0xabc...
```

On-chain:

```solidity
usedNullifier[seasonId][nullifierHash] = true;
```

If the same person tries to claim with a different wallet, the nullifier reveals they have already claimed:

```
"Already claimed Scout Credits for this season."
```

**Implementation:** Semaphore v4 (lightweight ZKP group membership) or Worldcoin IDKit as plug-and-play fallback.

---

# 6. AI: First Analyst, Not Judge

AI is not the arbiter. AI is the **first analyst and initial odds generator**.

When a project is submitted, the AI reads:

```
Project description
GitHub activity
Demo link
Contract address
On-chain data
Milestone description
Risk factors
```

And generates an analysis report:

```
AI Initial Probability: 64%

Bullish:
- Demo is live
- Contract deployed
- AI × Web3 payment narrative fits
- GitHub activity is high

Bearish:
- Real active users are low
- No security audit
- Milestone may be too aggressive
- Possible wash activity

Suggested Market:
YES = 0.64
NO = 0.36
```

### Why This Matters

Without AI → markets start with no price and no discussion anchor.
With AI → users can immediately react:

```
AI overestimated → buy NO
AI underestimated → buy YES
```

The AI is a **liquidity provider and conversation starter**, not a judge. Its prediction is a starting point to be corrected by the crowd.

---

# 7. Market Design: What Gets Predicted

Every market must be a **clear, settleable question**.

**Bad questions (too vague, cannot settle):**

```
Is this a good project?
Does this team have potential?
Is this AI Agent strong?
```

**Good questions (specific, verifiable, binary):**

```
Will AgentPay complete 1,000 verified AI-agent payments before June 30?
Will this project deploy a verified smart contract before demo day?
Will this AI Agent complete 500 on-chain tasks without unauthorized transfers?
Will this builder pass the backend challenge with p95 latency < 100ms?
Will this protocol reach 10,000 testnet interactions within 14 days?
```

Every market requires:
- Clear target
- Clear deadline
- Clear data source
- Clear PASS / FAIL criteria

---

# 8. End-to-End Product Flow

### Step 1: Season Entry

User connects wallet → system prompts zkID verification → proof generated → uniqueness confirmed → **10,000 Scout Credits issued**.

### Step 2: Project Submits Milestone

```
Project: AgentPay
Track: AI × Web3 Payment
Milestone: 1,000 verified AI-agent payments in 30 days
Proof Source: smart contract events + backend verifier + unique wallet filter
Deadline: 2026-06-30
```

Market created:

```
Will AgentPay complete 1,000 verified AI-agent payments within 30 days?
```

### Step 3: AI Seeds Initial Odds

```
AI Initial YES: 0.62

Bullish: demo live, contract deployed, clear payment flow
Bearish: low active wallets, user acquisition uncertain, possible wash activity

Market opens: YES = 0.62 / NO = 0.38
```

### Step 4: Scouts Predict with Credits

```
Scout A (checked on-chain data):
  "Only 20 real wallets, most tx look like wash trading."
  → Buys NO

Scout B (found partnership info):
  "They've integrated with a real API, partner is driving traffic."
  → Buys YES

Scout C submits evidence:
  → On-chain event analysis showing wash pattern
  → Gets Evidence Score bonus if verified useful
```

**Rule: Each scout can only hold a single-side position per market (YES or NO, not both).** This prevents risk-free hedging.

### Step 5: Milestone Settlement

```
Deadline arrives. System verifies:
  Total payment events: 1,483
  Valid agent payments: 1,238
  Unique wallets: 412
  Invalid tx filtered: 245
  
  Target: 1,000 valid payments
  Result: PASS ✅
```

YES wins. YES holders gain virtual PnL and Scout Score. NO holders lose credits.

### Step 6: Leaderboard Scoring

```
Scout Score =
  Virtual PnL
  + Accuracy Bonus
  + Early Discovery Bonus
  + Evidence Score
  - Risk Penalty (excessive concentration)
  - Spam Penalty
```

**Early Discovery Bonus** is key:
- Bought YES at 0.20, market settles PASS → **high score** (early alpha discovery)
- Bought YES at 0.90, market settles PASS → **low score** (late follower)
- Bought NO at 0.10, market settles FAIL → **high score** (contrarian insight)

This rewards people who genuinely identified mispricing early, not those who pile on after consensus forms.

### Step 7: Season Rewards

```
Top Scouts → token rewards from season pool
High-accuracy scouts → Alpha Scout SBT
Quality evidence submitters → bonus rewards
High-reputation scouts → higher credit allocation next season + whitelists
```

### Flywheel

```
AI seeds initial odds
      ↓
Scouts correct mispricing with credits
      ↓
Milestones settle with verifiable data
      ↓
Accurate scouts earn score + rewards
      ↓
Leaderboard attracts more smart participants
      ↓
Ecosystem gets more accurate project discovery signals
      ↓
Project resource allocation improves
      ↓
More projects want to be listed → more markets → cycle repeats
```

---

# 9. Product Modules

## Module 1: zkID Anti-Sybil Gate

```
Verify unique participant (Semaphore v4 / Worldcoin IDKit)
Prevent multi-wallet credit farming
Generate anonymous Scout ID (Scout_0x...)
Enforce 1 credit allocation per zkID per season
```

## Module 2: Scout Credit System

```
Issue non-transferable credits per season
Track virtual positions per market
Enforce single-side position rule (YES or NO, not both)
Cap per-market allocation (e.g., max 20% of total credits per market)
Prevent all-in luck-based leaderboard gaming
```

## Module 3: AI Analyst

```
Ingest project materials (description, GitHub, contract, on-chain data)
Generate initial probability estimate
Output structured bullish / bearish analysis
Assess whether proposed milestone is objectively settleable
Set initial market odds
```

## Module 4: Prediction Arena

```
Create YES / NO markets for each project milestone
Users buy positions with Scout Credits
Market price adjusts with trading activity
Support evidence submission (links, screenshots, on-chain analysis)
Display real-time odds and position sizes
```

**AMM note:** Production version can use LMSR for mathematically rigorous pricing:

$$ C(q) = b \ln \left( \sum_{i \in \{YES, NO\}} \exp(q_i / b) \right) $$

Hackathon MVP can use a simplified constant-product or fixed-ratio pool to reduce implementation complexity.

## Module 5: Settlement Oracle

```
Read on-chain events / GitHub data / API endpoints / test results
Determine milestone PASS / FAIL
Post result on-chain
Support challenge period (roadmap — V2)
```

## Module 6: Leaderboard & Reward Engine

```
Calculate Scout Score (PnL + accuracy + early discovery + evidence - penalties)
Rank all scouts
Distribute token rewards from season pool
Mint Alpha Scout SBT for top performers
Display historical accuracy, specialty, and track record
```

---

# 10. Why This Fits HTX Hackathon

This is not a generic prediction market. It is a **decentralized project discovery layer** purpose-built for the HTX / AI x Web3 ecosystem.

**What the ecosystem wants to know:**

```
Who can actually deliver?
Who is just packaging?
Who deserves continued support?
Who should enter incubation / grants / investment pipelines?
```

**What Veil Scout provides:**

```
AI initial screening
Community scouts predict with credits
zkID prevents multi-account gaming
Milestone settlement verifies judgment
Leaderboard rewards the best project evaluators
```

It upgrades hackathon evaluation from:

```
Judges scoring subjectively in a short window
```

To:

```
AI + community + market + data settlement = continuous discovery system
```

---

# 11. vs. Generic Prediction Markets

| Generic Prediction Market | Veil Scout |
|--------------------------|------------|
| Real money wagering | Scout Credits (non-transferable) |
| Predicts news, sports, politics, token prices | Predicts project execution capability |
| Users seek thrill | Users compete for leaderboard, tokens, reputation |
| Looks like gambling | Looks like a project discovery competition |
| Primarily about liquidity | Primarily about prediction accuracy |
| Wallets can Sybil-farm | zkID prevents multi-account abuse |
| Results disconnected from ecosystem | Results influence project resource allocation |

---

# 12. Pitch Summary

**English:**

> Veil Scout is a zkID-gated Scout-to-Earn prediction arena for AI x Web3 project discovery. Users do not wager real money. Instead, each verified unique participant receives non-transferable Scout Credits and uses them to predict whether projects will complete objective milestones. AI analysts seed the initial probabilities, human scouts correct mispriced odds, and verified milestone outcomes settle the markets. The most accurate scouts climb the leaderboard and earn token rewards, reputation badges, and ecosystem privileges.

**Chinese:**

> Veil Scout 是一个用 zkID 防女巫攻击的 Scout-to-Earn 项目发现预测平台。用户不拿真钱下注，而是每个通过 zkID 验证的唯一参与者领取不可转让的 Scout Credits，用这些积分预测项目能否完成客观 milestone。AI 先给初始概率，人类 Scout 用积分纠正错误定价，最终由可验证结果结算。预测最准确的人登上排行榜，获得代币奖励、声誉徽章和生态权益。

---

# 13. One-Liner

> **用 zkID 保证每个 Scout 唯一，用 AI 启动市场，用积分预测项目执行结果，用排行榜和代币奖励发现真正看得准的人。**

> **Predict with credits. Prove uniqueness with zkID. Earn by discovering real builders.**