from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from ai_explainer import GovernanceExplainer
from dao_wind_tunnel_core import (
    EnvironmentConfig,
    ProposalConfig,
    build_default_mechanisms,
    environment_presets,
    proposal_presets,
    run_wind_tunnel,
)
from htx_market import HTXMarketCalibrator


load_dotenv()

st.set_page_config(
    page_title="Cybernetic DAO Wind Tunnel",
    layout="wide",
    initial_sidebar_state="expanded",
)


LANGUAGE_OPTIONS = ["中文", "English"]

UI_TEXT = {
    "中文": {
        "language_label": "界面语言",
        "display_settings": "显示设置",
        "header_eyebrow": "HTX Genesis Hackathon / 提案先压测，再治理",
        "hero_title": "Cybernetic DAO 治理风洞",
        "hero_copy": (
            "别把 DAO 提案直接丢进生产环境。先看它在坏行情、低参与、大户联动和机制缺陷下会不会被带偏，"
            "再决定要不要真的执行。"
        ),
        "microcards": [
            ("先看会不会误过", "重点看“坏提案被通过”的概率，而不只是总通过率。"),
            ("再看会不会被控票", "直接识别大户主导、关键一票拍板、前 3 大钱包集中度。"),
            ("最后看抗冲击能力", "同一提案在不同投票机制下是否会因为市场波动而翻车。"),
        ],
        "scenario_controls": "场景设置",
        "proposal_preset": "提案模板",
        "environment_preset": "压力环境模板",
        "runs": "模拟次数",
        "seed": "随机种子",
        "quorum": "法定人数门槛",
        "approval_threshold": "通过阈值",
        "proposal_inputs": "提案参数",
        "proposal_name": "提案名称",
        "proposal_thesis": "一句话描述",
        "treasury_request": "金库动用比例",
        "expected_upside": "预期收益",
        "execution_risk": "执行风险",
        "decentralization_impact": "去中心化影响",
        "urgency": "紧急程度",
        "proposer_reputation": "提案人信誉",
        "stress_inputs": "环境压力参数",
        "market_volatility": "市场波动",
        "shock_probability": "负面冲击概率",
        "whale_coordination": "大户联动强度",
        "voter_apathy": "投票冷漠度",
        "social_sentiment": "社区情绪",
        "manipulation_pressure": "操纵压力",
        "noise_scale": "行为噪声",
        "use_htx": "启用 HTX 市场校准占位",
        "use_live_ai": "如果已配置，尝试实时 AI 解释",
        "best_mechanism": "推荐机制",
        "best_mechanism_delta": "韧性分 {score:.1f}",
        "highest_pass_rate": "最高通过率",
        "highest_pass_rate_delta": "{label}",
        "capture_risk_peak": "最高控票风险",
        "shock_delta": "最大行情敏感度",
        "shock_delta_delta": "机制间最大摆动",
        "executive_readout": "结果速读",
        "calibration": "校准信息",
        "vulnerability_report": "风险报告",
        "mechanism_table": "机制对比表",
        "agent_composition": "代理画像",
        "download_report": "下载 JSON 报告",
        "environment_label": "环境",
        "ai_mode_label": "解释模式",
        "simulation_count": "模拟次数",
        "calibration_off": "当前没有启用 HTX 校准占位，环境参数完全来自左侧手动设置。",
        "summary_chart_title": "三种投票机制的结果对比",
        "turnout_chart_title": "投票参与度分布",
        "shock_chart_title": "市场波动对投票结果的影响",
        "summary_chart_metrics": {
            "pass_rate": "总通过率",
            "false_positive_rate": "坏提案误通过",
            "false_negative_rate": "好提案被误杀",
            "whale_capture_rate": "被大户带票",
        },
        "passed_yes": "通过",
        "passed_no": "未通过",
        "shock_yes": "出现冲击",
        "shock_no": "无冲击",
        "risk_severity": "风险级别",
        "risk_action": "建议动作",
        "table_columns": {
            "label_display": "投票机制",
            "pass_rate": "通过率",
            "avg_turnout": "平均参与率",
            "avg_yes_share": "平均赞成票占比",
            "quorum_failure_rate": "流会率",
            "false_positive_rate": "坏提案误通过",
            "false_negative_rate": "好提案被误杀",
            "decisive_whale_rate": "关键票来自大户",
            "whale_capture_rate": "大户带票率",
            "shock_flip_delta": "冲击敏感度",
            "legitimacy_gap": "权重-人数割裂",
            "resilience_score": "韧性分",
        },
        "agent_columns": {
            "agent_id": "代理 ID",
            "archetype_display": "类型",
            "voting_power": "投票权",
            "turnout_discipline": "出勤稳定性",
            "manipulation_tendency": "操纵倾向",
        },
    },
    "English": {
        "language_label": "Interface language",
        "display_settings": "Display",
        "header_eyebrow": "HTX Genesis Hackathon / Governance Pre-Flight Lab",
        "hero_title": "Cybernetic DAO Wind Tunnel",
        "hero_copy": (
            "Do not ship DAO proposals straight into production. First test whether they fail under bad markets, low turnout, "
            "whale coordination, or mechanism-design flaws."
        ),
        "microcards": [
            ("Start With Bad Passes", "Focus on how often harmful proposals still pass, not just raw pass rate."),
            ("Then Check Vote Capture", "Watch whale control, decisive votes, and top-wallet concentration."),
            ("Finish With Shock Resilience", "See whether a market regime change flips the same proposal across mechanisms."),
        ],
        "scenario_controls": "Scenario Controls",
        "proposal_preset": "Proposal preset",
        "environment_preset": "Environment preset",
        "runs": "Monte Carlo runs",
        "seed": "Random seed",
        "quorum": "Quorum threshold",
        "approval_threshold": "Approval threshold",
        "proposal_inputs": "Proposal Inputs",
        "proposal_name": "Proposal name",
        "proposal_thesis": "One-line proposal thesis",
        "treasury_request": "Treasury request (% of treasury)",
        "expected_upside": "Expected upside",
        "execution_risk": "Execution risk",
        "decentralization_impact": "Decentralization impact",
        "urgency": "Urgency",
        "proposer_reputation": "Proposer reputation",
        "stress_inputs": "Stress Inputs",
        "market_volatility": "Market volatility",
        "shock_probability": "Negative shock probability",
        "whale_coordination": "Whale coordination",
        "voter_apathy": "Voter apathy",
        "social_sentiment": "Social sentiment",
        "manipulation_pressure": "Manipulation pressure",
        "noise_scale": "Behavioral noise",
        "use_htx": "Apply HTX calibration placeholder",
        "use_live_ai": "Try live AI explainer if configured",
        "best_mechanism": "Best Mechanism",
        "best_mechanism_delta": "{score:.1f} resilience",
        "highest_pass_rate": "Highest Pass Rate",
        "highest_pass_rate_delta": "{label}",
        "capture_risk_peak": "Capture Risk Peak",
        "shock_delta": "Shock Delta",
        "shock_delta_delta": "max mechanism swing",
        "executive_readout": "Executive Readout",
        "calibration": "Calibration",
        "vulnerability_report": "Vulnerability Report",
        "mechanism_table": "Mechanism Table",
        "agent_composition": "Agent Composition",
        "download_report": "Download JSON report",
        "environment_label": "Environment",
        "ai_mode_label": "AI mode",
        "simulation_count": "Simulations",
        "calibration_off": "HTX calibration placeholder is disabled for this run.",
        "summary_chart_title": "Mechanism Outcomes",
        "turnout_chart_title": "Turnout Distribution",
        "shock_chart_title": "Outcome Sensitivity To Market Regime",
        "summary_chart_metrics": {
            "pass_rate": "Pass Rate",
            "false_positive_rate": "Bad Proposal Passes",
            "false_negative_rate": "Good Proposal Rejections",
            "whale_capture_rate": "Capture Flag Rate",
        },
        "passed_yes": "Passed",
        "passed_no": "Rejected",
        "shock_yes": "Shock",
        "shock_no": "No shock",
        "risk_severity": "Severity",
        "risk_action": "Action",
        "table_columns": {
            "label_display": "Mechanism",
            "pass_rate": "Pass Rate",
            "avg_turnout": "Avg Turnout",
            "avg_yes_share": "Avg Yes Share",
            "quorum_failure_rate": "Quorum Failure",
            "false_positive_rate": "Bad Proposal Passes",
            "false_negative_rate": "Good Proposal Rejections",
            "decisive_whale_rate": "Decisive Whale",
            "whale_capture_rate": "Capture Rate",
            "shock_flip_delta": "Shock Delta",
            "legitimacy_gap": "Legitimacy Gap",
            "resilience_score": "Resilience",
        },
        "agent_columns": {
            "agent_id": "Agent ID",
            "archetype_display": "Archetype",
            "voting_power": "Voting Power",
            "turnout_discipline": "Turnout Discipline",
            "manipulation_tendency": "Manipulation Tendency",
        },
    },
}

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

