import json
from unittest.mock import patch

from src.main import main


@patch("src.main.get_dataframe_excel")
@patch("src.main.get_transactions_for_investment")
@patch("src.main.main_page")
def test_main(
    mock_main_page, mock_get_transactions_for_investment, mock_get_dataframe_excel, main_page_dict, df_excel_for_report
):
    mock_main_page.return_value = main_page_dict
    mock_get_transactions_for_investment.return_value = [
        {"Дата операции": "2021-12-31", "Сумма операции": -1020.20},
        {"Дата операции": "2021-12-30", "Сумма операции": -568.3},
        {"Дата операции": "2021-12-28", "Сумма операции": -101.00},
        {"Дата операции": "2021-12-26", "Сумма операции": -10.00},
        {"Дата операции": "2021-12-25", "Сумма операции": -50.00},
    ]

    mock_get_dataframe_excel.return_value = df_excel_for_report
    result = main("2024-12-14 09:00:00", "2021-12", 50, "Перевод", "2021-12-31")
    expected_result = {
        "main_page": main_page_dict,
        "services": {"service": "Инвесткопилка", "investment": 150.50},
        "reports": {"category": "Перевод", "total_spent": 4010.00},
    }
    assert result == json.dumps(expected_result, ensure_ascii=False)
    mock_main_page.assert_called_once()
    mock_get_transactions_for_investment.assert_called_once()
    mock_get_dataframe_excel.assert_called_once()
