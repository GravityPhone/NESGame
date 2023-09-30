
import random

UNIQUE_ITEMS = {
    'Sword of Destiny': {
        'type': 'sword',
        'attack': 100,
        'price': 1000
    },
    'Shield of Aegis': {
        'type': 'shield',
        'defense': 50,
        'price': 800
    }
}

ITEMS = {
    'sword': {
        'type': 'weapon',
        'base_attack': 5,
        'price': 50
    },
    'shield': {
        'type': 'armor',
        'base_defense': 3,
        'price': 30
    }
}

RARITY_MULTIPLIERS = {
    'common': 1,
    'uncommon': 1.5,
    'rare': 2,
    'epic': 3,
    'legendary': 5
}

def generate_random_item():
    rarity = random.choices(
        list(RARITY_MULTIPLIERS.keys()),
        [.6, .25, .1, .04, .01]
    )[0]

    item_type = random.choice(list(ITEMS.keys()))
    base_item = ITEMS[item_type]

    generated_item = {
        'type': base_item['type'],
        'rarity': rarity
    }

    if 'base_attack' in base_item:
        generated_item['attack'] = base_item['base_attack'] * RARITY_MULTIPLIERS[rarity]
    if 'base_defense' in base_item:
        generated_item['defense'] = base_item['base_defense'] * RARITY_MULTIPLIERS[rarity]

    generated_item['price'] = base_item['price'] * RARITY_MULTIPLIERS[rarity]

    return generated_item
