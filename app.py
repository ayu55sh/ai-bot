from flask import Flask, request
import requests, os, time, hmac, hashlib

app = Flask(__name__)

API_KEY = os.getenv("API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")

def sign(params):
    query = '&'.join([f"{k}={v}" for k,v in params.items()])
    return hmac.new(SECRET_KEY.encode(), query.encode(), hashlib.sha256).hexdigest()

def order(symbol, side, qty):
    params = {
        "symbol": symbol,
        "side": side,
        "type": "MARKET",
        "quantity": qty,
        "timestamp": int(time.time()*1000)
    }
    params["signature"] = sign(params)

    headers = {"X-MBX-APIKEY": API_KEY}
    return requests.post("https://fapi.binance.com/fapi/v1/order", headers=headers, params=params).json()

@app.route('/')
def home():
    return "Bot Running"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    
    symbol = data["symbol"]
    side = data["side"]
    price = float(data["price"])

    qty = round((1000 * 0.01) / price, 3)

    order(symbol, side.upper(), qty)

    return {"status": "done"}

app.run(host="0.0.0.0", port=5000)
