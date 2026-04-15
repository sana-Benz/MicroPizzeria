# all endpoints
from flask import Blueprint, request, jsonify
from .models import User
from . import db
from .auth import hash_password, check_password, generate_token, verify_token

main = Blueprint("main", __name__)

# REGISTER
@main.route("/auth/register", methods=["POST"])
def register():
    """Create a new user account"""
    data = request.json

    if not data.get("email") or not data.get("password"):
        return jsonify({"error": "Missing fields"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already exists"}), 409

    user = User(
        name=data.get("name"),
        email=data["email"],
        password=hash_password(data["password"]),
        phone=data.get("phone"),
        address=data.get("address")
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"id": user.id, "email": user.email}), 201

# LOGIN
@main.route("/auth/login", methods=["POST"])
def login():
    """Authenticate and get a JWT token"""
    data = request.json

    user = User.query.filter_by(email=data.get("email")).first()

    if not user or not check_password(data["password"], user.password):
        return jsonify({"error": "Invalid credentials"}), 401

    token = generate_token(user.id)

    return jsonify({
        "token": token,
        "expires_in": 3600
    })

# VALIDATE
@main.route("/auth/validate", methods=["GET"])
def validate():
    """Verify a JWT : this endpoint is called by order-service to authenticate users before processing orders."""
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return jsonify({"error": "Missing token"}), 401

    token = auth_header.split(" ")[1]
    user_id = verify_token(token)

    if not user_id:
        return jsonify({"error": "Invalid token"}), 401

    user = User.query.get(user_id)

    return jsonify({
        "valid": True,
        "user_id": user.id,
        "name": user.name
    })



@main.route("/users/me", methods=["GET"])
def get_me():
    """Get current user profile"""
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return jsonify({"error": "Missing token"}), 401

    token = auth_header.split(" ")[1]
    user_id = verify_token(token)

    if not user_id:
        return jsonify({"error": "Invalid token"}), 401

    user = User.query.get(user_id)

    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "address": user.address
    })

@main.route("/users/me", methods=["PUT"])
def update_me():
    """Update profile"""
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return jsonify({"error": "Missing token"}), 401

    token = auth_header.split(" ")[1]
    user_id = verify_token(token)

    if not user_id:
        return jsonify({"error": "Invalid token"}), 401

    user = User.query.get(user_id)
    data = request.json

    if "name" in data:
        user.name = data["name"]
    if "phone" in data:
        user.phone = data["phone"]
    if "address" in data:
        user.address = data["address"]

    db.session.commit()

    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "address": user.address
    })


