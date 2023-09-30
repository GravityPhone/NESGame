import os
import random
import sqlite3
import time

from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user
from werkzeug.security import check_password_hash, generate_password_hash

from items_generator import generate_random_item

app = Flask(__name__)
app.secret_key = os.urandom(24)

MAX_GOLD_VALUE = 10**12  # Set a maximum limit for gold


class Shop:
    def __init__(self):
        self.items = {
            "basic_sword": 100,
            "silver_sword": 250,
            "golden_sword": 500,
            "xp_sword": 200,
        }

    def buy(self, item, barbarian):
        if item in self.items and barbarian["gold"] >= self.items[item]:
            barbarian["gold"] -= self.items[item]
            barbarian["items"].append(item)
            return f"Bought a {item.replace('_', ' ')}!"
        else:
            return "Transaction failed. Either the item doesn't exist or you don't have enough gold."


def go_on_adventure(barbarian):
    base_gold_earned = random.randint(5, 15)
    gold_earned = base_gold_earned
    xp_earned = random.randint(1, 5)
    item_earned = generate_random_item()
    barbarian["items"].append(item_earned)

    # Sword bonuses
    if "basic_sword" in barbarian["items"]:
        gold_earned += 5
    if "silver_sword" in barbarian["items"]:
        gold_earned += int(base_gold_earned * 0.2)
    if "golden_sword" in barbarian["items"]:
        gold_earned += 10
        gold_earned += int(base_gold_earned * 0.1)
    if "xp_sword" in barbarian["items"]:
        xp_earned += 2

    barbarian["gold"] += gold_earned
    barbarian["experience"] += xp_earned
    barbarian["gold"] = min(barbarian["gold"], MAX_GOLD_VALUE)  # Limit the gold value

    while barbarian["experience"] >= barbarian["level"] * 10:
        barbarian["experience"] -= barbarian["level"] * 10
        barbarian["level"] += 1

    return gold_earned, xp_earned


def calculate_and_simulate_adventures(barbarian):
    current_time = time.time()
    last_time = barbarian.get("last_adventure_time", current_time)
    elapsed_time = current_time - last_time

    num_adventures = int(elapsed_time // 5)

    for _ in range(num_adventures):
        go_on_adventure(barbarian)

    barbarian["last_adventure_time"] = current_time


@app.route("/")
@login_required
def home():
    default_barbarian = {
        "gold": 0,
        "experience": 0,
        "level": 1,
        "items": [],
        "auto_adventure": False,
        "last_adventure_time": time.time(),
    }

    barbarian = session.get("barbarian", default_barbarian)

    # Check if 'id' key is in the barbarian dictionary
    if "id" not in barbarian:
        conn = sqlite3.connect("game.db")
        c = conn.cursor()
        c.execute("SELECT id FROM player WHERE username = ?", (current_user.username,))
        barbarian["id"] = c.fetchone()[0]
        conn.close()

    if barbarian["auto_adventure"]:
        calculate_and_simulate_adventures(barbarian)

    session["barbarian"] = barbarian
    return render_template(
        "home.html", barbarian=barbarian, shop=Shop().items, items=barbarian["items"]
    )


@app.route("/adventure", methods=["POST"])
def adventure():
    barbarian = session.get("barbarian")
    go_on_adventure(barbarian)
    session["barbarian"] = barbarian

    # Check if 'id' key is in the barbarian dictionary
    if "id" not in barbarian:
        return "Error: Player's id could not be found."

    conn = sqlite3.connect("game.db")
    c = conn.cursor()
    c.execute(
        "UPDATE player SET items = ? WHERE id = ?",
        (str(barbarian["items"]), barbarian["id"]),
    )
    conn.commit()
    conn.close()
    return redirect(url_for("home"))


@app.route("/buy/<item>", methods=["POST"])
def buy(item):
    barbarian = session.get("barbarian")
    shop = Shop()
    shop.buy(item, barbarian)
    session["barbarian"] = barbarian
    return redirect(url_for("home"))


@app.route("/toggle_auto_adventure", methods=["POST"])
def toggle_auto_adventure():
    barbarian = session.get("barbarian")
    barbarian["auto_adventure"] = not barbarian["auto_adventure"]
    barbarian["last_adventure_time"] = time.time()
    session["barbarian"] = barbarian
    return redirect(url_for("home"))


@app.route("/get_gold")
def get_gold():
    barbarian = session.get("barbarian")
    if barbarian["auto_adventure"]:
        calculate_and_simulate_adventures(barbarian)
    return str(barbarian["gold"])


@app.route("/get_xp")
def get_xp():
    barbarian = session.get("barbarian")
    if barbarian["auto_adventure"]:
        calculate_and_simulate_adventures(barbarian)
    return str(barbarian["experience"])


@app.route("/login", methods=["GET"])
def login():
    return render_template("login.html")


@app.route("/create_user", methods=["POST"])
def create_user():
    username = request.form.get("username")
    password = request.form.get("password")

    conn = sqlite3.connect("game.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO player (username, password) VALUES (?, ?)",
        (username, generate_password_hash(password)),
    )
    conn.commit()
    conn.close()

    return redirect(url_for("login"))


@app.route("/login", methods=["POST"])
def login_post():
    username = request.form.get("username")
    password = request.form.get("password")

    conn = sqlite3.connect("game.db")
    c = conn.cursor()
    c.execute("SELECT * FROM player WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()

    if not user:
        flash("User does not exist. Please create a new account.")
        return redirect(url_for("create_user"))
    elif not check_password_hash(user[1], password):
        flash("Please check your login details and try again.")
        return redirect(url_for("login"))

    login_user(user)
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=False)
