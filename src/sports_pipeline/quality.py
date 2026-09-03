def validate_data(df):

    print("\n" + "=" * 60)
    print("데이터 품질 검증")
    print("=" * 60)

    if df is None or df.empty:
        raise RuntimeError(
            "품질 검증할 데이터가 없습니다."
        )

    total_count = len(df)

    null_id_count = (
        df["서비스ID"]
        .isnull()
        .sum()
    )

    empty_id_count = (
        df["서비스ID"]
        .astype(str)
        .str.strip()
        .eq("")
        .sum()
    )

    duplicate_id_count = (
        df["서비스ID"]
        .duplicated()
        .sum()
    )

    print(
        f"전체 데이터: {total_count}건"
    )

    print(
        f"서비스ID 결측: {null_id_count}건"
    )

    print(
        f"서비스ID 빈 문자열: {empty_id_count}건"
    )

    print(
        f"서비스ID 중복: {duplicate_id_count}건"
    )

    if null_id_count > 0:
        raise RuntimeError(
            "서비스ID에 결측값이 존재합니다."
        )

    if empty_id_count > 0:
        raise RuntimeError(
            "서비스ID에 빈 문자열이 존재합니다."
        )

    if duplicate_id_count > 0:
        raise RuntimeError(
            "서비스ID가 중복됩니다."
        )

    print("데이터 품질 검증 완료")