from __future__ import annotations

import json
from typing import Any

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

from dao_wind_tunnel_core import (
    EnvironmentConfig,
    ProposalConfig,
    build_default_mechanisms,
    environment_presets,
    proposal_presets,
    run_wind_tunnel,
)
from htx_market import HTXMarketCalibrator


app = FastAPI(title="Cybernetic DAO Wind Tunnel")


PROPOSAL_PRESET_LABELS_ZH = {
    "Aggressive Liquidity Mining": "激进流动性挖矿",
    "Treasury Diversification": "金库分散配置",
    "Delegate Compensation": "委托人激励计划",
    "Emergency Buyback": "紧急回购授权",
    "Open Grants Council": "开放式 Grants 委员会轮换",
}

PROPOSAL_LOCALIZATION_ZH = {
    "Aggressive Liquidity Mining": {
        "name": "激进流动性挖矿续期",
        "summary": "在重大上币营销前，提高排放速度来快速拉升 TVL。",
    },
    "Treasury Diversification": {
        "name": "DAO 金库配置部分转向稳定币",
        "summary": "将部分金库转入稳定币，降低大盘回撤时的系统性风险。",
    },
    "Delegate Compensation": {
        "name": "委托人激励计划",
        "summary": "给活跃委托人提供预算，提高高质量投票参与和提案审查。",
    },
    "Emergency Buyback": {
        "name": "紧急回购授权",
        "summary": "允许在极端下跌时快速回购代币以稳住市场预期。",
    },
    "Open Grants Council": {
        "name": "开放式 Grants 委员会轮换",
        "summary": "按季度轮换 Grants 委员会席位，扩大贡献者代表性。",
    },
}

ENV_PRESET_LABELS_ZH = {
    "Calm Expansion": "平稳扩张",
    "Stress Mix": "混合压力",
    "Whale Raid": "大户突袭",
    "Apathy Spiral": "参与冷却",
    "Bear Shock": "熊市冲击",
}

MECHANISM_LABELS_ZH = {
    "Token Weighted": "代币加权",
    "Quadratic Voting": "二次投票",
    "Shielded Hybrid": "混合防护机制",
}

ARCHETYPE_LABELS_ZH = {
    "whale": "大户",
    "delegate": "委托人",
    "treasury_guard": "金库守门人",
    "activist": "治理激进派",
    "speculator": "投机者",
    "retail": "散户",
}

SEVERITY_LABELS_ZH = {
    "critical": "严重",
    "high": "高",
    "medium": "中",
    "low": "低",
}

VULNERABILITY_TITLES_ZH = {
    "Whale Capture Surface": "大户控票风险",
    "Toxic Proposal Passage Risk": "坏提案误通过风险",
    "Apathy And Quorum Fragility": "冷漠与流会风险",
    "Market Shock Sensitivity": "市场冲击敏感",
    "Mechanism Design Mismatch": "机制设计不匹配",
    "No Acute Governance Failure Mode": "未发现明显致命风险",
}


class SimulationRequest(BaseModel):
    proposal_preset: str = "Aggressive Liquidity Mining"
    environment_preset: str = "Stress Mix"
    run_count: int = Field(500, ge=100, le=1500)
    seed: int = Field(42, ge=1, le=999_999)
    quorum: float = Field(0.28, ge=0.05, le=0.60)
    approval_threshold: float = Field(0.55, ge=0.50, le=0.80)
    use_htx_calibration: bool = True
    language: str = "zh"

    treasury_request_pct: float | None = None
    expected_upside: float | None = None
    execution_risk: float | None = None
    decentralization_impact: float | None = None
    urgency: float | None = None
    proposer_reputation: float | None = None
    market_volatility: float | None = None
    negative_shock_probability: float | None = None
    whale_coordination: float | None = None
    voter_apathy: float | None = None
    social_sentiment: float | None = None
    manipulation_pressure: float | None = None
    noise_scale: float | None = None


def is_chinese(language: str) -> bool:
    return language.lower().startswith("zh") or language == "中文"


def localized_proposal_payload() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for key, preset in proposal_presets().items():
        localization = PROPOSAL_LOCALIZATION_ZH.get(key, {})
        items.append(
            {
                "key": key,
                "label_zh": PROPOSAL_PRESET_LABELS_ZH.get(key, key),
                "label_en": key,
                "name_zh": localization.get("name", preset.name),
                "name_en": preset.name,
                "summary_zh": localization.get("summary", preset.summary),
                "summary_en": preset.summary,
                "config": preset.model_dump(),
            }
        )
    return items


def localized_environment_payload() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for key, preset in environment_presets().items():
        items.append(
            {
                "key": key,
                "label_zh": ENV_PRESET_LABELS_ZH.get(key, key),
                "label_en": key,
                "config": preset.model_dump(),
            }
        )
    return items


def translate_mechanism(label: str, language: str) -> str:
    return MECHANISM_LABELS_ZH.get(label, label) if is_chinese(language) else label


def translate_environment_label(label: str, language: str) -> str:
    if not is_chinese(language):
        return label
    suffix = " + HTX Calibration"
    if label.endswith(suffix):
        base = label[: -len(suffix)]
        return f"{ENV_PRESET_LABELS_ZH.get(base, base)} + HTX 校准"
    return ENV_PRESET_LABELS_ZH.get(label, label)


def translate_archetype(archetype: str, language: str) -> str:
    if is_chinese(language):
        return ARCHETYPE_LABELS_ZH.get(archetype, archetype)
    return archetype.replace("_", " ").title()


def apply_request_to_proposal(request: SimulationRequest) -> ProposalConfig:
    preset = proposal_presets()[request.proposal_preset]
    updates = {}
    for field in (
        "treasury_request_pct",
        "expected_upside",
        "execution_risk",
        "decentralization_impact",
        "urgency",
        "proposer_reputation",
    ):
        value = getattr(request, field)
        if value is not None:
            updates[field] = value
    return preset.model_copy(update=updates)


def apply_request_to_environment(request: SimulationRequest) -> EnvironmentConfig:
    preset = environment_presets()[request.environment_preset]
    updates = {}
    for field in (
        "market_volatility",
        "negative_shock_probability",
        "whale_coordination",
        "voter_apathy",
        "social_sentiment",
        "manipulation_pressure",
        "noise_scale",
    ):
        value = getattr(request, field)
        if value is not None:
            updates[field] = value
    return preset.model_copy(update=updates)


