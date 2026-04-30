from __future__ import annotations

import math
from typing import Any, Literal

import numpy as np
import pandas as pd
from pydantic import BaseModel, Field


MechanismKey = Literal["token_weighted", "quadratic", "shielded_hybrid"]
Severity = Literal["critical", "high", "medium", "low"]


class ProposalConfig(BaseModel):
    name: str
    category: str = "governance"
    summary: str = ""
    treasury_request_pct: float = Field(0.10, ge=0.0, le=1.0)
    expected_upside: float = Field(0.15, ge=-1.0, le=1.0)
    execution_risk: float = Field(0.35, ge=0.0, le=1.0)
    decentralization_impact: float = Field(0.10, ge=-1.0, le=1.0)
    urgency: float = Field(0.50, ge=0.0, le=1.0)
    proposer_reputation: float = Field(0.10, ge=-1.0, le=1.0)


class EnvironmentConfig(BaseModel):
    label: str = "Stress Mix"
    market_volatility: float = Field(0.18, ge=0.0, le=1.0)
    negative_shock_probability: float = Field(0.22, ge=0.0, le=1.0)
    whale_coordination: float = Field(0.65, ge=0.0, le=1.0)
    voter_apathy: float = Field(0.35, ge=0.0, le=1.0)
    social_sentiment: float = Field(0.00, ge=-1.0, le=1.0)
    manipulation_pressure: float = Field(0.52, ge=0.0, le=1.0)
    noise_scale: float = Field(0.18, ge=0.0, le=1.0)


class MechanismConfig(BaseModel):
    key: MechanismKey
    label: str
    quorum: float = Field(0.28, ge=0.0, le=1.0)
    approval_threshold: float = Field(0.55, ge=0.0, le=1.0)
    whale_cap_pct: float | None = Field(default=None, ge=0.0, le=1.0)
    participant_yes_threshold: float | None = Field(default=None, ge=0.0, le=1.0)


class AgentProfile(BaseModel):
    agent_id: str
    archetype: str
    voting_power: float = Field(gt=0.0)
    reputation: float = Field(0.50, ge=0.0, le=1.0)
    risk_tolerance: float = Field(0.50, ge=0.0, le=1.0)
    growth_bias: float = Field(0.00, ge=-1.0, le=1.0)
    decentralization_bias: float = Field(0.00, ge=-1.0, le=1.0)
    treasury_guard_bias: float = Field(0.00, ge=-1.0, le=1.0)
    turnout_discipline: float = Field(0.50, ge=0.0, le=1.0)
    herd_sensitivity: float = Field(0.00, ge=0.0, le=1.0)
    manipulation_tendency: float = Field(0.00, ge=0.0, le=1.0)
    market_beta: float = Field(0.00, ge=-1.0, le=1.0)
    contrarian: float = Field(0.00, ge=0.0, le=1.0)
    description: str = ""


class RoundState(BaseModel):
    run_id: int
    market_return: float
    market_stress: float
    sentiment: float
    turnout_drag: float
    whale_alignment: float
    exploit_signal: float
    public_benefit: float
    market_shock: bool


class SimulationObservation(BaseModel):
    run_id: int
    mechanism: str
    mechanism_label: str
    passed: bool
    quorum_reached: bool
    quorum_failure: bool
    turnout_weight: float
    turnout_wallet: float
    yes_weight_share: float
    yes_wallet_share: float
    unique_voters: int
    decisive_voter: str | None = None
    decisive_voter_archetype: str | None = None
    decisive_whale: bool = False
    top3_yes_concentration: float = 0.0
    whale_yes_share: float = 0.0
    false_positive: bool = False
    false_negative: bool = False
    whale_capture_flag: bool = False
    public_benefit: float = 0.0
    market_return: float = 0.0
    market_shock: bool = False
    exploit_signal: float = 0.0
    turnout_drag: float = 0.0
    sentiment: float = 0.0


class MechanismSummary(BaseModel):
    mechanism: str
    label: str
    pass_rate: float
    avg_turnout: float
    avg_yes_share: float
    quorum_failure_rate: float
    false_positive_rate: float
    false_negative_rate: float
    decisive_whale_rate: float
    whale_capture_rate: float
    avg_top3_yes_concentration: float
    shock_flip_delta: float
    legitimacy_gap: float
    resilience_score: float


class VulnerabilityItem(BaseModel):
    title: str
    severity: Severity
    mechanism: str | None = None
    evidence: str
    recommendation: str


