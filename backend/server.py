# app.py
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from bson import ObjectId
import os
from flask_cors import CORS


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/GiaiPhapPhanMem"  # Update with your MongoDB URI
mongo = PyMongo(app)
bcrypt = Bcrypt(app)
CORS(app)
# MongoDB Collection
users = mongo.db.User



# Route to register user
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    # Check if user already exists
    if users.find_one({"email": email}):
        return jsonify({"error": "User already exists"}), 400

    # Hash table the password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    # Insert user into MongoDB
    user_id = users.insert_one({
        "username": username,
        "email": email,
        "password": hashed_password
    }).inserted_id

    return jsonify({"message": "User registered successfully", "user_id": str(user_id)}), 201
# Route to login user
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Find user by email
    user = users.find_one({"email": email})
    if user and bcrypt.check_password_hash(user['password'], password):
        # Return user ID and username upon successful login
        return jsonify({
            "message": "Login successful",
            "user_id": str(user["_id"]),
            "username": user.get("username")  # Ensure your user document has a 'username' field
        }), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401

@app.route('/account/vallet', methods=['POST'])
def recharge_wallet():
    try:
        # Get JSON data from request
        data = request.get_json()
        username = data.get('username')  # Extract username
        amount = data.get('amount')  # Extract amount

        # Log the received data
        print(f"Received username: {username}, amount: {amount}")

        # Validate input
        if not isinstance(amount, (int, float)) or username is None or amount <= 0:
            return jsonify({"error": "Invalid username or amount"}), 400

        # Find the user in the database by username
        user = users.find_one({"username": username})
        print(user)

        if user:
            # Initialize balance if it doesn't exist
            current_balance = user.get('balance', 0)  # Default to 0 if balance doesn't exist


            new_balance = int(current_balance) + int(amount)

            # Update the user's balance in MongoDB
            result = users.update_one({"username": username}, {"$set": {"balance": new_balance}})
            if result.modified_count == 0:
                return jsonify({"error": "Balance update failed"}), 500

            # Fetch the updated user data
            updated_user = users.find_one({"username": username}, {"_id": 0, "username": 1, "balance": 1})
            return jsonify(updated_user), 200
        else:
            return jsonify({"error": "User not found"}), 404

    except Exception as e:
        print(f"Error occurred: {str(e)}")  # Log the error
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/motorcycle_spots', methods=['GET'])
def get_motorcycle_spots():
    spots = mongo.db.motorcycle_spots.find()  # Assuming you have a collection named 'motorcycle_spots'
    output = []
    for spot in spots:
        output.append({
            'id': str(spot['_id']),  # Convert ObjectId to string
            'name': spot['name'],
            'status': spot['status']
        })
    return jsonify(output)
@app.route('/oto_spots', methods=['GET'])
def get_oto_spots():
    spots = mongo.db.oto_spots.find()  # Assuming you have a collection named 'motorcycle_spots'
    output = []
    for spot in spots:
        output.append({
            'id': str(spot['_id']),  # Convert ObjectId to string
            'name': spot['name'],
            'status': spot['status']
        })
    return jsonify(output)

@app.route('/account/license_plate', methods=['POST'])
def update_license_plate():
    data = request.get_json()
    username = data.get('username')
    license_plate = data.get('license_plate')
    print(data)
    # Validate the input
    if not username:
        return jsonify({"error": "Username is required"}), 400
    if not license_plate:
        return jsonify({"error": "License plate is required"}), 400
    print("Collection Name:", mongo.db.Users.name)
    print("Database URI:", app.config["MONGO_URI"])
    # Find the user by username
    user = users.find_one({"username": str(username)})
    print(user)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Update or add the license plate
    users.update_one({"_id": user["_id"]}, {"$set": {"license_plate": license_plate}})

    # Fetch and return the updated user information
    updated_user = users.find_one({"_id": user["_id"]})
    return jsonify({
        "username": updated_user["username"],
        "balance": updated_user.get("balance", 0),
        "license_plate": updated_user["license_plate"],
    })


if __name__ == "__main__": 
    app.run(debug=True)