def localize_proposal_text(proposal: ProposalConfig, preset_key: str, language: str) -> ProposalConfig:
    if not is_chinese(language):
        return proposal
    localization = PROPOSAL_LOCALIZATION_ZH.get(preset_key, {})
    return proposal.model_copy(
        update={
            "name": localization.get("name", proposal.name),
            "summary": localization.get("summary", proposal.summary),
        }
    )


def executive_summary(summary_rows: list[dict[str, Any]], vulnerability_rows: list[dict[str, Any]], language: str) -> str:
    best = summary_rows[0]
    riskiest = max(summary_rows, key=lambda item: item["whale_capture_rate"])
    if is_chinese(language):
        risk_title = vulnerability_rows[0]["title_display"] if vulnerability_rows else "未发现明显高风险"
        return (
            f"建议优先采用 {best['label_display']}，韧性分 {best['resilience_score']:.1f}。"
            f" 当前最需要盯住的是“{risk_title}”，其中 {riskiest['label_display']} 的大户带票率为 "
            f"{riskiest['whale_capture_rate']:.1%}。这页建议先看坏提案误通过，再看控票，再看行情冲击敏感度。"
        )
    return (
        f"Prefer {best['label_display']} with a resilience score of {best['resilience_score']:.1f}. "
        f"The main watch item is {vulnerability_rows[0]['title_display'] if vulnerability_rows else 'no acute vulnerability'}, "
        f"while {riskiest['label_display']} has the highest whale-capture rate at {riskiest['whale_capture_rate']:.1%}."
    )


def localize_vulnerability(row: dict[str, Any], summary_lookup: dict[str, dict[str, Any]], language: str) -> dict[str, Any]:
    title = row["title"]
    mechanism = row.get("mechanism")
    title_display = VULNERABILITY_TITLES_ZH.get(title, title) if is_chinese(language) else title
    severity_display = SEVERITY_LABELS_ZH.get(row["severity"], row["severity"]) if is_chinese(language) else row["severity"].title()

    if not is_chinese(language):
        return row | {"title_display": title_display, "severity_display": severity_display}

    summary_row = summary_lookup.get(mechanism, {}) if mechanism else {}
    mechanism_label = translate_mechanism(mechanism, language) if mechanism else "当前机制"

    if title == "Whale Capture Surface" and summary_row:
        evidence = (
            f"{mechanism_label} 下，大户主导通过的比例是 {summary_row['whale_capture_rate']:.1%}，"
            f"关键一票由大户决定的比例是 {summary_row['decisive_whale_rate']:.1%}。"
        )
        recommendation = "建议给单钱包投票权加上限，或者增加“参与人数通过门槛”，避免少数大户直接拍板。"
    elif title == "Toxic Proposal Passage Risk" and summary_row:
        evidence = f"{mechanism_label} 让“整体公共收益为负”的提案误通过的比例是 {summary_row['false_positive_rate']:.1%}。"
        recommendation = "对高耗资、低去中心化收益的提案，优先走更保守的投票路径，或者增加二次复核。"
    elif title == "Apathy And Quorum Fragility" and summary_row:
        evidence = (
            f"{mechanism_label} 的好提案误杀率是 {summary_row['false_negative_rate']:.1%}，"
            f"流会率是 {summary_row['quorum_failure_rate']:.1%}。"
        )
        recommendation = "可以考虑降低低风险提案门槛，或引入委托人激励，把散户参与率先拉起来。"
    elif title == "Market Shock Sensitivity" and summary_row:
        evidence = f"{mechanism_label} 在平稳与冲击行情之间的通过率摆动达到 {summary_row['shock_flip_delta']:.1%}。"
        recommendation = "对金库敏感提案增加冷静期，或者在大波动时要求二次确认。"
    elif title == "Mechanism Design Mismatch":
        best = max(summary_lookup.values(), key=lambda item: item["resilience_score"])
        worst = min(summary_lookup.values(), key=lambda item: item["resilience_score"])
        divergence = max(item["pass_rate"] for item in summary_lookup.values()) - min(
            item["pass_rate"] for item in summary_lookup.values()
        )
        evidence = (
            f"同一提案在不同投票机制下，通过率相差 {divergence:.1%}。"
            f"{best['label_display']} 明显比 {worst['label_display']} 更稳。"
        )
        recommendation = "不要默认所有提案都走同一治理流程，先用风洞判断应该配哪种治理机制。"
    else:
        evidence = "这次模拟里没有发现会立刻把提案带翻的尖锐治理故障。"
        recommendation = "继续盯参与率和大户集中度即可，当前配置在演示场景下相对稳定。"

    return row | {
        "title_display": title_display,
        "severity_display": severity_display,
        "evidence_display": evidence,
        "recommendation_display": recommendation,
    }


