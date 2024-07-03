import string
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import uuid
from flask_cors import CORS
import random
import json

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")
transactions = {}

# userName: string;
#   merchantName: string;
#   merchantId: string;
#   transactionID: string;
#   transactionAmount: number;
#   remainingBalance: number;

def random_string(length=10):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))

def random_number(min_value=0, max_value=1000):
    return round(random.uniform(min_value, max_value), 2)

def load_nepali_names(file_path='nepali_names.json'):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)["names"]

nepali_names = load_nepali_names()

def random_nepali_name():
    name = random.choice(nepali_names)
    return f"{name['firstName']} {name['surname']}"

@app.route('/getdata', methods=['GET'])
def generate_random_data():
    data = {
        "merchantName": random_nepali_name(),
        "merchantId": random_string(12),
        "transactionAmount": random_number(1, 1000)
    }
    return jsonify(data)

@app.route('/request_payment', methods=['POST'])
def request_payment():
    data = request.json
    print(data)
    transactionAmount = data.get('transactionAmount')
    merchantId = data.get('merchantId')
    transactionId = str(uuid.uuid4())
    merchantName = data.get('merchantName')
    
    transactions[transactionId] = {
        'transactionAmount': transactionAmount,
        'merchantId': merchantId,
        'status': 'pending'
    }
    
    response = {
        '_transactionId': transactionId
    }
    
    return jsonify(response)

@app.route('/confirm_payment', methods=['POST'])
def confirm_payment():
    data = request.json
    transactionId = data.get('transactionId')
    
    if transactionId in transactions:
        transactions[transactionId]['status'] = 'confirmed'
        socketio.emit('payment_confirmed', {'transactionId': transactionId})
        
        response = {
            'transactionId': transactionId,
            'status': 'confirmed'
        }
        
        return jsonify(response)
    else:
        return jsonify({'error': 'Invalid transaction ID'}), 400

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)