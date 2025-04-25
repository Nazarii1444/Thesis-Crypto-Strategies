import logging
from colorama import init, Back, Fore, Style

init(autoreset=True)


class ColorFormatter(logging.Formatter):
    def format(self, record):
        if record.levelno == logging.DEBUG:
            record.msg = f"{Back.GREEN}{Fore.BLACK}{record.msg}{Style.RESET_ALL}"
        elif record.levelno == logging.INFO:
            record.msg = f"{Back.BLUE}{Fore.BLACK}{record.msg}{Style.RESET_ALL}"
        elif record.levelno == logging.WARNING:
            record.msg = f"{Back.YELLOW}{Fore.BLACK}{record.msg}{Style.RESET_ALL}"
        elif record.levelno == logging.ERROR:
            record.msg = f"{Back.RED}{Fore.BLACK}{record.msg}{Style.RESET_ALL}"
        elif record.levelno == logging.CRITICAL:
            record.msg = f"{Back.MAGENTA}{Fore.BLACK}{record.msg}{Style.RESET_ALL}"

        return super().format(record)


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# formatter = ColorFormatter('%(asctime)s %(name)s %(levelname)s - %(message)s')
formatter = ColorFormatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


def log_debug(message):
    logger.debug(message)


def log_info(message):
    logger.info(message)


def log_warning(message):
    logger.warning(message)


def log_error(message):
    logger.error(message)


def log_critical(message):
    logger.critical(message)


def log_trade(trade):
    if trade.is_profitable():
        log_info(f"{Back.GREEN}{Fore.BLACK}{trade}{Style.RESET_ALL}")
    else:
        log_info(f"{Back.RED}{Fore.BLACK}{trade}{Style.RESET_ALL}")


if __name__ == "__main__":
    log_debug("This is a debug message.")
    log_info("This is an info message.")
    log_warning("This is a warning message.")
    log_error("This is an error message.")
    log_critical("This is a critical message.")
