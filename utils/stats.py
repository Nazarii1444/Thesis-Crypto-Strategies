import csv
from datetime import timedelta

import pandas as pd


class Stats:
    def __init__(self, initial_cash: float, lot_percentage: float, trades):
        self.initial_cash = initial_cash
        self.lot_percentage = lot_percentage
        self.trades = []
        self.cash = initial_cash
        self.profitable_trades_count = 0
        self.total_trade_duration = timedelta(0)
        self.longest_trade_duration = timedelta(0)
        self.shortest_trade_duration = None
        self.long_trades = 0
        self.short_trades = 0
        self.successful_long_trades = 0
        self.successful_short_trades = 0
        self.unsuccessful_long_trades = 0
        self.unsuccessful_short_trades = 0
        self.profit = 0
        self.average_trade_return = None
        self.average_trade_duration = None
        self.longest_trade_duration_str = None
        self.shortest_trade_duration_str = None
        self.profitable_return = None
        self.loss_return = None
        self.return_ = None
        self.net_return = None
        self.total_trades = 0

        self.process_trades(trades)
        self.calculate_statistics()

        self.statistics = {
            'initial_cash': self.initial_cash,
            'lot_percentage': self.lot_percentage,
            'cash': self.cash,
            'profitable_trades_count': self.profitable_trades_count,
            'total_trade_duration': self.total_trade_duration,
            'longest_trade_duration': self.longest_trade_duration,
            'shortest_trade_duration': self.shortest_trade_duration,
            'long_trades': self.long_trades,
            'short_trades': self.short_trades,
            'successful_long_trades': self.successful_long_trades,
            'successful_short_trades': self.successful_short_trades,
            'unsuccessful_long_trades': self.unsuccessful_long_trades,
            'unsuccessful_short_trades': self.unsuccessful_short_trades,
            'profit': self.profit,
            'average_trade_return': self.average_trade_return,
            'average_trade_duration': self.average_trade_duration,
            'longest_trade_duration_str': self.longest_trade_duration_str,
            'shortest_trade_duration_str': self.shortest_trade_duration_str,
            'profitable_return': self.profitable_return,
            'loss_return': self.loss_return,
            'return_': self.return_,
            'net_return': self.net_return
        }

    def process_trades(self, trades):
        for trade in trades:
            self.add_trade(trade)

    def add_trade(self, trade):
        self.trades.append(trade)

        if trade.closed:

            if trade.is_long():
                self.long_trades += 1
                if trade.is_profitable():
                    self.successful_long_trades += 1
                else:
                    self.unsuccessful_long_trades += 1

            elif trade.is_short():
                self.short_trades += 1
                if trade.is_profitable():
                    self.successful_short_trades += 1
                else:
                    self.unsuccessful_short_trades += 1

            if trade.is_profitable():
                self.profitable_trades_count += 1

            self.cash = trade.portfolio_value_after

            if trade.trade_duration is not None:
                self.total_trade_duration += trade.trade_duration

                if trade.trade_duration > self.longest_trade_duration:
                    self.longest_trade_duration = trade.trade_duration

                if self.shortest_trade_duration is None or trade.trade_duration < self.shortest_trade_duration:
                    self.shortest_trade_duration = trade.trade_duration

        else:
            self.profitable_trades_count += 1

    def calculate_statistics(self):
        total_trades = len(self.trades)
        if total_trades == 0:
            print("No trades")
            return

        if self.cash is None:
            self.cash = self.initial_cash

        percentage_profitable = round((self.profitable_trades_count / total_trades) * 100, 3)
        self.average_trade_return = round((self.cash - self.initial_cash) / total_trades, 3)
        initial_amount_in_dollars = self.initial_cash * self.lot_percentage / 100

        self.average_trade_duration = self.total_trade_duration / total_trades if total_trades > 0 else timedelta(0)

        self.longest_trade_duration_str = str(self.longest_trade_duration) if self.longest_trade_duration else "N/A"
        self.shortest_trade_duration_str = str(self.shortest_trade_duration) if self.shortest_trade_duration else "N/A"

        self.profitable_return = 0
        self.loss_return = 0

        for trade in self.trades:
            if trade.closed:
                if trade.is_profitable():
                    self.profitable_return += trade.profit
                else:
                    self.loss_return += trade.profit

        self.profit = self.profitable_return + self.loss_return
        after_trades = self.initial_cash + self.profit
        self.return_ = self.profit / self.initial_cash * 100
        self.net_return = self.cash - self.initial_cash
        self.successful_trades = self.successful_short_trades + self.successful_long_trades
        self.unsuccessful_trades = self.unsuccessful_short_trades + self.unsuccessful_long_trades

        print(f"""Initial cash: {self.initial_cash}
Lot %: {self.lot_percentage * 100}% or {initial_amount_in_dollars * 100}$ from {self.initial_cash}$
Total trades: {self.total_trades}
Profitable trades: {self.profitable_trades_count}
Percentage of profitable trades: {percentage_profitable:.2f}%
Portfolio value after trades: {after_trades:.2f}$
Return: {self.return_:.2f}%
================================================
Average trade return: {self.average_trade_return:.2f}$
Average trade duration: {self.average_trade_duration}
Longest trade duration: {self.longest_trade_duration_str}
Shortest trade duration: {self.shortest_trade_duration_str}
================================================
Total LONG trades: {self.long_trades}
Successful LONG trades: {self.successful_long_trades}
Unsuccessful LONG trades: {self.unsuccessful_long_trades}
================================================
Total SHORT trades: {self.short_trades}
Successful SHORT trades: {self.successful_short_trades}
Unsuccessful SHORT trades: {self.unsuccessful_short_trades}
================================================
Total profit from profitable trades: {self.profitable_return:.2f}$
Total loss from unprofitable trades: {self.loss_return:.2f}$
Net return: {self.net_return:.2f}$
Ex: {round((percentage_profitable / 100 * (self.profitable_return / self.successful_trades) + (self.profitable_return / self.unsuccessful_trades) * (100 - percentage_profitable) / 100), 3)}
""")

    def export_trades(self, trades_file_path: str, stats_file_path: str):
        with open(trades_file_path, mode='w', newline='', encoding='utf-8') as trades_file:
            trades_writer = csv.writer(trades_file)
            trades_writer.writerow([
                "Trade ID", "Type", "Total Size", "Total Invested", "Average Price",
                "Closed at", "Duration", "Profit", "Commission", "Portfolio Value After"
            ])

            for trade in self.trades:
                trades_writer.writerow([
                    trade.trade_id,
                    trade.type,
                    f"{trade.total_size:.6f}" if trade.total_size else "N/A",
                    f"{sum(p.invest_value for p in trade.additional_purchases):.2f}",
                    f"{trade.average_price:.2f}" if trade.average_price else "N/A",
                    f"{trade.close_price:.2f}" if trade.close_price else "N/A",
                    trade.trade_duration if trade.trade_duration else "N/A",
                    f"{trade.profit:.2f}" if trade.profit else "N/A",
                    f"{trade.commissions:.2f}" if trade.commissions else "N/A",
                    f"{trade.portfolio_value_after:.2f}" if trade.portfolio_value_after else "N/A",
                ])

        with open(stats_file_path, mode='w', newline='', encoding='utf-8') as stats_file:
            stats_writer = csv.writer(stats_file)
            stats_writer.writerow(["Metric", "Value"])

            for key, value in self.statistics.items():
                stats_writer.writerow([key, value])

    def export_stats_to_excel(self, output_file_path: str = "export.xlsx"):
        def format_duration(td: timedelta):
            if not td or td.total_seconds() == 0:
                return "N/A"
            days = td.days
            hours, remainder = divmod(td.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            parts = []
            if days:
                parts.append(f"{days} дн")
            if hours:
                parts.append(f"{hours} год")
            if minutes:
                parts.append(f"{minutes} хв")
            if seconds or not parts:
                parts.append(f"{seconds} с")
            return ' '.join(parts)

        def to_comma(value):
            return str(value).replace('.', ',')

        formatted_stats = {
            "Початковий капітал": to_comma(self.initial_cash),
            "Відсоток капіталу вкладений в трейд": to_comma(f"{self.lot_percentage * 100:.2f}"),
            "Кінцевий капітал": to_comma(f"{self.cash:.2f}"),
            "Кількість трейдів": len(self.trades),
            "Кількість прибуткових трейдів": self.profitable_trades_count,
            "Середній заробіток трейда ($)": to_comma(
                f"{self.average_trade_return:.2f}") if self.average_trade_return else "N/A",
            "Середня тривалість трейда": format_duration(self.average_trade_duration),
            "Найдовша тривалість трейда": format_duration(self.longest_trade_duration),
            "Найкоротша тривалість трейда": format_duration(self.shortest_trade_duration),
            "Кількість довгих трейдів": self.long_trades,
            "Кількість прибуткових довгих трейдів": self.successful_long_trades,
            "Кількість збиткових довгих трейдів": self.unsuccessful_long_trades,
            "Кількість коротких трейдів": self.short_trades,
            "Кількість прибуткових коротких трейдів": self.successful_short_trades,
            "Кількість збиткових коротких трейдів": self.unsuccessful_short_trades,
            "Прибуток від прибуткових трейдів ($)": to_comma(f"{self.profitable_return:.2f}"),
            "Збиток від збиткових трейдів ($)": to_comma(f"{self.loss_return:.2f}"),
            "Загальний прибуток ($)": to_comma(f"{self.profit:.2f}"),
            "Прибуток ($)": to_comma(f"{self.net_return:.2f}"),
            "Прибуток (%)": to_comma(f"{self.return_:.2f}")
        }

        df_stats = pd.DataFrame.from_dict(formatted_stats, orient='index', columns=["Значення"])
        df_stats.index.name = "Показник"
        df_stats.to_excel(output_file_path, sheet_name="Статистика")
