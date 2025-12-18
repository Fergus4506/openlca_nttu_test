# call_flask.py
import requests

url = "http://localhost:5001/calculate"  # 確認 Flask 正在跑
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
