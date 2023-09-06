import json
import os
import pandas as pd
import logging


# Загрузка данных из различных файлов
def load_data():
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)

        with open('dmail_abi.json', 'r') as f:
            abi = json.load(f)

        with open('words.txt', 'r') as file:
            words = [line.strip() for line in file]

        with open('pkey.txt', 'r') as f:
            private_keys = [line.strip() for line in f]

        with open('proxies.txt', 'r') as f:
            proxies = [line.strip() for line in f]
            proxies = [proxy.replace("http://", "").replace("https://", "") for proxy in proxies]

        return config, abi, words, private_keys, proxies

    except Exception as e:
        logging.error(f"Error loading data: {e}")
        raise


# Проверка наличия файла CSV и создание его при отсутствии
def check_and_create_csv():
    if not os.path.exists('transactions.csv'):
        df = pd.DataFrame(columns=['wallet', 'network', 'tx_hash', 'email', 'subject', 'status'])
        df.to_csv('transactions.csv', index=False)
        logging.info("Created transactions.csv file.")


# Сохранение информации о транзакции в CSV-файл
def save_transaction_to_csv(wallet, network_name, tx_hash, email, subject, status, network_config):
    if os.path.getsize('transactions.csv') == 0:
        df = pd.DataFrame(columns=['wallet', 'network', 'tx_hash', 'email', 'subject', 'status'])
    else:
        df = pd.read_csv('transactions.csv')

    transaction_url = f"{network_config['EXPLORER_URL']}{tx_hash}"
    df = df._append(
        {'wallet': wallet, 'network': network_name, 'tx_hash': transaction_url, 'email': email, 'subject': subject,
         'status': status}, ignore_index=True)
    df.to_csv('transactions.csv', index=False)

