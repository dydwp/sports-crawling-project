"""
서울시 체육시설 데이터 크롤링 파이프라인을 실행하는
AWS Lambda Handler입니다.

Selenium 크롤링 → 품질 검증 → 전처리 → CSV 저장 → RDS MySQL 적재까지
하나의 Lambda 안에서 순서대로 실행합니다.
"""

import time

from src.sports_pipeline import (
    crawl_data,
    create_database_and_table,
    load_database_config,
    preprocess_data,
    save_csv,
    save_to_mysql,
    validate_data,
)


def lambda_handler(event: dict | None, context: object) -> dict[str, object]:
    """
    서울시 체육시설 데이터 크롤링 파이프라인의 Lambda 진입점입니다.
    """

    if event is None:
        event = {}

    start_time = time.time()

    print("=" * 60)
    print("서울시 체육시설 데이터 크롤링 파이프라인 (Lambda)")
    print("=" * 60)

    # --------------------------------------------------------
    # 1. Selenium 크롤링
    # --------------------------------------------------------

    df = crawl_data()

    if df.empty:
        raise RuntimeError("수집된 데이터가 없습니다.")

    print(f"\n[Crawler 결과] {len(df)}건")

    # --------------------------------------------------------
    # 2. 데이터 품질 검증
    # --------------------------------------------------------

    validate_data(df)

    # --------------------------------------------------------
    # 3. Pandas 전처리
    # --------------------------------------------------------

    df = preprocess_data(df)

    if df.empty:
        raise RuntimeError("전처리 후 데이터가 없습니다.")

    print(f"\n[Preprocess 결과] {len(df)}건")

    # --------------------------------------------------------
    # 4. CSV 저장 (Lambda의 /tmp에 저장, 다음 실행 때 사라짐)
    # --------------------------------------------------------

    files = save_csv(df, raw=True, processed=True)

    # --------------------------------------------------------
    # 5. MySQL 적재
    # --------------------------------------------------------

    config = load_database_config()

    create_database_and_table(config)

    db_count = save_to_mysql(df, config)

    # --------------------------------------------------------
    # 6. 정합성 확인
    # --------------------------------------------------------

    if len(df) != db_count:
        raise RuntimeError("CSV와 DB 데이터 개수가 일치하지 않습니다.")

    elapsed = round(time.time() - start_time, 2)

    request_id = getattr(context, "aws_request_id", None)

    print(f"\n파이프라인 완료: {db_count}건, {elapsed}초")

    return {
        "stage": "pipeline",
        "status": "SUCCEEDED",
        "crawled_count": len(df),
        "db_count": db_count,
        "elapsed_seconds": elapsed,
        "raw_csv": str(files["raw"]),
        "processed_csv": str(files["processed"]),
        "request_id": request_id,
    }