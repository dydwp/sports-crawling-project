"""
MySQL 연결 설정 로딩과 접속을 담당하는 모듈입니다.

로컬 환경에서는 .env 파일에서 데이터베이스 접속 정보를 읽습니다.
AWS Lambda 환경에서는 AWS Secrets Manager(DB_SECRET_ARN)와
환경변수(DB_HOST, DB_NAME, DB_PORT)를 이용하여
Amazon RDS MySQL 접속 정보를 구성합니다.
"""

import json
import os

import mysql.connector
from dotenv import load_dotenv

from .config import (
    COLUMNS,
    ENV_FILE,
    TABLE_NAME,
)

REQUIRED_LOCAL_ENV_NAMES = {
    "DB_HOST",
    "DB_USER",
    "DB_PASSWORD",
    "DB_NAME",
}


# ============================================================
# AWS Secrets Manager
# ============================================================

def _load_secret_value(secret_arn, secrets_client=None):
    if not secret_arn:
        raise ValueError("DB_SECRET_ARN이 지정되지 않았습니다.")

    if secrets_client is None:
        import boto3
        secrets_client = boto3.client("secretsmanager")

    response = secrets_client.get_secret_value(SecretId=secret_arn)
    secret_string = response.get("SecretString")

    if not secret_string:
        raise ValueError("Secrets Manager의 SecretString이 없습니다.")

    try:
        secret = json.loads(secret_string)
    except json.JSONDecodeError as error:
        raise ValueError(
            "Secrets Manager의 SecretString이 올바른 JSON 형식이 아닙니다."
        ) from error

    if not isinstance(secret, dict):
        raise TypeError("Secrets Manager의 Secret 값은 JSON 객체여야 합니다.")

    return secret


def load_database_config_from_secret(secret_arn, secrets_client=None):
    secret = _load_secret_value(secret_arn=secret_arn, secrets_client=secrets_client)

    username = secret.get("username")
    password = secret.get("password")

    if not username:
        raise ValueError("Secrets Manager에 username이 없습니다.")
    if not password:
        raise ValueError("Secrets Manager에 password가 없습니다.")

    host = secret.get("host") or os.environ.get("DB_HOST")
    if not host:
        raise ValueError("DB_HOST가 지정되지 않았습니다.")

    database_name = secret.get("dbname") or os.environ.get("DB_NAME")
    if not database_name:
        raise ValueError("DB_NAME이 지정되지 않았습니다.")

    port_value = secret.get("port") or os.environ.get("DB_PORT") or "3306"

    try:
        port = int(port_value)
    except (TypeError, ValueError) as error:
        raise ValueError("DB_PORT는 정수여야 합니다.") from error

    return {
        "host": str(host),
        "port": port,
        "database": str(database_name),
        "user": str(username),
        "password": str(password),
    }


# ============================================================
# 데이터베이스 연결 설정
# ============================================================

def load_database_config(env_file=ENV_FILE, secrets_client=None):
    """
    실행 환경에 따라 MySQL 연결 정보를 읽고 검증한다.

    AWS Lambda: DB_SECRET_ARN 환경변수가 있으면 Secrets Manager 사용
    Local: 없으면 .env 파일 사용
    """

    secret_arn = os.environ.get("DB_SECRET_ARN")

    if secret_arn:
        return load_database_config_from_secret(
            secret_arn=secret_arn,
            secrets_client=secrets_client,
        )

    if not env_file.is_file():
        raise RuntimeError(f".env 파일이 없습니다: {env_file}")

    load_dotenv(dotenv_path=env_file)

    config = {
        "host": os.getenv("DB_HOST"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME"),
        "port": int(os.getenv("DB_PORT", "3306")),
    }

    missing = [
        key for key in ("host", "user", "password", "database")
        if not config[key]
    ]

    if missing:
        raise RuntimeError(".env에 다음 환경변수가 없습니다: " + ", ".join(missing))

    return config


# ============================================================
# 아래 두 함수는 기존 로직 그대로, connect() 호출부에 port만 추가
# ============================================================

def create_database_and_table(config):

    conn = mysql.connector.connect(
        host=config["host"],
        port=config.get("port", 3306),
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

    conn = mysql.connector.connect(
        host=config["host"],
        port=config.get("port", 3306),
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
        port=config.get("port", 3306),
        user=config["user"],
        password=config["password"],
        database=config["database"],
    )

    cursor = conn.cursor()

    try:
        cursor.execute(f"TRUNCATE TABLE {TABLE_NAME}")

        insert_sql = f"""
            INSERT INTO {TABLE_NAME}
            (서비스구분, 서비스ID, 대분류명, 소분류명, 서비스상태, 서비스명)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        data_to_insert = [
            tuple(row)
            for row in df[COLUMNS].itertuples(index=False, name=None)
        ]

        if data_to_insert:
            cursor.executemany(insert_sql, data_to_insert)

        conn.commit()

        cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
        db_count = cursor.fetchone()[0]

        return db_count

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()