from typing import Any
from unittest.mock import mock_open, patch

import pandas as pd

from src.utils import (
    get_cards_info,
    get_dataframe_excel,
    get_user_currency_rates,
    get_user_stocks,
    greeting,
    top_five_transactions,
)


def test_greeting_morning():
    assert greeting("2023-10-01 06:00:00") == "Доброе утро"


def test_greeting_afternoon():
    assert greeting("2023-10-01 12:00:00") == "Добрый день"


def test_greeting_evening():
    assert greeting("2023-10-01 18:00:00") == "Добрый вечер"


def test_greeting_night():
    assert greeting("2023-10-01 00:00:00") == "Доброй ночи"


def test_greeting_invalid_format():
    assert greeting("01-10-2023 00:00:00") == ""


@patch("pandas.read_excel")
def test_get_dataframe_excel(mock_excel: Any) -> Any:
    mock_excel.return_value = pd.DataFrame({"card_number": [1234, 5678], "amount": [1000.0, 2000.0]})
    df_excel = get_dataframe_excel(file_path="test.xlsx")
    expected = pd.DataFrame({"card_number": [1234, 5678], "amount": [1000.0, 2000.0]})
    assert df_excel.equals(expected)


def test_get_dataframe_excel_file_not_found():
    df_excel = get_dataframe_excel(file_path="no_file")
    expected = pd.DataFrame()
    assert df_excel.equals(expected)


@patch("pandas.read_excel")
def test_get_dataframe_value_error(mock_excel):
    mock_excel.return_value = pd.DataFrame()
    df_excel = get_dataframe_excel(file_path="empty.xlsx")
    expected = pd.DataFrame()
    assert df_excel.equals(expected)


def test_get_cards_info(df_excel_test):
    assert get_cards_info(df_excel_test) == [
        {"last_digits": "1111", "total_spent": 1000, "cashback": 10},
        {"last_digits": "2222", "total_spent": 500, "cashback": 5},
        {"last_digits": "3333", "total_spent": 100, "cashback": 1},
    ]


def test_get_cards_info_empty_df():
    empty_df = pd.DataFrame()
    assert get_cards_info(empty_df) == []


def test_get_cards_info_type_error(df_excel_test_invalid):
    assert get_cards_info(df_excel_test_invalid) == []


def test_top_five_transactions(df_excel_top_5_test):
    assert top_five_transactions(df_excel_top_5_test) == [
        {"date": "31.12.2021", "amount": 1000, "category": "Перевод", "description": "Перевод"},
        {"date": "30.12.2021", "amount": 500, "category": "Вклад", "description": "Вклад"},
        {"date": "28.12.2021", "amount": 100, "category": "Налоги", "description": "Налоги"},
        {"date": "26.12.2021", "amount": 1, "category": "Перевод", "description": "Перевод"},
        {"date": "25.12.2021", "amount": 0, "category": "Оплата", "description": "Оплата"},
    ]


def test_top_five_transactions_empty_df():
    empty_df = pd.DataFrame()
    assert top_five_transactions(empty_df) == []


def test_top_five_transactions_type_error(df_excel_top_5_invalid):
    assert top_five_transactions(df_excel_top_5_invalid) == []


@patch("builtins.open", new_callable=mock_open, read_data='{"user_currencies": ["USD", "EUR"]}')
@patch("src.utils.get_currency_rates_api")
def test_get_user_currency_rates(mock_get_currency_rates_api, mock_file):
    mock_get_currency_rates_api.return_value = {"rates": {"USD": 0.009393, "EUR": 0.008879}}
    currency_rates_list, rub_rate_usd = get_user_currency_rates("test_file")
    mock_get_currency_rates_api.assert_called_once()
    assert currency_rates_list == [{"currency": "USD", "rate": 106.46}, {"currency": "EUR", "rate": 112.63}]
    assert rub_rate_usd == 106.46


@patch("src.utils.get_currency_rates_api")
def test_get_user_currency_empty_response(mock_get_currency_rates_api):
    mock_get_currency_rates_api.return_value = {}
    currency_rates_list, rub_rate_usd = get_user_currency_rates("test_file")
    assert currency_rates_list == []
    assert rub_rate_usd == 0
    mock_get_currency_rates_api.assert_called_once()


@patch("src.utils.get_currency_rates_api")
def test_get_user_currency_zero_division(mock_get_currency_rates_api):
    mock_get_currency_rates_api.return_value = {"rates": {"USD": 0}}
    currency_rates_list, rub_rate_usd = get_user_currency_rates("test_file")
    mock_get_currency_rates_api.assert_called_once()
    assert currency_rates_list == []
    assert rub_rate_usd == 0


@patch("builtins.open", new_callable=mock_open, read_data='{"user_stocks": ["AAPL", "GOOGL", "TSLA"]}')
@patch("src.utils.get_stocks_api")
@patch("src.utils.get_user_currency_rates")
def test_get_user_stocks(mock_get_user_currency_rates, mock_get_stocks_api, mock_file):
    mock_get_stocks_api.return_value = [
        {"symbol": "PACI-WT", "price": 1, "type": "stock"},
        {"symbol": "TSLA", "price": 2, "type": "stock"},
        {"symbol": "SEC0.F", "price": 3, "type": "stock"},
        {"symbol": "GOOGL", "price": 4, "type": "stock"},
        {"symbol": "AAPL", "price": 5, "type": "stock"},
    ]
    mock_get_user_currency_rates.return_value = ([], 100)
    user_stocks_list = get_user_stocks("test_file")
    mock_get_stocks_api.assert_called_once()
    mock_get_user_currency_rates.assert_called_once()
    assert user_stocks_list == [
        {"stock": "AAPL", "price": 500},
        {"stock": "GOOGL", "price": 400},
        {"stock": "TSLA", "price": 200},
    ]


def test_get_user_stocks_file_not_found():
    file_path = "file_not_found.json"
    assert get_user_stocks(file_path) == []


@patch("builtins.open", new_callable=mock_open, read_data="")
def test_get_user_stocks_invalid_data(mock_file):
    result = get_user_stocks("invalid_data.json")
    assert result == []


@patch("builtins.open", new_callable=mock_open, read_data='{"user_stocks": ["AAPL", "GOOGL", "TSLA"]}')
@patch("src.utils.get_stocks_api")
def test_get_user_stocks_empty_api_response(mock_get_stocks_api, mock_file):
    mock_get_stocks_api.return_value = []
    user_stocks_list = get_user_stocks("test_file")
    mock_get_stocks_api.assert_called_once()
    assert user_stocks_list == []


@patch("builtins.open", new_callable=mock_open, read_data='{"user_stocks": ["AAPL", "GOOGL", "TSLA"]}')
@patch("src.utils.get_stocks_api")
@patch("src.utils.get_user_currency_rates")
def test_get_user_stocks_zero_rub_rate(mock_get_user_currency_rates, mock_get_stocks_api, mock_file):
    mock_get_stocks_api.return_value = [
        {"symbol": "PACI-WT", "price": 1, "type": "stock"},
        {"symbol": "TSLA", "price": 2, "type": "stock"},
        {"symbol": "SEC0.F", "price": 3, "type": "stock"},
        {"symbol": "GOOGL", "price": 4, "type": "stock"},
        {"symbol": "AAPL", "price": 5, "type": "stock"},
    ]
    mock_get_user_currency_rates.return_value = ([], 0)
    user_stocks_list = get_user_stocks("test_file")
    mock_get_stocks_api.assert_called_once()
    mock_get_user_currency_rates.assert_called_once()
    assert user_stocks_list == []