class WindTunnelResult(BaseModel):
    proposal: ProposalConfig
    environment: EnvironmentConfig
    mechanisms: list[MechanismConfig]
    agents: list[AgentProfile]
    run_count: int
    seed: int
    market_context: dict[str, Any] = Field(default_factory=dict)
    summaries: list[MechanismSummary]
    vulnerabilities: list[VulnerabilityItem]
    records: list[SimulationObservation]

    def records_frame(self) -> pd.DataFrame:
        return pd.DataFrame(record.model_dump() for record in self.records)

    def summaries_frame(self) -> pd.DataFrame:
        frame = pd.DataFrame(summary.model_dump() for summary in self.summaries)
        if frame.empty:
            return frame
        return frame.sort_values("resilience_score", ascending=False).reset_index(drop=True)

    def vulnerabilities_frame(self) -> pd.DataFrame:
        return pd.DataFrame(vulnerability.model_dump() for vulnerability in self.vulnerabilities)

    def agent_frame(self) -> pd.DataFrame:
        return pd.DataFrame(agent.model_dump() for agent in self.agents)

    def to_report_dict(self) -> dict[str, Any]:
        return {
            "proposal": self.proposal.model_dump(),
            "environment": self.environment.model_dump(),
            "market_context": self.market_context,
            "run_count": self.run_count,
            "seed": self.seed,
            "summaries": [summary.model_dump() for summary in self.summaries],
            "vulnerabilities": [vulnerability.model_dump() for vulnerability in self.vulnerabilities],
        }


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def sigmoid(value: float) -> float:
    return 1.0 / (1.0 + math.exp(-value))


def proposal_presets() -> dict[str, ProposalConfig]:
    return {
        "Aggressive Liquidity Mining": ProposalConfig(
            name="Aggressive Liquidity Mining Renewal",
            category="treasury",
            summary="Boost emissions for rapid TVL growth before a major listing campaign.",
            treasury_request_pct=0.18,
            expected_upside=0.32,
            execution_risk=0.58,
            decentralization_impact=-0.20,
            urgency=0.72,
            proposer_reputation=0.05,
        ),
        "Treasury Diversification": ProposalConfig(
            name="Treasury Diversification Into Stables",
            category="risk",
            summary="Rotate a portion of treasury into stables to reduce drawdown risk.",
            treasury_request_pct=0.12,
            expected_upside=0.11,
            execution_risk=0.22,
            decentralization_impact=0.08,
            urgency=0.44,
            proposer_reputation=0.24,
        ),
        "Delegate Compensation": ProposalConfig(
            name="Delegate Compensation Program",
            category="governance",
            summary="Fund delegate participation to improve informed turnout and proposal review.",
            treasury_request_pct=0.06,
            expected_upside=0.12,
            execution_risk=0.18,
            decentralization_impact=0.24,
            urgency=0.48,
            proposer_reputation=0.32,
        ),
        "Emergency Buyback": ProposalConfig(
            name="Emergency Buyback Authorization",
            category="treasury",
            summary="Authorize rapid buybacks during deep price drawdowns.",
            treasury_request_pct=0.15,
            expected_upside=0.20,
            execution_risk=0.46,
            decentralization_impact=-0.08,
            urgency=0.83,
            proposer_reputation=0.12,
        ),
        "Open Grants Council": ProposalConfig(
            name="Open Grants Council Rotation",
            category="governance",
            summary="Rotate grants council seats quarterly to widen contributor representation.",
            treasury_request_pct=0.05,
            expected_upside=0.09,
            execution_risk=0.16,
            decentralization_impact=0.38,
            urgency=0.31,
            proposer_reputation=0.28,
        ),
    }


def environment_presets() -> dict[str, EnvironmentConfig]:
    return {
        "Calm Expansion": EnvironmentConfig(
            label="Calm Expansion",
            market_volatility=0.10,
            negative_shock_probability=0.08,
            whale_coordination=0.42,
            voter_apathy=0.22,
            social_sentiment=0.18,
            manipulation_pressure=0.28,
            noise_scale=0.12,
        ),
        "Stress Mix": EnvironmentConfig(),
        "Whale Raid": EnvironmentConfig(
            label="Whale Raid",
            market_volatility=0.24,
            negative_shock_probability=0.26,
            whale_coordination=0.86,
            voter_apathy=0.34,
            social_sentiment=-0.06,
            manipulation_pressure=0.78,
            noise_scale=0.18,
        ),
        "Apathy Spiral": EnvironmentConfig(
            label="Apathy Spiral",
            market_volatility=0.16,
            negative_shock_probability=0.14,
            whale_coordination=0.58,
            voter_apathy=0.58,
            social_sentiment=-0.12,
            manipulation_pressure=0.50,
            noise_scale=0.20,
        ),
        "Bear Shock": EnvironmentConfig(
            label="Bear Shock",
            market_volatility=0.30,
            negative_shock_probability=0.42,
            whale_coordination=0.68,
            voter_apathy=0.40,
            social_sentiment=-0.22,
            manipulation_pressure=0.62,
            noise_scale=0.22,
        ),
    }


def build_default_mechanisms(quorum: float = 0.28, approval_threshold: float = 0.55) -> list[MechanismConfig]:
    return [
        MechanismConfig(
            key="token_weighted",
            label="Token Weighted",
            quorum=quorum,
            approval_threshold=approval_threshold,
        ),
        MechanismConfig(
            key="quadratic",
            label="Quadratic Voting",
            quorum=quorum,
            approval_threshold=approval_threshold,
        ),
        MechanismConfig(
            key="shielded_hybrid",
            label="Shielded Hybrid",
            quorum=quorum,
            approval_threshold=approval_threshold,
            whale_cap_pct=0.12,
            participant_yes_threshold=0.52,
        ),
    ]


