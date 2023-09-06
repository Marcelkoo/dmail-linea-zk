import random
import requests
from web3 import Web3, HTTPProvider, middleware
import logging
from tqdm import tqdm
import time


# Инициализация сессии для использования прокси
def initialize_session(proxies_list):
    session = requests.Session()
    if proxies_list:
        proxy_data = random.choice(proxies_list).split('@')
        credentials = proxy_data[0]
        ip_port = proxy_data[1]
        session.proxies = {
            "http": f"http://{credentials}@{ip_port}",
            "https": f"http://{credentials}@{ip_port}",
        }
    return session


# Настройка web3 и контракта
def setup_web3_and_contract(CONFIG, network_config, contract_abi, proxies):
    session = initialize_session(proxies) if CONFIG["USE_PROXY"] else None

    w3 = Web3(HTTPProvider(network_config["HTTP_PROVIDER"], session=session))
    w3.middleware_onion.inject(middleware.geth_poa_middleware, layer=0)

    contract = w3.eth.contract(address=Web3.to_checksum_address(network_config["CONTRACT_ADDRESS"]), abi=contract_abi)
    return w3, contract


# Подсчет гвей
def get_eth_gas_fee(CONFIG):
    w3 = Web3(Web3.HTTPProvider(CONFIG["NETWORKS"]["ETH"]["HTTP_PROVIDER"]))
    gas_price_gwei = w3.eth.gas_price / 1e9
    return gas_price_gwei


# Ожидает, пока гвей не станет приемлемым
def wait_for_acceptable_gas_fee(CONFIG):
    w3 = Web3(Web3.HTTPProvider(CONFIG["NETWORKS"]["ETH"]["HTTP_PROVIDER"]))

    while True:
        current_gas_fee = w3.eth.gas_price / 1e9  # Переводим в GWEI
        if current_gas_fee <= CONFIG["MAX_GWEI"]:
            return True
        else:
            for _ in tqdm(range(60),
                          desc=f"Current gas fee: {current_gas_fee} GWEI. Waiting for it to drop below {CONFIG['MAX_GWEI']} GWEI.",
                          leave=False):
                time.sleep(1)


# Отправка транзакции
def send_transaction(w3, contract, private_key, sender_address, email, subject, network_config, CONFIG):
    hex_email = email.encode('utf-8').hex()
    hex_subject = subject.encode('utf-8').hex()

    try:
        if CONFIG["NETWORK"] == "LINEA":
            transaction = contract.functions.send_mail(hex_email, hex_subject).build_transaction({
                'chainId': network_config["CHAIN_ID"],
                'nonce': w3.eth.get_transaction_count(sender_address),
                'maxPriorityFeePerGas': w3.eth.max_priority_fee,
                'maxFeePerGas': int(w3.eth.max_priority_fee * 1.1)
            })
        elif CONFIG["NETWORK"] == "ZKSYNC":
            transaction = contract.functions.send_mail(hex_email, hex_subject).build_transaction({
                'from': sender_address,
                'chainId': network_config["CHAIN_ID"],
                'nonce': w3.eth.get_transaction_count(sender_address),
                "gasPrice": w3.eth.gas_price,
            })
        else:
            # Обработка других сетей или вывод ошибки
            raise ValueError(f"Unsupported network: {CONFIG['NETWORK']}")

        signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        logging.info(f"Transaction {network_config['EXPLORER_URL']}{tx_hash.hex()} sent. Waiting for receipt...")

        # Ожидание завершения транзакции с таймаутом
        wait_for_receipt(w3, tx_hash)
        return tx_hash

    except Exception as e:
        logging.error(f"Error while sending transaction from address {sender_address}: {e}")
        return None


# Ожидание получения информации о транзакции
def wait_for_receipt(w3, tx_hash, timeout=120):
    try:
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
        return receipt
    except TimeoutError:
        logging.warning(f"Timeout while waiting for receipt of transaction {tx_hash.hex()}. Moving on...")
        return None
