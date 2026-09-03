from datetime import datetime

from .config import (
    PROCESSED_DIR,
    RAW_DIR,
)


def save_csv(
    df,
    raw=True,
    processed=True
):
    """
    Raw / Processed CSV 저장
    """

    today = datetime.now().strftime(
        "%Y%m%d"
    )

    saved_files = {}

    # --------------------------------------------------------
    # Raw CSV
    # --------------------------------------------------------

    if raw:

        raw_path = (
            RAW_DIR
            / f"sports_crawling_raw_{today}.csv"
        )

        df.to_csv(
            raw_path,
            index=False,
            encoding="utf-8-sig"
        )

        saved_files["raw"] = raw_path

    # --------------------------------------------------------
    # Processed CSV
    # --------------------------------------------------------

    if processed:

        processed_path = (
            PROCESSED_DIR
            / f"sports_crawling_processed_{today}.csv"
        )

        df.to_csv(
            processed_path,
            index=False,
            encoding="utf-8-sig"
        )

        saved_files["processed"] = processed_path

    return saved_files