def build_default_agents(seed: int = 42) -> list[AgentProfile]:
    rng = np.random.default_rng(seed)
    templates = [
        {
            "agent_id": "whale_alpha",
            "archetype": "whale",
            "voting_power": 0.19,
            "reputation": 0.78,
            "risk_tolerance": 0.64,
            "growth_bias": 0.42,
            "decentralization_bias": -0.16,
            "treasury_guard_bias": -0.08,
            "turnout_discipline": 0.97,
            "herd_sensitivity": 0.12,
            "manipulation_tendency": 0.68,
            "market_beta": 0.50,
            "contrarian": 0.05,
            "description": "Capital-heavy actor capable of coordinating fast and decisively.",
        },
        {
            "agent_id": "whale_beta",
            "archetype": "whale",
            "voting_power": 0.14,
            "reputation": 0.70,
            "risk_tolerance": 0.56,
            "growth_bias": 0.30,
            "decentralization_bias": -0.10,
            "treasury_guard_bias": -0.04,
            "turnout_discipline": 0.95,
            "herd_sensitivity": 0.18,
            "manipulation_tendency": 0.72,
            "market_beta": 0.42,
            "contrarian": 0.06,
            "description": "Opportunistic whale with strong upside appetite.",
        },
        {
            "agent_id": "delegate_orbit",
            "archetype": "delegate",
            "voting_power": 0.08,
            "reputation": 0.92,
            "risk_tolerance": 0.34,
            "growth_bias": 0.18,
            "decentralization_bias": 0.30,
            "treasury_guard_bias": 0.24,
            "turnout_discipline": 0.92,
            "herd_sensitivity": 0.08,
            "manipulation_tendency": 0.05,
            "market_beta": 0.08,
            "contrarian": 0.10,
            "description": "Institutional delegate focused on governance quality.",
        },
        {
            "agent_id": "delegate_vector",
            "archetype": "delegate",
            "voting_power": 0.07,
            "reputation": 0.89,
            "risk_tolerance": 0.38,
            "growth_bias": 0.12,
            "decentralization_bias": 0.26,
            "treasury_guard_bias": 0.18,
            "turnout_discipline": 0.88,
            "herd_sensitivity": 0.10,
            "manipulation_tendency": 0.03,
            "market_beta": 0.10,
            "contrarian": 0.14,
            "description": "Process-oriented delegate with moderate reform bias.",
        },
        {
            "agent_id": "delegate_metro",
            "archetype": "delegate",
            "voting_power": 0.06,
            "reputation": 0.84,
            "risk_tolerance": 0.44,
            "growth_bias": 0.22,
            "decentralization_bias": 0.16,
            "treasury_guard_bias": 0.16,
            "turnout_discipline": 0.85,
            "herd_sensitivity": 0.12,
            "manipulation_tendency": 0.04,
            "market_beta": 0.12,
            "contrarian": 0.08,
            "description": "Delegate that tolerates growth bets if execution risk is controlled.",
        },
        {
            "agent_id": "treasury_guard_nova",
            "archetype": "treasury_guard",
            "voting_power": 0.05,
            "reputation": 0.82,
            "risk_tolerance": 0.20,
            "growth_bias": -0.02,
            "decentralization_bias": 0.10,
            "treasury_guard_bias": 0.46,
            "turnout_discipline": 0.78,
            "herd_sensitivity": 0.06,
            "manipulation_tendency": 0.02,
            "market_beta": -0.10,
            "contrarian": 0.18,
            "description": "Treasury protector that dislikes capital-intensive experiments.",
        },
        {
            "agent_id": "treasury_guard_quill",
            "archetype": "treasury_guard",
            "voting_power": 0.04,
            "reputation": 0.76,
            "risk_tolerance": 0.26,
            "growth_bias": 0.00,
            "decentralization_bias": 0.04,
            "treasury_guard_bias": 0.42,
            "turnout_discipline": 0.76,
            "herd_sensitivity": 0.07,
            "manipulation_tendency": 0.02,
            "market_beta": -0.08,
            "contrarian": 0.12,
            "description": "Conservative operator that prioritizes balance-sheet durability.",
        },
        {
            "agent_id": "activist_mesh",
            "archetype": "activist",
            "voting_power": 0.035,
            "reputation": 0.60,
            "risk_tolerance": 0.52,
            "growth_bias": 0.08,
            "decentralization_bias": 0.56,
            "treasury_guard_bias": 0.04,
            "turnout_discipline": 0.74,
            "herd_sensitivity": 0.04,
            "manipulation_tendency": 0.00,
            "market_beta": 0.06,
            "contrarian": 0.32,
            "description": "Activist holder that rewards openness and resists capture.",
        },
        {
            "agent_id": "activist_lattice",
            "archetype": "activist",
            "voting_power": 0.03,
            "reputation": 0.56,
            "risk_tolerance": 0.58,
            "growth_bias": 0.10,
            "decentralization_bias": 0.48,
            "treasury_guard_bias": 0.02,
            "turnout_discipline": 0.70,
            "herd_sensitivity": 0.05,
            "manipulation_tendency": 0.00,
            "market_beta": 0.08,
            "contrarian": 0.28,
            "description": "Community organizer with strong anti-centralization instincts.",
        },
        {
            "agent_id": "activist_signal",
            "archetype": "activist",
            "voting_power": 0.025,
            "reputation": 0.54,
            "risk_tolerance": 0.50,
            "growth_bias": 0.02,
            "decentralization_bias": 0.44,
            "treasury_guard_bias": 0.08,
            "turnout_discipline": 0.66,
            "herd_sensitivity": 0.02,
            "manipulation_tendency": 0.01,
            "market_beta": 0.04,
            "contrarian": 0.24,
            "description": "Grassroots voter motivated by fairness and process legitimacy.",
        },
        {
            "agent_id": "speculator_flux",
            "archetype": "speculator",
            "voting_power": 0.045,
            "reputation": 0.50,
            "risk_tolerance": 0.82,
            "growth_bias": 0.54,
            "decentralization_bias": -0.06,
            "treasury_guard_bias": -0.06,
            "turnout_discipline": 0.64,
            "herd_sensitivity": 0.26,
            "manipulation_tendency": 0.18,
            "market_beta": 0.78,
            "contrarian": 0.03,
            "description": "Momentum trader that follows upside narratives and price action.",
        },
        {
            "agent_id": "speculator_echo",
            "archetype": "speculator",
            "voting_power": 0.04,
            "reputation": 0.46,
            "risk_tolerance": 0.76,
            "growth_bias": 0.48,
            "decentralization_bias": -0.04,
            "treasury_guard_bias": -0.08,
            "turnout_discipline": 0.62,
            "herd_sensitivity": 0.22,
            "manipulation_tendency": 0.14,
            "market_beta": 0.70,
            "contrarian": 0.02,
            "description": "Yield hunter that likes high-volatility governance moves.",
        },
        {
            "agent_id": "speculator_ion",
            "archetype": "speculator",
            "voting_power": 0.035,
            "reputation": 0.48,
            "risk_tolerance": 0.72,
            "growth_bias": 0.42,
            "decentralization_bias": 0.00,
            "treasury_guard_bias": -0.02,
            "turnout_discipline": 0.60,
            "herd_sensitivity": 0.20,
            "manipulation_tendency": 0.10,
            "market_beta": 0.62,
            "contrarian": 0.04,
            "description": "Macro-sensitive holder that leans into positive sentiment regimes.",
        },
        {
            "agent_id": "retail_01",
            "archetype": "retail",
            "voting_power": 0.032,
            "reputation": 0.36,
            "risk_tolerance": 0.54,
            "growth_bias": 0.16,
            "decentralization_bias": 0.12,
            "treasury_guard_bias": 0.02,
            "turnout_discipline": 0.44,
            "herd_sensitivity": 0.30,
            "manipulation_tendency": 0.02,
            "market_beta": 0.26,
            "contrarian": 0.06,
            "description": "Small holder with intermittent attention and strong sentiment sensitivity.",
        },
        {
            "agent_id": "retail_02",
            "archetype": "retail",
            "voting_power": 0.029,
            "reputation": 0.34,
            "risk_tolerance": 0.50,
            "growth_bias": 0.12,
            "decentralization_bias": 0.08,
            "treasury_guard_bias": 0.04,
            "turnout_discipline": 0.40,
            "herd_sensitivity": 0.34,
            "manipulation_tendency": 0.01,
            "market_beta": 0.22,
            "contrarian": 0.08,
            "description": "Retail holder that follows social proof and volatility spikes.",
        },
        {
            "agent_id": "retail_03",
            "archetype": "retail",
            "voting_power": 0.026,
            "reputation": 0.34,
            "risk_tolerance": 0.46,
            "growth_bias": 0.06,
            "decentralization_bias": 0.14,
            "treasury_guard_bias": 0.04,
            "turnout_discipline": 0.38,
            "herd_sensitivity": 0.28,
            "manipulation_tendency": 0.01,
            "market_beta": 0.20,
            "contrarian": 0.08,
            "description": "Community lurker that shows up when a proposal feels emotional.",
        },
        {
            "agent_id": "retail_04",
            "archetype": "retail",
            "voting_power": 0.024,
            "reputation": 0.32,
            "risk_tolerance": 0.42,
            "growth_bias": 0.04,
            "decentralization_bias": 0.18,
            "treasury_guard_bias": 0.06,
            "turnout_discipline": 0.42,
            "herd_sensitivity": 0.22,
            "manipulation_tendency": 0.00,
            "market_beta": 0.18,
            "contrarian": 0.10,
            "description": "Mission-driven retail participant with irregular turnout.",
        },
        {
            "agent_id": "retail_05",
            "archetype": "retail",
            "voting_power": 0.021,
            "reputation": 0.30,
            "risk_tolerance": 0.48,
            "growth_bias": 0.10,
            "decentralization_bias": 0.10,
            "treasury_guard_bias": 0.02,
            "turnout_discipline": 0.36,
            "herd_sensitivity": 0.32,
            "manipulation_tendency": 0.01,
            "market_beta": 0.24,
            "contrarian": 0.06,
            "description": "Part-time voter that tends to mirror public momentum.",
        },
        {
            "agent_id": "retail_06",
            "archetype": "retail",
            "voting_power": 0.018,
            "reputation": 0.28,
            "risk_tolerance": 0.52,
            "growth_bias": 0.08,
            "decentralization_bias": 0.08,
            "treasury_guard_bias": 0.04,
            "turnout_discipline": 0.34,
            "herd_sensitivity": 0.36,
            "manipulation_tendency": 0.01,
            "market_beta": 0.18,
            "contrarian": 0.04,
            "description": "Retail swing voter influenced by social feeds and urgency framing.",
        },
    ]

    agents: list[AgentProfile] = []
    total_power = sum(template["voting_power"] for template in templates)
    for template in templates:
        jitter = rng.normal(0.0, 0.02)
        agent_data = template | {
            "voting_power": max(0.005, template["voting_power"] / total_power),
            "risk_tolerance": clamp(template["risk_tolerance"] + jitter, 0.0, 1.0),
            "growth_bias": clamp(template["growth_bias"] + jitter * 0.6, -1.0, 1.0),
            "decentralization_bias": clamp(template["decentralization_bias"] - jitter * 0.3, -1.0, 1.0),
            "turnout_discipline": clamp(template["turnout_discipline"] + jitter * 0.4, 0.0, 1.0),
            "herd_sensitivity": clamp(template["herd_sensitivity"] + abs(jitter) * 0.2, 0.0, 1.0),
        }
        agents.append(AgentProfile(**agent_data))
    return agents


