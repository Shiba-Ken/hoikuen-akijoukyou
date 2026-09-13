"""
杉並区 保育園空き状況パーサー（リポジトリ組み込み版）
=========================================================

GitHub Actions から月1回実行されることを想定。
実行すると ../data/suginami.json を最新化する。

使い方:
    python scripts/suginami_parser.py

【重要】
実際の列構成は自治体側の更新でズレることがあるため、
COLUMN_MAP は定期的に検証・調整してください。
（スクリプト実行時に実際の列名一覧を標準出力に表示します）
"""

import pandas as pd
import requests
import json
from pathlib import Path
from datetime import date

# ---------------------------------------------------------
# 設定
# ---------------------------------------------------------

# 杉並区オープンデータカタログのCSV直リンク（月ごとにファイル名が変わる点に注意。
# 本来はカタログページをスクレイピングして最新URLを自動取得するのが望ましい）
CSV_URL = "https://www.city.suginami.tokyo.jp/documents/18016/202608aki-jokyo.csv"

SOURCE_LABEL = "杉並区オープンデータカタログ（CC-BY）"

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "suginami.json"

COLUMN_MAP = {
    0: "no",
    1: "facility_code",
    2: "area_name",
    3: "area_type",
    4: "facility_name",
    5: "facility_category",
    6: "city",
    7: "prefecture",
    8: "address",
    9: "full_address",
    10: "url",
    11: "geo_xml",
    12: "longitude",
    13: "latitude",
    14: "phone",
    15: "open_time",
    16: "close_time",
    17: "capacity_0",
    18: "capacity_1",
    19: "capacity_2",
    20: "capacity_3",
    21: "capacity_4",
    22: "capacity_5",
    23: "capacity_total",
    24: "vacancy_0",
    25: "vacancy_1",
    26: "vacancy_2",
    27: "vacancy_3",
    28: "vacancy_4",
    29: "vacancy_5",
    30: "accept_age_min",
    31: "accept_age_max",
}


def fetch_csv(url: str = CSV_URL, local_path: str | None = None) -> pd.DataFrame:
    if local_path:
        raw = Path(local_path).read_bytes()
    else:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        raw = resp.content

    return pd.read_csv(pd.io.common.BytesIO(raw), encoding="cp932", header=0)


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    n = min(len(df.columns), len(COLUMN_MAP))
    rename_dict = {df.columns[i]: COLUMN_MAP[i] for i in range(n)}
    return df.rename(columns=rename_dict)


def to_records(df: pd.DataFrame) -> list[dict]:
    records = []
    age_labels = ["0", "1", "2", "3", "4", "5"]

    for _, row in df.iterrows():
        vacancies = {}
        for age in age_labels:
            cap_col, vac_col = f"capacity_{age}", f"vacancy_{age}"
            if cap_col in row and vac_col in row:
                vacancies[age] = {
                    "capacity": row.get(cap_col),
                    "vacancy": row.get(vac_col),
                }

        has_vacancy = any(
            (v.get("vacancy") or 0) not in (0, "0", None) for v in vacancies.values()
        )

        records.append({
            "facility_code": row.get("facility_code"),
            "facility_name": row.get("facility_name"),
            "facility_category": row.get("facility_category"),
            "area_name": row.get("area_name"),
            "address": row.get("full_address") or row.get("address"),
            "phone": row.get("phone"),
            "hours": f"{row.get('open_time', '')}〜{row.get('close_time', '')}",
            "latitude": row.get("latitude"),
            "longitude": row.get("longitude"),
            "capacity_total": row.get("capacity_total"),
            "vacancy_by_age": vacancies,
            "has_vacancy": has_vacancy,
        })

    return records


def main():
    print("CSVを取得しています...")
    df = fetch_csv()

    print("--- 実際の列一覧（COLUMN_MAPとズレがないか確認） ---")
    print(df.columns.tolist())

    df = normalize_columns(df)
    records = to_records(df)

    output = {
        "updated_at": date.today().isoformat(),
        "source": SOURCE_LABEL,
        "facilities": records,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    vacant_count = sum(1 for r in records if r["has_vacancy"])
    print(f"件数: {len(records)} / 空きあり: {vacant_count}")
    print(f"出力先: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
