from unittest.mock import mock_open, patch

import requests

from src.external_api import get_currency_rates_api, get_stocks_api


@patch("requests.get")
@patch("builtins.open", new_callable=mock_open, read_data='{"user_currencies": ["USD", "EUR"]}')
def test_get_currency_rates_api(mock_file, mock_get):
    mock_response = {
        "success": True,
        "timestamp": 1732278484,
        "base": "RUB",
        "date": "2024-11-22",
        "rates": {"USD": 0.009706, "EUR": 0.009331},
    }
    mock_get.return_value.json.return_value = mock_response
    mock_get.return_value.status_code = 200
    assert get_currency_rates_api("test_user_settings.json") == mock_response
    mock_get.assert_called_once()


@patch("builtins.open", new_callable=mock_open, read_data='{"user_currencies": []}')
def test_get_currency_rates_api_empty_currency_list(mock_file):
    result = get_currency_rates_api(mock_file)
    assert result == {}


@patch("builtins.open", new_callable=mock_open, read_data="")
def test_get_currency_rates_api_empty_data(mock_file):
    result = get_currency_rates_api(mock_file)
    assert result == {}


def test_get_currency_rates_api_file_not_found():
    file_path = "file_not_found.json"
    assert get_currency_rates_api(file_path) == {}


@patch("requests.get")
@patch("builtins.open", new_callable=mock_open, read_data='{"user_currencies": ["USD", "EUR"]}')
def test_get_currency_rates_api_request_exception(mock_file, mock_get):
    mock_get.side_effect = requests.exceptions.RequestException()
    result = get_currency_rates_api("test_user_settings.json")
    assert result == {}
    mock_get.assert_called_once()


@patch("requests.get")
def test_get_stocks_api(mock_get):
    mock_response = [
        {"symbol": "ABC", "price": 10, "type": "etf"},
        {"symbol": "DFG", "price": 20, "type": "stock"},
        {"symbol": "HIJ", "price": 30, "type": "stock"},
    ]
    mock_get.return_value.json.return_value = mock_response
    mock_get.return_value.status_code = 200
    result = get_stocks_api()
    assert result == mock_response
    mock_get.assert_called_once()


@patch("requests.get")
def test_get_stocks_api_request_exception(mock_get):
    mock_get.side_effect = requests.exceptions.RequestException()
    result = get_stocks_api()
    assert result == []
    mock_get.assert_called_once()