def _generate_round_state(
    run_id: int,
    proposal: ProposalConfig,
    environment: EnvironmentConfig,
    rng: np.random.Generator,
) -> RoundState:
    market_return = float(rng.normal(environment.social_sentiment * 0.04, environment.market_volatility))
    market_shock = bool(rng.random() < environment.negative_shock_probability)
    if market_shock:
        market_return -= abs(float(rng.normal(0.16, environment.market_volatility * 0.35)))

    market_stress = clamp(abs(min(0.0, market_return)) * 1.8 + (0.22 if market_shock else 0.0), 0.0, 1.0)
    sentiment = clamp(
        environment.social_sentiment + market_return * 0.7 - proposal.execution_risk * 0.08 + rng.normal(0.0, 0.10),
        -1.0,
        1.0,
    )
    turnout_drag = clamp(
        environment.voter_apathy + market_stress * 0.35 - proposal.urgency * 0.18 + rng.normal(0.0, 0.06),
        0.0,
        1.0,
    )
    whale_alignment = clamp(environment.whale_coordination + rng.normal(0.0, 0.10), 0.0, 1.0)
    exploit_signal = clamp(
        environment.manipulation_pressure * 0.42
        + proposal.treasury_request_pct * 0.38
        + max(0.0, -proposal.decentralization_impact) * 0.28
        + proposal.execution_risk * 0.22
        - proposal.proposer_reputation * 0.12,
        0.0,
        1.0,
    )
    public_benefit = (
        proposal.expected_upside * 0.42
        + proposal.decentralization_impact * 0.26
        - proposal.execution_risk * 0.24
        - proposal.treasury_request_pct * 0.16
        + sentiment * 0.10
        - market_stress * 0.12
        - exploit_signal * 0.08
    )
    return RoundState(
        run_id=run_id,
        market_return=market_return,
        market_stress=market_stress,
        sentiment=sentiment,
        turnout_drag=turnout_drag,
        whale_alignment=whale_alignment,
        exploit_signal=exploit_signal,
        public_benefit=public_benefit,
        market_shock=market_shock,
    )