MODE_LABELS_ZH = {
    "template": "模板说明",
    "template_fallback": "模板回退",
    "live": "实时 AI",
}

VULNERABILITY_TITLES_ZH = {
    "Whale Capture Surface": "大户控票风险",
    "Toxic Proposal Passage Risk": "坏提案误通过风险",
    "Apathy And Quorum Fragility": "冷漠与流会风险",
    "Market Shock Sensitivity": "市场冲击敏感",
    "Mechanism Design Mismatch": "机制设计不匹配",
    "No Acute Governance Failure Mode": "未发现明显致命风险",
}


def copy_for(language: str) -> dict[str, object]:
    return UI_TEXT[language]


def translate_mechanism_label(label: str, language: str) -> str:
    if language == "中文":
        return MECHANISM_LABELS_ZH.get(label, label)
    return label


def translate_preset_options(options: list[str], mapping: dict[str, str], language: str) -> dict[str, str]:
    if language != "中文":
        return {option: option for option in options}
    return {mapping.get(option, option): option for option in options}


def localize_proposal_seed(key: str, seed: ProposalConfig, language: str) -> ProposalConfig:
    if language != "中文":
        return seed
    localization = PROPOSAL_LOCALIZATION_ZH.get(key, {})
    return seed.model_copy(
        update={
            "name": localization.get("name", seed.name),
            "summary": localization.get("summary", seed.summary),
        }
    )


