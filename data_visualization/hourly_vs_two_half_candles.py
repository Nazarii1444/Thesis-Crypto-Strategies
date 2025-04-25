import matplotlib.patches as patches
import matplotlib.pyplot as plt

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

ax1.set_title('Годинна OHLC-свічка', fontsize=14)
ax2.set_title('Дві півгодинні OHLC-свічки', fontsize=14)

hourly_candle = {
    'open': 150.0,
    'high': 160.0,
    'low': 145.0,
    'close': 155.0
}

half_hour_candles = [
    {'open': 150.0, 'high': 158.0, 'low': 148.0, 'close': 156.0},
    {'open': 156.0, 'high': 160.0, 'low': 145.0, 'close': 155.0}
]


def plot_ohlc_candle(ax, x_pos, candle, width=0.6, color_up='green', color_down='red'):
    color = color_up if candle['close'] >= candle['open'] else color_down

    body_bottom = min(candle['open'], candle['close'])
    body_height = abs(candle['close'] - candle['open'])
    rect = patches.Rectangle((x_pos - width / 2, body_bottom), width, body_height,
                             linewidth=1, edgecolor=color, facecolor=color, alpha=0.7)
    ax.add_patch(rect)

    ax.plot([x_pos, x_pos], [candle['high'], max(candle['open'], candle['close'])],
            color=color, linewidth=1.5)
    ax.plot([x_pos, x_pos], [min(candle['open'], candle['close']), candle['low']],
            color=color, linewidth=1.5)


plot_ohlc_candle(ax1, 1, hourly_candle, width=0.8)

plot_ohlc_candle(ax2, 0.5, half_hour_candles[0], width=0.6)
plot_ohlc_candle(ax2, 1.5, half_hour_candles[1], width=0.6)

ax1.axhline(y=hourly_candle['open'], color='blue', linestyle='--', alpha=0.5)
ax1.axhline(y=hourly_candle['high'], color='blue', linestyle='--', alpha=0.5)
ax1.axhline(y=hourly_candle['low'], color='blue', linestyle='--', alpha=0.5)
ax1.axhline(y=hourly_candle['close'], color='blue', linestyle='--', alpha=0.5)

ax2.axhline(y=half_hour_candles[0]['open'], color='blue', linestyle='--', alpha=0.5)
ax2.axhline(y=max(half_hour_candles[0]['high'], half_hour_candles[1]['high']), color='blue', linestyle='--', alpha=0.5)
ax2.axhline(y=min(half_hour_candles[0]['low'], half_hour_candles[1]['low']), color='blue', linestyle='--', alpha=0.5)
ax2.axhline(y=half_hour_candles[1]['close'], color='blue', linestyle='--', alpha=0.5)

# Настройка осей
for ax in [ax1, ax2]:
    ax.set_ylim(140, 165)
    ax.set_xlim(0, 2)
    ax.set_ylabel('Ціна')
    ax.grid(True, alpha=0.3)
    ax.set_xticks([])

plt.figtext(0.5, 0.11,
            f"Годинна свічка: O={hourly_candle['open']}, H={hourly_candle['high']}, L={hourly_candle['low']}, C={hourly_candle['close']}",
            ha='center', fontsize=10)

plt.figtext(0.5, 0.06,
            f"Перша півгодинна: O={half_hour_candles[0]['open']}, H={half_hour_candles[0]['high']}, L={half_hour_candles[0]['low']}, C={half_hour_candles[0]['close']}\n" +
            f"Друга півгодинна: O={half_hour_candles[1]['open']}, H={half_hour_candles[1]['high']}, L={half_hour_candles[1]['low']}, C={half_hour_candles[1]['close']}",
            ha='center', fontsize=10)

plt.tight_layout(rect=[0, 0.15, 1, 0.95])
plt.show()
