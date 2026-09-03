import os
from pathlib import Path

from dotenv import load_dotenv

# ============================================================
# 프로젝트 경로
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 크롤링 설정
# ============================================================

TARGET_URL = "https://data.seoul.go.kr/"
DATASET_URL = "https://data.seoul.go.kr/dataList/datasetList.do"

SEARCH_KEYWORD = "체육시설"

# 데이터셋 이름의 일부만 사용한다.
# 실제 검색 결과에는 '서울시 중랑구', '서울시 서초구'처럼
# 자치구명이 붙어 있기 때문에 정확한 전체 문자열 비교를 하지 않는다.
DATASET_KEYWORD = "체육시설 공공서비스예약 정보"

MIN_DATA_COUNT = 100

CRAWL_WAIT_SECONDS = 3
PAGE_WAIT_SECONDS = 2


# ============================================================
# 데이터 컬럼
# ============================================================

COLUMNS = [
    "서비스구분",
    "서비스ID",
    "대분류명",
    "소분류명",
    "서비스상태",
    "서비스명",
]


# ============================================================
# MySQL 설정
# ============================================================

TABLE_NAME = "sports_facility"


def load_database_config():
    """
    .env에서 MySQL 접속 정보를 읽는다.

    .env 예시:

    DB_HOST=호스트
    DB_USER=사용자
    DB_PASSWORD=비밀번호
    DB_NAME=sports_crawling
    """

    # 프로젝트 루트의 .env를 명시적으로 읽는다.
    env_path = PROJECT_ROOT / ".env"

    load_dotenv(dotenv_path=env_path)

    config = {
        "host": os.getenv("DB_HOST"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME"),
    }

    missing = [
        key
        for key, value in config.items()
        if value is None or value == ""
    ]

    if missing:
        raise RuntimeError(
            ".env에 다음 환경변수가 없습니다: "
            + ", ".join(missing)
        )

    return config