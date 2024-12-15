import logging
import os
from datetime import datetime
from typing import Any, Callable, Optional

import pandas as pd

# from utils import get_dataframe_excel


current_dir = os.path.dirname(os.path.abspath(__file__))
rel_file_path = os.path.join(current_dir, "../logs/reports.log")
abs_file_path = os.path.abspath(rel_file_path)


logger = logging.getLogger("reports")
file_handler = logging.FileHandler(abs_file_path, mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(filename)s %(funcName)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.WARNING)


CURRENT_DIR = os.path.dirname(__file__)
PATH_FILE_EXCEL = os.path.join(CURRENT_DIR, "..", "data", "operations.xlsx")
PATH_FILE_REPORT = os.path.join(CURRENT_DIR, "..", "reports", "report_by_category.xlsx")


def save_report_to_excel(filename: str) -> Any:
    """Функция-декоратор, которая сохраняет в excel-файл результат работы функции"""

    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if not result.empty:
                result.to_excel(filename, index=False)
            else:
                logger.error(f"Запись в файл {filename} не произведена, так как результат пустой.")
            return result

        return wrapper

    return decorator


@save_report_to_excel(filename=PATH_FILE_REPORT)
def spending_by_category(transactions_df: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Функция для сортировки банковских операций по выбранной категории за последние три месяца от заданной даты"""
    try:
        transactions_df["Дата платежа"] = pd.to_datetime(transactions_df["Дата платежа"], format="%d.%m.%Y")
        if date:
            start_date = pd.to_datetime(date)
        else:
            current_date = datetime.now()
            start_date = pd.to_datetime(current_date)

        three_months_ago = start_date - pd.DateOffset(months=3)
        try:
            transactions_category = transactions_df.loc[
                (
                    (transactions_df["Статус"] == "OK")
                    & (transactions_df["Валюта операции"] == "RUB")
                    & (transactions_df["Сумма операции"] < 0)
                    & (transactions_df["Категория"] == category)
                    & (three_months_ago <= transactions_df["Дата платежа"])
                    & (transactions_df["Дата платежа"] <= start_date)
                )
            ]

            return transactions_category.reset_index(drop=True)

        except KeyError:
            logger.error("Отсутствуют заданные столбцы для сортировки")
            return pd.DataFrame()
    except KeyError:
        logger.error("Отсутствуют заданные столбцы для сортировки")
        return pd.DataFrame()


def spending_by_category_dict(transactions_category_df):
    if not transactions_category_df.empty:
        try:
            spending_sum = 0 - float(transactions_category_df["Сумма операции"].sum())
            category_name = transactions_category_df["Категория"].iloc[0]
            reports_dict = {"category": category_name, "total_spent": spending_sum}
            return reports_dict
        except KeyError:
            logger.error("Отсутствуют заданные столбцы")
            return {}
        except ValueError:
            logger.error("Ошибка преобразования в float")
            return {}
    else:
        return {}


#
# transactions_dataframe = get_dataframe_excel(PATH_FILE_EXCEL)
# # # print(transactions_dataframe)
# #
# result = spending_by_category(transactions_dataframe, "Супермаркеты", "2021-12-31")
# # print(result)
#
# dict = spending_by_category_dict(result)
# print(dict)