def localize_environment_seed(key: str, seed: EnvironmentConfig, language: str) -> EnvironmentConfig:
    if language != "中文":
        return seed
    return seed.model_copy(update={"label": ENV_PRESET_LABELS_ZH.get(key, seed.label)})


def translate_environment_label(label: str, language: str) -> str:
    if language != "中文":
        return label
    suffix = " + HTX Calibration"
    if label.endswith(suffix):
        base = label[: -len(suffix)]
        return f"{ENV_PRESET_LABELS_ZH.get(base, base)} + HTX 校准"
    return ENV_PRESET_LABELS_ZH.get(label, label)


def translate_severity(severity: str, language: str) -> str:
    if language == "中文":
        return SEVERITY_LABELS_ZH.get(severity, severity)
    return severity.title()


def translate_ai_mode(mode: str, language: str) -> str:
    if language == "中文":
        return MODE_LABELS_ZH.get(mode, mode)
    return mode


def translate_archetype(archetype: str, language: str) -> str:
    if language == "中文":
        return ARCHETYPE_LABELS_ZH.get(archetype, archetype)
    return archetype.replace("_", " ").title()


def inject_styles() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Teko:wght@400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600&family=Noto+Sans+SC:wght@300;400;500;700&display=swap');

            :root {
                --bg-1: #08121d;
                --bg-2: #0f2331;
                --line: rgba(128, 198, 221, 0.24);
                --teal: #78e6d8;
                --amber: #ffb35c;
                --oxide: #ff7a45;
                --ink: #eff6fb;
                --muted: #91a6b6;
            }

            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(120, 230, 216, 0.10), transparent 30%),
                    radial-gradient(circle at bottom right, rgba(255, 122, 69, 0.12), transparent 28%),
                    linear-gradient(135deg, var(--bg-1) 0%, var(--bg-2) 48%, #081018 100%);
                color: var(--ink);
                font-family: "Noto Sans SC", "IBM Plex Sans", sans-serif;
            }

            .block-container {
                padding-top: 2rem;
                padding-bottom: 2.5rem;
            }

            h1, h2, h3 {
                font-family: "Teko", "Noto Sans SC", sans-serif !important;
                letter-spacing: 0.04em;
            }

            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, rgba(5, 14, 22, 0.96), rgba(10, 21, 33, 0.96));
                border-right: 1px solid var(--line);
            }

            .hero {
                background: linear-gradient(135deg, rgba(8, 18, 29, 0.86), rgba(9, 28, 40, 0.72));
                border: 1px solid rgba(120, 230, 216, 0.20);
                box-shadow: 0 24px 80px rgba(0, 0, 0, 0.28);
                border-radius: 24px;
                padding: 1.6rem 1.7rem 1.3rem;
                margin-bottom: 1rem;
                position: relative;
                overflow: hidden;
            }

            .hero::after {
                content: "";
                position: absolute;
                inset: auto -10% -40% 55%;
                height: 220px;
                background: radial-gradient(circle, rgba(255, 179, 92, 0.25), transparent 58%);
                transform: rotate(-12deg);
            }

            .eyebrow {
                color: var(--teal);
                font-size: 0.82rem;
                letter-spacing: 0.16em;
                text-transform: uppercase;
                margin-bottom: 0.35rem;
            }

            .hero-title {
                font-size: 4rem;
                line-height: 0.95;
                margin: 0;
            }

            .hero-copy {
                max-width: 58rem;
                color: var(--muted);
                font-size: 1rem;
                margin-top: 0.65rem;
            }

            .microgrid {
                display: grid;
                grid-template-columns: repeat(3, minmax(0, 1fr));
                gap: 0.9rem;
                margin-top: 1rem;
            }

            .microcard {
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 18px;
                padding: 0.85rem 1rem;
            }

            .microcard strong {
                color: var(--ink);
                font-size: 0.95rem;
            }

            .microcard span {
                display: block;
                color: var(--muted);
                font-size: 0.82rem;
                margin-top: 0.25rem;
                line-height: 1.55;
            }

            .section-tag {
                display: inline-block;
                color: var(--amber);
                border: 1px solid rgba(255, 179, 92, 0.26);
                border-radius: 999px;
                padding: 0.35rem 0.75rem;
                font-size: 0.76rem;
                letter-spacing: 0.12em;
                margin-bottom: 0.75rem;
            }

            .risk-card {
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 18px;
                padding: 1rem;
                min-height: 210px;
            }

            .risk-card h4 {
                margin: 0 0 0.45rem 0;
                font-family: "Teko", "Noto Sans SC", sans-serif;
                font-size: 1.8rem;
                letter-spacing: 0.04em;
            }

            .risk-card p {
                color: var(--muted);
                margin-bottom: 0.55rem;
                line-height: 1.58;
            }

            .severity-critical, .severity-high {
                border-color: rgba(255, 122, 69, 0.45);
                box-shadow: 0 0 0 1px rgba(255, 122, 69, 0.14) inset;
            }

            .severity-medium {
                border-color: rgba(255, 179, 92, 0.42);
            }

            .severity-low {
                border-color: rgba(120, 230, 216, 0.28);
            }

            div[data-testid="stMetric"] {
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 18px;
                padding: 0.8rem 1rem;
            }

            .captionline {
                color: var(--muted);
                font-size: 0.85rem;
                margin-top: 0.25rem;
                line-height: 1.5;
            }

            .summary-box {
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 18px;
                padding: 1rem 1.1rem;
            }

            .summary-box p {
                color: var(--muted);
                line-height: 1.65;
                margin: 0.35rem 0;
            }

            @media (max-width: 900px) {
                .hero-title {
                    font-size: 2.8rem;
                }

                .microgrid {
                    grid-template-columns: 1fr;
                }

                .risk-card {
                    min-height: auto;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_language_selector() -> str:
    if "ui_language" not in st.session_state:
        st.session_state["ui_language"] = "中文"
    st.sidebar.markdown("## 语言 / Language")
    return st.sidebar.selectbox(
        "界面语言 / Interface",
        LANGUAGE_OPTIONS,
        key="ui_language",
    )


def render_header(language: str) -> None:
    copy = copy_for(language)
    microcards = "".join(
        f"<div class='microcard'><strong>{title}</strong><span>{description}</span></div>"
        for title, description in copy["microcards"]
    )
    st.markdown(
        f"""
        <section class="hero">
            <div class="eyebrow">{copy['header_eyebrow']}</div>
            <h1 class="hero-title">{copy['hero_title']}</h1>
            <p class="hero-copy">{copy['hero_copy']}</p>
            <div class="microgrid">{microcards}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def localized_summary_df(summary_df: pd.DataFrame, language: str) -> pd.DataFrame:
    localized = summary_df.copy()
    localized["label_display"] = localized["label"].map(lambda label: translate_mechanism_label(label, language))
    return localized


def localized_records_df(records_df: pd.DataFrame, language: str) -> pd.DataFrame:
    localized = records_df.copy()
    localized["mechanism_label_display"] = localized["mechanism_label"].map(
        lambda label: translate_mechanism_label(label, language)
    )
    copy = copy_for(language)
    localized["passed_display"] = localized["passed"].map(
        lambda passed: copy["passed_yes"] if passed else copy["passed_no"]
    )
    localized["market_shock_display"] = localized["market_shock"].map(
        lambda shock: copy["shock_yes"] if shock else copy["shock_no"]
    )
    return localized


def vulnerability_copy(row: pd.Series, summary_df: pd.DataFrame, language: str) -> tuple[str, str, str, str]:
    title = str(row["title"])
    mechanism = row.get("mechanism")
    mechanism_row = pd.DataFrame()
    if isinstance(mechanism, str) and mechanism:
        mechanism_row = summary_df.loc[summary_df["label"] == mechanism]

    if language != "中文":
        return (
            title,
            translate_severity(str(row["severity"]), language),
            str(row["evidence"]),
            str(row["recommendation"]),
        )

    localized_title = VULNERABILITY_TITLES_ZH.get(title, title)
    severity = translate_severity(str(row["severity"]), language)
    mechanism_label = (
        translate_mechanism_label(str(mechanism), language) if isinstance(mechanism, str) and mechanism else "当前机制"
    )

    if title == "Whale Capture Surface" and not mechanism_row.empty:
        summary = mechanism_row.iloc[0]
        evidence = (
            f"{mechanism_label} 下，大户主导通过的比例是 {summary['whale_capture_rate']:.1%}，"
            f"其中关键一票由大户决定的比例是 {summary['decisive_whale_rate']:.1%}。"
        )
        recommendation = "建议给单钱包投票权加上限，或增加“参与人数通过门槛”，避免少数大户拍板。"
    elif title == "Toxic Proposal Passage Risk" and not mechanism_row.empty:
        summary = mechanism_row.iloc[0]
        evidence = f"{mechanism_label} 让“整体公共收益为负”的提案误通过的比例是 {summary['false_positive_rate']:.1%}。"
        recommendation = "对高耗资、低去中心化收益的提案，优先走更保守的投票路径，或者增加二次复核。"
    elif title == "Apathy And Quorum Fragility" and not mechanism_row.empty:
        summary = mechanism_row.iloc[0]
        evidence = (
            f"{mechanism_label} 的好提案误杀率是 {summary['false_negative_rate']:.1%}，"
            f"流会率是 {summary['quorum_failure_rate']:.1%}。"
        )
        recommendation = "可以考虑降低低风险提案门槛，或引入委托人激励，把散户参与率先拉起来。"
    elif title == "Market Shock Sensitivity" and not mechanism_row.empty:
        summary = mechanism_row.iloc[0]
        evidence = f"{mechanism_label} 在平稳与冲击行情之间的通过率摆动达到 {summary['shock_flip_delta']:.1%}。"
        recommendation = "对金库敏感提案增加冷静期，或者在大波动时要求二次确认。"
    elif title == "Mechanism Design Mismatch":
        divergence = summary_df["pass_rate"].max() - summary_df["pass_rate"].min()
        best_row = summary_df.iloc[0]
        worst_row = summary_df.iloc[-1]
        evidence = (
            f"同一提案在不同投票机制下，通过率相差 {divergence:.1%}。"
            f"{translate_mechanism_label(best_row['label'], language)} 明显比 "
            f"{translate_mechanism_label(worst_row['label'], language)} 更稳。"
        )
        recommendation = "不要默认所有提案都走同一治理流程，先用风洞决定应该配哪种机制。"
    else:
        evidence = "这次模拟里没有发现特别尖锐、会立刻把提案带翻的治理故障。"
        recommendation = "继续盯参与率和大户集中度即可，当前配置在演示场景下相对稳定。"

    return localized_title, severity, evidence, recommendation


def render_vulnerability_cards(vulnerabilities: pd.DataFrame, summary_df: pd.DataFrame, language: str) -> None:
    copy = copy_for(language)
    st.markdown(f"<div class='section-tag'>{copy['vulnerability_report']}</div>", unsafe_allow_html=True)
    columns = st.columns(max(1, len(vulnerabilities)))
    for column, (_, row) in zip(columns, vulnerabilities.iterrows()):
        title, severity, evidence, recommendation = vulnerability_copy(row, summary_df, language)
        with column:
            st.markdown(
                f"""
                <div class="risk-card severity-{row['severity']}">
                    <h4>{title}</h4>
                    <p><strong>{copy['risk_severity']}:</strong> {severity}</p>
                    <p>{evidence}</p>
                    <p><strong>{copy['risk_action']}:</strong> {recommendation}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def make_summary_chart(summary_df: pd.DataFrame, language: str) -> go.Figure:
    copy = copy_for(language)
    display_df = localized_summary_df(summary_df, language)
    melted = display_df.melt(
        id_vars=["label_display"],
        value_vars=["pass_rate", "false_positive_rate", "false_negative_rate", "whale_capture_rate"],
        var_name="metric",
        value_name="value",
    )
    metric_names = copy["summary_chart_metrics"]
    melted["metric"] = melted["metric"].map(metric_names)
    figure = px.bar(
        melted,
        x="label_display",
        y="value",
        color="metric",
        barmode="group",
        color_discrete_sequence=["#78e6d8", "#ff7a45", "#ffb35c", "#9ab4c4"],
    )
    figure.update_layout(
        title=str(copy["summary_chart_title"]),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend_title_text="",
        yaxis_tickformat=".0%",
        xaxis_title="",
        yaxis_title="",
        margin=dict(l=20, r=20, t=60, b=20),
    )
    return figure


def make_turnout_chart(records_df: pd.DataFrame, language: str) -> go.Figure:
    copy = copy_for(language)
    display_df = localized_records_df(records_df, language)
    figure = px.violin(
        display_df,
        x="mechanism_label_display",
        y="turnout_weight",
        color="mechanism_label_display",
        box=True,
        points=False,
        color_discrete_sequence=["#78e6d8", "#ffb35c", "#ff7a45"],
    )
    figure.update_layout(
        title=str(copy["turnout_chart_title"]),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        xaxis_title="",
        yaxis_title="",
        yaxis_tickformat=".0%",
        margin=dict(l=20, r=20, t=60, b=20),
    )
    return figure


def make_shock_chart(records_df: pd.DataFrame, language: str) -> go.Figure:
    copy = copy_for(language)
    display_df = localized_records_df(records_df, language)
    figure = px.scatter(
        display_df,
        x="market_return",
        y="yes_weight_share",
        color="passed_display",
        symbol="market_shock_display",
        facet_col="mechanism_label_display",
        color_discrete_map={
            str(copy["passed_yes"]): "#78e6d8",
            str(copy["passed_no"]): "#ff7a45",
        },
        opacity=0.65,
    )
    figure.update_layout(
        title=str(copy["shock_chart_title"]),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend_title_text="",
        xaxis_title="",
        yaxis_title="",
        margin=dict(l=20, r=20, t=60, b=20),
    )
    figure.update_yaxes(tickformat=".0%")
    figure.update_xaxes(tickformat=".0%")
    figure.for_each_annotation(lambda annotation: annotation.update(text=annotation.text.split("=")[-1]))
    return figure


def render_sidebar(language: str) -> dict[str, object]:
    copy = copy_for(language)
    proposal_map = proposal_presets()
    environment_map = environment_presets()

    proposal_options = translate_preset_options(list(proposal_map), PROPOSAL_PRESET_LABELS_ZH, language)
    environment_options = translate_preset_options(list(environment_map), ENV_PRESET_LABELS_ZH, language)

    st.sidebar.markdown(f"## {copy['scenario_controls']}")
    proposal_choice = st.sidebar.selectbox(str(copy["proposal_preset"]), list(proposal_options))
    proposal_key = proposal_options[proposal_choice]
    proposal_seed = localize_proposal_seed(proposal_key, proposal_map[proposal_key], language)

    environment_choice = st.sidebar.selectbox(str(copy["environment_preset"]), list(environment_options))
    environment_key = environment_options[environment_choice]
    environment_seed = localize_environment_seed(environment_key, environment_map[environment_key], language)

    run_count = st.sidebar.slider(str(copy["runs"]), min_value=100, max_value=2000, value=600, step=100)
    seed = st.sidebar.number_input(str(copy["seed"]), min_value=1, max_value=999_999, value=42, step=1)
    quorum = st.sidebar.slider(str(copy["quorum"]), min_value=0.05, max_value=0.60, value=0.28, step=0.01)
    approval_threshold = st.sidebar.slider(
        str(copy["approval_threshold"]), min_value=0.50, max_value=0.80, value=0.55, step=0.01
    )

    st.sidebar.markdown(f"## {copy['proposal_inputs']}")
    proposal = ProposalConfig(
        name=st.sidebar.text_input(str(copy["proposal_name"]), value=proposal_seed.name),
        category=proposal_seed.category,
        summary=st.sidebar.text_area(str(copy["proposal_thesis"]), value=proposal_seed.summary, height=90),
        treasury_request_pct=st.sidebar.slider(
            str(copy["treasury_request"]),
            0.0,
            0.50,
            float(proposal_seed.treasury_request_pct),
            0.01,
        ),
        expected_upside=st.sidebar.slider(
            str(copy["expected_upside"]), -0.20, 0.60, float(proposal_seed.expected_upside), 0.01
        ),
        execution_risk=st.sidebar.slider(
            str(copy["execution_risk"]), 0.0, 1.0, float(proposal_seed.execution_risk), 0.01
        ),
        decentralization_impact=st.sidebar.slider(
            str(copy["decentralization_impact"]),
            -0.60,
            0.60,
            float(proposal_seed.decentralization_impact),
            0.01,
        ),
        urgency=st.sidebar.slider(str(copy["urgency"]), 0.0, 1.0, float(proposal_seed.urgency), 0.01),
        proposer_reputation=st.sidebar.slider(
            str(copy["proposer_reputation"]), -0.50, 0.60, float(proposal_seed.proposer_reputation), 0.01
        ),
    )

    st.sidebar.markdown(f"## {copy['stress_inputs']}")
    environment = EnvironmentConfig(
        label=environment_seed.label,
        market_volatility=st.sidebar.slider(
            str(copy["market_volatility"]), 0.05, 0.60, float(environment_seed.market_volatility), 0.01
        ),
        negative_shock_probability=st.sidebar.slider(
            str(copy["shock_probability"]),
            0.0,
            0.80,
            float(environment_seed.negative_shock_probability),
            0.01,
        ),
        whale_coordination=st.sidebar.slider(
            str(copy["whale_coordination"]), 0.0, 1.0, float(environment_seed.whale_coordination), 0.01
        ),
        voter_apathy=st.sidebar.slider(
            str(copy["voter_apathy"]), 0.0, 1.0, float(environment_seed.voter_apathy), 0.01
        ),
        social_sentiment=st.sidebar.slider(
            str(copy["social_sentiment"]), -0.50, 0.50, float(environment_seed.social_sentiment), 0.01
        ),
        manipulation_pressure=st.sidebar.slider(
            str(copy["manipulation_pressure"]), 0.0, 1.0, float(environment_seed.manipulation_pressure), 0.01
        ),
        noise_scale=st.sidebar.slider(str(copy["noise_scale"]), 0.05, 0.40, float(environment_seed.noise_scale), 0.01),
    )

    use_htx_calibration = st.sidebar.toggle(str(copy["use_htx"]), value=True)
    use_live_explainer = st.sidebar.toggle(str(copy["use_live_ai"]), value=False)

    return {
        "proposal": proposal,
        "environment": environment,
        "run_count": int(run_count),
        "seed": int(seed),
        "quorum": float(quorum),
        "approval_threshold": float(approval_threshold),
        "use_htx_calibration": use_htx_calibration,
        "use_live_explainer": use_live_explainer,
    }


def render_executive_summary(
    proposal: ProposalConfig,
    effective_environment: EnvironmentConfig,
    result_runs: int,
    explanation: dict[str, str],
    summary_df: pd.DataFrame,
    vulnerabilities_df: pd.DataFrame,
    language: str,
) -> None:
    copy = copy_for(language)
    best_row = summary_df.iloc[0]
    worst_capture_row = summary_df.sort_values("whale_capture_rate", ascending=False).iloc[0]

    if language == "中文":
        top_risk = (
            VULNERABILITY_TITLES_ZH.get(str(vulnerabilities_df.iloc[0]["title"]), str(vulnerabilities_df.iloc[0]["title"]))
            if not vulnerabilities_df.empty
            else "未发现明显高风险"
        )
        summary_block = (
            f"<div class='summary-box'>"
            f"<p><strong>建议优先采用：</strong>{translate_mechanism_label(best_row['label'], language)}，"
            f"韧性分 {best_row['resilience_score']:.1f}。</p>"
            f"<p><strong>当前最危险点：</strong>{top_risk}。"
            f"{translate_mechanism_label(worst_capture_row['label'], language)} 的大户带票率为 "
            f"{worst_capture_row['whale_capture_rate']:.1%}。</p>"
            f"<p><strong>怎么理解这页：</strong>先看坏提案误通过，再看大户带票，最后看行情冲击会不会让结果翻转。</p>"
            f"</div>"
        )
    else:
        summary_block = (
            f"<div class='summary-box'>"
            f"<p><strong>Recommended path:</strong> {translate_mechanism_label(best_row['label'], language)} with a "
            f"resilience score of {best_row['resilience_score']:.1f}.</p>"
            f"<p><strong>Main risk:</strong> {translate_mechanism_label(worst_capture_row['label'], language)} has the "
            f"highest whale-capture rate at {worst_capture_row['whale_capture_rate']:.1%}.</p>"
            f"<p><strong>Reading guide:</strong> focus first on harmful proposal passes, then vote capture, then shock sensitivity.</p>"
            f"</div>"
        )

    st.markdown(f"<div class='section-tag'>{copy['executive_readout']}</div>", unsafe_allow_html=True)
    st.markdown(f"### {proposal.name}")
    st.write(proposal.summary)
    st.markdown(summary_block, unsafe_allow_html=True)
    if language == "中文" and explanation["mode"] == "live":
        st.markdown(explanation["summary"])
    elif language == "English":
        st.markdown(explanation["summary"])
    st.markdown(
        (
            f"<div class='captionline'>{copy['environment_label']}: {translate_environment_label(effective_environment.label, language)}"
            f" | {copy['ai_mode_label']}: {translate_ai_mode(explanation['mode'], language)}"
            f" | {copy['simulation_count']}: {result_runs}</div>"
        ),
        unsafe_allow_html=True,
    )


def localized_calibration_snapshot(snapshot: object, language: str) -> dict[str, object]:
    if language != "中文":
        return {
            "source": snapshot.source,
            "note": snapshot.note,
            "price_change_24h": round(snapshot.price_change_24h, 4),
            "volume_change_24h": round(snapshot.volume_change_24h, 4),
            "volatility_multiplier": round(snapshot.volatility_multiplier, 2),
        }
    return {
        "数据来源": "实时接口" if snapshot.source == "live" else "占位样本",
        "说明": "已根据 HTX 市场占位数据调整波动率与冲击概率。",
        "24h 价格变化": round(snapshot.price_change_24h, 4),
        "24h 成交量变化": round(snapshot.volume_change_24h, 4),
        "波动放大系数": round(snapshot.volatility_multiplier, 2),
    }


def main() -> None:
    inject_styles()
    language = render_language_selector()
    copy = copy_for(language)
    render_header(language)
    controls = render_sidebar(language)

    proposal: ProposalConfig = controls["proposal"]  # type: ignore[assignment]
    environment: EnvironmentConfig = controls["environment"]  # type: ignore[assignment]

    calibrator = HTXMarketCalibrator()
    market_snapshot = calibrator.fetch_snapshot() if controls["use_htx_calibration"] else None
    effective_environment = (
        calibrator.apply_to_environment(environment, market_snapshot)
        if market_snapshot is not None
        else environment
    )

    result = run_wind_tunnel(
        proposal=proposal,
        environment=effective_environment,
        run_count=controls["run_count"],  # type: ignore[arg-type]
        seed=controls["seed"],  # type: ignore[arg-type]
        mechanisms=build_default_mechanisms(
            quorum=controls["quorum"],  # type: ignore[arg-type]
            approval_threshold=controls["approval_threshold"],  # type: ignore[arg-type]
        ),
        market_context=market_snapshot.model_dump() if market_snapshot is not None else {},
    )

    explainer = GovernanceExplainer()
    explanation = explainer.explain(result, use_live_model=bool(controls["use_live_explainer"]))

    summary_df = result.summaries_frame()
    records_df = result.records_frame()
    vulnerabilities_df = result.vulnerabilities_frame()

    localized_summary = localized_summary_df(summary_df, language)
    best_mechanism = localized_summary.iloc[0]
    highest_pass = localized_summary.loc[localized_summary["pass_rate"].idxmax()]
    riskiest_mechanism = localized_summary.sort_values("whale_capture_rate", ascending=False).iloc[0]

    metrics = st.columns(4)
    metrics[0].metric(
        str(copy["best_mechanism"]),
        best_mechanism["label_display"],
        str(copy["best_mechanism_delta"]).format(score=best_mechanism["resilience_score"]),
    )
    metrics[1].metric(
        str(copy["highest_pass_rate"]),
        f"{localized_summary['pass_rate'].max():.1%}",
        str(copy["highest_pass_rate_delta"]).format(label=highest_pass["label_display"]),
    )
    metrics[2].metric(
        str(copy["capture_risk_peak"]),
        f"{riskiest_mechanism['whale_capture_rate']:.1%}",
        riskiest_mechanism["label_display"],
    )
    metrics[3].metric(
        str(copy["shock_delta"]),
        f"{localized_summary['shock_flip_delta'].max():.1%}",
        str(copy["shock_delta_delta"]),
    )

    context_columns = st.columns([1.15, 0.85])
    with context_columns[0]:
        render_executive_summary(
            proposal=proposal,
            effective_environment=effective_environment,
            result_runs=result.run_count,
            explanation=explanation,
            summary_df=summary_df,
            vulnerabilities_df=vulnerabilities_df,
            language=language,
        )
    with context_columns[1]:
        st.markdown(f"<div class='section-tag'>{copy['calibration']}</div>", unsafe_allow_html=True)
        if market_snapshot is None:
            st.info(str(copy["calibration_off"]))
        else:
            st.write(localized_calibration_snapshot(market_snapshot, language))

    render_vulnerability_cards(vulnerabilities_df, summary_df, language)

    charts = st.columns(2)
    with charts[0]:
        st.plotly_chart(make_summary_chart(summary_df, language), use_container_width=True)
    with charts[1]:
        st.plotly_chart(make_turnout_chart(records_df, language), use_container_width=True)

    st.plotly_chart(make_shock_chart(records_df, language), use_container_width=True)

    lower = st.columns([1.05, 0.95])
    with lower[0]:
        st.markdown(f"<div class='section-tag'>{copy['mechanism_table']}</div>", unsafe_allow_html=True)
        display_df = localized_summary.copy()
        display_df = display_df[
            [
                "label_display",
                "pass_rate",
                "avg_turnout",
                "avg_yes_share",
                "quorum_failure_rate",
                "false_positive_rate",
                "false_negative_rate",
                "decisive_whale_rate",
                "whale_capture_rate",
                "shock_flip_delta",
                "legitimacy_gap",
                "resilience_score",
            ]
        ]
        pct_columns = [
            "pass_rate",
            "avg_turnout",
            "avg_yes_share",
            "quorum_failure_rate",
            "false_positive_rate",
            "false_negative_rate",
            "decisive_whale_rate",
            "whale_capture_rate",
            "shock_flip_delta",
            "legitimacy_gap",
        ]
        for column in pct_columns:
            display_df[column] = display_df[column].map(lambda value: f"{value:.1%}")
        display_df["resilience_score"] = display_df["resilience_score"].map(lambda value: f"{value:.1f}")
        display_df = display_df.rename(columns=copy["table_columns"])
        st.dataframe(display_df, use_container_width=True, hide_index=True)

    with lower[1]:
        st.markdown(f"<div class='section-tag'>{copy['agent_composition']}</div>", unsafe_allow_html=True)
        agent_df = result.agent_frame()[
            ["agent_id", "archetype", "voting_power", "turnout_discipline", "manipulation_tendency"]
        ].copy()
        agent_df["archetype_display"] = agent_df["archetype"].map(lambda archetype: translate_archetype(archetype, language))
        agent_df["voting_power"] = agent_df["voting_power"].map(lambda value: f"{value:.1%}")
        agent_df["turnout_discipline"] = agent_df["turnout_discipline"].map(lambda value: f"{value:.0%}")
        agent_df["manipulation_tendency"] = agent_df["manipulation_tendency"].map(lambda value: f"{value:.0%}")
        agent_df = agent_df[
            ["agent_id", "archetype_display", "voting_power", "turnout_discipline", "manipulation_tendency"]
        ].rename(columns=copy["agent_columns"])
        st.dataframe(agent_df, use_container_width=True, hide_index=True)

    report_payload = json.dumps(result.to_report_dict(), indent=2, ensure_ascii=False)
    st.download_button(
        str(copy["download_report"]),
        data=report_payload,
        file_name="cybernetic_dao_wind_tunnel_report.json",
        mime="application/json",
    )

    sample_path = Path("sample_outputs/latest_report.json")
    sample_path.parent.mkdir(exist_ok=True)
    sample_path.write_text(report_payload, encoding="utf-8")


if __name__ == "__main__":
    main()