def serialize_result(request: SimulationRequest) -> dict[str, Any]:
    proposal = apply_request_to_proposal(request)
    environment = apply_request_to_environment(request)
    calibrator = HTXMarketCalibrator()
    market_snapshot = calibrator.fetch_snapshot() if request.use_htx_calibration else None
    effective_environment = (
        calibrator.apply_to_environment(environment, market_snapshot) if market_snapshot is not None else environment
    )
    result = run_wind_tunnel(
        proposal=proposal,
        environment=effective_environment,
        run_count=request.run_count,
        seed=request.seed,
        mechanisms=build_default_mechanisms(
            quorum=request.quorum,
            approval_threshold=request.approval_threshold,
        ),
        market_context=market_snapshot.model_dump() if market_snapshot is not None else {},
    )

    display_proposal = localize_proposal_text(result.proposal, request.proposal_preset, request.language)
    summary_rows = result.summaries_frame().to_dict(orient="records")
    summary_rows = [
        row | {"label_display": translate_mechanism(row["label"], request.language)}
        for row in summary_rows
    ]
    summary_lookup = {row["label"]: row for row in summary_rows}

    vulnerabilities = [item.model_dump() for item in result.vulnerabilities]
    vulnerability_rows = [localize_vulnerability(item, summary_lookup, request.language) for item in vulnerabilities]

    records_rows = result.records_frame().to_dict(orient="records")
    records_rows = [
        row
        | {
            "mechanism_label_display": translate_mechanism(row["mechanism_label"], request.language),
            "passed_display": "通过" if (is_chinese(request.language) and row["passed"]) else (
                "未通过" if is_chinese(request.language) else ("Passed" if row["passed"] else "Rejected")
            ),
            "market_shock_display": "出现冲击"
            if (is_chinese(request.language) and row["market_shock"])
            else ("无冲击" if is_chinese(request.language) else ("Shock" if row["market_shock"] else "No shock")),
        }
        for row in records_rows
    ]

    agent_rows = result.agent_frame().to_dict(orient="records")
    agent_rows = [
        row | {"archetype_display": translate_archetype(row["archetype"], request.language)}
        for row in agent_rows
    ]

    return {
        "language": request.language,
        "proposal": display_proposal.model_dump(),
        "environment": {
            **effective_environment.model_dump(),
            "label_display": translate_environment_label(effective_environment.label, request.language),
        },
        "market_snapshot": (
            {
                "source": "占位样本" if is_chinese(request.language) and market_snapshot and market_snapshot.source != "live" else (
                    "实时接口" if is_chinese(request.language) and market_snapshot and market_snapshot.source == "live" else (
                        market_snapshot.source if market_snapshot else None
                    )
                ),
                "note": (
                    "已根据 HTX 市场占位数据调整波动率与冲击概率。"
                    if is_chinese(request.language) and market_snapshot
                    else (market_snapshot.note if market_snapshot else None)
                ),
                "price_change_24h": market_snapshot.price_change_24h if market_snapshot else None,
                "volume_change_24h": market_snapshot.volume_change_24h if market_snapshot else None,
                "volatility_multiplier": market_snapshot.volatility_multiplier if market_snapshot else None,
            }
            if market_snapshot
            else None
        ),
        "summary_rows": summary_rows,
        "vulnerability_rows": vulnerability_rows,
        "records_rows": records_rows,
        "agent_rows": agent_rows,
        "metrics": {
            "best_mechanism": summary_rows[0]["label_display"],
            "best_mechanism_score": summary_rows[0]["resilience_score"],
            "highest_pass_rate": max(row["pass_rate"] for row in summary_rows),
            "highest_pass_label": max(summary_rows, key=lambda item: item["pass_rate"])["label_display"],
            "capture_risk_peak": max(row["whale_capture_rate"] for row in summary_rows),
            "capture_risk_label": max(summary_rows, key=lambda item: item["whale_capture_rate"])["label_display"],
            "shock_delta": max(row["shock_flip_delta"] for row in summary_rows),
        },
        "executive_summary": executive_summary(summary_rows, vulnerability_rows, request.language),
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/bootstrap")
def bootstrap() -> JSONResponse:
    request = SimulationRequest()
    payload = {
        "default_request": request.model_dump(),
        "proposal_presets": localized_proposal_payload(),
        "environment_presets": localized_environment_payload(),
        "initial_result": serialize_result(request),
    }
    return JSONResponse(payload)


@app.post("/api/simulate")
def simulate(request: SimulationRequest) -> JSONResponse:
    return JSONResponse(serialize_result(request))


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    html = """
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Cybernetic DAO Wind Tunnel</title>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    :root {
      --bg-1: #07121b;
      --bg-2: #102433;
      --panel: rgba(10, 20, 31, 0.72);
      --line: rgba(125, 220, 209, 0.16);
      --cyan: #79e9dc;
      --amber: #ffb55d;
      --oxide: #ff7b4f;
      --ink: #f0f7fb;
      --muted: #97afbe;
      --card: rgba(255, 255, 255, 0.035);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(121, 233, 220, 0.12), transparent 28%),
        radial-gradient(circle at bottom right, rgba(255, 123, 79, 0.11), transparent 25%),
        linear-gradient(135deg, var(--bg-1) 0%, var(--bg-2) 48%, #071019 100%);
      min-height: 100vh;
    }
    .shell {
      display: grid;
      grid-template-columns: 360px minmax(0, 1fr);
      min-height: 100vh;
    }
    .sidebar {
      border-right: 1px solid var(--line);
      background: linear-gradient(180deg, rgba(7, 16, 25, 0.96), rgba(10, 22, 34, 0.96));
      padding: 18px 18px 22px;
      position: sticky;
      top: 0;
      height: 100vh;
      overflow: auto;
    }
    .content {
      padding: 24px;
    }
    .hero {
      background: linear-gradient(135deg, rgba(9, 21, 32, 0.88), rgba(11, 31, 44, 0.74));
      border: 1px solid rgba(121, 233, 220, 0.18);
      border-radius: 26px;
      padding: 22px 24px;
      box-shadow: 0 28px 80px rgba(0,0,0,0.28);
      margin-bottom: 16px;
    }
    .eyebrow {
      color: var(--cyan);
      letter-spacing: 0.16em;
      text-transform: uppercase;
      font-size: 12px;
      margin-bottom: 8px;
    }
    h1 {
      margin: 0;
      font-size: 46px;
      line-height: 1.02;
    }
    .hero p, .muted {
      color: var(--muted);
      line-height: 1.65;
    }
    .grid3, .metrics, .risk-grid, .two-col {
      display: grid;
      gap: 14px;
    }
    .grid3 { grid-template-columns: repeat(3, minmax(0, 1fr)); margin-top: 14px; }
    .metrics { grid-template-columns: repeat(4, minmax(0, 1fr)); margin: 16px 0; }
    .risk-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); margin-top: 12px; }
    .two-col { grid-template-columns: 1.15fr 0.85fr; margin-top: 16px; }
    .panel, .metric, .mini-card, .risk-card {
      background: var(--card);
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: 18px;
    }
    .panel { padding: 16px; }
    .mini-card { padding: 14px; }
    .metric { padding: 14px 16px; }
    .risk-card { padding: 16px; min-height: 220px; }
    .severity-critical, .severity-high { border-color: rgba(255, 123, 79, 0.42); }
    .severity-medium { border-color: rgba(255, 181, 93, 0.42); }
    .severity-low { border-color: rgba(121, 233, 220, 0.28); }
    .tag {
      display: inline-block;
      color: var(--amber);
      border: 1px solid rgba(255, 181, 93, 0.25);
      border-radius: 999px;
      padding: 6px 12px;
      font-size: 12px;
      letter-spacing: 0.12em;
      margin-bottom: 10px;
    }
    .metric .label, .side-label {
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 6px;
    }
    .metric .value {
      font-size: 24px;
      font-weight: 700;
    }
    .metric .delta {
      font-size: 13px;
      color: var(--cyan);
      margin-top: 6px;
    }
    .section {
      margin-top: 18px;
    }
    .section h2 {
      margin: 6px 0 12px;
      font-size: 24px;
    }
    .field {
      margin-bottom: 13px;
    }
    .field label {
      display: block;
      font-size: 13px;
      color: var(--muted);
      margin-bottom: 6px;
    }
    .field input, .field select, .field textarea {
      width: 100%;
      background: rgba(255,255,255,0.035);
      color: var(--ink);
      border: 1px solid rgba(255,255,255,0.10);
      border-radius: 12px;
      padding: 10px 12px;
      font: inherit;
    }
    .field input[type="checkbox"] {
      width: auto;
      transform: scale(1.15);
      margin-right: 8px;
    }
    .checkbox-row {
      display: flex;
      align-items: center;
      color: var(--ink);
      gap: 8px;
      padding: 8px 0;
    }
    button {
      width: 100%;
      border: none;
      border-radius: 14px;
      padding: 13px 16px;
      background: linear-gradient(90deg, var(--cyan), #4dd6c6);
      color: #06212b;
      font-weight: 800;
      cursor: pointer;
      margin-top: 8px;
    }
    button:hover { filter: brightness(1.03); }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }
    th, td {
      border-bottom: 1px solid rgba(255,255,255,0.08);
      padding: 10px 8px;
      text-align: left;
      vertical-align: top;
    }
    th { color: var(--muted); font-weight: 600; }
    .summary-box {
      background: rgba(255,255,255,0.03);
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: 18px;
      padding: 14px 16px;
      line-height: 1.7;
      color: var(--muted);
      margin-top: 12px;
    }
    .loading {
      display: none;
      color: var(--amber);
      margin-top: 10px;
      font-size: 13px;
    }
    .calibration-box {
      white-space: pre-wrap;
      color: var(--muted);
      line-height: 1.65;
    }
    .topbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 14px;
    }
    .lang-toggle {
      display: inline-flex;
      gap: 8px;
    }
    .lang-toggle button {
      width: auto;
      margin: 0;
      padding: 9px 12px;
      border-radius: 999px;
      background: rgba(255,255,255,0.06);
      color: var(--ink);
      border: 1px solid rgba(255,255,255,0.09);
    }
    .lang-toggle button.active {
      background: linear-gradient(90deg, var(--cyan), #4dd6c6);
      color: #06212b;
    }
    @media (max-width: 1180px) {
      .shell { grid-template-columns: 1fr; }
      .sidebar { position: static; height: auto; }
      .grid3, .metrics, .risk-grid, .two-col { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="shell">
    <aside class="sidebar">
      <div class="topbar">
        <strong id="sideTitle">场景设置</strong>
        <div class="lang-toggle">
          <button id="langZh" class="active" type="button">中文</button>
          <button id="langEn" type="button">EN</button>
        </div>
      </div>
      <form id="controlForm">
        <div class="field">
          <label id="labelProposalPreset">提案模板</label>
          <select id="proposalPreset"></select>
        </div>
        <div class="field">
          <label id="labelEnvironmentPreset">压力环境模板</label>
          <select id="environmentPreset"></select>
        </div>
        <div class="field">
          <label id="labelRunCount">模拟次数</label>
          <input id="runCount" type="number" min="100" max="1500" step="100" />
        </div>
        <div class="field">
          <label id="labelSeed">随机种子</label>
          <input id="seed" type="number" min="1" max="999999" step="1" />
        </div>
        <div class="field">
          <label id="labelQuorum">法定人数门槛</label>
          <input id="quorum" type="number" min="0.05" max="0.6" step="0.01" />
        </div>
        <div class="field">
          <label id="labelApproval">通过阈值</label>
          <input id="approvalThreshold" type="number" min="0.5" max="0.8" step="0.01" />
        </div>
        <div class="field">
          <label id="labelTreasury">金库动用比例</label>
          <input id="treasuryRequestPct" type="number" min="0" max="0.5" step="0.01" />
        </div>
        <div class="field">
          <label id="labelUpside">预期收益</label>
          <input id="expectedUpside" type="number" min="-0.2" max="0.6" step="0.01" />
        </div>
        <div class="field">
          <label id="labelExecutionRisk">执行风险</label>
          <input id="executionRisk" type="number" min="0" max="1" step="0.01" />
        </div>
        <div class="field">
          <label id="labelDecentralization">去中心化影响</label>
          <input id="decentralizationImpact" type="number" min="-0.6" max="0.6" step="0.01" />
        </div>
        <div class="field">
          <label id="labelUrgency">紧急程度</label>
          <input id="urgency" type="number" min="0" max="1" step="0.01" />
        </div>
        <div class="field">
          <label id="labelReputation">提案人信誉</label>
          <input id="proposerReputation" type="number" min="-0.5" max="0.6" step="0.01" />
        </div>
        <div class="field">
          <label id="labelMarketVol">市场波动</label>
          <input id="marketVolatility" type="number" min="0.05" max="0.6" step="0.01" />
        </div>
        <div class="field">
          <label id="labelShockProb">负面冲击概率</label>
          <input id="negativeShockProbability" type="number" min="0" max="0.8" step="0.01" />
        </div>
        <div class="field">
          <label id="labelWhaleCoord">大户联动强度</label>
          <input id="whaleCoordination" type="number" min="0" max="1" step="0.01" />
        </div>
        <div class="field">
          <label id="labelApathy">投票冷漠度</label>
          <input id="voterApathy" type="number" min="0" max="1" step="0.01" />
        </div>
        <div class="field">
          <label id="labelSentiment">社区情绪</label>
          <input id="socialSentiment" type="number" min="-0.5" max="0.5" step="0.01" />
        </div>
        <div class="field">
          <label id="labelManipulation">操纵压力</label>
          <input id="manipulationPressure" type="number" min="0" max="1" step="0.01" />
        </div>
        <div class="field">
          <label id="labelNoise">行为噪声</label>
          <input id="noiseScale" type="number" min="0.05" max="0.4" step="0.01" />
        </div>
        <label class="checkbox-row"><input id="useHtxCalibration" type="checkbox" /> <span id="labelUseHtx">启用 HTX 市场校准占位</span></label>
        <button type="submit" id="runButton">运行风洞模拟</button>
        <div class="loading" id="loadingText">正在运行模拟，请稍候...</div>
      </form>
    </aside>
    <main class="content">
      <section class="hero">
        <div class="eyebrow" id="heroEyebrow">HTX Genesis Hackathon / 提案先压测，再治理</div>
        <h1 id="heroTitle">Cybernetic DAO 治理风洞</h1>
        <p id="heroCopy">别把 DAO 提案直接丢进生产环境。先看它在坏行情、低参与、大户联动和机制缺陷下会不会被带偏，再决定要不要真的执行。</p>
        <div class="grid3">
          <div class="mini-card"><strong id="mini1Title">先看会不会误过</strong><p class="muted" id="mini1Desc">重点看“坏提案被通过”的概率，而不只是总通过率。</p></div>
          <div class="mini-card"><strong id="mini2Title">再看会不会被控票</strong><p class="muted" id="mini2Desc">直接识别大户主导、关键一票拍板、前 3 大钱包集中度。</p></div>
          <div class="mini-card"><strong id="mini3Title">最后看抗冲击能力</strong><p class="muted" id="mini3Desc">同一提案在不同投票机制下是否会因为市场波动而翻车。</p></div>
        </div>
      </section>

      <section class="metrics" id="metrics"></section>

      <section class="two-col">
        <div class="panel">
          <div class="tag" id="summaryTag">结果速读</div>
          <h2 id="proposalName"></h2>
          <p class="muted" id="proposalSummary"></p>
          <div class="summary-box" id="executiveSummary"></div>
          <p class="muted" id="envLine"></p>
        </div>
        <div class="panel">
          <div class="tag" id="calibrationTag">校准信息</div>
          <div class="calibration-box" id="calibrationBox"></div>
        </div>
      </section>

      <section class="section">
        <div class="tag" id="riskTag">风险报告</div>
        <div class="risk-grid" id="riskGrid"></div>
      </section>

      <section class="section">
        <div class="panel"><div id="summaryChart" style="height: 360px;"></div></div>
      </section>
      <section class="section">
        <div class="panel"><div id="shockChart" style="height: 420px;"></div></div>
      </section>
      <section class="section">
        <div class="two-col">
          <div class="panel">
            <div class="tag" id="tableTag">机制对比表</div>
            <div id="summaryTable"></div>
          </div>
          <div class="panel">
            <div class="tag" id="agentsTag">代理画像</div>
            <div id="agentTable"></div>
          </div>
        </div>
      </section>
    </main>
  </div>

  <script>
    const TEXT = {
      zh: {
        sideTitle: "场景设置",
        heroEyebrow: "HTX Genesis Hackathon / 提案先压测，再治理",
        heroTitle: "Cybernetic DAO 治理风洞",
        heroCopy: "别把 DAO 提案直接丢进生产环境。先看它在坏行情、低参与、大户联动和机制缺陷下会不会被带偏，再决定要不要真的执行。",
        mini1Title: "先看会不会误过",
        mini1Desc: "重点看“坏提案被通过”的概率，而不只是总通过率。",
        mini2Title: "再看会不会被控票",
        mini2Desc: "直接识别大户主导、关键一票拍板、前 3 大钱包集中度。",
        mini3Title: "最后看抗冲击能力",
        mini3Desc: "同一提案在不同投票机制下是否会因为市场波动而翻车。",
        summaryTag: "结果速读",
        calibrationTag: "校准信息",
        riskTag: "风险报告",
        tableTag: "机制对比表",
        agentsTag: "代理画像",
        labels: {
          proposalPreset: "提案模板",
          environmentPreset: "压力环境模板",
          runCount: "模拟次数",
          seed: "随机种子",
          quorum: "法定人数门槛",
          approval: "通过阈值",
          treasury: "金库动用比例",
          upside: "预期收益",
          executionRisk: "执行风险",
          decentralization: "去中心化影响",
          urgency: "紧急程度",
          reputation: "提案人信誉",
          marketVol: "市场波动",
          shockProb: "负面冲击概率",
          whaleCoord: "大户联动强度",
          apathy: "投票冷漠度",
          sentiment: "社区情绪",
          manipulation: "操纵压力",
          noise: "行为噪声",
          useHtx: "启用 HTX 市场校准占位",
          runButton: "运行风洞模拟",
          loading: "正在运行模拟，请稍候...",
        },
        metrics: {
          best: "推荐机制",
          bestDelta: (score) => `韧性分 ${score.toFixed(1)}`,
          pass: "最高通过率",
          capture: "最高控票风险",
          shock: "最大行情敏感度",
          shockDelta: "机制间最大摆动",
        },
        envLine: (env, runs) => `环境：${env} | 模拟次数：${runs}`,
        noCalibration: "当前没有启用 HTX 校准占位，环境参数完全来自左侧手动设置。",
        calibrationTitleSource: "数据来源",
        calibrationTitleNote: "说明",
        summaryChartTitle: "三种投票机制的结果对比",
        shockChartTitle: "市场波动对投票结果的影响",
        summarySeries: {
          pass: "总通过率",
          falsePositive: "坏提案误通过",
          falseNegative: "好提案被误杀",
          capture: "被大户带票",
        },
        summaryTableHeaders: ["投票机制", "通过率", "平均参与率", "坏提案误通过", "大户带票率", "韧性分"],
        agentTableHeaders: ["代理 ID", "类型", "投票权", "出勤稳定性", "操纵倾向"],
        riskSeverity: "风险级别",
        riskAction: "建议动作",
      },
      en: {
        sideTitle: "Scenario Controls",
        heroEyebrow: "HTX Genesis Hackathon / Governance Pre-Flight Lab",
        heroTitle: "Cybernetic DAO Wind Tunnel",
        heroCopy: "Do not ship DAO proposals straight into production. First test whether they fail under bad markets, low turnout, whale coordination, or mechanism-design flaws.",
        mini1Title: "Start With Bad Passes",
        mini1Desc: "Focus on how often harmful proposals still pass, not just raw pass rate.",
        mini2Title: "Then Check Vote Capture",
        mini2Desc: "Watch whale control, decisive votes, and top-wallet concentration.",
        mini3Title: "Finish With Shock Resilience",
        mini3Desc: "See whether a market regime change flips the same proposal across mechanisms.",
        summaryTag: "Executive Readout",
        calibrationTag: "Calibration",
        riskTag: "Vulnerability Report",
        tableTag: "Mechanism Table",
        agentsTag: "Agent Composition",
        labels: {
          proposalPreset: "Proposal preset",
          environmentPreset: "Environment preset",
          runCount: "Monte Carlo runs",
          seed: "Random seed",
          quorum: "Quorum threshold",
          approval: "Approval threshold",
          treasury: "Treasury request (% of treasury)",
          upside: "Expected upside",
          executionRisk: "Execution risk",
          decentralization: "Decentralization impact",
          urgency: "Urgency",
          reputation: "Proposer reputation",
          marketVol: "Market volatility",
          shockProb: "Negative shock probability",
          whaleCoord: "Whale coordination",
          apathy: "Voter apathy",
          sentiment: "Social sentiment",
          manipulation: "Manipulation pressure",
          noise: "Behavioral noise",
          useHtx: "Apply HTX calibration placeholder",
          runButton: "Run Wind Tunnel",
          loading: "Running simulation...",
        },
        metrics: {
          best: "Best Mechanism",
          bestDelta: (score) => `${score.toFixed(1)} resilience`,
          pass: "Highest Pass Rate",
          capture: "Capture Risk Peak",
          shock: "Shock Delta",
          shockDelta: "max mechanism swing",
        },
        envLine: (env, runs) => `Environment: ${env} | Simulations: ${runs}`,
        noCalibration: "HTX calibration placeholder is disabled for this run.",
        calibrationTitleSource: "Source",
        calibrationTitleNote: "Note",
        summaryChartTitle: "Mechanism Outcomes",
        shockChartTitle: "Outcome Sensitivity To Market Regime",
        summarySeries: {
          pass: "Pass Rate",
          falsePositive: "Bad Proposal Passes",
          falseNegative: "Good Proposal Rejections",
          capture: "Capture Flag Rate",
        },
        summaryTableHeaders: ["Mechanism", "Pass Rate", "Avg Turnout", "Bad Passes", "Capture Rate", "Resilience"],
        agentTableHeaders: ["Agent ID", "Archetype", "Voting Power", "Turnout", "Manipulation"],
        riskSeverity: "Severity",
        riskAction: "Action",
      }
    };

    let bootstrap = null;
    let currentLanguage = "zh";
    let currentResult = null;
    let proposalPresets = [];
    let environmentPresets = [];

    async function init() {
      const response = await fetch("/api/bootstrap");
      bootstrap = await response.json();
      proposalPresets = bootstrap.proposal_presets;
      environmentPresets = bootstrap.environment_presets;
      fillStaticText();
      populatePresetOptions();
      applyRequestToForm(bootstrap.default_request);
      currentResult = bootstrap.initial_result;
      renderResult(currentResult);
      bindEvents();
    }

    function fillStaticText() {
      const t = TEXT[currentLanguage];
      document.getElementById("sideTitle").textContent = t.sideTitle;
      document.getElementById("heroEyebrow").textContent = t.heroEyebrow;
      document.getElementById("heroTitle").textContent = t.heroTitle;
      document.getElementById("heroCopy").textContent = t.heroCopy;
      document.getElementById("mini1Title").textContent = t.mini1Title;
      document.getElementById("mini1Desc").textContent = t.mini1Desc;
      document.getElementById("mini2Title").textContent = t.mini2Title;
      document.getElementById("mini2Desc").textContent = t.mini2Desc;
      document.getElementById("mini3Title").textContent = t.mini3Title;
      document.getElementById("mini3Desc").textContent = t.mini3Desc;
      document.getElementById("summaryTag").textContent = t.summaryTag;
      document.getElementById("calibrationTag").textContent = t.calibrationTag;
      document.getElementById("riskTag").textContent = t.riskTag;
      document.getElementById("tableTag").textContent = t.tableTag;
      document.getElementById("agentsTag").textContent = t.agentsTag;
      document.getElementById("labelProposalPreset").textContent = t.labels.proposalPreset;
      document.getElementById("labelEnvironmentPreset").textContent = t.labels.environmentPreset;
      document.getElementById("labelRunCount").textContent = t.labels.runCount;
      document.getElementById("labelSeed").textContent = t.labels.seed;
      document.getElementById("labelQuorum").textContent = t.labels.quorum;
      document.getElementById("labelApproval").textContent = t.labels.approval;
      document.getElementById("labelTreasury").textContent = t.labels.treasury;
      document.getElementById("labelUpside").textContent = t.labels.upside;
      document.getElementById("labelExecutionRisk").textContent = t.labels.executionRisk;
      document.getElementById("labelDecentralization").textContent = t.labels.decentralization;
      document.getElementById("labelUrgency").textContent = t.labels.urgency;
      document.getElementById("labelReputation").textContent = t.labels.reputation;
      document.getElementById("labelMarketVol").textContent = t.labels.marketVol;
      document.getElementById("labelShockProb").textContent = t.labels.shockProb;
      document.getElementById("labelWhaleCoord").textContent = t.labels.whaleCoord;
      document.getElementById("labelApathy").textContent = t.labels.apathy;
      document.getElementById("labelSentiment").textContent = t.labels.sentiment;
      document.getElementById("labelManipulation").textContent = t.labels.manipulation;
      document.getElementById("labelNoise").textContent = t.labels.noise;
      document.getElementById("labelUseHtx").textContent = t.labels.useHtx;
      document.getElementById("runButton").textContent = t.labels.runButton;
      document.getElementById("loadingText").textContent = t.labels.loading;
      document.getElementById("langZh").classList.toggle("active", currentLanguage === "zh");
      document.getElementById("langEn").classList.toggle("active", currentLanguage === "en");
    }

    function populatePresetOptions() {
      const proposalSelect = document.getElementById("proposalPreset");
      const environmentSelect = document.getElementById("environmentPreset");
      proposalSelect.innerHTML = "";
      environmentSelect.innerHTML = "";
      proposalPresets.forEach((item) => {
        const option = document.createElement("option");
        option.value = item.key;
        option.textContent = currentLanguage === "zh" ? item.label_zh : item.label_en;
        proposalSelect.appendChild(option);
      });
      environmentPresets.forEach((item) => {
        const option = document.createElement("option");
        option.value = item.key;
        option.textContent = currentLanguage === "zh" ? item.label_zh : item.label_en;
        environmentSelect.appendChild(option);
      });
    }

    function applyRequestToForm(request) {
      document.getElementById("proposalPreset").value = request.proposal_preset;
      document.getElementById("environmentPreset").value = request.environment_preset;
      document.getElementById("runCount").value = request.run_count;
      document.getElementById("seed").value = request.seed;
      document.getElementById("quorum").value = request.quorum;
      document.getElementById("approvalThreshold").value = request.approval_threshold;
      const proposal = proposalPresets.find((item) => item.key === request.proposal_preset)?.config || {};
      const environment = environmentPresets.find((item) => item.key === request.environment_preset)?.config || {};
      document.getElementById("treasuryRequestPct").value = proposal.treasury_request_pct;
      document.getElementById("expectedUpside").value = proposal.expected_upside;
      document.getElementById("executionRisk").value = proposal.execution_risk;
      document.getElementById("decentralizationImpact").value = proposal.decentralization_impact;
      document.getElementById("urgency").value = proposal.urgency;
      document.getElementById("proposerReputation").value = proposal.proposer_reputation;
      document.getElementById("marketVolatility").value = environment.market_volatility;
      document.getElementById("negativeShockProbability").value = environment.negative_shock_probability;
      document.getElementById("whaleCoordination").value = environment.whale_coordination;
      document.getElementById("voterApathy").value = environment.voter_apathy;
      document.getElementById("socialSentiment").value = environment.social_sentiment;
      document.getElementById("manipulationPressure").value = environment.manipulation_pressure;
      document.getElementById("noiseScale").value = environment.noise_scale;
      document.getElementById("useHtxCalibration").checked = request.use_htx_calibration;
    }

    function collectRequest() {
      return {
        proposal_preset: document.getElementById("proposalPreset").value,
        environment_preset: document.getElementById("environmentPreset").value,
        run_count: Number(document.getElementById("runCount").value),
        seed: Number(document.getElementById("seed").value),
        quorum: Number(document.getElementById("quorum").value),
        approval_threshold: Number(document.getElementById("approvalThreshold").value),
        treasury_request_pct: Number(document.getElementById("treasuryRequestPct").value),
        expected_upside: Number(document.getElementById("expectedUpside").value),
        execution_risk: Number(document.getElementById("executionRisk").value),
        decentralization_impact: Number(document.getElementById("decentralizationImpact").value),
        urgency: Number(document.getElementById("urgency").value),
        proposer_reputation: Number(document.getElementById("proposerReputation").value),
        market_volatility: Number(document.getElementById("marketVolatility").value),
        negative_shock_probability: Number(document.getElementById("negativeShockProbability").value),
        whale_coordination: Number(document.getElementById("whaleCoordination").value),
        voter_apathy: Number(document.getElementById("voterApathy").value),
        social_sentiment: Number(document.getElementById("socialSentiment").value),
        manipulation_pressure: Number(document.getElementById("manipulationPressure").value),
        noise_scale: Number(document.getElementById("noiseScale").value),
        use_htx_calibration: document.getElementById("useHtxCalibration").checked,
        language: currentLanguage,
      };
    }

    function bindEvents() {
      document.getElementById("proposalPreset").addEventListener("change", (event) => {
        const item = proposalPresets.find((x) => x.key === event.target.value);
        if (!item) return;
        const config = item.config;
        document.getElementById("treasuryRequestPct").value = config.treasury_request_pct;
        document.getElementById("expectedUpside").value = config.expected_upside;
        document.getElementById("executionRisk").value = config.execution_risk;
        document.getElementById("decentralizationImpact").value = config.decentralization_impact;
        document.getElementById("urgency").value = config.urgency;
        document.getElementById("proposerReputation").value = config.proposer_reputation;
      });

      document.getElementById("environmentPreset").addEventListener("change", (event) => {
        const item = environmentPresets.find((x) => x.key === event.target.value);
        if (!item) return;
        const config = item.config;
        document.getElementById("marketVolatility").value = config.market_volatility;
        document.getElementById("negativeShockProbability").value = config.negative_shock_probability;
        document.getElementById("whaleCoordination").value = config.whale_coordination;
        document.getElementById("voterApathy").value = config.voter_apathy;
        document.getElementById("socialSentiment").value = config.social_sentiment;
        document.getElementById("manipulationPressure").value = config.manipulation_pressure;
        document.getElementById("noiseScale").value = config.noise_scale;
      });

      document.getElementById("controlForm").addEventListener("submit", async (event) => {
        event.preventDefault();
        document.getElementById("loadingText").style.display = "block";
        try {
          const response = await fetch("/api/simulate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(collectRequest()),
          });
          currentResult = await response.json();
          renderResult(currentResult);
        } finally {
          document.getElementById("loadingText").style.display = "none";
        }
      });

      document.getElementById("langZh").addEventListener("click", () => switchLanguage("zh"));
      document.getElementById("langEn").addEventListener("click", () => switchLanguage("en"));
    }

    async function switchLanguage(language) {
      currentLanguage = language;
      fillStaticText();
      populatePresetOptions();
      const req = collectRequest();
      req.language = currentLanguage;
      document.getElementById("loadingText").style.display = "block";
      try {
        const response = await fetch("/api/simulate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(req),
        });
        currentResult = await response.json();
        renderResult(currentResult);
      } finally {
        document.getElementById("loadingText").style.display = "none";
      }
    }

    function renderMetrics(result) {
      const t = TEXT[currentLanguage];
      const metrics = result.metrics;
      const items = [
        { label: t.metrics.best, value: metrics.best_mechanism, delta: t.metrics.bestDelta(metrics.best_mechanism_score) },
        { label: t.metrics.pass, value: formatPct(metrics.highest_pass_rate), delta: metrics.highest_pass_label },
        { label: t.metrics.capture, value: formatPct(metrics.capture_risk_peak), delta: metrics.capture_risk_label },
        { label: t.metrics.shock, value: formatPct(metrics.shock_delta), delta: t.metrics.shockDelta },
      ];
      document.getElementById("metrics").innerHTML = items.map((item) => `
        <div class="metric">
          <div class="label">${item.label}</div>
          <div class="value">${item.value}</div>
          <div class="delta">${item.delta}</div>
        </div>
      `).join("");
    }

    function renderSummary(result) {
      const t = TEXT[currentLanguage];
      document.getElementById("proposalName").textContent = result.proposal.name;
      document.getElementById("proposalSummary").textContent = result.proposal.summary;
      document.getElementById("executiveSummary").textContent = result.executive_summary;
      document.getElementById("envLine").textContent = t.envLine(result.environment.label_display, result.records_rows.length / 3);
      const box = document.getElementById("calibrationBox");
      if (!result.market_snapshot) {
        box.textContent = t.noCalibration;
      } else {
        const snap = result.market_snapshot;
        box.textContent = `${t.calibrationTitleSource}: ${snap.source}\n${t.calibrationTitleNote}: ${snap.note}\n24h: ${formatPct(snap.price_change_24h)}\nVolume: ${formatPct(snap.volume_change_24h)}\nMultiplier: ${Number(snap.volatility_multiplier).toFixed(2)}`;
      }
    }

    function renderRisks(result) {
      const t = TEXT[currentLanguage];
      document.getElementById("riskGrid").innerHTML = result.vulnerability_rows.map((item) => `
        <div class="risk-card severity-${item.severity}">
          <h3 style="margin-top:0">${item.title_display}</h3>
          <p><strong>${t.riskSeverity}:</strong> ${item.severity_display}</p>
          <p>${item.evidence_display || item.evidence}</p>
          <p><strong>${t.riskAction}:</strong> ${item.recommendation_display || item.recommendation}</p>
        </div>
      `).join("");
    }

    function renderSummaryTable(result) {
      const headers = TEXT[currentLanguage].summaryTableHeaders;
      const rows = result.summary_rows.map((row) => `
        <tr>
          <td>${row.label_display}</td>
          <td>${formatPct(row.pass_rate)}</td>
          <td>${formatPct(row.avg_turnout)}</td>
          <td>${formatPct(row.false_positive_rate)}</td>
          <td>${formatPct(row.whale_capture_rate)}</td>
          <td>${row.resilience_score.toFixed(1)}</td>
        </tr>
      `).join("");
      document.getElementById("summaryTable").innerHTML = `
        <table>
          <thead><tr>${headers.map((header) => `<th>${header}</th>`).join("")}</tr></thead>
          <tbody>${rows}</tbody>
        </table>
      `;
    }

    function renderAgentTable(result) {
      const headers = TEXT[currentLanguage].agentTableHeaders;
      const rows = result.agent_rows.slice(0, 14).map((row) => `
        <tr>
          <td>${row.agent_id}</td>
          <td>${row.archetype_display}</td>
          <td>${formatPct(row.voting_power)}</td>
          <td>${formatPct(row.turnout_discipline)}</td>
          <td>${formatPct(row.manipulation_tendency)}</td>
        </tr>
      `).join("");
      document.getElementById("agentTable").innerHTML = `
        <table>
          <thead><tr>${headers.map((header) => `<th>${header}</th>`).join("")}</tr></thead>
          <tbody>${rows}</tbody>
        </table>
      `;
    }

    function renderSummaryChart(result) {
      const t = TEXT[currentLanguage];
      const labels = result.summary_rows.map((row) => row.label_display);
      Plotly.newPlot("summaryChart", [
        { x: labels, y: result.summary_rows.map((row) => row.pass_rate), type: "bar", name: t.summarySeries.pass, marker: { color: "#79e9dc" } },
        { x: labels, y: result.summary_rows.map((row) => row.false_positive_rate), type: "bar", name: t.summarySeries.falsePositive, marker: { color: "#ff7b4f" } },
        { x: labels, y: result.summary_rows.map((row) => row.false_negative_rate), type: "bar", name: t.summarySeries.falseNegative, marker: { color: "#ffb55d" } },
        { x: labels, y: result.summary_rows.map((row) => row.whale_capture_rate), type: "bar", name: t.summarySeries.capture, marker: { color: "#9ab5c4" } },
      ], {
        title: t.summaryChartTitle,
        barmode: "group",
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        font: { color: "#f0f7fb" },
        yaxis: { tickformat: ".0%" },
        margin: { l: 40, r: 18, t: 52, b: 40 },
      }, { displayModeBar: false, responsive: true });
    }

    function renderShockChart(result) {
      const groups = [...new Set(result.records_rows.map((row) => row.mechanism_label_display))];
      const data = groups.flatMap((group) => {
        const passed = result.records_rows.filter((row) => row.mechanism_label_display === group && row.passed);
        const rejected = result.records_rows.filter((row) => row.mechanism_label_display === group && !row.passed);
        return [
          {
            x: passed.map((row) => row.market_return),
            y: passed.map((row) => row.yes_weight_share),
            mode: "markers",
            type: "scatter",
            name: `${group} / ${currentLanguage === "zh" ? "通过" : "Passed"}`,
            marker: { color: "#79e9dc", size: 7, opacity: 0.6 },
          },
          {
            x: rejected.map((row) => row.market_return),
            y: rejected.map((row) => row.yes_weight_share),
            mode: "markers",
            type: "scatter",
            name: `${group} / ${currentLanguage === "zh" ? "未通过" : "Rejected"}`,
            marker: { color: "#ff7b4f", size: 7, opacity: 0.6 },
          }
        ];
      });
      Plotly.newPlot("shockChart", data, {
        title: TEXT[currentLanguage].shockChartTitle,
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        font: { color: "#f0f7fb" },
        xaxis: { tickformat: ".0%", title: "" },
        yaxis: { tickformat: ".0%", title: "" },
        margin: { l: 44, r: 18, t: 56, b: 42 },
      }, { displayModeBar: false, responsive: true });
    }

    function renderResult(result) {
      renderMetrics(result);
      renderSummary(result);
      renderRisks(result);
      renderSummaryTable(result);
      renderAgentTable(result);
      renderSummaryChart(result);
      renderShockChart(result);
    }

    function formatPct(value) {
      return `${(Number(value) * 100).toFixed(1)}%`;
    }

    init();
  </script>
</body>
</html>
    """
    return HTMLResponse(html)
