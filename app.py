from flask import Flask, request, jsonify
from flask_cors import CORS
from db import get_connection
import bcrypt

app = Flask(__name__)
CORS(app)


# ✅ HOME
@app.route("/")
def home():
    return "✅ SIP Backend Running 🚀"


# ✅ REGISTER
@app.route("/register", methods=["POST"])
def register():
    data = request.json

    name = data["name"]
    email = data["email"]
    password = data["password"]

    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (%s,%s,%s)",
            (name, email, hashed_password.decode("utf-8"))
        )
        conn.commit()
        return jsonify({"message": "✅ Registered Successfully!"})

    except:
        return jsonify({"error": "❌ Email already exists!"})

    finally:
        cursor.close()
        conn.close()


# ✅ LOGIN
@app.route("/login", methods=["POST"])
def login():
    data = request.json

    email = data["email"]
    password = data["password"]

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user is None:
        return jsonify({"error": "❌ User not found!"})

    stored_password = user["password"].encode("utf-8")

    if bcrypt.checkpw(password.encode("utf-8"), stored_password):
        return jsonify({
            "message": "✅ Login Successful!",
            "user": user["name"],
            "user_id": user["id"]
        })

    return jsonify({"error": "❌ Invalid Password!"})


# ✅ SIP SAVE
@app.route("/sip-calculate", methods=["POST"])
def sip_calculate():
    data = request.json

    user_id = data["user_id"]
    monthly_amount = int(data["monthly_amount"])
    years = int(data["years"])
    rate = float(data["rate"])

    months = years * 12
    r = rate / 12 / 100

    maturity_amount = monthly_amount * (((1 + r) ** months - 1) / r) * (1 + r)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO sip_plans (user_id, monthly_amount, years, rate, maturity_amount) "
        "VALUES (%s,%s,%s,%s,%s)",
        (user_id, monthly_amount, years, rate, maturity_amount)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({
        "message": "✅ SIP Saved Successfully!",
        "maturity_amount": round(maturity_amount, 2)
    })


# ✅ SIP PLANS VIEW
@app.route("/my-sips/<int:user_id>", methods=["GET"])
def my_sips(user_id):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM sip_plans WHERE user_id=%s", (user_id,))
    plans = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({"sip_plans": plans})


# ✅ PROFILE API (BALANCE FIX)
@app.route("/profile/<int:user_id>", methods=["GET"])
def profile(user_id):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT id, name, email, balance FROM users WHERE id=%s",
        (user_id,)
    )

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user is None:
        return jsonify({"error": "❌ User not found"}), 404

    return jsonify(user)


# ✅ RUN SERVER (LAST LINE ALWAYS)
if __name__ == "__main__":
    app.run(port=5000, debug=True)