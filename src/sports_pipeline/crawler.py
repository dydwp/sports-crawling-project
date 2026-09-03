import time

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .config import (
    COLUMNS,
    CRAWL_WAIT_SECONDS,
    DATASET_KEYWORD,
    DATASET_URL,
    MIN_DATA_COUNT,
    PAGE_WAIT_SECONDS,
    SEARCH_KEYWORD,
    TARGET_URL,
)

# ============================================================
# Selenium Driver
# ============================================================

def create_driver():
    options = Options()

    options.add_argument("--start-maximized")

    # 불필요한 로그 최소화
    options.add_experimental_option(
        "excludeSwitches",
        ["enable-logging"]
    )

    return webdriver.Chrome(options=options)


# ============================================================
# 검색 수행 (매 데이터셋 처리 전마다 새로 호출한다)
# ============================================================

def perform_search(driver, wait):
    """
    데이터셋 목록 페이지로 이동해서 SEARCH_KEYWORD로 검색한다.

    중요:
    이전 페이지에서 찾아둔 <a> 엘리먼트를 재사용하면
    페이지 이동(back 포함) 이후 DOM이 다시 그려지면서
    stale element reference 오류가 발생한다.

    따라서 데이터셋을 하나 처리할 때마다 이 함수로
    검색 결과 페이지를 완전히 새로 만든 뒤,
    그 화면에서 바로 엘리먼트를 찾아 클릭하는 방식으로 동작한다.
    """

    driver.get(DATASET_URL)

    search_input = wait.until(
        EC.presence_of_element_located(
            (By.ID, "searchKeyword")
        )
    )

    search_input.clear()
    search_input.send_keys(SEARCH_KEYWORD)

    search_button = wait.until(
        EC.element_to_be_clickable(
            (
                By.CSS_SELECTOR,
                "button.btn-ico[title='공공데이터 검색']"
            )
        )
    )

    search_button.click()

    time.sleep(PAGE_WAIT_SECONDS)

    # 검색 결과의 데이터셋 링크가 나타날 때까지 기다린다.
    wait.until(
        lambda d: len(
            d.find_elements(
                By.XPATH,
                f"//a[contains(normalize-space(.), '{DATASET_KEYWORD}')]"
            )
        ) > 0
    )


# ============================================================
# 검색 결과에서 체육시설 데이터셋 "이름" 목록 찾기
# ============================================================

def find_dataset_names(driver, wait):
    """
    검색 결과에서 '체육시설 공공서비스예약 정보'가 포함된
    데이터셋 이름 목록만 수집한다. (엘리먼트 객체는 저장하지 않는다.)

    엘리먼트 객체를 미리 저장해두면 페이지 이동 후 stale이 되므로
    이름만 저장해두고, 실제 클릭 시점에 이름으로 다시 엘리먼트를 찾는다.
    """

    perform_search(driver, wait)

    links = driver.find_elements(
        By.XPATH,
        f"//a[contains(normalize-space(.), '{DATASET_KEYWORD}')]"
    )

    names = []

    for link in links:
        name = link.text.strip()

        if not name:
            continue

        if DATASET_KEYWORD not in name:
            continue

        # 같은 이름이 여러 번 잡힐 수 있다.
        if name in names:
            continue

        names.append(name)

    return names


def _xpath_literal(text):
    """
    XPath 문자열 리터럴로 안전하게 감싼다.
    (이름에 따옴표가 포함되는 경우는 거의 없지만 안전하게 처리한다.)
    """

    if "'" not in text:
        return f"'{text}'"

    if '"' not in text:
        return f'"{text}"'

    parts = text.split("'")
    return "concat('" + "', \"'\", '".join(parts) + "')"


def click_dataset_by_name(driver, wait, name):
    """
    현재 화면(검색 결과 페이지)에서 이 이름을 포함하는
    데이터셋 링크를 새로 찾아서 클릭한다.

    find_dataset_names()에서 이름을 뽑을 때도 완전일치가 아니라
    contains(normalize-space(.), DATASET_KEYWORD) 방식으로 찾았으므로,
    여기서도 동일하게 contains로 찾아야 한다. 완전일치(=)를 쓰면
    링크 텍스트에 섞인 미세한 공백/부가 텍스트 때문에 매칭이
    실패해서 항상 TimeoutException이 발생한다.
    """

    literal = _xpath_literal(name)

    element = wait.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                f"//a[contains(normalize-space(.), {literal})]"
            )
        )
    )

    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});",
        element
    )

    time.sleep(0.5)

    driver.execute_script(
        "arguments[0].click();",
        element
    )


