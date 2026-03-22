from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
from werkzeug.utils import secure_filename
import urllib.parse
import uuid

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24))

# =============================
# Upload Configuration
# =============================
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def get_cart():
    if "cart" not in session:
        session["cart"] = []
    return session["cart"]

# =============================
# Product Data (UPDATED WITH IMAGES)
# =============================
products = {
    "Garelu (Pappu)": {
        "desc": "1 Kg - 50 Units | Rice flour, Channa dal, Salt, Red mirchi, Sesame seeds, Spring onion, Coriander, Curry leaves",
        "image": "images/pappu_garelu.jpeg",
        "price": 399,
        "tags": ["snack"]
    },
    "Garelu (Palli)": {
        "desc": "1 Kg - 50 Units | Rice flour, Ground nut, Salt, Red mirchi, Sesame seeds, Spring onion, Coriander, Curry leaves",
        "image": "images/palli_garelu.jpeg",
        "price": 399,
        "tags": ["snack"]
    },
    "Murukulu (Regular)": {
        "desc": "1 Kg - 40 Units | Channa dal, Jeera, Sesame seeds, Coriander cumin powder, Red mirchi, Salt",
        "image": "images/murukulu_regular.jpeg",
        "price": 399,
        "tags": ["snack", "bestseller"]
    },
    "Murukulu (Broad)": {
        "desc": "1 Kg - 40 Units | Channa dal, Jeera, Sesame seeds, Coriander cumin powder, Red mirchi, Salt",
        "image": "images/murukulu_broad.jpeg",
        "price": 399,
        "tags": ["snack", "bestseller"]
    },
    "Arisalu": {
        "desc": "1 Kg - 24 Units | Jaggery, Rice flour, Sesame seeds",
        "image": "images/arisalu.jpeg",
        "price": 399,
        "tags": ["sweet", "bestseller"]
    },
    "Karjikayalu": {
        "desc": "1 Kg - 20 Units | Maida, Wheat, Groundnut, Coconut, Sesame seeds, Jaggery, Ravva, Sugar",
        "image": "images/karjikayalu.jpeg",
        "price": 399,
        "tags": ["sweet"]
    },
    "Sunnundalu": {
        "desc": "1 Kg - 24 Units | Ghee, Urad dal, Moong dal, Sugar",
        "image": "images/sunnundalu.jpeg",
        "price": 599,
        "tags": ["sweet"]
    },
    "Boondhi Laddu": {
        "desc": "1 Kg - 24 Units | Channa dal, Sugar, Dry fruits",
        "image": "images/boondhi_laddu.jpeg",
        "price": 399,
        "tags": ["sweet", "bestseller"]
    },
    "Ravva Laddu": {
        "desc": "1 Kg - 24 Units | Ravva, Sugar, Dry fruits",
        "image": "images/ravva_laddu.jpeg",
        "price": 399,
        "tags": ["sweet"]
    },
    "Palli Laddu": {
        "desc": "1 Kg - 20 Units | Groundnut, Jaggery, Sesame seeds",
        "image": "images/palli_laddu.jpeg",
        "price": 399,
        "tags": ["sweet"]
    },
    "Sakinalu (Salted)": {
        "desc": "1 Kg - 55 Units | Rice flour, Jeera, Vamu, Salt",
        "image": "images/sakinalu_salted.jpeg",
        "price": 399,
        "tags": ["snack"]
    },
    "Sakinalu (Karam)": {
        "desc": "1 Kg - 55 Units | Rice flour, Jeera, Red/Green mirchi, Garlic, Vamu, Coriander leaves, Salt",
        "image": "images/sakinalu_karam.jpeg",
        "price": 399,
        "tags": ["snack"]
    },
    "Gavvalu": {
        "desc": "1 Kg - 24 Units | Wheat, Maida, Sugar/Jaggery, Ravva",
        "image": "images/gavvalu.jpeg",
        "price": 399,
        "tags": ["sweet"]
    },
    "Salividi": {
        "desc": "1 Kg | Rice flour, Sugar, Dry fruits",
        "image": "images/salividi.jpeg",
        "price": 399,
        "tags": ["sweet"]
    },
    "Chuduva": {
        "desc": "1 Kg | Karam Boondhi",
        "image": "images/chuduva.jpeg",
        "price": 399,
        "tags": ["snack"]
    },
    "Avakaya (Mango Pickle)": {
        "desc": "500g | Raw mango, Red mirchi powder, Mustard seeds, Salt, Sesame oil",
        "image": "images/mango.jpeg",
        "price": 499,
        "tags": ["pickle"]
    },
    "Nimmakaya (Lemon Pickle)": {
        "desc": "500g | Lemon, Red mirchi powder, Salt, Sesame oil",
        "image": "images/lemon.jpeg",
        "price": 499,
        "tags": ["pickle"]
    },
    "Tomato Pickle": {
        "desc": "500g | Tomato, Red mirchi, Garlic, Mustard seeds, Sesame oil",
        "image": "images/tomato.jpeg",
        "price": 499,
        "tags": ["pickle"]
    }
}