def _agent_decision(
    agent: AgentProfile,
    proposal: ProposalConfig,
    state: RoundState,
    environment: EnvironmentConfig,
    rng: np.random.Generator,
) -> dict[str, Any]:
    governance_score = (
        proposal.expected_upside * (0.85 + agent.growth_bias)
        + proposal.decentralization_impact * (0.90 + agent.decentralization_bias)
        - proposal.treasury_request_pct * (0.95 + agent.treasury_guard_bias)
        - proposal.execution_risk * (1.15 - agent.risk_tolerance)
        + proposal.urgency * 0.14
        + proposal.proposer_reputation * (0.18 + agent.reputation * 0.15)
        + state.market_return * (0.22 + agent.market_beta)
        + state.sentiment * 0.16
        - state.market_stress * (1.0 - agent.risk_tolerance) * 0.22
    )
    manipulation_bonus = agent.manipulation_tendency * state.exploit_signal * (0.42 + state.whale_alignment * 0.30)
    social_noise = rng.normal(0.0, environment.noise_scale * 0.35)
    score = (
        governance_score
        + manipulation_bonus
        + agent.herd_sensitivity * state.sentiment * 0.18
        - agent.contrarian * state.sentiment * 0.10
        + social_noise
    )

    turnout_signal = (
        agent.turnout_discipline * 1.35
        - state.turnout_drag * 1.15
        + abs(score) * 0.55
        + proposal.urgency * 0.28
        + (0.18 if agent.archetype in {"whale", "delegate", "treasury_guard"} else 0.0)
        + (0.08 if state.market_shock and agent.archetype in {"whale", "speculator"} else 0.0)
    )
    turnout_probability = sigmoid(turnout_signal * 2.0 - 1.1)
    participates = bool(rng.random() < turnout_probability)

    if agent.manipulation_tendency > 0.55 and state.exploit_signal > 0.58 and state.whale_alignment > 0.62:
        participates = True
        score += 0.18

    stance = "yes" if score >= 0 else "no"
    conviction = clamp(0.55 + abs(score) * 1.25, 0.55, 1.60)
    return {
        "agent": agent,
        "participates": participates,
        "stance": stance,
        "score": score,
        "conviction": conviction,
    }


