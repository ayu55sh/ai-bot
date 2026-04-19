from flask import Flask, request, jsonify
import requests, os, hmac, hashlib, time, json

app = Flask(__name__)

# Railway Variables se match kiya gaya hai
API_KEY = os.getenv("DELTA_API_KEY")
API_SECRET = os.getenv("DELTA_API_SECRET")
BASE_URL = "https://api.delta.exchange"

def generate_signature(method, endpoint, payload, timestamp):
    signature_data = method + timestamp + endpoint + payload
    return hmac.new(API_SECRET.encode('utf-8'), signature_data.encode('utf-8'), hashlib.sha256).hexdigest()

@app.route('/')
def home():
    return "Delta Exchange Bot is Active!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if not data:
        return jsonify({"error": "No data received"}), 400
    
    print(f"Signal Received: {data}")

    # Logic: Agar TradingView se symbol: BTCUSDT aa raha hai toh use product_id: 1 maan lo
    product_id = data.get("product_id")
    if not product_id:
        symbol = data.get("symbol", "").upper()
        if "BTC" in symbol:
            product_id = 1
        elif "ETH" in symbol:
            product_id = 2
        else:
            product_id = 1 # Default BTC

    side = data.get("side", "buy").lower()
    
    # Qty Logic: Delta pe 1 Lot = 0.001 BTC. 
    # Agar TradingView se 0.001 bhej rahe ho toh use 1 Lot bana do.
    qty = data.get("qty", 1)
    if qty < 1:
        qty = int(qty * 1000)

    endpoint = "/v2/orders"
    method = "POST"
    timestamp = str(int(time.time()))
    
    payload = {
        "product_id": product_id,
        "size": int(qty),
        "side": side,
        "order_type": "market"
    }
    
    payload_str = json.dumps(payload, separators=(',', ':'))
    signature = generate_signature(method, endpoint, payload_str, timestamp)

    headers = {
        "api-key": API_KEY,
        "signature": signature,
        "timestamp": timestamp,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(BASE_URL + endpoint, data=payload_str, headers=headers)
        res_data = response.json()
        print(f"Delta Response: {res_data}")
        return jsonify(res_data)
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Railway automatically defines PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
