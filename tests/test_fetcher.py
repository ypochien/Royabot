import polars as pl
import pytest

from royabot.fetcher import ParquetStore


class TestParquetStore:
    def test_display_stats_file_not_found(self):
        store = ParquetStore("nonexistent.parquet")
        store.display_stats()  # Should not raise

    def test_get_latest_date_file_not_found(self):
        store = ParquetStore("nonexistent.parquet")
        result = store.get_latest_date()
        assert result is None

    def test_save_and_read(self, tmp_path):
        filepath = str(tmp_path / "test.parquet")
        store = ParquetStore(filepath)
        df = pl.DataFrame(
            {
                "date": ["2024-01-15"],
                "code": ["2330"],
                "close": [580.0],
            }
        )
        store.save(df)
        lf = store.read_full()
        assert lf is not None
        assert lf.collect().shape[0] == 1

    def test_append_creates_file_if_not_exists(self, tmp_path):
        filepath = str(tmp_path / "test.parquet")
        store = ParquetStore(filepath)
        df = pl.DataFrame(
            {
                "date": ["2024-01-15"],
                "code": ["2330"],
                "close": [580.0],
            }
        )
        store.append(df)
        result = store.read_full()
        assert result.collect().shape[0] == 1

    def test_append_deduplicates_by_date_code(self, tmp_path):
        filepath = str(tmp_path / "test.parquet")
        store = ParquetStore(filepath)
        df1 = pl.DataFrame(
            {
                "date": ["2024-01-15"],
                "code": ["2330"],
                "close": [580.0],
            }
        )
        df2 = pl.DataFrame(
            {
                "date": ["2024-01-15"],
                "code": ["2330"],
                "close": [585.0],
            }
        )
        store.save(df1)
        store.append(df2, overwrite=True)
        result = store.read_full().collect()
        assert result.shape[0] == 1
        assert result["close"][0] == 585.0

    def test_append_same_date_different_code_not_deduped(self, tmp_path):
        filepath = str(tmp_path / "test.parquet")
        store = ParquetStore(filepath)
        df1 = pl.DataFrame(
            {
                "date": ["2024-01-15"],
                "code": ["2330"],
                "close": [580.0],
            }
        )
        df2 = pl.DataFrame(
            {
                "date": ["2024-01-15"],
                "code": ["2317"],
                "close": [105.0],
            }
        )
        store.save(df1)
        store.append(df2, overwrite=True)
        result = store.read_full().collect()
        assert result.shape[0] == 2

    def test_append_without_overwrite_keeps_existing(self, tmp_path):
        filepath = str(tmp_path / "test.parquet")
        store = ParquetStore(filepath)
        df1 = pl.DataFrame(
            {
                "date": ["2024-01-15"],
                "code": ["2330"],
                "close": [580.0],
            }
        )
        df2 = pl.DataFrame(
            {
                "date": ["2024-01-15"],
                "code": ["2330"],
                "close": [585.0],
            }
        )
        store.save(df1)
        store.append(df2, overwrite=False)
        result = store.read_full().collect()
        assert result.shape[0] == 1
        assert result["close"][0] == 580.0

    def test_save_empty_df_does_nothing(self, tmp_path):
        filepath = str(tmp_path / "test.parquet")
        store = ParquetStore(filepath)
        df = pl.DataFrame({"date": [], "code": [], "close": []})
        store.save(df)
        # File not created because df is empty (shape[0] == 0)
        import os
        assert not os.path.exists(filepath)

    def test_append_none_does_nothing(self, tmp_path):
        filepath = str(tmp_path / "test.parquet")
        store = ParquetStore(filepath)
        store.append(None)
        # File not created because None was passed
        import os
        assert not os.path.exists(filepath)

    def test_get_latest_date(self, tmp_path):
        filepath = str(tmp_path / "test.parquet")
        store = ParquetStore(filepath)
        df = pl.DataFrame(
            {
                "date": ["2024-01-15", "2024-01-16"],
                "code": ["2330", "2330"],
                "close": [580.0, 586.0],
            }
        )
        store.save(df)
        result = store.get_latest_date()
        assert result is not None
        assert str(result) == "2024-01-16"
