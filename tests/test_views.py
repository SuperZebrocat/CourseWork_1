from unittest.mock import patch

import pandas as pd

from src.views import main_page


@patch("src.views.get_user_stocks")
@patch("src.views.get_user_currency_rates")
@patch("src.views.top_five_transactions")
@patch("src.views.get_cards_info")
@patch("src.views.greeting")
@patch("src.views.get_dataframe_excel")
def test_main_page_success(
    mock_get_dataframe_excel,
    mock_greeting,
    mock_get_cards_info,
    mock_top_five_transactions,
    mock_get_user_currency_rates,
    mock_get_user_stocks,
    main_page_dict,
):
    mock_get_dataframe_excel.return_value = pd.DataFrame({"card_number": [1234, 5678], "amount": [1000.0, 2000.0]})
    mock_greeting.return_value = "Доброе утро"
    mock_get_cards_info.return_value = [
        {"last_digits": "1111", "total_spent": 1000, "cashback": 10},
        {"last_digits": "2222", "total_spent": 500, "cashback": 5},
        {"last_digits": "3333", "total_spent": 100, "cashback": 0},
    ]
    mock_top_five_transactions.return_value = [
        {"date": "31.12.2021", "amount": 1000, "category": "Перевод", "description": "Перевод"},
        {"date": "30.12.2021", "amount": 500, "category": "Вклад", "description": "Вклад"},
        {"date": "28.12.2021", "amount": 100, "category": "Налоги", "description": "Налоги"},
        {"date": "26.12.2021", "amount": 1, "category": "Перевод", "description": "Перевод"},
        {"date": "25.12.2021", "amount": 0, "category": "Оплата", "description": "Оплата"},
    ]
    mock_get_user_currency_rates.return_value = (
        [{"currency": "USD", "rate": 106.46}, {"currency": "EUR", "rate": 112.63}],
        106.46,
    )
    mock_get_user_stocks.return_value = [
        {"stock": "AAPL", "price": 500},
        {"stock": "GOOGL", "price": 400},
        {"stock": "TSLA", "price": 200},
    ]

    result_dict = main_page("2023-10-01 09:00:00")
    assert result_dict == main_page_dict
    mock_get_dataframe_excel.assert_called_once()
    mock_greeting.assert_called_once()
    mock_get_cards_info.assert_called_once()
    mock_top_five_transactions.assert_called_once()
    mock_get_user_currency_rates.assert_called_once()
    mock_get_user_stocks.assert_called_once()


@patch("src.views.get_user_stocks")
@patch("src.views.get_user_currency_rates")
@patch("src.views.top_five_transactions")
@patch("src.views.get_cards_info")
@patch("src.views.greeting")
@patch("src.views.get_dataframe_excel")
def test_main_page_empty_data(
    mock_get_dataframe_excel,
    mock_greeting,
    mock_get_cards_info,
    mock_top_five_transactions,
    mock_get_user_currency_rates,
    mock_get_user_stocks,
    main_page_dict,
):
    mock_get_dataframe_excel.return_value = pd.DataFrame()
    mock_greeting.return_value = ""
    mock_get_cards_info.return_value = []
    mock_top_five_transactions.return_value = []
    mock_get_user_currency_rates.return_value = ([], 0)
    mock_get_user_stocks.return_value = []

    result_dict = main_page("2023-10-01 09:00:00")
    assert result_dict == {
        "greeting": "",
        "cards": [],
        "top_transactions": [],
        "currency_rates": [],
        "stock_prices": [],
    }

    mock_get_dataframe_excel.assert_called_once()
    mock_greeting.assert_called_once()
    mock_get_cards_info.assert_called_once()
    mock_top_five_transactions.assert_called_once()
    mock_get_user_currency_rates.assert_called_once()
    mock_get_user_stocks.assert_called_once()
