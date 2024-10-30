# app.py
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from bson import ObjectId
import os
from flask_cors import CORS
import qrcode
from io import BytesIO
from gridfs import GridFS 
from datetime import datetime
from bson import ObjectId, Binary
from flask import send_file
import base64
app = Flask(__name__)



app.config["MONGO_URI"] = "mongodb://localhost:27017/GiaiPhapPhanMem"  # Update with your MongoDB URI
mongo = PyMongo(app)
bcrypt = Bcrypt(app)
CORS(app)



# GridFS for handling file storage
fs = GridFS(mongo.db)
# MongoDB Collection
users = mongo.db.User

data_collection = mongo.db.data

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


def get_user_by_id(user_id):
    try:
        user = users.find_one({"_id": ObjectId(user_id)})  # Use ObjectId for MongoDB ID
        if user:
            user['_id'] = str(user['_id'])  # Convert ObjectId to string
            return user
        return None
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None

@app.route('/user', methods=['GET'])
def get_user():
    user_id = request.args.get('id')  # Get user ID from query parameters
    user = get_user_by_id(user_id)    # Fetch user from database
    if user:
        return jsonify(user), 200
    return jsonify({'error': 'User not found'}), 404

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
        # if not isinstance(amount, (int, float)) or username is None or amount <= 0:
        #     return jsonify({"error": "Invalid username or amount"}), 400

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
            updated_user = users.find_one({"username": username}, {"_id": 0, "username": 1, "balance": 1, "license_plate": 1})
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

@app.route('/generate_qr', methods=['GET'])
def generate_qr_code():
    username = request.args.get('username')
    date = request.args.get('date')
    if not username or not date:
        return jsonify({"error": "Username and date are required"}), 400
    try:
        # Generate QR code
        qr_data = f"Username: {username}\nDate: {date}"
        qr = qrcode.make(qr_data)
        img_io = BytesIO()
        qr.save(img_io, 'PNG')
        img_io.seek(0)
        # Tạo dữ liệu QR code
        qr_data = {
            "date": date,
            "qr_image": Binary(img_io.getvalue()),  # Lưu ảnh dưới dạng dữ liệu nhị phân
            "created_at": datetime.utcnow()
        }
        # Cập nhật tài liệu cho người dùng với tên đăng nhập
        data_collection.update_one(
            {"username": username},  # Tìm kiếm tài liệu theo username
            {"$push": {"qr_codes": qr_data}},  # Thêm dữ liệu QR code vào mảng qr_codes
            upsert=True  # Tạo tài liệu mới nếu không tìm thấy
        )
        return jsonify({"message": "QR code generated and saved"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_qr_codes', methods=['GET'])
def get_qr_codes():
    username = request.args.get('username')

    if not username:
        return jsonify({"error": "Username is required"}), 400

    user_data = data_collection.find_one({"username": username}, {"_id": 0, "qr_codes": 1})

    if not user_data or "qr_codes" not in user_data:
        return jsonify({"qrCodes": []})  # Return empty list if no QR codes found

    # Decode binary images to base64 for client-side rendering
    qr_codes = [
        {
            "date": qr["date"], "qr_image": base64.b64encode(qr["qr_image"]).decode('utf-8')
        }
        for qr in user_data["qr_codes"]]
    
    return jsonify({"qrCodes": qr_codes})



@app.route('/qr_image/<collection>/<qr_id>', methods=['GET'])
def get_qr_image(collection, qr_id):
    try:
        # Lấy collection dựa trên tên `username`
        user_collection = mongo.db[collection]
        
        # Lấy mã QR bằng ID từ collection đó
        qr_record = user_collection.find_one({"_id": ObjectId(qr_id)})
        
        if not qr_record:
            return jsonify({"error": "QR code not found"}), 404

        # Gửi ảnh QR dưới dạng file
        img_io = BytesIO(qr_record["qr_image"])
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png')

    except Exception as e:
        return jsonify({"error": str(e)}), 500




if __name__ == "__main__": 
    app.run(debug=True)
