import json, os, shutil, glob
from datetime import datetime
from domain import Portfolio, Asset, Holding

class PortfolioRepository:
    def __init__(self, file_path="portfolio.json"):
        self.file_path = file_path

    def load(self) -> Portfolio:
        if not os.path.exists(self.file_path):
            return Portfolio(cash_balances={"USD": 0.0, "JPY": 0.0, "SGD": 0.0, "IDR": 0.0})
        with open(self.file_path, "r") as f:
            data = json.load(f)
            assets = [Asset(a['ticker'], a['target_percent'], [Holding(**h) for h in a['holdings']]) for a in data.get('assets', [])]
            return Portfolio(cash_balances=data['cash_balances'], assets=assets)

    def save(self, portfolio: Portfolio):
        if os.path.exists(self.file_path):
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            shutil.copy(self.file_path, f"backup_portfolio_{ts}.json")
        with open(self.file_path, "w") as f:
            json.dump(portfolio.to_dict(), f, indent=4)

    def rollback(self):
        backups = sorted(glob.glob("backup_portfolio_*.json"), reverse=True)
        if backups:
            shutil.copy(backups[0], self.file_path)
            os.remove(backups[0])
            return True
        return False
