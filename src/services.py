import logging
import os
import re
from datetime import datetime
from typing import Any, Dict, List

from src.utils import get_dataframe_excel

current_dir = os.path.dirname(os.path.abspath(__file__))
rel_file_path = os.path.join(current_dir, "../logs/services.log")
abs_file_path = os.path.abspath(rel_file_path)


logger = logging.getLogger("services")
file_handler = logging.FileHandler(abs_file_path, mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(filename)s %(funcName)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.WARNING)

#
# CURRENT_DIR = os.path.dirname(__file__)
# PATH_FILE_EXCEL = os.path.join(CURRENT_DIR, "..", "data", "operations.xlsx")


def get_transactions_for_investment(file_path: str) -> list[dict]:
    """Функция для получения списка банковских операций из файла xlsx, содержащих расходы"""
    df_excel = get_dataframe_excel(file_path)
    try:
        df_excel_filtered = df_excel[
            (df_excel["Статус"] == "OK") & (df_excel["Валюта операции"] == "RUB") & (df_excel["Сумма операции"] < 0)
        ]
        df_excel_filtered_columns = df_excel_filtered[["Дата операции", "Сумма операции"]]
        transaction_list = df_excel_filtered_columns.to_dict(orient="records")
        for transaction in transaction_list:
            date_str = transaction["Дата операции"].split(" ")[0]
            date_converted = datetime.strptime(date_str, "%d.%m.%Y").strftime("%Y-%m-%d")
            transaction["Дата операции"] = date_converted
        return transaction_list
    except KeyError:
        logger.error("Отсутствуют заданные столбцы для сортировки")
        return []


def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int = 50) -> float:
    """Функция для вычисления возможной суммы инвестирования с учетом порога округления суммы затрат"""
    investment = []
    if transactions:
        for transaction in transactions:
            try:
                if month in transaction["Дата операции"]:
                    amount = abs(transaction["Сумма операции"])
                    amount_str = str(amount)
                    pattern = r"\d{1,2}\.\d{1,2}"
                    tail_str = re.findall(pattern, amount_str)[0]
                    if tail_str:
                        tail_float = float(tail_str)
                        if 0 < tail_float < limit:
                            investment_amount = round(limit - tail_float, 2)
                            investment.append(investment_amount)
                        elif limit < tail_float < 100:
                            investment_amount = round(100 - tail_float, 2)
                            investment.append(investment_amount)
            except KeyError as e:
                logger.warning(f"Отсутствует ключ {e}")
    else:
        logger.warning("Отсутствует список транзакций")
        return 0
    investment_sum = sum(investment)
    if investment_sum == 0:
        logger.warning(f"Заданный месяц {month} отсутствует в выборке")
    return investment_sum
