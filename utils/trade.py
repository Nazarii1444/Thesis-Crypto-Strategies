from utils.config import LONG, SHORT


class Trade:
    def __init__(self, trade_id, trade_type, invest_value, open_price, open_datetime):
        self.trade_id = trade_id  # autoincrement
        self.type = trade_type  # LONG or SHORT
        self.invest_value = invest_value  # how much we invest: e.g. 5$ or 10$
        self.open_price = open_price  # open price of a coin at the beginning
        self.open_datetime = open_datetime  # time of creating a trade
        self.size = self.invest_value / self.open_price  # size of a coin: if we buy a coin at price 140$ for 5$, then we buy 5 / 140 = 0,0357 coins
        self.close_price = None  # price when we closed trade
        self.close_datetime = None  # time when we closed trade
        self.trade_duration = None  # trade duration = close time - open time
        self.profit = None  # profit we got from this order
        self.portfolio_value_after = None  # portfolio value after this trade
        self.closed = False  # is trade is closed
        self.commissions = None  # how much we spend on commissions

        self.take_profit_percentage = 0.0221  # take profit percentage
        self.stop_loss_percentage = 0.03  # stop loss percentage

        self.take_profit_price = self.eval_take_profit_price()  # take profit price
        self.stop_loss_price = self.eval_stop_loss_price()  # stop loss price

        self.opening_commision = 0.001  # 0.1% - percentage of opening commission
        self.closing_commision = 0.001  # 0.1% - percentage of closing commission

    def close(self, close_price, close_datetime, cash):
        self.close_price = close_price
        self.close_datetime = close_datetime
        self.trade_duration = self.close_datetime - self.open_datetime

        if self.is_long():
            self.profit = (close_price - self.open_price) * self.size
        elif self.is_short():
            self.profit = (self.open_price - close_price) * self.size

        self.commissions = (self.opening_commision * self.invest_value) + (self.closing_commision * self.invest_value)
        self.profit -= self.commissions
        cash += self.profit + self.invest_value

        self.portfolio_value_after = cash
        self.closed = True

    def eval_take_profit_price(self):
        if self.is_long():
            return self.open_price * (1 + self.take_profit_percentage)
        elif self.is_short():
            return self.open_price * (1 - self.take_profit_percentage)

    def eval_stop_loss_price(self):
        if self.is_long():
            return self.open_price * (1 - self.take_profit_percentage)
        elif self.is_short():
            return self.open_price * (1 + self.stop_loss_percentage)

    def is_profitable(self):
        return self.profit > 0

    def is_long(self):
        return self.type == LONG

    def is_short(self):
        return self.type == SHORT

    def __str__(self):
        return (
            f"ID: {self.trade_id}, {self.type} "
            f"{(self.size if self.size is not None else 0.00):.2f} "
            f"({(self.invest_value if self.invest_value is not None else 0.00):.2f}$) at "
            f"{(self.open_price if self.open_price is not None else 0.00):.2f} "
            f"closed at {(self.close_price if self.close_price is not None else 0.00):.2f} "
            f"Dur: {self.trade_duration if self.trade_duration is not None else 'N/A'}, "
            f"Profit: {(self.profit if self.profit is not None else 0.00):.2f}, "
            f"Commision: {(self.commissions if self.commissions is not None else 0.00):.2f} "
            f"Port value after: {(self.portfolio_value_after if self.portfolio_value_after is not None else 0.00):.2f}"
        )
