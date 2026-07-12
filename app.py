from flask import Flask, render_template, request, redirect, session, jsonify
import mysql.connector
import bcrypt

app = Flask(__name__)
app.secret_key = "secure_fintech_key"

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="ahorro_app",
    autocommit=True
)

cursor = db.cursor(dictionary=True)

# =========================
# LOGIN
# =========================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["user"]
        pw = request.form["password"]

        cursor.execute("SELECT * FROM usuarios WHERE nombre=%s", (user,))
        u = cursor.fetchone()

        if u and bcrypt.checkpw(pw.encode(), u["password"].encode()):
            session["user_id"] = u["id"]
            return redirect("/dashboard")

        return "❌ Usuario o contraseña incorrecta"

    return render_template("login.html")


# =========================
# REGISTER
# =========================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = request.form["user"]
        pw = request.form["password"]
        ingreso = request.form["ingreso"]

        hashed = bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

        try:
            cursor.execute(
                "INSERT INTO usuarios (nombre, password, ingreso_mensual) VALUES (%s,%s,%s)",
                (user, hashed, ingreso)
            )
            return redirect("/")
        except:
            return "❌ Usuario ya existe"

    return render_template("register.html")


# =========================
# DASHBOARD
# =========================
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user_id" not in session:
        return redirect("/")

    uid = session["user_id"]

    # crear meta
    if request.method == "POST":
        monto = request.form["monto"]
        meses = request.form["meses"]

        cursor.execute(
            "INSERT INTO metas (usuario_id, monto_objetivo, meses) VALUES (%s,%s,%s)",
            (uid, monto, meses)
        )

    cursor.execute("SELECT * FROM metas WHERE usuario_id=%s", (uid,))
    metas = cursor.fetchall()

    return render_template("dashboard.html", metas=metas)


# =========================
# PROGRESO API
# =========================
@app.route("/api/progreso/<int:meta_id>")
def progreso(meta_id):
    cursor.execute(
        "SELECT SUM(monto) as total FROM ahorros WHERE meta_id=%s",
        (meta_id,)
    )
    r = cursor.fetchone()

    return jsonify({
        "total": r["total"] if r["total"] else 0
    })


# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)