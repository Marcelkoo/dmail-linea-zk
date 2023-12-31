## DMAIL LINEA/ZKSYNC
Этот скрипт предназначен для автоматической отправки DMAIL транзакций в сетях Linea и ZkSync.

## Основные возможности
- Возможность выбора сети для выполнения транзакций [LINEA/ZKSYNC].
- Автоматическая генерация получателя и темы письма в dmail на основе содержимого файла words.txt.
- Возможность задавать случайные интервалы задержки между транзакциями и между обработкой разных кошельков.
- Возможность указать количество "повторных транзакций" для каждого кошелька.
- Автоматическое ожидание оптимального значения GWEI перед выполнением транзакции.
- Поддержка прокси.
- Запись результатов каждой транзакции в CSV файл.
- Используется tqdm для отображения прогресс-бара при задержках, что делает ожидание более наглядным для пользователя.
- Используется logging для записи информации о выполнении программы, ошибок и других важных событий.

## Конфигурация
Перед началом работы, убедитесь, что вы заполнили 'pkey.txt' и настроили файл 'config.json':

- NETWORK: Выберите сеть, в которой будут выполняться транзакции [LINEA/ZKSYNC].
- DELAY_MIN и DELAY_MAX: Установите интервал задержки между отправкой транзакций.
- DELAY_WALLET_MIN и DELAY_WALLET_MAX: Установите интервал задержки между обработкой разных кошельков.
- REPEAT_SEND_MIN и REPEAT_SEND_MAX: Задайте диапазон количества транзакций для каждого кошелька.
- MAX_GWEI: Задайте максимальный возможный гвей в сети ETH.
- SHUFFLE_WALLETS: Решите, нужно ли перемешивать кошельки перед их обработкой.
- USE_PROXY: Определите, будете ли вы использовать прокси при выполнении транзакций.

## Установка
Установите необходимые зависимости с помощью команды:
1) pip install -r requirements.txt

## Запуск
Для запуска основного скрипта выполните:
1) cd путь
2) python main.py
