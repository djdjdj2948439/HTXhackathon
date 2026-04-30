# Cybernetic DAO Wind Tunnel

AI-powered governance stress testing for DAO proposals.

Cybernetic DAO Wind Tunnel is a runnable MVP built for demo scenarios like the HTX Genesis Hackathon. Instead of shipping governance proposals straight into production, it simulates how they behave under whale coordination, voter apathy, market stress, and mechanism-design failure before execution.

## What This MVP Includes

- Python simulation engine with Monte Carlo governance runs
- Stochastic DAO environment with market shocks, apathy, and manipulation pressure
- Heterogeneous mock governance agents: whales, delegates, activists, treasury guards, speculators, and retail
- Voting mechanism comparison:
  - Token Weighted
  - Quadratic Voting
  - Shielded Hybrid
- Streamlit dashboard with interactive scenario controls and Plotly charts
- Vulnerability report with explainable findings
- Optional HTX market calibration placeholder
- Optional AI explainer placeholder with template fallback

## Project Structure

```text
.
├── app.py
├── dao_wind_tunnel_core.py
├── htx_market.py
├── ai_explainer.py
├── requirements.txt
├── README.md
├── .env.example
└── sample_outputs/
```

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The app does not require live APIs to work. If you do nothing else, it will run with:

- a built-in stochastic environment
- synthetic HTX calibration fallback data
- template-based AI explanations

## Vercel Deployment

This repo now includes a Vercel-compatible FastAPI entrypoint in [vercel_app.py](/Users/ruihansun/Desktop/htx/vercel_app.py) while keeping the richer Streamlit app for local demos in [app.py](/Users/ruihansun/Desktop/htx/app.py).

- Local Streamlit demo:
  `streamlit run app.py`
- Vercel deployment target:
  `vercel_app:app` via [pyproject.toml](/Users/ruihansun/Desktop/htx/pyproject.toml)

The deployed Vercel version keeps the core simulation engine, mechanism comparison, Chinese-first UI, and vulnerability reporting, but serves them through a FastAPI single-page app instead of Streamlit because Vercel natively supports ASGI/WSGI Python apps rather than long-running Streamlit servers.

## Optional Environment Variables

Copy `.env.example` to `.env` if you want to wire live placeholders.

### HTX Calibration Placeholder

- `HTX_MARKET_ENDPOINT`
- `HTX_TIMEOUT_SECONDS`
- `HTX_USE_SAMPLE_ON_ERROR`

Expected response shape from a compatible endpoint:

```json
{
  "price_change_24h": -0.032,
  "volume_change_24h": 0.14
}
```

### AI Explainer Placeholder

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `OPENAI_MODEL`
- `BAI_API_BASE`
- `BAI_API_KEY`
- `BAI_MODEL`

The app only attempts a live call if you enable the toggle in the UI. Otherwise it uses a deterministic explanation template.

## Demo Flow

1. Pick a proposal preset like `Aggressive Liquidity Mining` or `Treasury Diversification`.
2. Pick an environment preset like `Whale Raid` or `Bear Shock`.
3. Run 600-2000 Monte Carlo simulations.
4. Compare mechanism resilience, capture risk, and false-positive / false-negative rates.
5. Use the vulnerability report as the governance pre-flight check.

## Design Notes

- No smart contracts in v1
- No mandatory HTX dependency
- No mandatory LLM dependency
- No agent framework overhead
- Focused on being demo-ready, explainable, and stable

## Suggested Hackathon Positioning

> Cybernetic DAO Wind Tunnel helps HTX DAO and other Web3 ecosystems stress-test governance proposals before execution using stochastic environments and AI-driven governance agents.

## Sample Outputs

Generated example files live in [sample_outputs](/Users/ruihansun/Desktop/htx/sample_outputs).
