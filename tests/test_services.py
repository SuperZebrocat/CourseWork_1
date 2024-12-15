from unittest.mock import patch

import pandas as pd

from src.services import get_transactions_for_investment, investment_bank


def test_investment_bank(transactions_for_investment_bank):
    result = investment_bank("2018-01", transactions_for_investment_bank, 50)
    assert result == 462.51


def test_investment_bank_invalid_month(transactions_for_investment_bank):
    result = investment_bank("2010-01", transactions_for_investment_bank, 50)
    assert result == 0


def test_investment_bank_empty_data():
    transactions = []
    result = investment_bank("2018-01", transactions, 50)
    assert result == 0


def test_investment_bank_key_error():
    transactions = [{"Сумма операции": 50.00}]
    result = investment_bank("2018-01", transactions, 50)
    assert result == 0


@patch("src.services.get_dataframe_excel")
def test_get_transactions_for_investment(mock_get_dataframe_excel, df_excel_for_investment):
    mock_get_dataframe_excel.return_value = df_excel_for_investment
    result = get_transactions_for_investment("test_file.xlsx")
    expected_result = [
        {"Дата операции": "2021-12-31", "Сумма операции": -1000},
        {"Дата операции": "2021-12-30", "Сумма операции": -500},
        {"Дата операции": "2021-12-28", "Сумма операции": -100},
        {"Дата операции": "2021-12-26", "Сумма операции": -10},
        {"Дата операции": "2021-12-25", "Сумма операции": -50},
    ]
    assert result == expected_result
    mock_get_dataframe_excel.assert_called_once()


@patch("src.services.get_dataframe_excel")
def test_get_transactions_for_investment_empty_df(mock_get_dataframe_excel):
    mock_get_dataframe_excel.return_value = pd.DataFrame()
    result = get_transactions_for_investment("test_file.xlsx")
    assert result == []
