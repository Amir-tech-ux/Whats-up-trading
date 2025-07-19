from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print("Incoming data:", data)

    reply = {
        "text": "התקבל! ✅ הבוט פעיל!"
    }

    return jsonify(reply)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
