from flask import Flask, render_template, request, jsonify

import config
from database import init_db
from services.auth_service import AuthService

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY

init_db()
auth_service = AuthService()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"status": "error", "message": "Debe enviar usuario y contraseña"}), 400

    user = auth_service.authenticate(username, password)
    if not user:
        return jsonify({"status": "error", "message": "Credenciales inválidas"}), 401

    return jsonify({
        "status": "success",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "role": user["role"]
        }
    }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

@app.route('/create_order', methods=['POST'])
def create_order():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    product_id = data.get('product_id')
    quantity = int(data.get('quantity', 1))

    conn = get_db_connection()
    cursor = conn.cursor()

    product = cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    if not product:
        conn.close()
        return jsonify({"error": "Producto no encontrado"}), 404

    if product['stock'] < quantity:
        conn.close()
        return jsonify({"error": "Stock insuficiente"}), 400

    total = product['price'] * quantity

    cursor.execute(
        "INSERT INTO orders (user_id, product_id, quantity, total, status) VALUES (?, ?, ?, ?, ?)",
        (user_id, product_id, quantity, total, 'PENDING')
    )
    order_id = cursor.lastrowid

    new_stock = product['stock'] - quantity
    cursor.execute("UPDATE products SET stock = ? WHERE id = ?", (new_stock, product_id))
    conn.commit()
    conn.close()

    print(f"[LOG LEGADO]: Notificando al servicio de correos para la orden ID: {order_id}...")

    return jsonify({
        "message": "Orden creada con éxito",
        "order_id": order_id,
        "total": total
    }), 201

@app.route('/get_all_orders_legacy', methods=['GET'])
def get_orders():
    conn = get_db_connection()
    orders = conn.execute("SELECT * FROM orders").fetchall()
    conn.close()
    
    result = [dict(o) for o in orders]
    return jsonify(result), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)