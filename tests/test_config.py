from pathlib import Path
from royabot import config


def test_parquet_filename_is_set():
    assert config.PARQUET_FILENAME == "daily_quotes.parquet"


def test_downloads_dir_is_path():
    assert isinstance(config.DOWNLOADS_DIR, Path)


def test_init_polars_runs_without_error():
    config.init_polars()
