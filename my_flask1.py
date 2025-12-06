from flask import Flask, request, jsonify
import olca_schema as o
import olca_ipc as ipc

app = Flask(__name__)
client = ipc.Client(8081)  # 連線到 openLCA IPC Server

# 固定模型與影響評估方法 UUID
PRODUCT_SYSTEM_ID = "724bff37-cc16-4af4-a059-a1948f61af93"
IMPACT_METHOD_ID = "fb0bfc55-63f1-4c38-8167-25be95473fee"

# 將原本的計算流程封裝成函式
def calculate_openlca(distance, factor, load, amount):
    # 取得模型
    model = client.get(o.ProductSystem, PRODUCT_SYSTEM_ID)
    method = client.get(o.ImpactMethod, IMPACT_METHOD_ID)

    # 取得參數
    parameters = client.get_parameters(o.ProductSystem, model.id)

    # 建立計算設定
    setup = o.CalculationSetup(
        target=model,
        amount=amount,
        impact_method=method,
        parameters=[
            o.ParameterRedef(name=parameters[0].name, value=distance, context=parameters[0].context),
            o.ParameterRedef(name=parameters[1].name, value=factor, context=parameters[1].context),
            o.ParameterRedef(name=parameters[2].name, value=load, context=parameters[2].context),
        ],
    )

    # 計算
    result = client.calculate(setup)
    result.wait_until_ready()
    impacts = result.get_total_impacts()
    result.dispose()

    # 篩選 GWP
    gwp_impacts = []
    for i in impacts:
        if "GWP" in i.impact_category.name:
            gwp_impacts.append({
                "category": i.impact_category.name,
                "value": i.amount,
                "unit": i.impact_category.ref_unit
            })
    return gwp_impacts

# Flask API
@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.json
    distance = data.get("distance")
    factor = data.get("factor")
    load = data.get("load")
    amount = data.get("amount")

    if None in (distance, factor, load, amount):
        return jsonify({"status": "error", "message": "缺少參數"}), 400

    try:
        impacts = calculate_openlca(distance, factor, load, amount)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({
        "status": "ok",
        "inputs": {"distance": distance, "factor": factor, "load": load, "amount": amount},
        "impacts": impacts
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
