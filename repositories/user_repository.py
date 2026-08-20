from database import get_db_connection


class UserRepository:
    def get_by_credentials(self, username, password):
        conn = get_db_connection()
        cursor = conn.cursor()
        user = cursor.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password)
        ).fetchone()
        conn.close()
        return user

    def get_by_username(self, username):
        conn = get_db_connection()
        cursor = conn.cursor()
        user = cursor.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()
        return user
