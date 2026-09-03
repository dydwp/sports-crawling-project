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


def main():

    start_time = time.time()

    print()
    print("#" * 60)
    print("서울시 체육시설 데이터 크롤링 파이프라인")
    print("#" * 60)

    try:

        # ====================================================
        # 1. Selenium
        # ====================================================

        df = crawl_data()

        if df.empty:
            raise RuntimeError(
                "수집된 데이터가 없습니다."
            )

        print(
            f"\n[Crawler 결과] {len(df)}건"
        )

        # 최소 데이터 수 확인
        if len(df) < 100:
            raise RuntimeError(
                f"수집 데이터가 100건 미만입니다: "
                f"{len(df)}건"
            )

        # ====================================================
        # 2. 데이터 품질 검증
        # ====================================================

        validate_data(df)

        # ====================================================
        # 3. Pandas 전처리
        # ====================================================

        df = preprocess_data(df)

        if df.empty:
            raise RuntimeError(
                "전처리 후 데이터가 없습니다."
            )

        print(
            f"\n[Preprocess 결과] {len(df)}건"
        )

        # ====================================================
        # 4. CSV
        # ====================================================

        print("\n" + "=" * 60)
        print("CSV 저장")
        print("=" * 60)

        files = save_csv(
            df,
            raw=True,
            processed=True
        )

        print(
            f"Raw CSV: {files['raw']}"
        )

        print(
            f"Processed CSV: {files['processed']}"
        )

        print(
            f"저장 데이터: {len(df)}건"
        )

        # ====================================================
        # 5. MySQL
        # ====================================================

        print("\n" + "=" * 60)
        print("MySQL 데이터 저장")
        print("=" * 60)

        config = load_database_config()

        create_database_and_table(
            config
        )

        db_count = save_to_mysql(
            df,
            config
        )

        print(
            f"DB 저장 완료: {db_count}건"
        )

        # ====================================================
        # 6. 최종 결과
        # ====================================================

        elapsed = round(
            time.time() - start_time,
            2
        )

        print("\n" + "=" * 60)
        print("파이프라인 완료")
        print("=" * 60)

        print(
            f"크롤링 데이터: {len(df)}건"
        )

        print(
            f"CSV 데이터: {len(df)}건"
        )

        print(
            f"DB 데이터: {db_count}건"
        )

        print(
            f"처리 시간: {elapsed}초"
        )

        # CSV와 DB 개수 일치 여부
        if len(df) == db_count:

            print(
                "데이터 정합성: 정상"
            )

        else:

            raise RuntimeError(
                "CSV와 DB 데이터 개수가 일치하지 않습니다."
            )

        print()
        print("전체 작업 완료")

    except Exception as e:

        print("\n" + "=" * 60)
        print("작업 실패")
        print("=" * 60)

        print(
            f"{type(e).__name__}: {e}"
        )

        raise


if __name__ == "__main__":
    main()