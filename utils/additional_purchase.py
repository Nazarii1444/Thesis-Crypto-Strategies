from dataclasses import dataclass


@dataclass
class AdditionalPurchase:
    open_price: float
    invest_value: float
    purchase_number: int
    commission: float
    date: str

    def __post_init__(self):
        self.size = self.invest_value / self.open_price

    def __str__(self):
        return (f"Purchase #{self.purchase_number} at {self.date}: "
                f"price: {self.open_price:.2f}, "
                f"invested: {self.invest_value:.2f}$, "
                f"size: {self.size:.6f}, "
                f"commission: {self.commission:.4f}$")
