import pytest
import polars as pl
from royabot.config import init_polars


@pytest.fixture(autouse=True, scope="session")
def setup_polars():
    """Initialize polars config once for the test session."""
    init_polars()


@pytest.fixture
def sample_market_df() -> pl.DataFrame:
    """Provide a sample market data DataFrame for testing."""
    return pl.DataFrame(
        {
            "date": ["2024-01-15", "2024-01-15", "2024-01-16", "2024-01-16"],
            "code": ["2330", "2317", "2330", "2317"],
            "open": [580.0, 105.0, 582.0, 106.0],
            "high": [585.0, 106.0, 588.0, 107.0],
            "low": [578.0, 104.0, 580.0, 105.0],
            "close": [583.0, 105.5, 586.0, 106.5],
            "volume": [30000, 20000, 31000, 21000],
        }
    )
