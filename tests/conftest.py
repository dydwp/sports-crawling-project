import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가해서
# `from src.sports_pipeline import ...` 임포트가
# 어느 위치에서 pytest를 실행하든 동작하도록 한다.
PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
