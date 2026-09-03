# 서울시 체육시설 공공서비스예약 데이터 크롤링 & 적재 프로젝트

서울열린데이터광장에서 제공하는 서울시 체육시설 공공서비스예약 데이터를 Selenium으로 동적 크롤링하고, Pandas로 전처리한 뒤 MySQL 데이터베이스에 적재하는 프로젝트입니다.

## 프로젝트 개요

- **수집 목적**: 서울시 각 자치구의 체육시설 공공서비스예약 정보를 자동으로 수집하여 데이터베이스화
- **데이터 출처**: [서울열린데이터광장](https://data.seoul.go.kr) - "체육시설" 키워드로 검색되는 자치구별 데이터셋
- **수집 방식**: API 대신 Selenium 기반 동적 크롤링
- **목표 수집량**: 최소 100건 이상

## 수집 항목

| 컬럼 | 설명 |
|---|---|
| 서비스구분 | 자체/위탁 등 서비스 구분 |
| 서비스ID | 서비스 고유 ID (PK) |
| 대분류명 | 대분류명 (체육시설) |
| 소분류명 | 시설 종류 (축구장, 농구장 등) |
| 서비스상태 | 접수중 / 접수종료 / 예약마감 등 |
| 서비스명 | 서비스(시설) 이름 |

## 파이프라인 구조

```
main.py
  └─ crawl_data()            # Selenium: 데이터셋 검색 → 자치구별 순회 크롤링
  └─ validate_data()         # 품질 검증 (결측/중복/빈 문자열)
  └─ preprocess_data()       # Pandas 전처리 (헤더 제거, strip, 중복 제거)
  └─ save_csv()              # data/raw, data/processed에 날짜별 CSV 저장
  └─ load_database_config()  # .env에서 MySQL 접속 정보 로드
  └─ create_database_and_table()
  └─ save_to_mysql()         # 기존 데이터 삭제 후 이번 실행 결과만 저장
```

## 분석/개발 환경

- Language: Python 3
- Library: Selenium, Pandas, mysql-connector-python, python-dotenv, pytest
- Database: MySQL
- Tool: Jupyter Lab (탐색/검증용), Chrome WebDriver

## 실행 방법

### 1. 패키지 설치

```bash
pip install -r requirements.txt
```

테스트/린트까지 실행하려면 개발용 의존성(pytest, ruff)을 추가로 설치합니다. `requirements-dev.txt`가 `requirements.txt`를 상속하므로 이 한 줄이면 됩니다.

```bash
pip install -r requirements-dev.txt
```

### 2. 환경변수 설정

프로젝트 루트에 `.env` 파일을 만들고 아래 항목을 채워주세요. (`.env`는 절대 GitHub에 올리지 않습니다.)

```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=sports_crawling
```

### 3. 파이프라인 실행

```bash
python main.py
```

### 4. 테스트 실행

Selenium/DB 없이 동작하는 순수 로직(전처리, 품질 검증, 설정)에 대한 단위 테스트입니다.

```bash
pytest tests/ -v
```

## 폴더 구조

```
sports-crawling-project/
│
├── main.py                      # 파이프라인 실행 진입점
├── requirements.txt
├── .env                         # DB 접속 정보 (Git 제외 대상)
│
├── notebooks/                   # 탐색/검증용 Jupyter 노트북
│   ├── 01_environment_selenium_crawling_clean.ipynb
│   ├── 02_preprocessing.ipynb
│   └── 03_database.ipynb
│
├── src/
│   └── sports_pipeline/         # 파이프라인 모듈
│       ├── config.py            # 경로/URL/컬럼 등 설정값
│       ├── crawler.py           # Selenium 크롤링
│       ├── preprocess.py        # Pandas 전처리
│       ├── quality.py           # 데이터 품질 검증
│       ├── csv_writer.py        # CSV 저장
│       └── database.py          # MySQL 저장
│
├── tests/                       # pytest 단위 테스트
│   ├── conftest.py
│   ├── test_config.py
│   ├── test_preprocess.py
│   └── test_quality.py
│
├── data/
│   ├── raw/                     # 크롤링 원본 CSV (날짜별)
│   └── processed/               # 전처리 완료 CSV (날짜별)
│
└── .github/workflows/ci.yml     # GitHub Actions CI
```
