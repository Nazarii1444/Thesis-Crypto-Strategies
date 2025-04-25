import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from utils.loader import load_csv


def point_and_figure(
        df: pd.DataFrame,
        column: str = "Close",
        box_size: float | None = None,
        reversal: int = 3,
        last_n: int | None = 60,
        figsize=(10, 7),
        up_color="#4daf4a",
        dn_color="#e41a1c",
        grid_color="#d0d0d0",
) -> plt.Axes:
    """
    Графік 'хрестики-нулики' (Point and Figure).

    Параметри:
    - df: DataFrame з даними
    - column: назва стовпця з цінами
    - box_size: розмір коробки у одиницях ціни
    - reversal: кількість боксів для зміни тренду
    - last_n: кількість останніх колонок для відображення
    - figsize: розмір графіка
    - up_color: колір для хрестиків (зростання)
    - dn_color: колір для нуликів (падіння)
    - grid_color: колір сітки
    """
    price = df[column].dropna()
    if price.empty:
        raise ValueError("Колонка порожня")

    if box_size is None:
        box_size = np.round(price.mean() * 0.01, 2) or 0.01

    to_lvl = lambda p: int(np.floor(p / box_size))

    data = []

    current_price = price.iloc[0]
    current_lvl = to_lvl(current_price)

    col_idx = 0
    direction = None

    column_values = []

    for p in price.iloc[1:]:
        lvl = to_lvl(p)

        if direction is None:
            direction = "X" if lvl > current_lvl else "O"
            if direction == "X":
                for i in range(current_lvl, lvl + 1):
                    column_values.append(i)
            else:
                for i in range(current_lvl, lvl - 1, -1):
                    column_values.append(i)
            current_lvl = lvl
            continue

        if direction == "X":
            if lvl > current_lvl:
                for i in range(current_lvl + 1, lvl + 1):
                    column_values.append(i)
                current_lvl = lvl
            elif current_lvl - lvl >= reversal:
                for v in column_values:
                    data.append((col_idx, v, "X"))

                col_idx += 1
                direction = "O"
                column_values = []
                for i in range(current_lvl, lvl - 1, -1):
                    column_values.append(i)
                current_lvl = lvl
        else:
            if lvl < current_lvl:
                for i in range(current_lvl - 1, lvl - 1, -1):
                    column_values.append(i)
                current_lvl = lvl
            elif lvl - current_lvl >= reversal:
                for v in column_values:
                    data.append((col_idx, v, "O"))

                col_idx += 1
                direction = "X"
                column_values = []
                for i in range(current_lvl, lvl + 1):
                    column_values.append(i)
                current_lvl = lvl

    for v in column_values:
        data.append((col_idx, v, direction))

    if not data:
        raise RuntimeError("Неправильні параметри!")

    if last_n is not None:
        max_col = max(col for col, _, _ in data)
        min_col = max(0, max_col - last_n + 1)
        data = [(col - min_col, lvl, mark) for col, lvl, mark in data if col >= min_col]

    x_coords = [col for col, _, _ in data]
    y_levels = [lvl for _, lvl, _ in data]
    markers = [mark for _, _, mark in data]

    y_coords = [lvl * box_size for lvl in y_levels]

    min_y = min(y_levels) * box_size
    max_y = max(y_levels) * box_size
    max_col = max(x_coords) if x_coords else 0

    fig, ax = plt.subplots(figsize=figsize)

    ax.set_aspect('equal')

    ax.set_xlim(-0.5, max_col + 0.5)
    ax.set_ylim(max_y + box_size, min_y - box_size)

    ax.set_xticks(np.arange(0, max_col + 1))
    y_ticks = np.arange(
        np.floor(min_y / box_size) * box_size,
        np.ceil(max_y / box_size) * box_size + box_size,
        box_size
    )
    ax.set_yticks(y_ticks)

    ax.set_xticks(np.arange(-0.5, max_col + 1), minor=True)
    ax.set_yticks(y_ticks - box_size / 2, minor=True)

    ax.grid(which="both", color=grid_color, linewidth=0.5)

    ax.scatter(
        [col + 0.5 for col, _, mark in data if mark == "X"],
        [lvl * box_size + box_size / 2 for _, lvl, mark in data if mark == "X"],
        marker="x", s=100, linewidths=2, color=up_color,
        label="X (зростання)"
    )

    ax.scatter(
        [col + 0.5 for col, _, mark in data if mark == "O"],
        [lvl * box_size + box_size / 2 for _, lvl, mark in data if mark == "O"],
        marker="o", s=100, facecolors="none", edgecolors=dn_color, linewidths=2,
        label="O (падіння)"
    )

    ax.set_xlabel("Колонки (зміна тренду)")
    ax.set_ylabel(f"Ціна ({column})")
    ax.set_title("Графік «хрестики-нулики»")

    ax.legend(loc="upper left", frameon=False)

    twin_ax = ax.twinx()
    twin_ax.set_ylim(ax.get_ylim())
    twin_ax.set_yticks(ax.get_yticks())
    twin_ax.set_yticklabels([f"{y:.2f}" for y in ax.get_yticks()])
    twin_ax.grid(False)

    ax.set_yticklabels([f"{y:.2f}" for y in ax.get_yticks()])

    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    plt.tight_layout()
    return ax


if __name__ == '__main__':
    df = load_csv("./test_data/custom_csvs/AAVE_USDT_RECENT.csv")[:6000]

    point_and_figure(
        df,
        column="Close",
        box_size=1.0,  # Розмір боксу в 1 одиницю ціни
        reversal=3,  # Зміна тренду при русі на 3 бокси
        last_n=40,  # останні 40 колонок
        figsize=(10, 7)
    )
    plt.show()
