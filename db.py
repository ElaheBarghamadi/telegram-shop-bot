import os
import sqlite3
import psycopg2

USE_PG = os.getenv("DATABASE_URL") is not None

if USE_PG:
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
else:
    conn = sqlite3.connect("shop.db", check_same_thread=False)

cur = conn.cursor()

# ---------- INIT ----------
def init_db():
    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id SERIAL PRIMARY KEY,
        name TEXT,
        price INT,
        image TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS cart (
        user_id BIGINT,
        product_id INT,
        qty INT DEFAULT 1
    )
    """)
    conn.commit()


# ---------- PRODUCTS ----------
def add_product(name, price, image):
    cur.execute(
        "INSERT INTO products (name, price, image) VALUES (%s, %s, %s)",
        (name, price, image)
    )
    conn.commit()


def get_products():
    cur.execute("SELECT * FROM products")
    return cur.fetchall()


def get_product(pid):
    cur.execute("SELECT * FROM products WHERE id=%s", (pid,))
    return cur.fetchone()


# ---------- CART ----------
def add_to_cart(uid, pid):
    cur.execute(
        "SELECT qty FROM cart WHERE user_id=%s AND product_id=%s",
        (uid, pid)
    )
    row = cur.fetchone()

    if row:
        cur.execute(
            "UPDATE cart SET qty = qty + 1 WHERE user_id=%s AND product_id=%s",
            (uid, pid)
        )
    else:
        cur.execute(
            "INSERT INTO cart (user_id, product_id, qty) VALUES (%s,%s,1)",
            (uid, pid)
        )

    conn.commit()


def get_cart(uid):
    cur.execute("SELECT product_id, qty FROM cart WHERE user_id=%s", (uid,))
    return cur.fetchall()