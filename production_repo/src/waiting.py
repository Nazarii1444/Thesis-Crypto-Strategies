import time
from datetime import datetime, timedelta

from logger import logger


def wait_for_next_5_minute_cycle():
    current_time = datetime.now()
    minutes_to_next_5_minute_cycle = (5 - current_time.minute % 5) % 5
    seconds_until_next_cycle = (minutes_to_next_5_minute_cycle * 60) - current_time.second

    if seconds_until_next_cycle == 0:
        seconds_until_next_cycle = 5 * 60
    elif minutes_to_next_5_minute_cycle == 0:
        seconds_until_next_cycle = 4 * 60 + (60 - current_time.second)

    logger.info(f"WAITING {seconds_until_next_cycle + 1}s...")
    time.sleep(seconds_until_next_cycle + 1)


def wait_for_next_15_minute_cycle():
    current_time = datetime.now()
    minutes_to_add = 15 - (current_time.minute % 15)
    if minutes_to_add == 0 and current_time.second == 0:
        minutes_to_add = 15

    next_cycle = current_time.replace(second=0, microsecond=0) + timedelta(minutes=minutes_to_add)
    seconds_until_next_cycle = (next_cycle - current_time).total_seconds()
    time.sleep(seconds_until_next_cycle + 1)


def wait_for_next_30_minute_cycle():
    current_time = datetime.now()
    minutes_to_add = 30 - (current_time.minute % 30)
    if minutes_to_add == 0 and current_time.second == 0:
        minutes_to_add = 30

    next_cycle = current_time.replace(second=0, microsecond=0) + timedelta(minutes=minutes_to_add)
    seconds_until_next_cycle = (next_cycle - current_time).total_seconds()
    time.sleep(seconds_until_next_cycle + 1)


def get_to_log():
    return datetime.now().minute in list(range(0, 60, 5)) and datetime.now().second in range(1, 7)
