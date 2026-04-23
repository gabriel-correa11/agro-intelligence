# Agro Intelligence — SLCE3 Climate Impact Dashboard

An interactive data analytics dashboard exploring the correlation between **climate variables** and the stock performance of **SLCE3 (SLC Agrícola)** on the Brazilian Stock Exchange (B3).

Built as part of a **Data Engineering & Business Intelligence academic project— 6th semester, Software Engineering.

---

## What it does

- Correlates meteorological data (temperature, rainfall, wind) from Sorriso, MT with SLCE3 daily stock price
- Calculates Pearson correlation coefficients to quantify climate impact on asset valuation
- Provides interactive visualizations across 4 pages: Market Overview, Climate Impact, Statistical Correlation, and Dataset Explorer
- Covers H1 2025 (January to June) — 122 trading sessions

## Tech Stack

| Layer | Tools |
|---|---|
| Data ingestion | `openpyxl` |
| Data processing | `pandas`, `numpy` |
| Statistics | `scipy.stats` |
| Visualization | `plotly` |
| Dashboard | `streamlit` |
| Containerization | `docker` |

---

## Running locally with Docker

Make sure you have [Docker](https://www.docker.com/products/docker-desktop) installed.

```bash
git clone https://github.com/gabriel-correa11/agro-intelligence.git
cd agro-intelligence
docker build -t agro-inteligente .
docker run -p 8501:8501 agro-inteligente
```

Open your browser at `http://localhost:8501`.

## Running locally without Docker

```bash
pip install -r requirements.txt
streamlit run dashboard.py
```

---

## Project structure

```
agro-intelligence/
├── dashboard.py        # Streamlit application
├── dados.xlsx          # Dataset (market + climate data)
├── Dockerfile          # Container definition
├── requirements.txt    # Python dependencies
└── README.md
```

---

## Dataset

- **Market data:** SLCE3 daily OHLCV, sourced via [brapi.dev](https://brapi.dev)
- **Climate data:** Temperature, rainfall, wind speed for Sorriso/MT, sourced via [Open-Meteo](https://open-meteo.com)
- **Period:** January 2, 2025 — June 30, 2025

---

## Academic context

This project was developed as a learning exercise in:
- Building data pipelines with Python
- Applying statistical analysis (Pearson correlation) to real-world datasets
- Designing interactive BI dashboards
- Containerizing applications with Docker

> **Note:** This is an academic project built for learning purposes. The analysis covers a single semester and a single asset — it is not financial advice.

---

## Author

**Gabriel Pires Pinheiro Correa**  
Software Engineering Student 
[LinkedIn](https://linkedin.com/in/gabriel-correa11) · [GitHub](https://github.com/gabriel-correa11)
