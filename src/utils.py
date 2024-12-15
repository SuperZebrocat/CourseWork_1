import json
import logging
import os
from datetime import datetime

import pandas as pd

from src.external_api import get_currency_rates_api, get_stocks_api

current_dir = os.path.dirname(os.path.abspath(__file__))
rel_file_path = os.path.join(current_dir, "../logs/utils.log")
abs_file_path = os.path.abspath(rel_file_path)


logger = logging.getLogger("utils")
file_handler = logging.FileHandler(abs_file_path, mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(filename)s %(funcName)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.WARNING)


def greeting(datetime_str: str) -> str:
    """Функция возвращения приветствия пользователю, исходя из времени суток"""
    try:
        dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        current_hour = dt.hour
        if 0 <= current_hour < 6:
            return "Доброй ночи"
        elif 6 <= current_hour < 12:
            return "Доброе утро"
        elif 12 <= current_hour < 18:
            return "Добрый день"
        elif 18 <= current_hour <= 23:
            return "Добрый вечер"
    except ValueError:
        logger.error("Неверный формат переданного значения времени")
        return ""


def get_dataframe_excel(file_path: str) -> pd.DataFrame:
    """Функция для извлечения данных из excel-файла, возвращает объект DataFrame"""
    try:
        df_excel = pd.read_excel(file_path)
        return df_excel
    except FileNotFoundError:
        logger.error(f'Ошибка получения данных: файл "{file_path}" не найден')
        return pd.DataFrame()
    except ValueError:
        logger.error(f"Отсутствуют данные в файле {file_path}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Ошибка: {e}")
        logger.error(f"Ошибка: {e}")
        return pd.DataFrame()


def get_cards_info(df_excel: pd.DataFrame) -> list[dict]:
    """Функция для агрегации информации по картам пользователя из объекта DataFrame, возвращает список словарей"""
    try:
        filtered_by_status_rub = df_excel[
            (df_excel["Статус"] == "OK") & (df_excel["Валюта операции"] == "RUB") & (df_excel["Сумма операции"] < 0)
        ]
        filtered_by_status_rub.loc[:, "Кэшбэк"] = (filtered_by_status_rub["Сумма операции"] / 100).astype(int)
        cards_info = (
            filtered_by_status_rub.groupby("Номер карты", dropna=True)
            .agg({"Сумма операции": lambda x: abs(x.sum()), "Кэшбэк": lambda x: abs(x.sum())})
            .reset_index()
        )
        cards_info.columns = ["last_digits", "total_spent", "cashback"]
        cards_info_list = cards_info.to_dict(orient="records")
        for card in cards_info_list:
            card["last_digits"] = card["last_digits"].lstrip("*")
        return cards_info_list
    except TypeError:
        logger.error("Ошибка соответствия типов данных")
        return []
    except KeyError:
        logger.error("Отсутствуют заданные столбцы для сортировки")
        return []


def top_five_transactions(df_excel: pd.DataFrame) -> list[dict]:
    """Функция для получения топ-5 транзакций по сумме операции, возвращает список словарей"""
    try:
        filtered_by_status_rub = df_excel.loc[(df_excel["Статус"] == "OK") & (df_excel["Валюта операции"] == "RUB")]
        sorted_by_value = filtered_by_status_rub.sort_values("Сумма операции", ascending=False)
        sorted_by_value_columns = sorted_by_value[["Дата операции", "Сумма операции", "Категория", "Описание"]]
        top_5_transactions = sorted_by_value_columns.head(5)
        top_5_transactions.columns = ["date", "amount", "category", "description"]
        top_5_transactions_list = top_5_transactions.to_dict(orient="records")
        for transaction in top_5_transactions_list:
            transaction["date"] = transaction["date"].split(" ")[0]
        return top_5_transactions_list
    except TypeError:
        logger.error("Ошибка соответствия типов данных")
        return []
    except KeyError:
        logger.error("Отсутствуют заданные столбцы для сортировки")
        return []


def get_user_currency_rates(file_path: str) -> [list, float]:
    """Функция получения списка словарей с курсами валют согласно пользовательским
    настройкам и курса валют рубля к доллару"""
    response_result = get_currency_rates_api(file_path)
    if response_result and "rates" in response_result:
        currency_dict_api = response_result.get("rates")
        currency_rates_list = []
        for key, value in currency_dict_api.items():
            if value != 0:
                currency_rates_list.append({"currency": key, "rate": round(1 / value, 2)})
            else:
                logger.warning("Отсутсвуют данные о курсах валют пользователя")
        rub_rate_usd = 0
        for item in currency_rates_list:
            if item.get("currency") == "USD":
                rub_rate_usd = item.get("rate")
            else:
                logger.warning("Отсутсвуют данные о курсе валюты USD")
        return currency_rates_list, rub_rate_usd
    else:
        logger.warning("Отсутсвуют данные о курсах валют, полученные от API")
        return [], 0


def get_user_stocks(file_path: str) -> list[dict]:
    """Функция получения списка словарей со стоимостью заданных пользователем акций в рублях"""
    try:
        with open(file_path, "r") as file:
            user_settings = json.load(file)
    except FileNotFoundError:
        logger.error(f'Ошибка получения данных: файл "{file_path}" не найден')
        return []
    except json.JSONDecodeError:
        logger.error(f"Ошибка декодирования JSON файла {file_path}")
        return []
    stocks = user_settings.get("user_stocks", [])
    response_result = get_stocks_api()
    if stocks and response_result:
        user_stocks_list = []
        rub_rate_usd = get_user_currency_rates(file_path)[1]
        if rub_rate_usd != 0:
            for stock in response_result:
                if stock.get("symbol") in stocks:
                    price_usd = float(stock["price"])
                    new_stock = {"stock": stock["symbol"], "price": round(price_usd * rub_rate_usd, 2)}
                    user_stocks_list.append(new_stock)
                else:
                    logger.warning("Отсутсвуют данные по выбранным пользователем акциям")
        else:
            logger.warning("Отсутствуют данные о курсе валюты USD")
        return sorted(user_stocks_list, key=lambda x: x["stock"])
    else:
        logger.warning("Отсутствуют данные о стоимости акций, выбранных пользователем")
        return []
