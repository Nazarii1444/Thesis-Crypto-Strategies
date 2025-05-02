from dataclasses import dataclass
from datetime import datetime
from typing import List

LONG, SHORT = 'LONG', 'SHORT'


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
                f" - price: {self.open_price:.2f}\n"
                f" - invested: {self.invest_value:.2f}$\n"
                f" - size: {self.size:.6f}\n"
                f" - commission: {self.commission:.4f}$\n")


class AdditionalTrade:
    def __init__(self, trade_type, size, open_price, open_datetime):
        self.type = trade_type
        self.size = size  # how much size of coin: if we buy coin that cost 140$ for 5$, then we buy 5 / 140 = 0,0357 amount of coin
        self.open_price = open_price  # open price of coin

        self.invest_value = size * open_price  # how much we invest: 5$ or 10$
        self.open_datetime = open_datetime  # time of creating trade
        self.close_price = None  # price when we closed trade
        self.close_datetime = None  # time when we closed trade
        self.trade_duration = None  # trade duration = close time - open time
        self.profit = 0  # profit we got from this order
        self.portfolio_value_after = None  # how much will our portfolio weight after this trade
        self.closed = False
        self.opening_commission = 0.001
        self.closing_commision = 0.001

        self.additional_purchases: List[AdditionalPurchase] = [
            AdditionalPurchase(
                open_price, self.invest_value, -1,
                open_price * self.size * self.opening_commission,
                open_datetime
            )
        ]

        self.percentage_levels = self.eval_percentage_levels()
        self.price_levels = self.eval_price_levels()

        self.percentage_to_win = 0.01

        self.commissions = open_price * self.size * self.opening_commission
        self.expected_price_to_exit = 0
        self.adjust_average_value()
        self.closing_commission_price = None

        self.total_size = self.size
        self.total_invested = self.invest_value
        self.average_price = open_price

        self.times_made_additional_purchase = 0
        self.min_purchase_level_index = 0

    def increment_times(self):
        self.times_made_additional_purchase += 1

    @staticmethod
    def eval_percentage_levels():
        return [4.6, 10.17, 16.46, 21.55, 26.63, 33.87, 43.1]

    def eval_price_levels(self):
        return [round(self.open_price - (self.open_price * i / 100), 2) for i in self.percentage_levels]

    def create_additional_purchase(self, open_price, invest_value):
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        new_purchase = AdditionalPurchase(
            open_price, invest_value,
            self.times_made_additional_purchase, self.opening_commission * self.invest_value,
            date
        )
        self.commissions += invest_value * self.opening_commission
        self.additional_purchases.append(new_purchase)
        self.times_made_additional_purchase += 1
        self.total_invested += invest_value
        self.adjust_average_value()

        _, idx = self.eval_index(open_price)
        if idx > self.min_purchase_level_index:
            self.min_purchase_level_index = idx

    def adjust_average_value(self):
        total_spent_amount, total_size = 0, 0

        for purchase in self.additional_purchases:
            total_spent_amount += purchase.open_price * purchase.size
            total_size += purchase.size

        self.total_size = total_size
        self.average_price = total_spent_amount / total_size

        average_buy_price = ((total_spent_amount + self.commissions) / total_size)

        # if self.type == LONG:
        self.expected_price_to_exit = average_buy_price * (1 + self.percentage_to_win)
        # elif self.type == SHORT:
        #     self.expected_price_to_exit = average_buy_price * (1 - self.percentage_to_win)

    def should_create_additional_purchase(self, current_price):
        if self.times_made_additional_purchase >= len(self.price_levels) - 1:
            return False

        _, idx = self.eval_index(current_price)
        return idx > self.min_purchase_level_index

    def eval_index(self, current_price):
        # max_v, max_i = 0, 0
        # if self.type == LONG:
        max_v, max_i = max(
            [(value, index) for index, value in enumerate(self.price_levels) if value <= current_price],
            key=lambda x: x[0])
        # elif self.type == SHORT:
        #     filtered_levels = [(value, index) for index, value in enumerate(self.price_levels) if
        #                        value >= current_price]
        #     if not filtered_levels:
        #         return 0, 0
        #     else:
        #         max_v, max_i = min(
        #             [(value, index) for index, value in enumerate(self.price_levels) if value >= current_price],
        #             key=lambda x: x[0])
        return max_v, max_i

    def __repr__(self):
        trade_info = f"Type: {self.type}\n"
        trade_info += f"Total Size: {self.total_size:.6f}\n" if self.total_size is not None else "Total Size: N/A\n"
        trade_info += f"Total Invested: {sum(p.invest_value for p in self.additional_purchases):.2f}$\n"
        trade_info += f"Average Price: {self.average_price:.2f}\n" if self.average_price is not None else "Average Price: N/A\n"
        trade_info += f"Closed at: {self.close_price:.2f}\n" if self.close_price is not None else "Closed at: N/A\n"
        trade_info += f"Duration: {self.trade_duration}\n" if self.trade_duration is not None else "Duration: N/A\n"
        trade_info += f"Profit: {self.profit:.2f}$\n" if self.profit is not None else "Profit: N/A\n"
        trade_info += f"Commission: {self.commissions:.2f}$\n" if self.commissions is not None else "Commission: N/A\n"
        trade_info += f"Portfolio Value After: {self.portfolio_value_after:.2f}$\n" if self.portfolio_value_after is not None else "Portfolio Value After: N/A\n"
        trade_info += "Additional Purchases:"
        for purchase in self.additional_purchases:
            trade_info += f"\n  - {purchase}"
        return trade_info
