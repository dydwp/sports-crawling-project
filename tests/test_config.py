import pytest

from src.sports_pipeline.config import (
    COLUMNS,
    DATASET_KEYWORD,
    MIN_DATA_COUNT,
    load_database_config,
)


def test_columns_definition():
    assert COLUMNS == [
        "서비스구분",
        "서비스ID",
        "대분류명",
        "소분류명",
        "서비스상태",
        "서비스명",
    ]


def test_min_data_count_is_100():
    assert MIN_DATA_COUNT == 100


def test_dataset_keyword_is_set():
    assert "체육시설" in DATASET_KEYWORD


def test_load_database_config_raises_when_env_missing(monkeypatch, tmp_path):
    # 실제 .env를 건드리지 않도록 존재하지 않는 빈 경로를 가리키게 한다.
    monkeypatch.delenv("DB_HOST", raising=False)
    monkeypatch.delenv("DB_USER", raising=False)
    monkeypatch.delenv("DB_PASSWORD", raising=False)
    monkeypatch.delenv("DB_NAME", raising=False)

    monkeypatch.setattr(
        "src.sports_pipeline.config.PROJECT_ROOT",
        tmp_path,
    )

    with pytest.raises(RuntimeError):
        load_database_config()