# ============================================================
# 그리드 로딩 대기 (placeholder -> 실제 데이터 전환 대기)
# ============================================================

def wait_for_grid_rows(driver, wait, max_attempts=6, interval_seconds=1.5):
    """
    AXGridTarget_AX_gridBodyTable 내부에 실제 데이터 행이
    채워질 때까지 재시도한다.

    상세 페이지 이동 직후에는 잠깐 "조회된 데이터가 없습니다."
    placeholder 행만 보이다가, AJAX 응답이 온 뒤에 실제 데이터로
    바뀌는 경우가 있으므로 한 번만 확인하지 않고 여러 번 재확인한다.
    """

    try:
        data_table = wait.until(
            EC.presence_of_element_located(
                (
                    By.ID,
                    "AXGridTarget_AX_gridBodyTable"
                )
            )
        )
    except Exception:
        return None, []

    rows = []

    for _ in range(max_attempts):
        rows = data_table.find_elements(
            By.CSS_SELECTOR,
            "tbody#AXGridTarget_AX_tbody tr"
        )

        if not rows:
            rows = data_table.find_elements(
                By.CSS_SELECTOR,
                "tbody tr"
            )

        # placeholder("조회된 데이터가 없습니다.") 행인지 확인
        is_placeholder = False

        if len(rows) == 1:
            cells = rows[0].find_elements(By.TAG_NAME, "td")
            texts = [c.text.strip() for c in cells]

            if any("조회된 데이터가 없습니다" in t for t in texts):
                is_placeholder = True

        if rows and not is_placeholder:
            return data_table, rows

        time.sleep(interval_seconds)

    # 마지막까지도 placeholder이거나 비어있으면 그 결과를 그대로 반환한다.
    # (실제로 데이터가 0건인 데이터셋일 수도 있기 때문이다.)
    return data_table, rows


# ============================================================
# 상세 페이지 데이터 수집
# ============================================================

def collect_dataset_data(driver, wait, name):
    """
    검색 결과에서 이름이 일치하는 데이터셋을 클릭한 뒤
    상세 페이지의 AXGrid 데이터를 수집한다.
    """

    # 검색 결과에서 클릭 (매번 새로 찾은 엘리먼트를 사용)
    try:
        click_dataset_by_name(driver, wait, name)
    except Exception as e:
        print(f"  [디버그] 클릭 실패: {type(e).__name__}")

        # 실제 화면에 있는 후보 링크들의 텍스트를 찍어서
        # 이름이 왜 안 맞는지 비교할 수 있게 한다.
        candidates = driver.find_elements(
            By.XPATH,
            f"//a[contains(normalize-space(.), '{DATASET_KEYWORD}')]"
        )
        candidate_texts = [c.text.strip() for c in candidates[:12]]
        print(f"  [디버그] 화면상 후보 링크 텍스트: {candidate_texts}")
        return []

    # 상세 페이지 이동 대기
    try:
        wait.until(
            lambda d: "/datasetView.do" in d.current_url
        )
    except Exception:
        print(f"  [디버그] 상세 페이지 이동 실패 (현재 URL: {driver.current_url})")
        return []

    time.sleep(CRAWL_WAIT_SECONDS)

    data_table, rows = wait_for_grid_rows(driver, wait)

    if data_table is None:
        # gridBodyTable 자체가 안 뜬 경우
        no_data = driver.find_elements(
            By.XPATH,
            "//*[contains(text(), '조회된 데이터가 없습니다')]"
        )
        outer = driver.find_elements(By.ID, "AXGridTarget")

        if no_data:
            print("  [디버그] '조회된 데이터가 없습니다' 메시지 확인됨")
        elif outer:
            print("  [디버그] AXGridTarget은 있으나 gridBodyTable 없음 (id 변경 가능성)")
        else:
            print("  [디버그] AXGridTarget 자체도 없음 (그리드 미로딩)")

        return []

    if not rows:
        inner_html = data_table.get_attribute("innerHTML")
        preview = (inner_html or "")[:300].replace("\n", " ")
        print(f"  [디버그] gridBodyTable은 찾았지만 tr 없음. innerHTML 미리보기: {preview}")
        return []

    rows_data = []

    for row in rows:
        cells = row.find_elements(
            By.TAG_NAME,
            "td"
        )

        if len(cells) < 6:
            continue

        values = [
            cell.text.strip()
            for cell in cells[:6]
        ]

        # 헤더 행 제거
        if (
            "서비스ID" in values[1]
            or "서비스구분" in values[0]
            or "서비스상태" in values[4]
        ):
            continue

        # 빈 서비스ID 제거
        if not values[1]:
            continue

        rows_data.append(values)

    if rows and not rows_data:
        sample_cells = rows[0].find_elements(By.TAG_NAME, "td")
        sample_texts = [c.text.strip() for c in sample_cells]
        print(
            f"  [디버그] tr {len(rows)}개 발견했지만 필터 후 0건. "
            f"첫 행 td 텍스트: {sample_texts}"
        )

    return rows_data