# =============================
# Routes
# =============================
@app.route("/")
def home():
    return render_template("index.html", products=products)


@app.route("/menu")
def menu():
    return render_template("menu.html", products=products)


@app.route("/add", methods=["POST"])
def add():
    item = request.form.get("item", "").strip()
    qty_raw = request.form.get("qty", "").strip()

    if not item or not qty_raw.isdigit() or int(qty_raw) <= 0:
        return "Invalid item or quantity", 400

    qty = int(qty_raw)
    price = products.get(item, {}).get("price", 399)
    cart = get_cart()
    for entry in cart:
        if entry["item"] == item:
            entry["qty"] += qty
            session.modified = True
            break
    else:
        cart.append({"item": item, "qty": qty, "price": price})
        session.modified = True

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"status": "ok", "cart_count": len(cart)})

    return redirect(url_for("cart_page"))


@app.route("/update/<int:index>", methods=["POST"])
def update(index):
    cart = get_cart()
    if 0 <= index < len(cart):
        qty_raw = request.form.get("qty", "").strip()
        if qty_raw.isdigit() and int(qty_raw) > 0:
            cart[index]["qty"] = int(qty_raw)
        else:
            cart.pop(index)
        session.modified = True
    return redirect(url_for("cart_page"))


@app.route("/delete/<int:index>")
def delete(index):
    cart = get_cart()
    if 0 <= index < len(cart):
        cart.pop(index)
        session.modified = True
    return redirect(url_for("cart_page"))


@app.route("/cart")
def cart_page():
    cart = get_cart()
    total = sum(i["qty"] * i.get("price", 399) for i in cart)
    advance = round(total * 0.20, 2)
    return render_template("cart.html", cart=cart, total=total, advance=advance)


@app.route("/booking", methods=["GET", "POST"])
def booking():
    cart = get_cart()
    total = sum(i["qty"] * i.get("price", 399) for i in cart)
    advance = round(total * 0.20, 2)

    if request.method == "POST":

        name = request.form.get("name")
        phone = request.form.get("phone")
        address = request.form.get("address")

        # Use form-embedded values as fallback if session cart is empty
        if total == 0:
            try:
                total = float(request.form.get("total", 0))
                advance = float(request.form.get("advance", 0))
            except (ValueError, TypeError):
                pass

        message = f"""
New Order Placed!

Name: {name}
Customer Phone: {phone}
Delivery Address: {address}

Order Details:
"""

        for item in cart:
            subtotal = item['qty'] * item.get('price', 399)
            message += f"- {item['item']} x {item['qty']} kg @ ₹{item.get('price', 399)}/kg = ₹{subtotal}\n"

        message += f"""
--------------------------------
Total Amount: ₹{total}
Advance Required (20%): ₹{advance}
--------------------------------
"""

        encoded_message = urllib.parse.quote(message)

        whatsapp_number = "918247336418"

        whatsapp_url = f"https://wa.me/{whatsapp_number}?text={encoded_message}"

        session.pop("cart", None)

        return redirect(whatsapp_url)

    return render_template("booking.html", cart=cart, total=total, advance=advance)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)