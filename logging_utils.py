import logging
import time
from tqdm import tqdm
import random


# Настройка логирования
def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Задержка между транзакциями
def delay_between_transactions(config):
    delay = random.randint(config["DELAY_MIN"], config["DELAY_MAX"])
    logging.info(f"Status success. Delaying for {delay} seconds before the next mail...")
    time.sleep(delay)


# Задержка между обработкой кошельков
def delay_between_wallets(config):
    wallet_delay = random.randint(config["DELAY_WALLET_MIN"], config["DELAY_WALLET_MAX"])
    logging.info(f"Delaying for {wallet_delay} seconds before processing the next wallet...")
    time.sleep(wallet_delay)


# Задержка с использованием tqdm для отображения прогресса
def delay_with_tqdm(seconds):
    for _ in tqdm(range(seconds), desc="Delaying", leave=False):
        time.sleep(1)
