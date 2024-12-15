from unittest.mock import MagicMock, patch

import pandas as pd

from src.reports import PATH_FILE_REPORT, save_report_to_excel, spending_by_category, spending_by_category_dict


def test_spending_by_category_if_date(df_excel_for_report, df_excel_for_report_expected):
    result = spending_by_category(df_excel_for_report, "Перевод", "2021-12-31")
    expected_df = pd.DataFrame(df_excel_for_report_expected)
    expected_df["Дата платежа"] = pd.to_datetime(expected_df["Дата платежа"], format="%d.%m.%Y")
    pd.testing.assert_frame_equal(result, expected_df)


@patch("src.reports.datetime")
def test_spending_by_category_if_not_date(mock_datetime, df_excel_for_report, df_excel_for_report_expected):
    mock_date = "2021-12-31 22:12:59.264523"
    mock_datetime.now.return_value = pd.to_datetime(mock_date)
    result = spending_by_category(df_excel_for_report, "Перевод")
    mock_datetime.now.assert_called_once()
    expected_df = pd.DataFrame(df_excel_for_report_expected)
    expected_df["Дата платежа"] = pd.to_datetime(expected_df["Дата платежа"], format="%d.%m.%Y")
    pd.testing.assert_frame_equal(result, expected_df)


def test_spending_by_category_empty_df():
    transactions = pd.DataFrame()
    result = spending_by_category(transactions, "Перевод", "2021-12-31")
    expected_result = pd.DataFrame()
    pd.testing.assert_frame_equal(result, expected_result)


def test_spending_by_category_unknown_category(df_excel_for_report):
    result = spending_by_category(df_excel_for_report, "Супермаркеты", "2021-12-31")
    assert result.empty


@patch("src.reports.pd.DataFrame.to_excel")
def test_save_to_excel_success(mock_to_excel, df_excel_for_report, df_excel_for_report_expected):
    result = spending_by_category(df_excel_for_report, "Перевод", "2021-12-31")
    mock_to_excel.assert_called_once_with(PATH_FILE_REPORT, index=False)
    expected_result = df_excel_for_report_expected
    pd.testing.assert_frame_equal(result, expected_result)


def test_decorator_does_not_call_to_excel_if_empty_df():
    mock_to_excel = MagicMock()
    pd.DataFrame.to_excel = mock_to_excel

    @save_report_to_excel(filename=PATH_FILE_REPORT)
    def spending_by_category_empty_df():
        return pd.DataFrame()

    spending_by_category_empty_df()
    mock_to_excel.assert_not_called()


def test_spending_by_category_dict(df_excel_for_report_expected):
    result = spending_by_category_dict(df_excel_for_report_expected)
    assert result == {"category": "Перевод", "total_spent": 4010.00}


def test_spending_by_category_dict_empty_df():
    transactions = pd.DataFrame()
    result = spending_by_category_dict(transactions)
    assert result == {}


def test_spending_by_category_dict_key_error(df_excel_no_columns):
    result = spending_by_category_dict(df_excel_no_columns)
    assert result == {}


def test_spending_by_category_dict_value_error(df_excel_invalid_sum):
    result = spending_by_category_dict(df_excel_invalid_sum)
    assert result == {}
