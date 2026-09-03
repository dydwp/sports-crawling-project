import pandas as pd
import pytest

from src.sports_pipeline.config import COLUMNS
from src.sports_pipeline.preprocess import preprocess_data


def make_df(rows):
    """테스트용 DataFrame 생성 헬퍼."""
    return pd.DataFrame(rows, columns=COLUMNS)


def test_preprocess_removes_header_row():
    df = make_df([
        ["서비스구분", "서비스ID", "대분류명", "소분류명", "서비스상태", "서비스명"],
        ["자체", "S001", "체육시설", "축구장", "접수중", "잠원한강공원 축구장"],
    ])

    result = preprocess_data(df)

    assert len(result) == 1
    assert result.iloc[0]["서비스ID"] == "S001"


def test_preprocess_removes_empty_service_id():
    df = make_df([
        ["자체", "", "체육시설", "축구장", "접수중", "이름만 있는 행"],
        ["자체", "S002", "체육시설", "농구장", "접수중", "농구장1"],
    ])

    result = preprocess_data(df)

    assert len(result) == 1
    assert result.iloc[0]["서비스ID"] == "S002"


def test_preprocess_removes_duplicate_service_id():
    df = make_df([
        ["자체", "S003", "체육시설", "농구장", "접수중", "농구장A"],
        ["자체", "S003", "체육시설", "농구장", "접수중", "농구장A(중복)"],
    ])

    result = preprocess_data(df)

    assert len(result) == 1
    assert result.iloc[0]["서비스명"] == "농구장A"


def test_preprocess_strips_whitespace():
    df = make_df([
        ["자체 ", " S004", "체육시설", "축구장", " 접수중", "  잠실 축구장  "],
    ])

    result = preprocess_data(df)

    assert result.iloc[0]["서비스ID"] == "S004"
    assert result.iloc[0]["서비스명"] == "잠실 축구장"


def test_preprocess_raises_on_empty_dataframe():
    df = make_df([])

    with pytest.raises(RuntimeError):
        preprocess_data(df)


def test_preprocess_raises_on_missing_columns():
    df = pd.DataFrame([{"엉뚱한컬럼": "값"}])

    with pytest.raises(RuntimeError):
        preprocess_data(df)
