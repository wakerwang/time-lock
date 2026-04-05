from flask import Flask, render_template, request, jsonify
import crypto

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/encrypt", methods=["POST"])
def encrypt():
    data = request.json
    result = crypto.encrypt_message(data["content"], data["unlock_date"], data["password"])
    return jsonify(result)

@app.route("/api/decrypt", methods=["POST"])
def decrypt():
    data = request.json
    result = crypto.decrypt_message(data["id"], data["password"])
    return jsonify(result)

@app.route("/api/list", methods=["GET"])
def list_msgs():
    return jsonify(crypto.list_messages())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)