# ============================================================
# 데이터셋 하나씩 순회
# ============================================================

def crawl_data():
    """
    서울 열린데이터광장에서 체육시설 데이터셋을 검색하고
    여러 자치구 데이터셋을 순회하여 데이터를 수집한다.
    """

    print("=" * 60)
    print("Selenium 크롤링 시작")
    print("=" * 60)

    driver = create_driver()

    wait = WebDriverWait(
        driver,
        15
    )

    all_data = []

    try:
        # ----------------------------------------------------
        # 서울 열린데이터광장 접속
        # ----------------------------------------------------

        driver.get(TARGET_URL)

        wait.until(
            EC.presence_of_element_located(
                (By.TAG_NAME, "body")
            )
        )

        print("서울 열린데이터광장 접속 완료")

        # ----------------------------------------------------
        # 데이터셋 이름 목록 검색
        # ----------------------------------------------------

        names = find_dataset_names(
            driver,
            wait
        )

        if not names:
            raise RuntimeError(
                "체육시설 데이터셋을 찾지 못했습니다."
            )

        print(
            f"체육시설 데이터셋 검색 결과: {len(names)}개"
        )

        # 최대 10개까지만 사용
        names = names[:10]

        # ----------------------------------------------------
        # 데이터셋 순회
        # ----------------------------------------------------

        for index, name in enumerate(
            names,
            start=1
        ):
            print(
                f"[{index}/{len(names)}] {name}"
            )

            # 매 데이터셋마다 검색 결과 페이지를 새로 만든 뒤
            # 그 화면에서 이름으로 링크를 찾아 클릭한다.
            # (엘리먼트 재사용으로 인한 stale 문제를 피하기 위함)
            if index > 1:
                try:
                    perform_search(driver, wait)
                except Exception as e:
                    print(f"  [디버그] 검색 재수행 실패: {type(e).__name__}")
                    continue

            rows = collect_dataset_data(
                driver,
                wait,
                name
            )

            count = len(rows)

            print(
                f"  수집: {count}건"
            )

            all_data.extend(rows)

            # 목표 데이터 이상이면 중단
            if len(all_data) >= MIN_DATA_COUNT:
                print(
                    f"  목표 달성: {len(all_data)}건"
                )
                break

        # ----------------------------------------------------
        # DataFrame 생성
        # ----------------------------------------------------

        df = pd.DataFrame(
            all_data,
            columns=COLUMNS
        )

        # 서비스ID 기준 중복 제거
        before = len(df)

        if not df.empty:
            df = df.drop_duplicates(
                subset=["서비스ID"],
                keep="first"
            ).reset_index(drop=True)

        duplicate_count = before - len(df)

        if duplicate_count > 0:
            print(
                f"중복 제거: {duplicate_count}건"
            )

        print(
            f"전체 수집: {len(df)}건"
        )

        print(
            f"DataFrame: {df.shape}"
        )

        return df

    finally:
        driver.quit()
        print("Selenium 종료")
