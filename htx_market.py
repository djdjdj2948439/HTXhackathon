from __future__ import annotations

import os
from typing import Any

import httpx
from pydantic import BaseModel, Field

from dao_wind_tunnel_core import EnvironmentConfig, clamp


class HTXMarketSnapshot(BaseModel):
    source: str = "synthetic"
    note: str = "Demo fallback snapshot."
    price_change_24h: float = 0.0
    volume_change_24h: float = 0.0
    volatility_multiplier: float = Field(1.0, ge=0.5, le=2.0)
    sentiment_shift: float = Field(0.0, ge=-0.5, le=0.5)
    shock_probability_shift: float = Field(0.0, ge=-0.25, le=0.25)
    raw_payload: dict[str, Any] = Field(default_factory=dict)


class HTXMarketCalibrator:
    def __init__(
        self,
        endpoint: str | None = None,
        timeout_seconds: float | None = None,
        use_sample_on_error: bool | None = None,
    ) -> None:
        self.endpoint = endpoint or os.getenv("HTX_MARKET_ENDPOINT")
        self.timeout_seconds = timeout_seconds or float(os.getenv("HTX_TIMEOUT_SECONDS", "4.0"))
        self.use_sample_on_error = (
            use_sample_on_error
            if use_sample_on_error is not None
            else os.getenv("HTX_USE_SAMPLE_ON_ERROR", "true").lower() == "true"
        )

    def fetch_snapshot(self) -> HTXMarketSnapshot:
        if not self.endpoint:
            return self._sample_snapshot("No HTX endpoint configured. Using built-in market stress placeholder.")

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.get(self.endpoint)
                response.raise_for_status()
            payload = response.json()
            price_change_24h = float(payload.get("price_change_24h", 0.0))
            volume_change_24h = float(payload.get("volume_change_24h", 0.0))
            volatility_multiplier = clamp(1.0 + abs(price_change_24h) * 1.2 + abs(volume_change_24h) * 0.15, 0.7, 1.9)
            sentiment_shift = clamp(price_change_24h * 0.55, -0.35, 0.35)
            shock_probability_shift = clamp(abs(min(price_change_24h, 0.0)) * 0.45, -0.1, 0.2)
            return HTXMarketSnapshot(
                source="live",
                note="Calibrated from HTX-compatible market endpoint.",
                price_change_24h=price_change_24h,
                volume_change_24h=volume_change_24h,
                volatility_multiplier=volatility_multiplier,
                sentiment_shift=sentiment_shift,
                shock_probability_shift=shock_probability_shift,
                raw_payload=payload,
            )
        except Exception as exc:  # noqa: BLE001
            if not self.use_sample_on_error:
                raise
            return self._sample_snapshot(f"HTX fetch failed: {exc}. Using fallback calibration.")

    def apply_to_environment(self, environment: EnvironmentConfig, snapshot: HTXMarketSnapshot) -> EnvironmentConfig:
        return environment.model_copy(
            update={
                "label": f"{environment.label} + HTX Calibration",
                "market_volatility": clamp(environment.market_volatility * snapshot.volatility_multiplier, 0.05, 0.65),
                "social_sentiment": clamp(environment.social_sentiment + snapshot.sentiment_shift, -1.0, 1.0),
                "negative_shock_probability": clamp(
                    environment.negative_shock_probability + snapshot.shock_probability_shift,
                    0.01,
                    0.75,
                ),
            }
        )

    def _sample_snapshot(self, note: str) -> HTXMarketSnapshot:
        return HTXMarketSnapshot(
            source="synthetic",
            note=note,
            price_change_24h=-0.032,
            volume_change_24h=0.14,
            volatility_multiplier=1.18,
            sentiment_shift=-0.06,
            shock_probability_shift=0.04,
        )
