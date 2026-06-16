from flask import Flask, request, jsonify, send_from_directory
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import base64
import os
import sqlite3
import random

app = Flask(__name__, static_folder="static")

# AES Key (Must be 16, 24, or 32 bytes long)
SECRET_KEY = b'SixteenByteKey!!'  # Must be exactly 16 bytes for AES-128

# Dictionary to keep track of failed attempts (only affects UI users)
failed_attempts = {}
MAX_ATTEMPTS = 3


# Encrypt function using AES CBC mode
def aes_encrypt(plain_text):
    iv = os.urandom(16)  # Generate a random IV
    cipher = Cipher(algorithms.AES(SECRET_KEY), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # Pad the text
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plain_text.encode()) + padder.finalize()

    # Encrypt
    encrypted_text = encryptor.update(padded_data) + encryptor.finalize()

    return base64.b64encode(iv + encrypted_text).decode()


# Decrypt function using AES CBC mode
def aes_decrypt(encrypted_text):
    try:
        raw = base64.b64decode(encrypted_text)
        iv = raw[:16]
        cipher = Cipher(algorithms.AES(SECRET_KEY), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()

        decrypted_padded_text = decryptor.update(raw[16:]) + decryptor.finalize()

        # Unpad the decrypted text
        unpadder = padding.PKCS7(128).unpadder()
        decrypted_text = unpadder.update(decrypted_padded_text) + unpadder.finalize()

        return decrypted_text.decode()
    except Exception:
        return None  # Return None if decryption fails


# Fake honey encryption responses for brute force attack
def honey_encrypt_response():
    fake_data = [
        {"status": "success", "message": "Successful attempt!"},
        {"status": "success", "message": "Login successful!"},
        {"status": "success", "message": "Access granted!"}
    ]
    return random.choice(fake_data)


# Initialize SQLite database
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )""")
    conn.commit()
    conn.close()


# Add a user to the database
def add_user(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    encrypted_password = aes_encrypt(password)
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, encrypted_password))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # Ignore if user already exists
    conn.close()


# API to handle login
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    user_data = cursor.fetchone()
    conn.close()

    user_agent = request.headers.get("User-Agent", "").lower()

    # **For Brute-Force Attacks (Python scripts using requests)**
    if "python-requests" in user_agent:
        return jsonify(honey_encrypt_response())  # Always show success

    # **For Normal Users (Web UI)**
    if user_data:
        encrypted_password = user_data[0]
        decrypted_password = aes_decrypt(encrypted_password)

        if decrypted_password and decrypted_password == password:
            # Reset failed attempts on successful login
            failed_attempts[username] = 0
            return jsonify({"status": "success", "message": "Welcome back!"})

        # Track failed attempts for UI logins only
        failed_attempts[username] = failed_attempts.get(username, 0) + 1

        # **Block UI login if too many failed attempts**
        if failed_attempts[username] >= MAX_ATTEMPTS:
            return jsonify({"status": "failed", "message": "Login is blocked. Too many failed attempts."})

        return jsonify({"status": "failed", "message": "Incorrect password."})

    return jsonify({"status": "failed", "message": "User not found."})


# Serve the frontend
@app.route("/")
def serve_frontend():
    return send_from_directory("static", "index.html")


# Serve static files (CSS, JS)
@app.route("/<path:path>")
def serve_static_files(path):
    return send_from_directory("static", path)


if __name__ == "__main__":
    init_db()
    add_user("admin", "admin123")  # Default users
    add_user("user1", "login123")
    app.run(debug=True, port=5500)
