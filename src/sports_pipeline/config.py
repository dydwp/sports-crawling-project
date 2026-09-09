import os
from pathlib import Path

# ============================================================
# 프로젝트 경로
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR = Path(os.getenv("DATA_DIR", str(DEFAULT_DATA_DIR)))
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

ENV_FILE = PROJECT_ROOT / ".env"