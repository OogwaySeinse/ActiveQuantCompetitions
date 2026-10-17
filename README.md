# 📈 Active Quant Competitions (`WUNDERQUANT // QUANT ARENA`)

> **Live, daily-updated index and interactive dashboard of active Quantitative Finance, Algorithmic Trading, Limit Order Book, Alpha Research, and Financial ML competitions** — inspired by [QuantBender Quant Contests](https://quantbender.github.io/quant-contests/) and architected after [ActiveMLCompetitions](https://github.com/OogwaySeinse/ActiveMLCompetitions).

[![Daily Quant Competitions Update & Deploy](https://github.com/OogwaySeinse/ActiveQuantCompetitions/actions/workflows/daily-update.yml/badge.svg)](https://github.com/OogwaySeinse/ActiveQuantCompetitions/actions/workflows/daily-update.yml)

---

## ✨ Key Capabilities

1. **13 Automated Multi-Source Quant Scrapers (`scraper/sources/`)**:
   - **Numerai GraphQL API** (`numerai.py`): Live round telemetry for *Numerai Classic*, *Numerai Signals*, and *Numerai Crypto* (`$112,000+` annualized NMR staking pools).
   - **CrunchDAO Hub API** (`crunchdao.py`): Live decentralized quantitative finance competitions including the *ADIA Lab Structural Break Challenge: Real-Time Edition* (`100,000 $USDC`), *DataCrunch Equity Market Neutral #2* (`1,000 $USDC/week`), *Synth: Synthetic Price Data* (`30k $USDC`), *BTC Implied Volatility (Deribit DVOL)*, and *Xentiment* (automatically filtering out non-financial biomedical challenges).
   - **ENS Challenge Data (`challengedata.ens.fr`)** (`ens.py`): Quantitative hedge fund & financial regulator challenges sponsored by **QRT (Qube Research & Technologies)**, **CFM (Capital Fund Management)**, **Autorité des Marchés Financiers (AMF)**, **Natixis**, **BNP Paribas**, **Crédit Agricole Assurances**, **Generali**, **Napoleon X**, and **Institut Louis Bachelier**.
   - **Jane Street Monthly Quant Puzzles** (`janestreet.py`): Live active monthly probability, combinatorics, and quantitative trading brainteaser.
   - **QuantContests & Prop-Trading Arenas** (`quantcontests.py`): Direct sync with [QuantBender/quant-contests](https://quantbender.github.io/quant-contests/) plus flagship prop-trading and university arenas (**WorldQuant BRAIN Alpha Research & IQC**, **Wunder Fund Connectome Limit Order Book Prediction**, **IMC Prosperity**, **Citadel & Citadel Securities Data Open**, **Optiver Ready Trader Go**, **QuantConnect Quant League**, **Algogene**, **Rotman RITC**, **UChicago Trading Competition**, **CMU MSCF**, **Bloomberg Global Trading Challenge**, **CME Group Futures Challenge**, **The5ers**, **G-Research**, **FMWC / MEWC**, **CFA Institute**, **McGill MIPC**, **NIBC**, **Harvard GCCH**).
   - **General ML Platforms with Strict Quant Domain Filtering** (`kaggle.py`, `zindi.py`, `drivendata.py`, `aicrowd.py`, `codalab.py`, `devpost.py`, `tianchi.py`, `mlcontests.py`): Filtered through `is_quant_competition()` to capture genuine financial ML, crypto/DeFi, order-book, actuarial, credit risk, and econometric competitions while excluding biomedical, gaming, and non-financial false positives.

2. **9-Category Quantitative Domain Taxonomy (`scraper/normalize.py`)**:
   - `Alpha & Equity Prediction`
   - `Market Microstructure & HFT`
   - `Algorithmic & Prop Trading`
   - `Crypto, DeFi & Digital Assets`
   - `Macro, Commodities & Derivatives`
   - `Credit, Risk & Insurance`
   - `Financial NLP & Sentiment`
   - `Valuation, Portfolio & Case Arenas`
   - `Time Series & Econometrics`

3. **Wunderquant Interactive Dashboard (`apps/dashboard/`)**:
   - Built with **React 18 + Vite 6 + TypeScript + Tailwind CSS v4 + TanStack Table v8 + Recharts**.
   - **Drifting Stochastic Calculus & Order-Book ASCII Backdrop** (`AsciiBackdrop.tsx`).
   - **Gemini 3.8 Flash Quant Strategy Matchmaker** (`AiRecommender.tsx` + `recommender.ts`): Includes 1-click Quant Researcher Archetype presets (*Cross-Sectional Equity Alpha*, *HFT & Limit Order Book Modeler*, *Crypto, Volatility & Derivatives*, *University Trading & Valuation League*) and collapsible **4-Phase Walk-Forward Backtesting Roadmaps** (Purged/Embargo CV, OFI/Factor Engineering, Era-Boosted Ensembling, and Turnover/Neutralization Optimization).
   - **Rolling Alpha Tournaments vs. Fixed-Deadline Arenas vs. Archive Benchmarks**: Toggle `♾️ Archive Benchmarks` to inspect historical 2019–2025 ENS Challenge Data hedge fund datasets alongside live 2026–2027 competitions.

---

## 🚀 Quickstart

### 1. Run the Python Scraper Pipeline & Tests
```bash
pip install -r requirements.txt
pytest -v
python -m scraper
```
Outputs are written to:
- `data/competitions.json`
- `data/competitions.csv`
- `apps/dashboard/public/data/competitions.json`
- `apps/dashboard/public/data/competitions.csv`

### 2. Run the React Dashboard Locally
```bash
cd apps/dashboard
npm install
npm run dev
```

### 3. Build for Production (GitHub Pages)
```bash
cd apps/dashboard
npm run build
```

