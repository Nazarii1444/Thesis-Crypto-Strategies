from dataclasses import dataclass
from typing import List

from utils.config import LONG, SHORT


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


class AdditionalPosition:
    def __init__(self, trade_id, trade_type, invest_value, open_price, open_datetime, main=0):
        self.trade_id = trade_id  # autoincrement
        self.type = trade_type  # 'LONG' або 'SHORT'
        self.invest_value = invest_value  # how much we invest: 5$ or 10$
        self.open_price = open_price  # open price of coin
        self.open_datetime = open_datetime  # time of creating trade
        self.size = self.invest_value / self.open_price  # how much size of coin: if we buy coin that cost 140$ for 5$, then we buy 5 / 140 = 0,0357 amount of coin
        self.close_price = None  # price when we closed trade
        self.close_datetime = None  # time when we closed trade
        self.trade_duration = None  # trade duration = close time - open time
        self.profit = 0  # profit we got from this order
        self.portfolio_value_after = None  # how much will our portfolio weight after this trade
        self.closed = False
        self.opening_commission = 0.0005
        self.closing_commision = 0.0005
        self.max_drawdown = 50
        self.main = main

        self.additional_purchases: List[AdditionalPurchase] = [
            AdditionalPurchase(
                open_price, self.invest_value, -1,
                open_price * self.size * self.opening_commission,
                open_datetime
            )
        ]
        self.lot_size = 5  # must be in range(5, 101)
        self.lot_size_percentage = self.lot_size / 100

        self.atr_multiplier = 2.1
        self.atr_value = 0

        self.percentage_levels = self.eval_percentage_levels()
        self.start_percentage_levels = self.eval_percentage_levels()
        self.price_levels = self.eval_price_levels()

        self.percentage_to_win = 0.002

        self.commissions = open_price * self.size * self.opening_commission
        self.expected_price_to_exit = 0
        self.new_expected_price_to_exit = 0
        self.adjust_average_value()
        self.closing_commission_price = None
        self.total_size = self.size
        self.total_invested = invest_value
        self.average_price = open_price

        self.times_made_additional_purchase = 0
        self.min_purchase_level_index = 0

        self.trailing_stop = self.expected_price_to_exit
        self.highest_price_achieved = self.open_price
        self.was_passed = False

        self.take_profit = None
        self.stop_loss = None
        self.eval_tp_and_sl()

        self.max_profit_price_during_trade = open_price

    def eval_percentage_levels(self):
        return [4.6, 10.17, 16.46, 21.55, 26.63, 33.87, 43.1]
        # return [4, 8, 12, 18, 24, 31, 38, 43]
        # return list(round(i, 2) for i in accumulate([3, 6, 6, 7, 8, 9, 10]))
        # distribution = 'equal'
        # count_of_additional_purchases = 10 #(100 // self.lot_size) - 1
        # levels = []
        #
        # if distribution == 'equal':
        #     levels = [self.max_drawdown / count_of_additional_purchases for _ in range(1, count_of_additional_purchases)]
        #
        # elif distribution == 'logarithmic':
        #     levels = [math.log(i + 1) for i in range(1, count_of_additional_purchases + 1 - 8)]
        #     total = sum(levels)
        #     levels = [(level / total) * self.max_drawdown for level in levels]
        #
        # elif distribution == 'fibonacci':
        #     fib_seq = self.generate_fibonacci(count_of_additional_purchases)
        #     total = sum(fib_seq)
        #     levels = [(fib / total) * self.max_drawdown for fib in fib_seq]
        #
        # elif distribution == 'reverse':
        #     levels = [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]
        #
        # elif distribution == 'aggressive':
        #     levels = [2, 5, 2]#, 6, 6, 8, 10, 12, 14]
        #
        # levels = list(round(i, 2) for i in accumulate(levels))
        # return levels

    def update_levels_with_atr(self, atr):
        self.percentage_levels = [i + atr * self.atr_multiplier for i in self.start_percentage_levels]
        self.price_levels = self.eval_price_levels()

    def get_current_win_percentage(self, current_price):
        if self.type == LONG:
            return (current_price - self.average_price) / self.average_price * 100
        elif self.type == SHORT:
            return (self.average_price - current_price) / self.average_price * 100

    @staticmethod
    def generate_fibonacci(n):
        fib_seq = []
        a, b = 1, 1
        for _ in range(n):
            fib_seq.append(a)
            a, b = b, a + b
        return fib_seq

    def eval_price_levels(self):
        if self.type == LONG:
            return [round(self.open_price - (self.open_price * i / 100), 2) for i in self.percentage_levels]
        else:
            return [round(self.open_price + (self.open_price * i / 100), 2) for i in self.percentage_levels]

    def update_trailing_stop(self, current_price):
        if self.type == LONG:
            if current_price > self.highest_price_achieved:
                self.highest_price_achieved = current_price
            self.trailing_stop = self.highest_price_achieved * 0.975
        elif self.type == SHORT:
            if current_price < self.highest_price_achieved:
                self.highest_price_achieved = current_price
            self.trailing_stop = self.highest_price_achieved * 1.025

    def update_max_profit_price(self, current_price):
        if self.type == LONG:
            self.max_profit_price_during_trade = max(self.max_profit_price_during_trade, current_price)

        elif self.type == SHORT:
            self.max_profit_price_during_trade = min(self.max_profit_price_during_trade, current_price)

    def update_percentage_to_win(self):
        self.percentage_to_win *= 0.9

    def should_close_due_to_trailing_stop(self, current_price):
        if self.type == LONG and current_price <= self.trailing_stop and self.was_passed:
            return True
        elif self.type == SHORT and current_price >= self.trailing_stop and self.was_passed:
            return True
        return False

    def create_additional_purchase(self, open_price, invest_value, date):
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
        self.update_percentage_to_win()

        # _, idx = self.eval_index(open_price)
        # if idx > self.min_purchase_level_index:
        #     self.min_purchase_level_index = idx

    def adjust_average_value(self):
        total_spent_amount, total_size = 0, 0

        for purchase in self.additional_purchases:
            total_spent_amount += purchase.open_price * purchase.size
            total_size += purchase.size

        self.total_size = total_size
        self.average_price = total_spent_amount / total_size

        average_buy_price = ((total_spent_amount + self.commissions) / total_size)

        if self.type == LONG:
            self.expected_price_to_exit = average_buy_price * (1 + self.percentage_to_win)
            self.new_expected_price_to_exit = self.expected_price_to_exit
        elif self.type == SHORT:
            self.expected_price_to_exit = average_buy_price * (1 - self.percentage_to_win)
            self.new_expected_price_to_exit = self.expected_price_to_exit

    def update_percentage_levels(self, levels):
        self.percentage_levels = levels
        self.eval_price_levels()

    def update_expected_to_exit(self, atr_value):
        self.new_expected_price_to_exit = self.expected_price_to_exit + 2.5 * atr_value

    def should_create_additional_purchase(self, current_price):
        if self.times_made_additional_purchase >= len(self.price_levels) - 1:
            return False

        # print(f"PRICE LEVELS {self.price_levels}")

        _, idx = self.eval_index(current_price)
        return idx > self.min_purchase_level_index

    def eval_tp_and_sl(self):
        tp_percent = 0.2
        sl_percent = 0.4

        if self.type == LONG:
            self.take_profit = self.open_price * (1 + tp_percent / 100)
            self.stop_loss = self.open_price * (1 - sl_percent / 100)
        elif self.type == SHORT:
            self.stop_loss = self.open_price * (1 + sl_percent / 100)
            self.take_profit = self.open_price * (1 - tp_percent / 100)

    def has_to_be_closed(self, current_price):
        if self.type == LONG:
            return self.take_profit < current_price
        elif self.type == SHORT:
            return self.take_profit > current_price

    def has_to_be_closed_in_range(self, high, low):
        if self.type == LONG:
            return self.expected_price_to_exit < high
        elif self.type == SHORT:
            return self.expected_price_to_exit > low

    def eval_index(self, current_price):
        max_v, max_i = 0, 0
        if self.type == LONG:
            max_v, max_i = max([(value, index) for index, value in enumerate(self.price_levels) if
                                value <= current_price], key=lambda x: x[0])
        elif self.type == SHORT:
            filtered_levels = [(value, index) for index, value in enumerate(self.price_levels) if
                               value >= current_price]
            if not filtered_levels:
                return 0, 0
            else:
                max_v, max_i = min(
                    [(value, index) for index, value in enumerate(self.price_levels) if value >= current_price],
                    key=lambda x: x[0])
        return max_v, max_i

    def close(self, close_price, close_datetime, cash):
        self.close_price = close_price
        self.close_datetime = close_datetime
        self.trade_duration = self.close_datetime - self.open_datetime
        self.closing_commission_price = close_price * self.closing_commision * self.total_size
        self.commissions += self.closing_commission_price

        if self.type == LONG:
            self.profit = (close_price - self.average_price) * self.total_size
        elif self.type == SHORT:
            self.profit = (self.average_price - close_price) * self.total_size

        self.profit -= self.commissions
        cash += self.profit + self.total_invested
        self.portfolio_value_after = cash
        self.closed = True

    def is_profitable(self):
        return self.profit > 0

    def is_opened(self):
        return not self.closed

    def is_closed(self):
        return self.closed

    def is_long(self):
        return self.type == LONG

    def is_short(self):
        return self.type == SHORT

    def __repr__(self):
        trade_info = f"Trade ID: {self.trade_id}\n"
        trade_info += f"Type: {self.type}\n"
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
