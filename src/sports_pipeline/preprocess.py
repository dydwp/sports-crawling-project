import pandas as pd

from .config import COLUMNS


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:

    print("\n" + "=" * 60)
    print("Pandas 전처리 시작")
    print("=" * 60)

    if df is None or df.empty:
        raise RuntimeError(
            "전처리할 데이터가 없습니다."
        )

    print(
        f"원본 데이터: {len(df)}건"
    )

    # --------------------------------------------------------
    # 컬럼 확인
    # --------------------------------------------------------

    missing_columns = [
        column
        for column in COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise RuntimeError(
            "필수 컬럼이 없습니다: "
            + ", ".join(missing_columns)
        )

    df = df[COLUMNS].copy()

    # --------------------------------------------------------
    # 문자열 정리
    # --------------------------------------------------------

    for column in COLUMNS:

        df[column] = (
            df[column]
            .fillna("")
            .astype(str)
            .str.replace("\r", " ", regex=False)
            .str.replace("\n", " ", regex=False)
            .str.replace("\t", " ", regex=False)
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
        )

    # --------------------------------------------------------
    # 헤더 행 제거
    # --------------------------------------------------------

    before = len(df)

    header_mask = (
        df["서비스구분"].str.contains(
            "서비스구분",
            na=False
        )
        |
        df["서비스ID"].str.contains(
            "서비스ID",
            na=False
        )
        |
        df["서비스상태"].str.contains(
            "서비스상태",
            na=False
        )
    )

    df = df[
        ~header_mask
    ].copy()

    header_removed = before - len(df)

    if header_removed:
        print(
            f"헤더 행 제거: {header_removed}건"
        )

    # --------------------------------------------------------
    # 서비스ID 없는 행 제거
    # --------------------------------------------------------

    before = len(df)

    df = df[
        (df["서비스ID"] != "")
    ].copy()

    empty_id_removed = before - len(df)

    if empty_id_removed:
        print(
            f"서비스ID 없는 행 제거: "
            f"{empty_id_removed}건"
        )

    # --------------------------------------------------------
    # 서비스명 없는 행 제거
    # --------------------------------------------------------

    before = len(df)

    df = df[
        (df["서비스명"] != "")
    ].copy()

    empty_name_removed = before - len(df)

    if empty_name_removed:
        print(
            f"서비스명 없는 행 제거: "
            f"{empty_name_removed}건"
        )

    # --------------------------------------------------------
    # 중복 제거
    # --------------------------------------------------------

    duplicate_count = (
        df["서비스ID"].duplicated().sum()
    )

    if duplicate_count:
        df = df.drop_duplicates(
            subset=["서비스ID"],
            keep="first"
        )

        print(
            f"서비스ID 중복 제거: "
            f"{duplicate_count}건"
        )

    # --------------------------------------------------------
    # 인덱스 정리
    # --------------------------------------------------------

    df = df.reset_index(drop=True)

    # --------------------------------------------------------
    # 결과
    # --------------------------------------------------------

    print(
        f"전처리 완료: {len(df)}건"
    )

    return df