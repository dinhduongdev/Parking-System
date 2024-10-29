from flask import Flask, jsonify, request
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/GiaiPhapPhanMem"
mongo = PyMongo(app)
from flask_cors import CORS
CORS(app)
@app.route('/api/data', methods=['GET'])
def get_data():
    data = mongo.db.User.find()
    result = [{"id": str(item["_id"]), "name": item["name"]} for item in data]
    return jsonify(result)

@app.route('/api/data', methods=['POST'])
def add_data():
    new_data = request.json
    mongo.db.User.insert_one(new_data)
    return jsonify(new_data), 201

if __name__ == '__main__':
    app.run(debug=True)