def _effective_weight(agent: AgentProfile, decision: dict[str, Any], mechanism: MechanismConfig) -> float:
    base_weight = agent.voting_power * decision["conviction"]
    if mechanism.key == "quadratic":
        return math.sqrt(base_weight)
    if mechanism.key == "shielded_hybrid":
        capped_weight = min(base_weight, mechanism.whale_cap_pct or base_weight)
        return capped_weight
    return base_weight


def _find_decisive_voter(
    participating: list[dict[str, Any]],
    mechanism: MechanismConfig,
    total_effective_weight: float,
    yes_effective_weight: float,
    turnout_weight: float,
) -> tuple[str | None, str | None]:
    if not participating:
        return None, None
    if turnout_weight < mechanism.quorum:
        return None, None
    if total_effective_weight <= 0 or yes_effective_weight / total_effective_weight < mechanism.approval_threshold:
        return None, None

    yes_voters = [item for item in participating if item["stance"] == "yes"]
    yes_voters.sort(key=lambda item: item["effective_weight"], reverse=True)
    participant_count = len(participating)
    yes_count = sum(1 for item in participating if item["stance"] == "yes")

    for item in yes_voters:
        remaining_yes_effective = yes_effective_weight - item["effective_weight"]
        remaining_total_effective = total_effective_weight - item["effective_weight"]
        if remaining_total_effective <= 0:
            return item["agent"].agent_id, item["agent"].archetype

        remaining_wallet_yes = yes_count - 1
        remaining_wallet_share = remaining_wallet_yes / max(1, participant_count - 1)
        still_passes = (
            remaining_yes_effective / remaining_total_effective >= mechanism.approval_threshold
            and turnout_weight >= mechanism.quorum
        )
        if mechanism.participant_yes_threshold is not None:
            still_passes = still_passes and remaining_wallet_share >= mechanism.participant_yes_threshold
        if not still_passes:
            return item["agent"].agent_id, item["agent"].archetype
    return None, None


