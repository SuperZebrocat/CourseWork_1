import json
import os
from typing import Any, Optional

from src.reports import spending_by_category, spending_by_category_dict
from src.services import get_transactions_for_investment, investment_bank
from src.utils import get_dataframe_excel
from src.views import main_page

CURRENT_DIR = os.path.dirname(__file__)
PATH_FILE_EXCEL = os.path.join(CURRENT_DIR, "..", "data", "operations.xlsx")


def main(datetime_str: str, month: str, limit: int, category: str, date: Optional[str]) -> Any:
    """ункция для формирования JSON-ответа для всех страниц и сервисов банковского приложения"""
    main_page_dict = main_page(datetime_str)
    transactions = get_transactions_for_investment(PATH_FILE_EXCEL)
    services_response = investment_bank(month, transactions, limit)
    services_dict = {"service": "Инвесткопилка", "investment": services_response}
    transactions_df = get_dataframe_excel(PATH_FILE_EXCEL)
    reports_response = spending_by_category(transactions_df, category, date)
    reports_dict = spending_by_category_dict(reports_response)

    application_dict = {"main_page": main_page_dict, "services": services_dict, "reports": reports_dict}

    json_application_dict = json.dumps(application_dict, ensure_ascii=False)

    return json_application_dict


# if __name__ == "__main__":
#     result = main("2024-12-14 12:00:00", "2021-12", 50, "Супермаркеты", "2021-12-31")
#     print(result)
