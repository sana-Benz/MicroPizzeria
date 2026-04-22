from flask import Blueprint, request, jsonify
from .models import MenuItem, Order, OrderItem
from . import db
from .auth_client import validate_token

main = Blueprint("main", __name__)

@main.route("/health", methods=["GET"])
def health():
    """Helps k8s know if the pod is still alive"""
    return jsonify({"status": "ok"}), 200

@main.route("/menu", methods=["GET"])
def get_menu():
    """Returns all the menu"""
    items = MenuItem.query.all()

    return jsonify([
        {
            "id": i.id,
            "name": i.name,
            "category": i.category,
            "price": i.price,
            "description": i.description
        } for i in items
    ])

@main.route("/menu/<int:id>", methods=["GET"])
def get_menu_item(id):
    """Returns information about one menu item"""
    item = MenuItem.query.get(id)

    if not item:
        return jsonify({"error": "Not found"}), 404

    return jsonify({
        "id": item.id,
        "name": item.name,
        "category": item.category,
        "price": item.price,
        "description": item.description
    })

@main.route("/orders", methods=["POST"])
def create_order():
    """Validates one order. Requires authentication."""
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return jsonify({"error": "Missing token"}), 401

    token = auth_header.split(" ")[1]

    user_data = validate_token(token)

    if not user_data:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    items = data.get("items")
    delivery_address = data.get("delivery_address")

    if not items or not delivery_address:
        return jsonify({"error": "Invalid data"}), 400

    total = 0
    order = Order(
        user_id=user_data["user_id"],
        delivery_address=delivery_address
    )

    db.session.add(order)
    db.session.commit()

    for item in items:
        menu_item = MenuItem.query.get(item["menu_item_id"])

        if not menu_item:
            continue

        quantity = item["quantity"]
        total += menu_item.price * quantity

        order_item = OrderItem(
            order_id=order.id,
            menu_item_id=menu_item.id,
            quantity=quantity,
            unit_price=menu_item.price
        )

        db.session.add(order_item)

    order.total = total
    db.session.commit()

    return jsonify({
        "order_id": order.id,
        "status": order.status,
        "total": total
    }), 201

@main.route("/orders", methods=["GET"])
def get_orders():
    """Get the user's order history. Requires Authentication."""
    auth_header = request.headers.get("Authorization")

    token = auth_header.split(" ")[1]
    user_data = validate_token(token)

    orders = Order.query.filter_by(user_id=user_data["user_id"]).all()

    result = []

    for o in orders:
        items = OrderItem.query.filter_by(order_id=o.id).all()

        result.append({
            "order_id": o.id,
            "status": o.status,
            "total": o.total,
            "created_at": o.created_at,
            "items": [
                {
                    "menu_item_id": i.menu_item_id,
                    "quantity": i.quantity,
                    "price": i.unit_price
                } for i in items
            ]
        })

    return jsonify(result)

@main.route("/orders/<int:id>", methods=["GET"])
def get_order(id):
    """Get one particular user order. Requires authentication."""
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return jsonify({"error": "Missing token"}), 401

    token = auth_header.split(" ")[1]
    user_data = validate_token(token)

    if not user_data:
        return jsonify({"error": "Unauthorized"}), 401

    order = Order.query.get(id)

    if not order or order.user_id != user_data["user_id"]:
        return jsonify({"error": "Not found"}), 404

    items = OrderItem.query.filter_by(order_id=order.id).all()

    return jsonify({
        "order_id": order.id,
        "status": order.status,
        "total": order.total,
        "delivery_address": order.delivery_address,
        "created_at": order.created_at,
        "items": [
            {
                "menu_item_id": i.menu_item_id,
                "quantity": i.quantity,
                "price": i.unit_price
            } for i in items
        ]
    })

@main.route("/orders/<int:id>/status", methods=["PUT"])
def update_status(id):
    """Updates the order's status. Requires Authentication"""
    auth_header = request.headers.get("Authorization")
    token = auth_header.split(" ")[1]

    user_data = validate_token(token)
    if not user_data:
        return jsonify({"error": "Unauthorized"}), 401

    order = Order.query.get(id)
    if not order:
        return jsonify({"error": "Not found"}), 404

    data = request.json
    new_status = data.get("status")

    allowed = ["pending", "preparing", "delivered"]

    if new_status not in allowed:
        return jsonify({"error": "Invalid status"}), 400

    order.status = new_status
    db.session.commit()

    return jsonify({
        "order_id": order.id,
        "status": order.status
    })


@main.route("/orders/<int:id>/cancel", methods=["PUT"])
def cancel_order(id):
    """Cancels one order. Requires authentication."""
    auth_header = request.headers.get("Authorization")
    token = auth_header.split(" ")[1]

    user_data = validate_token(token)
    if not user_data:
        return jsonify({"error": "Unauthorized"}), 401

    order = Order.query.get(id)

    if not order:
        return jsonify({"error": "Not found"}), 404

    if order.status != "pending":
        return jsonify({"error": "Cannot cancel"}), 400

    order.status = "cancelled"
    db.session.commit()

    return jsonify({
        "order_id": order.id,
        "status": order.status
    })