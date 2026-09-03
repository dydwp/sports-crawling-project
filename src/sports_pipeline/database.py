import mysql.connector

from .config import (
    COLUMNS,
    TABLE_NAME,
)


def create_database_and_table(config):

    # --------------------------------------------------------
    # DB 생성
    # --------------------------------------------------------

    conn = mysql.connector.connect(
        host=config["host"],
        user=config["user"],
        password=config["password"],
    )

    cursor = conn.cursor()

    database_name = config["database"]

    cursor.execute(
        f"""
        CREATE DATABASE IF NOT EXISTS
        `{database_name}`
        CHARACTER SET utf8mb4
        COLLATE utf8mb4_unicode_ci
        """
    )

    conn.commit()

    cursor.close()
    conn.close()

    # --------------------------------------------------------
    # 테이블 생성
    # --------------------------------------------------------

    conn = mysql.connector.connect(
        host=config["host"],
        user=config["user"],
        password=config["password"],
        database=database_name,
    )

    cursor = conn.cursor()

    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (

            서비스구분 VARCHAR(20),

            서비스ID VARCHAR(50) PRIMARY KEY,

            대분류명 VARCHAR(100),

            소분류명 VARCHAR(100),

            서비스상태 VARCHAR(50),

            서비스명 VARCHAR(500)

        )
        CHARACTER SET utf8mb4
        COLLATE utf8mb4_unicode_ci
        """
    )

    conn.commit()

    cursor.close()
    conn.close()


def save_to_mysql(df, config):

    """
    이번 크롤링 결과를 DB에 저장한다.

    기존 데이터를 TRUNCATE한 후
    최신 전처리 데이터를 저장한다.

    따라서:
        CSV 데이터 수 = DB 전체 데이터 수
    """

    conn = mysql.connector.connect(
        host=config["host"],
        user=config["user"],
        password=config["password"],
        database=config["database"],
    )

    cursor = conn.cursor()

    try:

        # ----------------------------------------------------
        # 기존 데이터 삭제
        # ----------------------------------------------------

        cursor.execute(
            f"TRUNCATE TABLE {TABLE_NAME}"
        )

        # ----------------------------------------------------
        # INSERT
        # ----------------------------------------------------

        insert_sql = f"""
            INSERT INTO {TABLE_NAME}
            (
                서비스구분,
                서비스ID,
                대분류명,
                소분류명,
                서비스상태,
                서비스명
            )
            VALUES
            (%s, %s, %s, %s, %s, %s)
        """

        data_to_insert = [
            tuple(row)
            for row in df[COLUMNS].itertuples(
                index=False,
                name=None
            )
        ]

        if data_to_insert:

            cursor.executemany(
                insert_sql,
                data_to_insert
            )

        conn.commit()

        # ----------------------------------------------------
        # DB 데이터 개수 확인
        # ----------------------------------------------------

        cursor.execute(
            f"""
            SELECT COUNT(*)
            FROM {TABLE_NAME}
            """
        )

        db_count = cursor.fetchone()[0]

        return db_count

    except Exception:

        conn.rollback()

        raise

    finally:

        cursor.close()
        conn.close()