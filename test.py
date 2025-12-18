# call_flask.py
import requests

#第一部分 以距離為碳排計算標準
url = "http://localhost:5001/calculate/Co2BYTKM"  # 確認 Flask 正在跑
payload = {
    # 若你已在 Flask 把 Product System 與 Method 固定，這裡就只送四個參數
    "distance": 164,
    "factor": 0.131,
    "load": 12.6,
    "amount": 0.151
    # 若沒有固定，請加入 product_system_id 與 impact_method_id
}

res = requests.post(url, json=payload)
print("HTTP status:", res.status_code)
print(res.json())

# 第二部分 以油耗為碳排計算標準
url_oil = "http://localhost:5001/calculate/Co2BYOilKM"  # 確認 Flask 正在跑
payload = {
    # 若你已在 Flask 把 Product System 與 Method 固定，這裡就只送四個參數
    "distance": 164,
    "factor": 3.32,
    "load": 12.6,
    "amount": 0.151,
    "oilUse": 58.57
    # 若沒有固定，請加入 product_system_id 與 impact_method_id
}

res = requests.post(url_oil, json=payload)
print("HTTP status:", res.status_code)
print(res.json())