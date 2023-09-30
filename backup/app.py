
from flask import Flask, render_template, session, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
import time
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game.db'
db = SQLAlchemy(app)
app.secret_key = 'super secret key'

DEFAULT_BARBARIAN = {
    'gold': 0,
    'experience': 0,
    'level': 1,
    'inventory': [],
    'auto_adventure': False,
    'last_adventure_time': time.time()
}

class Shop:
    def __init__(self):
        self.items = {
            "basic_sword": 100,
            "silver_sword": 250,
            "golden_sword": 500,
            "xp_sword": 200
        }

    def buy(self, item, barbarian):
        if item in self.items and barbarian['gold'] >= self.items[item]:
            barbarian['gold'] -= self.items[item]
            barbarian['inventory'].append(item)
            return f"Bought a {item.replace('_', ' ')}!"
        else:
            return "Transaction failed. Either the item doesn't exist or you don't have enough gold."

def go_on_adventure(barbarian):
    base_gold_earned = random.randint(5, 15)
    gold_earned = barbarian['gold'] + base_gold_earned
    xp_earned = random.randint(1, 5)

    # Sword bonuses
    if "basic_sword" in barbarian['inventory']:
        gold_earned += 5
    if "silver_sword" in barbarian['inventory']:
        gold_earned += int(base_gold_earned * 0.2)
    if "golden_sword" in barbarian['inventory']:
        gold_earned += 10
        gold_earned += int(base_gold_earned * 0.1)
    if "xp_sword" in barbarian['inventory']:
        xp_earned += 2

    barbarian['gold'] += gold_earned
    barbarian['experience'] += xp_earned

    while barbarian['experience'] >= barbarian['level'] * 10:
        barbarian['experience'] -= barbarian['level'] * 10
        barbarian['level'] += 1

    return gold_earned, xp_earned

def calculate_and_simulate_adventures(barbarian):
    current_time = time.time()
    last_time = barbarian.get('last_adventure_time', current_time)
    elapsed_time = current_time - last_time

    num_adventures = int(elapsed_time // 5)
    
    for _ in range(num_adventures):
        go_on_adventure(barbarian)

    barbarian['last_adventure_time'] = current_time

@app.route('/')
def home():
    barbarian = session.get('barbarian', DEFAULT_BARBARIAN.copy())

    for key, value in DEFAULT_BARBARIAN.items():
        if key not in barbarian:
            barbarian[key] = value

    if barbarian['auto_adventure']:
        calculate_and_simulate_adventures(barbarian)
    
    session['barbarian'] = barbarian
    return render_template('home.html', barbarian=barbarian, shop=Shop().items)

@app.route('/adventure', methods=['POST'])
def adventure():
    barbarian = session.get('barbarian')
    go_on_adventure(barbarian)
    session['barbarian'] = barbarian
    return redirect(url_for('home'))

@app.route('/buy/<item>', methods=['POST'])
def buy(item):
    barbarian = session.get('barbarian')
    shop = Shop()
    shop.buy(item, barbarian)
    session['barbarian'] = barbarian
    return redirect(url_for('home'))

@app.route('/toggle_auto_adventure', methods=['POST'])
def toggle_auto_adventure():
    barbarian = session.get('barbarian', DEFAULT_BARBARIAN.copy())
    barbarian['auto_adventure'] = not barbarian['auto_adventure']
    barbarian['last_adventure_time'] = time.time()
    session['barbarian'] = barbarian
    return redirect(url_for('home'))

@app.route('/get_gold')
def get_gold():
    barbarian = session.get('barbarian')
    if barbarian['auto_adventure']:
        calculate_and_simulate_adventures(barbarian)
    return str(barbarian['gold'])

if __name__ == '__main__':
    app.run(debug=True)