def _evaluate_mechanism(
    mechanism: MechanismConfig,
    decisions: list[dict[str, Any]],
    state: RoundState,
    total_supply: float,
) -> SimulationObservation:
    participating = [decision for decision in decisions if decision["participates"]]
    turnout_weight = sum(decision["agent"].voting_power for decision in participating) / total_supply
    turnout_wallet = len(participating) / len(decisions)
    unique_voters = len(participating)

    weighted_votes: list[dict[str, Any]] = []
    for decision in participating:
        effective_weight = _effective_weight(decision["agent"], decision, mechanism)
        weighted_votes.append(decision | {"effective_weight": effective_weight})

    total_effective_weight = sum(item["effective_weight"] for item in weighted_votes)
    yes_votes = [item for item in weighted_votes if item["stance"] == "yes"]
    yes_effective_weight = sum(item["effective_weight"] for item in yes_votes)
    yes_weight_share = yes_effective_weight / total_effective_weight if total_effective_weight else 0.0
    yes_wallet_share = len(yes_votes) / unique_voters if unique_voters else 0.0

    quorum_reached = turnout_weight >= mechanism.quorum
    passed = quorum_reached and total_effective_weight > 0 and yes_weight_share >= mechanism.approval_threshold
    if mechanism.participant_yes_threshold is not None:
        passed = passed and yes_wallet_share >= mechanism.participant_yes_threshold

    top3_yes_concentration = 0.0
    whale_yes_share = 0.0
    if yes_effective_weight > 0:
        sorted_yes = sorted(yes_votes, key=lambda item: item["effective_weight"], reverse=True)
        top3_yes_concentration = sum(item["effective_weight"] for item in sorted_yes[:3]) / yes_effective_weight
        whale_yes_share = (
            sum(item["effective_weight"] for item in yes_votes if item["agent"].archetype == "whale") / yes_effective_weight
        )

    decisive_voter, decisive_voter_archetype = _find_decisive_voter(
        weighted_votes,
        mechanism,
        total_effective_weight,
        yes_effective_weight,
        turnout_weight,
    )
    decisive_whale = decisive_voter_archetype == "whale"

    false_positive = passed and state.public_benefit < 0.0
    false_negative = (not passed) and state.public_benefit >= 0.0
    whale_capture_flag = (
        passed
        and yes_wallet_share < 0.56
        and (whale_yes_share > 0.52 or top3_yes_concentration > 0.78 or decisive_whale)
        and state.exploit_signal > 0.46
    )

    return SimulationObservation(
        run_id=state.run_id,
        mechanism=mechanism.key,
        mechanism_label=mechanism.label,
        passed=passed,
        quorum_reached=quorum_reached,
        quorum_failure=not quorum_reached,
        turnout_weight=turnout_weight,
        turnout_wallet=turnout_wallet,
        yes_weight_share=yes_weight_share,
        yes_wallet_share=yes_wallet_share,
        unique_voters=unique_voters,
        decisive_voter=decisive_voter,
        decisive_voter_archetype=decisive_voter_archetype,
        decisive_whale=decisive_whale,
        top3_yes_concentration=top3_yes_concentration,
        whale_yes_share=whale_yes_share,
        false_positive=false_positive,
        false_negative=false_negative,
        whale_capture_flag=whale_capture_flag,
        public_benefit=state.public_benefit,
        market_return=state.market_return,
        market_shock=state.market_shock,
        exploit_signal=state.exploit_signal,
        turnout_drag=state.turnout_drag,
        sentiment=state.sentiment,
    )


def _summarize_records(records_frame: pd.DataFrame) -> list[MechanismSummary]:
    summaries: list[MechanismSummary] = []
    for mechanism, group in records_frame.groupby("mechanism"):
        label = str(group["mechanism_label"].iloc[0])
        shock_pass_rate = float(group.loc[group["market_shock"], "passed"].mean()) if group["market_shock"].any() else 0.0
        calm_pass_rate = (
            float(group.loc[~group["market_shock"], "passed"].mean()) if (~group["market_shock"]).any() else 0.0
        )
        legitimacy_gap = float((group["yes_weight_share"] - group["yes_wallet_share"]).clip(lower=0).mean())
        resilience_score = 100.0 * (
            1.0
            - (
                float(group["false_positive"].mean()) * 0.28
                + float(group["false_negative"].mean()) * 0.24
                + float(group["decisive_whale"].mean()) * 0.18
                + float(group["whale_capture_flag"].mean()) * 0.16
                + float(group["quorum_failure"].mean()) * 0.08
                + abs(shock_pass_rate - calm_pass_rate) * 0.06
            )
        )
        summaries.append(
            MechanismSummary(
                mechanism=mechanism,
                label=label,
                pass_rate=float(group["passed"].mean()),
                avg_turnout=float(group["turnout_weight"].mean()),
                avg_yes_share=float(group["yes_weight_share"].mean()),
                quorum_failure_rate=float(group["quorum_failure"].mean()),
                false_positive_rate=float(group["false_positive"].mean()),
                false_negative_rate=float(group["false_negative"].mean()),
                decisive_whale_rate=float(group["decisive_whale"].mean()),
                whale_capture_rate=float(group["whale_capture_flag"].mean()),
                avg_top3_yes_concentration=float(group["top3_yes_concentration"].mean()),
                shock_flip_delta=abs(shock_pass_rate - calm_pass_rate),
                legitimacy_gap=legitimacy_gap,
                resilience_score=resilience_score,
            )
        )
    return sorted(summaries, key=lambda summary: summary.resilience_score, reverse=True)


def _severity_from_score(score: float) -> Severity:
    if score >= 0.75:
        return "critical"
    if score >= 0.55:
        return "high"
    if score >= 0.35:
        return "medium"
    return "low"


