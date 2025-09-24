from flask import Flask, render_template, request, redirect, url_for, session


app = Flask(__name__)
app.secret_key = "dev-secret-key-change-me"


# Demo users and roles (no password for simplicity)
DEMO_USERS = {
    "admin": "admin",
    "buyer": "buyer",
    "warehouse": "warehouse",
    "finance": "finance",
}


# In-memory demo data stores
ORDERS = []  # {id, customer, product, quantity, unit_price, status}
PURCHASES = []  # {id, vendor, product, quantity, unit_cost, status}
INVENTORY = {}  # product -> quantity


def require_login(view_func):
    def wrapper(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)

    wrapper.__name__ = view_func.__name__
    return wrapper


@app.route("/")
def index():
    if session.get("user"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        role = DEMO_USERS.get(username)
        if role:
            session["user"] = username
            session["role"] = role
            return redirect(url_for("dashboard"))
        error = "無效的帳號（可用：admin/buyer/warehouse/finance）"
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@require_login
def dashboard():
    role = session.get("role")
    return render_template("dashboard.html", role=role)


# --- Modules (initial placeholders) ---


@app.route("/orders")
@require_login
def orders():
    return render_template("orders.html", orders=ORDERS)


@app.route("/purchase")
@require_login
def purchase():
    return render_template("purchase.html", purchases=PURCHASES)


@app.route("/inventory")
@require_login
def inventory():
    # Build simple inventory list
    items = sorted(({"product": p, "quantity": q} for p, q in INVENTORY.items()), key=lambda x: x["product"])
    return render_template("inventory.html", inventory_items=items)


@app.route("/finance")
@require_login
def finance():
    # Simple totals for demo
    total_revenue = sum(o["quantity"] * o["unit_price"] for o in ORDERS if o.get("status") in {"已出貨", "已付款"})
    total_cost = sum(p["quantity"] * p["unit_cost"] for p in PURCHASES if p.get("status") == "已入庫")
    inventory_value = 0
    # If we had unit cost per product, sum(INVENTORY[product] * average_cost). For demo keep 0.
    return render_template(
        "finance.html",
        total_revenue=total_revenue,
        total_cost=total_cost,
        inventory_value=inventory_value,
    )


@app.route("/admin", methods=["GET", "POST"])
@require_login
def admin():
    message = None
    if request.method == "POST":
        action = request.form.get("action")
        if action == "reset":
            ORDERS.clear()
            PURCHASES.clear()
            INVENTORY.clear()
            message = "系統已初始化（暫存資料已清空）"
    return render_template("admin.html", users=list(DEMO_USERS.keys()), message=message)


if __name__ == "__main__":
    app.run(debug=True)


