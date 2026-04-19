from flask import Flask, request, jsonify
import requests, os, hmac, hashlib, time

app = Flask(__name__)

# Delta Exchange Credentials (Railway variables mein add karein)
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("SECRET_KEY")
BASE_URL = "https://api.delta.exchange"

def generate_signature(method, endpoint, payload, timestamp):
    signature_data = method + timestamp + endpoint + payload
    return hmac.new(API_SECRET.encode('utf-8'), signature_data.encode('utf-8'), hashlib.sha256).hexdigest()

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print(f"Incoming Data: {data}")

    # Delta Exchange requires Product ID (e.g., 1 for BTCUSDT Futures)
    product_id = data.get("product_id", 1) 
    side = data.get("side").lower()
    qty = data.get("qty", 1) # Lots mein hota hai Delta pe

    endpoint = "/v2/orders"
    method = "POST"
    timestamp = str(int(time.time()))
    
    payload = {
        "product_id": product_id,
        "size": qty,
        "side": side,
        "order_type": "market"
    }
    
    import json
    payload_str = json.dumps(payload, separators=(',', ':'))
    signature = generate_signature(method, endpoint, payload_str, timestamp)

    headers = {
        "api-key": API_KEY,
        "signature": signature,
        "timestamp": timestamp,
        "Content-Type": "application/json"
    }

    response = requests.post(BASE_URL + endpoint, data=payload_str, headers=headers)
    return jsonify(response.json())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
