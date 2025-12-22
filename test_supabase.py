"""
test_supabase.py

用途：讀取專案中的 .env（包含 REACT_APP_SUPABASE_URL 與 REACT_APP_SUPABASE_ANON_KEY），
並示範如何連線、查詢與插入資料到 Supabase。

使用方式（在 venv 啟動後）：
  pip install supabase python-dotenv
  python test_supabase.py

注意：請確認 .env 中的 REACT_APP_SUPABASE_URL 以及 REACT_APP_SUPABASE_ANON_KEY 已正確設定。
"""

import os
import uuid
from dotenv import load_dotenv

try:
    # supabase-py v1
    from supabase import create_client
except Exception:
    raise RuntimeError("請先安裝 supabase 套件：pip install supabase")


# 讀取 .env
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("找不到 Supabase 設定，請確認 .env 內有 SUPABASE_URL 與 SUPABASE_ANON_KEY")
# 建立客戶端
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def test_select(table_name: str, limit: int = 5):
    """示範如何從指定 table 讀取資料"""
    print(f"=== 從 {table_name} 讀取前 {limit} 筆資料 ===")
    try:
        # 使用 table(...) 或 from_(...) 都可以（依 supabase-py 版本）
        resp = supabase.table(table_name).select("*").limit(limit).execute()
        # supabase-py 回傳的格式通常為 dict，包含 data 與 error
        data = resp.get("data") if isinstance(resp, dict) else getattr(resp, "data", None)
        error = resp.get("error") if isinstance(resp, dict) else getattr(resp, "error", None)

        if error:
            print("查詢錯誤:", error)
            return

        if not data:
            print("未取得資料或資料為空。")
            return

        for i, row in enumerate(data, 1):
            print(f"# {i}: {row}")
    except Exception as e:
        print("查詢發生例外：", e)


def test_insert_co2_by_distance():
    """示範如何將一筆資料插入 `Co2ByDistance` 範例表。請依實際欄位調整 dict 內容。"""
    table = "Co2ByDistance"
    payload = {
        # 若有必填欄位請填入對應 key
        "Distance": 12.34,
        "Coefficient": 0.56,
        "Load": 1000,
        "Amount": 1.23,
        # CarbonEmissionID 為 uuid（如果 schema 需要）
        "CarbonEmissionID": str(uuid.uuid4()),
    }

    print(f"=== 向 {table} 插入範例資料 ===")
    try:
        resp = supabase.table(table).insert(payload).execute()
        data = resp.get("data") if isinstance(resp, dict) else getattr(resp, "data", None)
        error = resp.get("error") if isinstance(resp, dict) else getattr(resp, "error", None)

        if error:
            print("插入錯誤:", error)
            return

        print("插入成功，回傳：", data)
    except Exception as e:
        print("插入發生例外：", e)


def main():
    print("Supabase 測試開始")
    # 請將 table 名稱改成你資料庫裡確實存在的 table（可參考附圖的 Co2ByDistance, Co2ByOiluse 等）
    test_table = "Co2ByDistance"

    # 先做一次查詢
    test_select(test_table, limit=5)

    # 再做一次插入（僅示範，實際執行請謹慎）
    try:
        prompt = input("是否要執行插入示例到 Co2ByDistance？(y/N): ")
    except Exception:
        prompt = "n"

    if prompt.lower() == "y":
        test_insert_co2_by_distance()
    else:
        print("跳過插入測試。")

    print("測試結束")


if __name__ == "__main__":
    main()
