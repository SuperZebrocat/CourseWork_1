import json
import logging
import os
from typing import Any, Dict, List, Union

import requests
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
rel_file_path = os.path.join(current_dir, "../logs/external_api.log")
abs_file_path = os.path.abspath(rel_file_path)


logger = logging.getLogger("external_api")
file_handler = logging.FileHandler(abs_file_path, mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(filename)s %(funcName)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.WARNING)


load_dotenv()
API_KEY_EXCHANGE = os.getenv("API_KEY_EXCHANGE")
API_KEY_STOCKS = os.getenv("API_KEY_STOCKS")


def get_currency_rates_api(file_path: str) -> Union[Dict, Any]:
    """Функция для получения выбранных пользователем курсов валют от внешнего сервиса, возращает словарь"""
    try:
        with open(file_path, "r") as file:
            user_settings = json.load(file)
    except FileNotFoundError:
        logger.error(f'Ошибка получения данных: файл "{file_path}" не найден')
        return {}
    except json.JSONDecodeError:
        logger.error(f"Ошибка декодирования JSON файла {file_path}")
        return {}
    currencies = user_settings.get("user_currencies")
    if currencies and len(currencies) > 0:
        try:
            payload = {"base": "RUB", "symbols": ",".join(currencies)}
            url = "https://api.apilayer.com/exchangerates_data/latest"
            headers = {"apikey": API_KEY_EXCHANGE}
            response = requests.get(url, headers=headers, params=payload)
            response.raise_for_status()
            response_result = response.json()
            return response_result
        except requests.exceptions.RequestException:
            logger.error("Ошибка при выполнении запроса к API")
            return {}
    else:
        logger.warning("Нет данных для запроса к API")
        return {}


def get_stocks_api() -> Union[List, Any]:
    """Функция получения стоимости акций от внешнего сервиса, возвращает список словарей"""
    try:
        url = "https://financialmodelingprep.com/api/v3/stock/list"
        params = {"apikey": API_KEY_STOCKS}
        response = requests.get(url, params=params)
        response_result = response.json()
        return response_result
    except requests.exceptions.RequestException:
        logger.error("Ошибка при выполнении запроса к API")
        return []
