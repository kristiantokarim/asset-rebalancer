# Asset Rebalancer

A full-stack, professional portfolio management and automated rebalancing tool. This project is built using a **Clean Architecture** approach, separating a **FastAPI Backend** from a **Streamlit Frontend**.

## Background

Maintaining a target asset allocation is the most important factor in long-term investment success. However, manually calculating how many shares to buy across multiple brokerage accounts and currencies is error-prone and tedious.

## What can you do with this Rebalancer?

Unlike a simple spreadsheet, this tool provides an automated workflow to keep your portfolio on track:

* **Multi-Currency Consolidation:** Automatically fetches live FX rates to convert JPY, SGD, or IDR cash balances into USD, giving you a true "Total Net Worth" view.
* **Live Market Valuation:** Connects to Yahoo Finance to provide real-time pricing for your stocks, ETFs, and Crypto.
* **Gap Analysis:** Instantly identifies which assets are "Underweight" compared to your target percentages.
* **Smart Cash Deployment:** Use a slider to decide how much cash you want to invest. The rebalancer calculates a "Pro-Rata" distribution, prioritizing the assets that have drifted furthest from their targets.
* **Multi-Account Management:** Track holdings for the same ticker across different brokers (e.g., IBKR vs. Schwab) and choose which account to "fund" during a rebalance.
* **Automated Bookkeeping:** When you click "Execute," the tool:
  1. Updates your share counts.
  2. Recalculates your new average cost basis.
  3. Deducts the exact amount from your USD cash balance.
  4. Creates a timestamped backup of your data for safety.

## Technical Architecture (SOLID)

This repository follows **Clean Architecture** and **SOLID** principles:

* **Domain Layer:** Pure Python dataclasses representing the "Enterprise Logic."
* **Service Layer:** Business rules for rebalancing and trade execution.
* **Repository Layer:** Handles data persistence (JSON) and automatic backups.
* **API Layer (FastAPI):** A RESTful interface for the frontend to consume data.
* **Presentation Layer (Streamlit):** A reactive, web-based dashboard for the end-user.

---

## Getting Started

### 1. Prerequisites

Ensure you have Python 3.9+ installed. Install the required dependencies:

```bash
pip install -r requirements.txt
```

### 2. Prepare Your Initial Data

Before running the app, you **must** create a file named `portfolio.json` in the root directory. This acts as your initial database. Use the template in portfolio.example.json below:

### 3. Running the Application

You need to run the Backend and Frontend simultaneously.

**Terminal 1: Start Backend (API)**

```bash
uvicorn backend:app --reload --port 8000
```

**Terminal 2: Start Frontend (UI)**

```bash
streamlit run app.py
```

---

## Planned Future Features

* [ ] **Historical Performance:** Track Net Worth over time using a time-series database.
* [ ] **Transaction Log:** A "ledger" view to see every trade executed through the app.
* [ ] **Dark Mode UI:** Enhanced visual themes for the dashboard.
* [ ] Move configurable variable to .env

## Rollback & Safety

Every time a trade is executed, the Backend creates a timestamped backup (e.g., `backup_portfolio_20231027.json`). If a mistake is made, simply click the **Rollback** button in the Sidebar to revert to the previous state.

---

**Disclaimer:** *This tool is for informational purposes only. It does not execute real trades on any exchange. Always verify your numbers before placing real orders with your broker.*
