from __future__ import annotations

import os
from typing import Any

import httpx

from dao_wind_tunnel_core import WindTunnelResult


class GovernanceExplainer:
    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        timeout_seconds: float = 12.0,
    ) -> None:
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL") or os.getenv("BAI_API_BASE")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("BAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL") or os.getenv("BAI_MODEL") or "placeholder-governance-analyst"
        self.timeout_seconds = timeout_seconds

    def explain(self, result: WindTunnelResult, use_live_model: bool = False) -> dict[str, Any]:
        summary_table = result.summaries_frame()
        best = summary_table.iloc[0]
        worst = summary_table.iloc[-1]
        template_summary = (
            f"{best['label']} is the strongest mechanism in this run with a resilience score of "
            f"{best['resilience_score']:.1f}. {worst['label']} is the weakest and is most exposed to the current stress mix."
        )
        vulnerability_lines = [
            f"{item.severity.title()}: {item.title} - {item.evidence}" for item in result.vulnerabilities[:3]
        ]
        payload = {
            "mode": "template",
            "summary": template_summary,
            "vulnerabilities": vulnerability_lines,
            "next_steps": [
                "Review proposals with high treasury draw and negative decentralization impact under at least two mechanisms.",
                "Use the vulnerability report to justify pre-vote guardrails instead of changing governance live.",
            ],
        }

        if not use_live_model or not self.base_url or not self.api_key:
            return payload

        try:
            prompt = self._build_prompt(result)
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(
                    f"{self.base_url.rstrip('/')}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You explain DAO governance stress tests in concise, plain English.",
                            },
                            {"role": "user", "content": prompt},
                        ],
                        "temperature": 0.2,
                    },
                )
                response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            return {
                "mode": "live",
                "summary": content,
                "vulnerabilities": vulnerability_lines,
                "next_steps": payload["next_steps"],
            }
        except Exception as exc:  # noqa: BLE001
            payload["mode"] = "template_fallback"
            payload["summary"] = f"{template_summary} Live explainer fallback triggered: {exc}"
            return payload

    def _build_prompt(self, result: WindTunnelResult) -> str:
        top_summary = result.summaries_frame().head(3).to_dict(orient="records")
        return (
            "Summarize this DAO governance wind tunnel result in under 180 words. "
            "Highlight the most resilient mechanism, the biggest vulnerability, and one concrete mitigation.\n\n"
            f"Proposal: {result.proposal.model_dump_json(indent=2)}\n"
            f"Environment: {result.environment.model_dump_json(indent=2)}\n"
            f"Summaries: {top_summary}\n"
            f"Vulnerabilities: {[item.model_dump() for item in result.vulnerabilities]}"
        )
