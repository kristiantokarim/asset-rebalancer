from fastapi import FastAPI, HTTPException
from domain import Portfolio, Asset, Holding
from repository import PortfolioRepository
import yfinance as yf

app = FastAPI()
repo = PortfolioRepository()

@app.get("/portfolio")
def get_portfolio():
    return repo.load().to_dict()

@app.get("/market-data")
def get_market_data(tickers: str = "", currencies: str = ""):
    t_list = [t for t in tickers.split(",") if t]
    c_list = [c for c in currencies.split(",") if c]
    res = {"prices": {}, "fx": {}}
    for t in t_list:
        res["prices"][t] = yf.Ticker(t).fast_info['last_price']
    for c in c_list:
        if c != "USD":
            res["fx"][f"{c}USD=X"] = yf.Ticker(f"{c}USD=X").fast_info['last_price']
    return res

@app.post("/save")
def save_portfolio(data: dict):
    assets = [Asset(a['ticker'], a['target_percent'], [Holding(**h) for h in a['holdings']]) for a in data['assets']]
    portfolio = Portfolio(cash_balances=data['cash_balances'], assets=assets)
    repo.save(portfolio)
    return {"status": "success"}

@app.post("/trade")
def execute_trade(payload: dict):
    portfolio = repo.load()
    spent = 0.0
    for t in payload['trades']:
        asset = next(a for a in portfolio.assets if a.ticker == t['ticker'])
        new_sh = t['amount'] / t['price']
        
        found = False
        for h in asset.holdings:
            if h.account == t['account']: # FIXED: Dot notation for objects
                h.avg_price = (h.shares * h.avg_price + t['amount']) / (h.shares + new_sh)
                h.shares += new_sh
                found = True
        if not found:
            asset.holdings.append(Holding(t['account'], new_sh, t['price']))
        spent += t['amount']
    
    portfolio.cash_balances["USD"] -= spent
    repo.save(portfolio)
    return {"status": "success"}

@app.post("/rollback")
def rollback():
    if repo.rollback(): return {"status": "success"}
    raise HTTPException(status_code=400, detail="No backups found")