def _build_vulnerabilities(result_frame: pd.DataFrame, summaries: list[MechanismSummary]) -> list[VulnerabilityItem]:
    vulnerabilities: list[VulnerabilityItem] = []
    ordered_summaries = sorted(summaries, key=lambda item: item.whale_capture_rate, reverse=True)
    capture_candidate = ordered_summaries[0]
    capture_score = max(capture_candidate.whale_capture_rate, capture_candidate.decisive_whale_rate)
    if capture_score > 0.05:
        vulnerabilities.append(
            VulnerabilityItem(
                title="Whale Capture Surface",
                severity=_severity_from_score(capture_score * 2.4 + capture_candidate.avg_top3_yes_concentration * 0.28),
                mechanism=capture_candidate.label,
                evidence=(
                    f"{capture_candidate.label} shows whale-driven passage in {capture_candidate.whale_capture_rate:.1%} of runs, "
                    f"with decisive whale votes in {capture_candidate.decisive_whale_rate:.1%}."
                ),
                recommendation="Cap per-wallet influence, add a participant approval floor, or review proposals under a quadratic or hybrid path before execution.",
            )
        )

    toxic_pass_candidate = max(summaries, key=lambda item: item.false_positive_rate)
    if toxic_pass_candidate.false_positive_rate > 0.04:
        vulnerabilities.append(
            VulnerabilityItem(
                title="Toxic Proposal Passage Risk",
                severity=_severity_from_score(toxic_pass_candidate.false_positive_rate * 5.0),
                mechanism=toxic_pass_candidate.label,
                evidence=(
                    f"{toxic_pass_candidate.label} passes proposals with negative public benefit in "
                    f"{toxic_pass_candidate.false_positive_rate:.1%} of runs."
                ),
                recommendation="Route treasury-heavy or centralizing proposals through a guarded mechanism or require a second-stage review before execution.",
            )
        )

    apathy_candidate = max(summaries, key=lambda item: item.false_negative_rate + item.quorum_failure_rate)
    apathy_score = apathy_candidate.false_negative_rate + apathy_candidate.quorum_failure_rate * 0.7
    if apathy_score > 0.12:
        vulnerabilities.append(
            VulnerabilityItem(
                title="Apathy And Quorum Fragility",
                severity=_severity_from_score(apathy_score),
                mechanism=apathy_candidate.label,
                evidence=(
                    f"{apathy_candidate.label} misses beneficial proposals {apathy_candidate.false_negative_rate:.1%} of the time "
                    f"and fails quorum in {apathy_candidate.quorum_failure_rate:.1%} of runs."
                ),
                recommendation="Lower quorum for low-risk proposals, fund delegate participation, or add better pre-vote signaling to pull retail turnout forward.",
            )
        )

    shock_candidate = max(summaries, key=lambda item: item.shock_flip_delta)
    if shock_candidate.shock_flip_delta > 0.12:
        vulnerabilities.append(
            VulnerabilityItem(
                title="Market Shock Sensitivity",
                severity=_severity_from_score(shock_candidate.shock_flip_delta * 2.5),
                mechanism=shock_candidate.label,
                evidence=(
                    f"Pass probability moves by {shock_candidate.shock_flip_delta:.1%} between calm and shock regimes under {shock_candidate.label}."
                ),
                recommendation="Delay execution during large volatility spikes or require a second confirmation window for treasury-intensive proposals.",
            )
        )

    divergence = max(summary.pass_rate for summary in summaries) - min(summary.pass_rate for summary in summaries)
    if divergence > 0.06:
        best = max(summaries, key=lambda item: item.resilience_score)
        worst = min(summaries, key=lambda item: item.resilience_score)
        vulnerabilities.append(
            VulnerabilityItem(
                title="Mechanism Design Mismatch",
                severity=_severity_from_score(divergence * 5.0),
                mechanism=None,
                evidence=(
                    f"Pass rates diverge by {divergence:.1%} across mechanisms. {best.label} is materially more resilient than {worst.label} for this proposal profile."
                ),
                recommendation="Use the tunnel as a pre-flight check and route risky proposals to the mechanism that minimizes false positives and capture risk.",
            )
        )

    if not vulnerabilities:
        vulnerabilities.append(
            VulnerabilityItem(
                title="No Acute Governance Failure Mode",
                severity="low",
                mechanism=None,
                evidence="Across the simulated mechanisms, no single risk signal crossed the alert threshold for this proposal and environment mix.",
                recommendation="Keep monitoring turnout and whale concentration, but the current configuration appears reasonably stable for an MVP demo.",
            )
        )

    return vulnerabilities


def run_wind_tunnel(
    proposal: ProposalConfig,
    environment: EnvironmentConfig,
    run_count: int = 500,
    seed: int = 42,
    mechanisms: list[MechanismConfig] | None = None,
    agents: list[AgentProfile] | None = None,
    market_context: dict[str, Any] | None = None,
) -> WindTunnelResult:
    rng = np.random.default_rng(seed)
    active_mechanisms = mechanisms or build_default_mechanisms()
    active_agents = agents or build_default_agents(seed)
    total_supply = sum(agent.voting_power for agent in active_agents)

    records: list[SimulationObservation] = []
    for run_id in range(run_count):
        state = _generate_round_state(run_id, proposal, environment, rng)
        decisions = [_agent_decision(agent, proposal, state, environment, rng) for agent in active_agents]
        for mechanism in active_mechanisms:
            records.append(_evaluate_mechanism(mechanism, decisions, state, total_supply))

    frame = pd.DataFrame(record.model_dump() for record in records)
    summaries = _summarize_records(frame)
    vulnerabilities = _build_vulnerabilities(frame, summaries)
    return WindTunnelResult(
        proposal=proposal,
        environment=environment,
        mechanisms=active_mechanisms,
        agents=active_agents,
        run_count=run_count,
        seed=seed,
        market_context=market_context or {},
        summaries=summaries,
        vulnerabilities=vulnerabilities,
        records=records,
    )
