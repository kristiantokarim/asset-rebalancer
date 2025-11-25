from dataclasses import dataclass, field, asdict
from typing import List, Dict

@dataclass
class Holding:
    account: str
    shares: float
    avg_price: float

@dataclass
class Asset:
    ticker: str
    target_percent: float
    holdings: List[Holding] = field(default_factory=list)

    @property
    def total_shares(self) -> float:
        return sum(h.shares for h in self.holdings)
    
    @property
    def cost_basis(self) -> float:
        return sum(h.shares * h.avg_price for h in self.holdings)

@dataclass
class Portfolio:
    cash_balances: Dict[str, float]
    assets: List[Asset] = field(default_factory=list)

    def to_dict(self):
        return {
            "cash_balances": self.cash_balances,
            "assets": [{"ticker": a.ticker, "target_percent": a.target_percent, 
                        "holdings": [asdict(h) for h in a.holdings]} for a in self.assets]
        }
