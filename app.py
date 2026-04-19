from flask import Flask, request, jsonify
import requests, os, time, hmac, hashlib

app = Flask(__name__)

# Environment Variables (Railway variables se aayenge)
API_KEY = os.getenv("API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")

def sign(params):
    query = '&'.join([f"{k}={v}" for k, v in params.items()])
    return hmac.new(SECRET_KEY.encode(), query.encode(), hashlib.sha256).hexdigest()

def order(symbol, side, qty):
    endpoint = "https://fapi.binance.com/fapi/v1/order"
    params = {
        "symbol": symbol.upper(),
        "side": side.upper(),
        "type": "MARKET",
        "quantity": float(qty),
        "timestamp": int(time.time() * 1000),
        "recvWindow": 5000
    }
    params["signature"] = sign(params)
    headers = {"X-MBX-APIKEY": API_KEY}
    
    try:
        response = requests.post(endpoint, headers=headers, params=params)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@app.route('/')
def home():
    return "Bot is Running and Ready!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print(f"Data Received: {data}") # Logs check karne ke liye

    # Check if necessary data is present
    if not data or 'symbol' not in data or 'side' not in data:
        return jsonify({"status": "error", "message": "Invalid Data Received"}), 400

    symbol = data["symbol"]
    side = data["side"]
    
    # Qty calculation fix: 
    # TradingView se agar qty bhej rahe ho toh wo lo, warna default 0.001 (BTC minimum)
    qty = data.get("qty", 0.001)

    # Execute Order
    res = order(symbol, side, qty)
    
    print(f"Binance Response: {res}")
    return jsonify({"status": "success", "binance_response": res})

if __name__ == "__main__":
    # Railway automatically defines PORT, use it or default to 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
