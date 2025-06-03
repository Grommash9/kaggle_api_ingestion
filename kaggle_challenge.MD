# 📊 Audience & Ads Insights Feed – Python Ingestion Challenge

---

## 🎯 High-Level Objective

Build a **Python 3.11 mini-service** that

1. **Fetches** latest data from Kaggle via the official API using data from the below urls. 
   Trending YouTube Video Statistics
   https://www.kaggle.com/datasets/datasnaek/youtube-new/data?select=GB_category_id.json
   https://www.kaggle.com/datasets/datasnaek/youtube-new/data?select=GBvideos.csv
2. **Transforms & graphs** raw files into a useful graph output.  

You own everything config, tests, logging, docs.

---

## ✅ Core Tasks

| Step | What we need |
|------|-----------------------------------------|
| **Dataset pull** | Use Kaggle REST auth. Download **only if the remote version is newer**. |
| **Transformation layer** | Parse CSV/JSON into a format that will be good for graphing.|
| **Graphing** | Plot the data into a useful graph output |
| **Testing** | Unit tests for logic, integration tests. |

---

## 🛠️ Technical Expectations

### Python best practices
* PEP 8
* Docstrings + type hints (pass **mypy**)
* **Structured JSON logging**

### Tooling & CI (lightweight)
| Tool | Purpose |
|------|---------|
| **pre-commit** | `black`, `isort` on every commit |
| **pytest -q** | Total runtime < 1 minute |

---

## 📦 Deliverables

1. **Source repo** with this README covering:
   * local setup (venv, Kaggle token)  
   * example usage & expected output
   * architecture decisions (short ADRs or bullet list)
2. **Automated test suite** – all green with `pytest`.
4. **Sample logs** from a successful run.

> No need for a UI, Kubernetes charts, or complex deployment scripts—we’re after **production-quality Python**, not infrastructure wizardry.
---

## 🔍 How We’ll Evaluate

| Area | Signals we look for |
|------|--------------------|
| **Code quality** | Clear, idiomatic, well-structured, SOLID, documented. |
| **Testing discipline** | High branch coverage, meaningful fixtures/mocks, fast run-time. |
| **Professional polish** | CI passes first time, comments and/or a README someone *wants* to read. |

---

## 🚀 Starting steps (local)

1. Get Kaggle API key

2. Set up venv
python -m venv .venv
pip install -r requirements.txt

3. Move kaggle.json → ~/.kaggle/kaggle.json
