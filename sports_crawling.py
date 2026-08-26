import os
import time

import pandas as pd
import mysql.connector
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

TARGET_URL = 'https://data.seoul.go.kr/'
DATASET_URL = 'https://data.seoul.go.kr/dataList/datasetList.do'
SEARCH_KEYWORD = '체육시설'
DATASET_NAME = '서울시 체육시설 공공서비스예약 정보'
CSV_FILE = 'sports_crawling_raw.csv'
COLUMNS = ['서비스구분', '서비스ID', '대분류명', '소분류명', '서비스상태', '서비스명']


def load_database_config():
    load_dotenv()
    config = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('DB_NAME')
    }
    missing = [key for key, value in config.items() if value is None]
    if missing:
        raise RuntimeError('.env에 다음 환경변수가 없습니다: ' + ', '.join(missing))
    return config


def create_driver():
    options = Options()
    options.add_argument('--start-maximized')
    return webdriver.Chrome(options=options)


def crawl_data():
    print('=' * 60)
    print('1. Selenium 크롤링 시작')
    print('=' * 60)
    driver = create_driver()
    wait = WebDriverWait(driver, 10)
    data = []
    try:
        driver.get(TARGET_URL)
        print('사이트 접속 완료')
        print('현재 URL:', driver.current_url)
        print('페이지 제목:', driver.title)
        driver.get(DATASET_URL)

        search_input = wait.until(EC.element_to_be_clickable((By.ID, 'searchKeyword')))
        search_input.click()
        search_input.clear()
        search_input.send_keys(SEARCH_KEYWORD)
        print('검색어 입력 완료:', SEARCH_KEYWORD)

        search_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-ico[title='공공데이터 검색']")))
        search_button.click()
        print('검색 버튼 클릭 완료')
        time.sleep(2)

        dataset_link = wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[contains(normalize-space(.), '{DATASET_NAME}') ]")))
        dataset_link.click()
        print('대상 데이터셋 이동 완료')
        print('데이터셋:', DATASET_NAME)

        data_table = wait.until(EC.presence_of_element_located((By.ID, 'AXGridTarget_AX_gridBodyTable')))
        time.sleep(2)
        rows = data_table.find_elements(By.CSS_SELECTOR, 'tbody#AXGridTarget_AX_tbody tr')
        print('검색된 Grid 행:', len(rows))

        for row in rows:
            cells = row.find_elements(By.TAG_NAME, 'td')
            if len(cells) < 6:
                continue
            values = [cells[i].text.strip() for i in range(6)]
            if not values[1]:
                continue
            data.append(values)
        print('실제 수집 데이터:', len(data), '건')
    except Exception as e:
        print('크롤링 중 오류 발생')
        print('오류 유형:', type(e).__name__)
        print('오류 내용:', e)
        raise
    finally:
        driver.quit()
        print('Selenium WebDriver 종료')
    return pd.DataFrame(data, columns=COLUMNS)


def preprocess_data(df):
    print('\n' + '=' * 60)
    print('2. Pandas 전처리 시작')
    print('=' * 60)
    print('원본 데이터 크기:', df.shape)
    print('\n[결측치 확인]')
    print(df.isnull().sum())
    print('\n전체 행 중복:', df.duplicated().sum(), '건')
    print('서비스ID 중복:', df['서비스ID'].duplicated().sum(), '건')
    df = df.drop_duplicates(subset=['서비스ID'], keep='first')
    for column in COLUMNS:
        df[column] = df[column].fillna('').astype(str).str.strip()
    print('\n[서비스 상태별 데이터]')
    print(df['서비스상태'].value_counts())
    print('\n전처리 후 데이터 크기:', df.shape)
    print(df)
    return df


def save_csv(df):
    print('\n' + '=' * 60)
    print('3. CSV 저장')
    print('=' * 60)
    df.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')
    print('CSV 저장 완료')
    print('파일:', CSV_FILE)
    print('데이터:', len(df), '건')


def create_database_and_table(config):
    print('\n' + '=' * 60)
    print('4. MySQL DB 및 테이블 준비')
    print('=' * 60)
    server_conn = mysql.connector.connect(host=config['host'], user=config['user'], password=config['password'])
    server_cursor = server_conn.cursor()
    database_name = config['database']
    server_cursor.execute(f'''CREATE DATABASE IF NOT EXISTS `{database_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci''')
    server_conn.commit()
    server_cursor.close()
    server_conn.close()

    conn = mysql.connector.connect(host=config['host'], user=config['user'], password=config['password'], database=database_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sports_facility (
            서비스구분 VARCHAR(20),
            서비스ID VARCHAR(30) PRIMARY KEY,
            대분류명 VARCHAR(50),
            소분류명 VARCHAR(50),
            서비스상태 VARCHAR(20),
            서비스명 VARCHAR(500)
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
    ''')
    conn.commit()
    cursor.close()
    conn.close()
    print('데이터베이스 준비 완료')
    print('DB:', database_name)
    print('TABLE: sports_facility')


def save_to_mysql(df, config):
    print('\n' + '=' * 60)
    print('5. MySQL 데이터 저장')
    print('=' * 60)
    conn = mysql.connector.connect(host=config['host'], user=config['user'], password=config['password'], database=config['database'])
    cursor = conn.cursor()
    insert_sql = '''
        INSERT INTO sports_facility
        (서비스구분, 서비스ID, 대분류명, 소분류명, 서비스상태, 서비스명)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            서비스구분 = VALUES(서비스구분),
            대분류명 = VALUES(대분류명),
            소분류명 = VALUES(소분류명),
            서비스상태 = VALUES(서비스상태),
            서비스명 = VALUES(서비스명)
    '''
    data_to_insert = [tuple(row) for row in df[COLUMNS].itertuples(index=False, name=None)]
    cursor.executemany(insert_sql, data_to_insert)
    conn.commit()
    print('MySQL 저장 처리 완료:', len(data_to_insert), '건')
    cursor.execute('SELECT COUNT(*) FROM sports_facility')
    db_count = cursor.fetchone()[0]
    print('현재 DB 전체 데이터:', db_count, '건')
    cursor.close()
    conn.close()
    print('MySQL 연결 종료')
    return db_count


def main():
    start_time = time.time()
    print('\n' + '#' * 60)
    print('서울시 체육시설 데이터 크롤링 시스템')
    print('#' * 60)
    try:
        df = crawl_data()
        if df.empty:
            raise RuntimeError('수집된 데이터가 없습니다.')
        df = preprocess_data(df)
        if df.empty:
            raise RuntimeError('전처리 후 데이터가 없습니다.')
        save_csv(df)
        config = load_database_config()
        create_database_and_table(config)
        db_count = save_to_mysql(df, config)
        print('\n' + '=' * 60)
        print('최종 결과')
        print('=' * 60)
        print('CSV 데이터:', len(df), '건')
        print('DB 전체 데이터:', db_count, '건')
        print('처리 시간:', round(time.time() - start_time, 2), '초')
        print('\n전체 작업 완료')
    except Exception as e:
        print('\n' + '=' * 60)
        print('작업 실패')
        print('=' * 60)
        print('오류 유형:', type(e).__name__)
        print('오류 내용:', e)
        raise


if __name__ == '__main__':
    main()
