# add_natr requires TA-Lib C library and enough data points per stock code.
# These tests are skipped if TA-Lib is not installed.

import pytest

try:
    import talib

    HAS_TALIB = True
except ImportError:
    HAS_TALIB = False


@pytest.mark.skipif(not HAS_TALIB, reason="TA-Lib not installed")
def test_add_natr_returns_natr_column(sample_market_df):
    from royabot.indicators import add_natr

    result = add_natr(sample_market_df, timeperiod=1)
    assert "natr" in result.columns
    assert result.shape[0] == sample_market_df.shape[0]
