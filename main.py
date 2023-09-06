from data_utils import load_data, check_and_create_csv, save_transaction_to_csv
from network_utils import setup_web3_and_contract, send_transaction, wait_for_acceptable_gas_fee
from logging_utils import setup_logging, delay_with_tqdm
import random
import logging


# Генерация случайного адреса электронной почты и темы письма
def generate_random_email_subject(words):
    email = random.choice(words) + random.choice(['@gmail.com', '@yandex.com', '@dmail.ai'])
    subject_length = random.randint(1, 25)
    subject = ' '.join(random.sample(words, subject_length))
    return email, subject


# Обработка каждой транзакции
def handle_transaction(w3, contract, private_key, sender_address, email, subject, network_config, CONFIG):
    tx_hash = send_transaction(w3, contract, private_key, sender_address, email, subject, network_config, CONFIG)

    try:
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)  # ждем 2 минуты

        if receipt.status == 1:
            logging.info("Transaction was successful")
            save_transaction_to_csv(sender_address, CONFIG["NETWORK"], tx_hash.hex(), email, subject, 'success', network_config)
        else:
            logging.warning("Transaction failed")
            save_transaction_to_csv(sender_address, CONFIG["NETWORK"], tx_hash.hex(), email, subject, 'error', network_config)
    except TimeoutError:
        logging.warning(f"Timeout while waiting for receipt of transaction {tx_hash.hex()}. Moving on...")
        save_transaction_to_csv(sender_address, CONFIG["NETWORK"], tx_hash.hex(), email, subject, 'error', network_config)


# Отправка писем для каждого кошелька
def send_emails(w3, contract, private_key, sender_address, repeat_send, words, network_config, CONFIG):
    for i in range(repeat_send):
        logging.info(f"Sending transactions: {i + 1}/{repeat_send}")

        try:
            email, subject = generate_random_email_subject(words)
            handle_transaction(w3, contract, private_key, sender_address, email, subject, network_config, CONFIG)
        except Exception as e:
            logging.error(f"Error while processing address {sender_address}: {e}")
            save_transaction_to_csv(sender_address, CONFIG["NETWORK"], None, None, None, 'error', network_config)
            continue

        if i < repeat_send - 1:
            delay = random.randint(CONFIG["DELAY_MIN"], CONFIG["DELAY_MAX"])
            delay_with_tqdm(delay)


# Обработка каждого кошелька
def process_wallet(w3, contract, private_key, idx, total_wallets, words, network_config, CONFIG):
    sender_address = w3.eth.account.from_key(private_key).address
    repeat_send = random.randint(CONFIG["REPEAT_SEND_MIN"], CONFIG["REPEAT_SEND_MAX"])

    logging.info(sender_address)
    logging.info(f"Processing wallet: {idx + 1}/{total_wallets}")

    send_emails(w3, contract, private_key, sender_address, repeat_send, words, network_config, CONFIG)

    wallet_delay = random.randint(CONFIG["DELAY_WALLET_MIN"], CONFIG["DELAY_WALLET_MAX"])
    delay_with_tqdm(wallet_delay)


def main():
    setup_logging()

    CONFIG, contract_abi, words, private_keys, proxies = load_data()
    logging.info(f"Connected to {CONFIG['NETWORK']} network")

    network_config = CONFIG["NETWORKS"][CONFIG["NETWORK"]]
    w3, contract = setup_web3_and_contract(CONFIG, network_config, contract_abi, proxies)

    if CONFIG["SHUFFLE_WALLETS"]:
        random.shuffle(private_keys)

    wait_for_acceptable_gas_fee(CONFIG)

    total_wallets = len(private_keys)
    for idx, private_key in enumerate(private_keys):
        process_wallet(w3, contract, private_key, idx, total_wallets, words, network_config, CONFIG)


if __name__ == "__main__":
    check_and_create_csv()
    main()
