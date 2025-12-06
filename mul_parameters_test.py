import olca_schema as o
import olca_ipc as ipc # <--- 修改點 1: 改用標準 IPC client

# <--- 修改點 2: 初始化 Client，不需要打 http://，只要輸入 Port 號 (預設 8080)
client = ipc.Client(3000)

# 確認連線並選取資料庫中的第一個產品系統
# 注意：請確保 openLCA 中已開啟 (Activate) 一個資料庫
model = client.get(o.ProductSystem,"724bff37-cc16-4af4-a059-a1948f61af93") # get_descriptors 在標準 client 中通常用 get 取代或用法略有不同，這裡示範最通用的 get

if not model:
    print("錯誤: 找不到產品系統，請確認 openLCA 資料庫已啟用且包含產品系統。")
    exit()
print(f"正在使用模型: {model.name}")

# 取得衝擊評估方法
method = client.get(o.ImpactMethod,"fb0bfc55-63f1-4c38-8167-25be95473fee")
if not method:
    print("錯誤: 找不到衝擊評估方法。")
    exit()

# 取得該模型的參數
# get_descriptors 或 get 都可以，但要找該 ProductSystem 關聯的參數通常需要遍歷或已知名稱
# 為了範例簡單，我們直接搜尋全域參數 (Global Parameters)
parameters = client.get_parameters(o.ProductSystem, model.id)
for param in parameters:
    print(f"parameter: {param.name} = {param.value}")

# # --- 開始計算 ---
print("開始計算廚餘運輸至外地的處理...")

# target : 計算目標 (使用什麼模型)
# amount : 計算量 (單位通常是 kg 或 m3，視模型而定)
# impact_method : 使用的衝擊評估方法
# parameters : 重新定義的參數列表
setup = o.CalculationSetup(
    target=model,
    amount=0.151,
    impact_method=method,
    parameters=[
        o.ParameterRedef(name=parameters[0].name, value=0.131, context=parameters[0].context),
        o.ParameterRedef(name=parameters[1].name, value=0, context=parameters[1].context),
        o.ParameterRedef(name=parameters[2].name, value=164*1000, context=parameters[2].context),
    ],
)
result = client.calculate(setup)
assert result
result.wait_until_ready()
impacts = result.get_total_impacts()
for i in impacts:
    # 篩選出包含 GWP (Global Warming Potential) 的衝擊類別
    if "GWP" in i.impact_category.name:
        print(f"{i.impact_category.name}: {i.amount} {i.impact_category.ref_unit}")
result.dispose()

print("開始計算廚餘運輸本地的處理...")
setup = o.CalculationSetup(
    target=model,
    amount=0.151,
    impact_method=method,
    parameters=[
        o.ParameterRedef(name=parameters[0].name, value=0, context=parameters[0].context),
        o.ParameterRedef(name=parameters[1].name, value=1.1, context=parameters[1].context),
        o.ParameterRedef(name=parameters[2].name, value=0.019, context=parameters[2].context),
    ],
)
result = client.calculate(setup)
assert result
result.wait_until_ready()
impacts = result.get_total_impacts()
for i in impacts:
    # 篩選出包含 GWP (Global Warming Potential) 的衝擊類別
    if "GWP" in i.impact_category.name:
        print(f"{i.impact_category.name}: {i.amount} {i.impact_category.ref_unit}")
result.dispose()