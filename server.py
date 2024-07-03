from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import uuid
from flask_cors import CORS

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