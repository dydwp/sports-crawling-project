import pandas as pd
import pytest

from src.sports_pipeline.config import COLUMNS
from src.sports_pipeline.quality import validate_data


def make_df(rows):
    return pd.DataFrame(rows, columns=COLUMNS)


def test_validate_passes_on_clean_data():
    df = make_df([
        ["자체", "S001", "체육시설", "축구장", "접수중", "축구장A"],
        ["자체", "S002", "체육시설", "농구장", "접수중", "농구장A"],
    ])

    # 예외 없이 통과해야 한다.
    validate_data(df)


def test_validate_raises_on_null_service_id():
    df = make_df([
        ["자체", None, "체육시설", "축구장", "접수중", "축구장A"],
    ])

    with pytest.raises(RuntimeError):
        validate_data(df)


def test_validate_raises_on_empty_service_id():
    df = make_df([
        ["자체", "", "체육시설", "축구장", "접수중", "축구장A"],
    ])

    with pytest.raises(RuntimeError):
        validate_data(df)


def test_validate_raises_on_duplicate_service_id():
    df = make_df([
        ["자체", "S001", "체육시설", "축구장", "접수중", "축구장A"],
        ["자체", "S001", "체육시설", "축구장", "접수중", "축구장A(중복)"],
    ])

    with pytest.raises(RuntimeError):
        validate_data(df)


def test_validate_raises_on_empty_dataframe():
    df = make_df([])

    with pytest.raises(RuntimeError):
        validate_data(df)
