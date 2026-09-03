from .config import (
    load_database_config,
)
from .crawler import (
    crawl_data,
)
from .csv_writer import (
    save_csv,
)
from .database import (
    create_database_and_table,
    save_to_mysql,
)
from .preprocess import (
    preprocess_data,
)
from .quality import (
    validate_data,
)

# 이 패키지의 목적은 하위 모듈의 함수들을 한곳에 모아
# `from src.sports_pipeline import ...`로 바로 쓸 수 있게 하는 것이다.
# ruff(F401)는 재노출(re-export)을 "가져왔는데 안 쓴다"고 오탐하므로
# __all__을 명시해서 이 함수들이 공개 API임을 분명히 한다.
__all__ = [
    "crawl_data",
    "create_database_and_table",
    "load_database_config",
    "preprocess_data",
    "save_csv",
    "save_to_mysql",
    "validate_data",
]
