# Role and Task
You are an Expert Web3 Software Architect, DeFi Protocol Designer, and Hackathon Coach.
My team consists of one Mathematics/Statistics major and one Mechanical Engineering major. We have a 60-day development cycle for an AI x Web3 Hackathon.
We are building **Project Veil: The Continuous Hackathon Protocol**, a "Decentralized Micro-Seed Engine based on Streaming Finance and Proof-of-Execution".
I need you to evaluate our architectural design, assess edge cases in the tokenomics, and provide a minimal viable code scaffold for the core smart contract.

# Project Overview: Project Veil
**Problem:** Traditional VC and hackathons have immense friction: months of due diligence, complex legal contracts, and opaque post-investment fund usage. This limits seed funding to those with "perfect backgrounds."

**Solution:** A protocol that reduces the startup barrier to zero. It replaces lump-sum funding with Streaming Finance and Soulbound Tokens (SBTs). Anyone with a great idea and execution capability can raise micro-funds that stream by the second based on development milestones. Execution history replaces static diplomas.

# System Architecture (3 Core Modules)

**Module 1: Permissionless Micro-Curation**
- Founders submit an MVP plan and funding request to generate a vault.
- The community, micro-VCs, or geeks fund the vault via prediction markets or Quadratic Funding (QF). Founders achieve consensus but CANNOT withdraw any lump sum.

**Module 2: Streaming Finance & Circuit Breaker**
- **Streaming Engine:** Funds are locked in an Escrow contract. A release curve drips funds block-by-block into the founder's public working wallet.
- **Extreme Transparency:** Every gas fee or server rental paid from the working wallet is traceable on-chain.
- **Trustless Circuit Breaker:** If investors notice stalled Github activity or misappropriated funds, they can initiate a "halt proposal." If passed, the smart contract instantly shuts the valve and refunds remaining funds to investors.

**Module 3: Proof-of-Execution & Dynamic SBT**
- **Behavior Assetization:** Hitting a milestone (e.g., high-quality PR, API integration) triggers the smart contract to unlock a higher fund flow rate.
- **Reputation Accumulation:** Successful unlocks mint/upgrade an "Execution SBT" for the founder. This high-level SBT becomes their strongest credit credential for future startups, even if the current project fails.

# Strict Scope (Legitimacy Boundary)
- **NO Offline Businesses:** We acknowledge the Oracle Problem. We strictly refuse to serve real-world entities (e.g., cafes, hardware manufacturing) where offline data uploads can be easily faked.
- **100% Digital-Native:** V1 focuses entirely on open-source software, AI Agent dev, and Web3 infra. Execution (Github commits, contract deployments, API calls) can be objectively captured and settled by on-chain data or AI verifier nodes, ensuring absolute fairness for the streaming valve.

# Evaluation Requests for You

1. **Control Theory & Security:** From a systems engineering perspective, what are the biggest attack vectors in a "cancellable streaming finance" contract with milestone triggers? How do we prevent reentrancy or griefing attacks when the circuit breaker is pulled?
2. **Optimal Tech Stack:** Should we build on top of existing streaming protocols (like Sablier / Superfluid) or write a custom escrow contract optimized for our milestone-trigger logic? How do we handle dynamic metadata updates for the SBT?
3. **Core Smart Contract Scaffold:** Please write the Solidity code scaffold for the intersection of **Module 2 and Module 3**. I need the escrow logic that streams funds per block, includes a `haltStream()` function for community circuit breaking, and an `unlockHigherStreamRate()` function triggered by verified milestones.