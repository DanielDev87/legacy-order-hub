from database import get_db_connection


class ProductRepository:
    def get_by_id(self, product_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        product = cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
        conn.close()
        return product

    def create(self, name, price, stock):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
            (name, float(price), int(stock))
        )
        conn.commit()
        product_id = cursor.lastrowid
        conn.close()
        return product_id
