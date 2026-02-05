import polars as pl

from royabot.data_processing import get_latest_date_data


def test_get_latest_date_data():
    df = pl.DataFrame(
        {
            "date": ["2024-01-15", "2024-01-16", "2024-01-16"],
            "code": ["2330", "2330", "2317"],
            "close": [580.0, 586.0, 106.5],
        }
    )
    result = get_latest_date_data(df)
    assert result.shape[0] == 2
    assert all(d == "2024-01-16" for d in result["date"].to_list())


def test_get_latest_date_data_single_date():
    df = pl.DataFrame(
        {
            "date": ["2024-01-15", "2024-01-15"],
            "code": ["2330", "2317"],
            "close": [580.0, 105.5],
        }
    )
    result = get_latest_date_data(df)
    assert result.shape[0] == 2
