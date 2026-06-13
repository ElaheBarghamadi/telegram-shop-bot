import sqlite3

conn = sqlite3.connect("shop.db", check_same_thread=False)
cursor = conn.cursor()

# محصولات
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    price INTEGER,
    image TEXT
)
""")

# سبد خرید
cursor.execute("""
CREATE TABLE IF NOT EXISTS cart (
    user_id INTEGER,
    product_id INTEGER
)
""")

conn.commit()


# ===== محصولات =====
def add_product(name, price, image):
    cursor.execute(
        "INSERT INTO products (name, price, image) VALUES (?, ?, ?)",
        (name, price, image)
    )
    conn.commit()


def get_products():
    cursor.execute("SELECT * FROM products")
    return cursor.fetchall()


def get_product(pid):
    cursor.execute("SELECT * FROM products WHERE id=?", (pid,))
    return cursor.fetchone()


# ===== سبد خرید =====
def add_to_cart(user_id, pid):
    cursor.execute(
        "INSERT INTO cart (user_id, product_id) VALUES (?, ?)",
        (user_id, pid)
    )
    conn.commit()


def get_cart(user_id):
    cursor.execute("SELECT product_id FROM cart WHERE user_id=?", (user_id,))
    return cursor.fetchall()


def clear_cart(user_id):
    cursor.execute("DELETE FROM cart WHERE user_id=?", (user_id,))
    conn.commit()