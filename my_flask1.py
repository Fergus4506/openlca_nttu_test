from flask import Flask, request, jsonify
import olca_schema as o
import olca_ipc as ipc

app = Flask(__name__)
client = ipc.Client(3001)  # 連線到 openLCA IPC Server



# 將原本的計算流程封裝成函式
def calculate_openlca(distance, factor, load, amount):
    # 取得模型
    model = client.get(o.ProductSystem, name="廚餘處理量")
    method = client.get(o.ImpactMethod, name="IPCC 2021 AR6")

    print("Model ID:", model.id)
    print("Method ID:", method.id)

    # 取得參數
    parameters = client.get_parameters(o.ProductSystem, model.id)
    
    mass_group_descriptor = client.find(o.UnitGroup, "Units of mass")
    mass_group = client.get(o.UnitGroup, mass_group_descriptor.id)
    ton_unit = next((unit for unit in mass_group.units if unit.name == 't'), None)

    # 建立計算設定
    setup = o.CalculationSetup(
        target=model,
        amount=amount,
        unit=ton_unit,
        impact_method=method,
        parameters=[
            o.ParameterRedef(name=parameters[0].name, value=factor, context=parameters[0].context),
            o.ParameterRedef(name=parameters[1].name, value=distance, context=parameters[1].context),
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
    app.run(host="0.0.0.0", port=5001)
