import logging
import os

from src.utils import (
    get_cards_info,
    get_dataframe_excel,
    get_user_currency_rates,
    get_user_stocks,
    greeting,
    top_five_transactions,
)

current_dir = os.path.dirname(os.path.abspath(__file__))
rel_file_path = os.path.join(current_dir, "../logs/views.log")
abs_file_path = os.path.abspath(rel_file_path)


logger = logging.getLogger("views")
file_handler = logging.FileHandler(abs_file_path, mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(filename)s %(funcName)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.WARNING)


CURRENT_DIR = os.path.dirname(__file__)
PATH_FILE_EXCEL = os.path.join(CURRENT_DIR, "..", "data", "operations.xlsx")
PATH_FILE_SETTINGS = os.path.join(CURRENT_DIR, "..", "user_settings.json")


def main_page(datetime_str: str) -> dict:
    """Функция формирует словарь для отображения страницы приложения "Главная" """

    df_excel = get_dataframe_excel(PATH_FILE_EXCEL)
    if df_excel.empty:
        logger.warning(f"Полученный DataFrame из файла {PATH_FILE_EXCEL} пустой")

    main_page_dict = {
        "greeting": greeting(datetime_str),
        "cards": get_cards_info(df_excel),
        "top_transactions": top_five_transactions(df_excel),
        "currency_rates": get_user_currency_rates(PATH_FILE_SETTINGS)[0],
        "stock_prices": get_user_stocks(PATH_FILE_SETTINGS),
    }

    if not main_page_dict["cards"]:
        logger.warning("Не удалось получить информацию о картах.")

    if not main_page_dict["top_transactions"]:
        logger.warning("Не удалось получить информацию топ-5 транзакциях.")

    if not main_page_dict["currency_rates"]:
        logger.warning("Не удалось получить информацию о курсах валют")

    if not main_page_dict["stock_prices"]:
        logger.warning("Не удалось получить информацию о стоимости акций")

    return main_page_dict
