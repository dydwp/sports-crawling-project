# 서울시 체육시설 공공서비스예약 데이터 크롤링 & 적재 프로젝트

서울열린데이터광장에서 제공하는 서울시 체육시설 공공서비스예약 데이터를 Selenium으로 동적 크롤링하고, Pandas로 전처리한 뒤 MySQL 데이터베이스에 적재하는 프로젝트입니다.

## 프로젝트 개요

- **분석/수집 목적**: 공공서비스예약 사이트의 체육시설 정보를 자동으로 수집하여 데이터베이스화
- **데이터 출처**: [서울열린데이터광장](https://data.seoul.go.kr) - 서울시 체육시설 공공서비스예약 정보
- **수집 방식**: API 대신 Selenium 기반 동적 크롤링 (URL 방식)

## 수집 항목

- 서비스구분
- 서비스ID
- 대분류명
- 소분류명
- 서비스상태
- 서비스명

## 파이프라인 구조

```
01. Selenium 크롤링 (01_environment_selenium_crawling_clean.ipynb)
        ↓ CSV 중간 저장 (sports_crawling_raw.csv)
02. Pandas 전처리 (02_preprocessing.ipynb)
        ↓ 결측치/중복 제거, 문자열 정리
        ↓ CSV 저장 (전처리 완료 데이터)
03. MySQL 적재 (03_database.ipynb)
        ↓ DB/테이블 생성 후 저장 및 검증
```

`sports_crawling.py`는 위 01~03단계 전체를 하나의 스크립트로 통합해 자동 실행할 수 있도록 만든 버전입니다.

## 분석 환경

- Language: Python 3
- Library: Selenium, Pandas, mysql-connector-python, python-dotenv
- Database: MySQL
- Tool: Jupyter Lab, Chrome WebDriver

## 실행 방법

### 1. 패키지 설치

```bash
pip install selenium pandas mysql-connector-python python-dotenv
```

### 2. 환경변수 설정

프로젝트 루트에 `.env` 파일을 만들고 아래 항목을 채워주세요. (`.env`는 절대 GitHub에 올리지 않습니다.)

```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=sports_crawling
```

### 3. 실행

노트북을 순서대로(01 → 02 → 03) 실행하거나, 통합 스크립트를 실행합니다.

```bash
python sports_crawling.py
```

## 폴더 구조

```
├── 01_environment_selenium_crawling_clean.ipynb   # 1단계: Selenium 크롤링
├── 02_preprocessing.ipynb                          # 2단계: 데이터 전처리
├── 03_database.ipynb                               # 3단계: MySQL 적재
├── sports_crawling.py                              # 전체 파이프라인 통합 스크립트
├── sports_crawling_raw.csv                         # 크롤링 원본 데이터
├── sports_crawling_요구사항_정의서.docx              # 요구사항 정의서
├── .env                                            # DB 접속 정보 (Git 제외 대상)
└── README.md
```
