from flask import Flask, request, jsonify, abort

app = Flask(__name__)

@app.errorhandler(404)
def not_found(err):
    return jsonify({'error': 'Not found'}), 404

@app.route('/home')
def home():
    return 'Hello'

if __name__ == '__main__':
    app.run(debug = True)