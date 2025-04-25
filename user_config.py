import json
import os
import random

ADJECTIVES = [
    "Blue", "Red", "Green", "Yellow", "Purple", "Orange", "Silver", "Golden", "Swift", "Silent", "Brave", "Clever", "Lucky", "Gentle", "Wild", "Mighty", "Happy", "Calm", "Fuzzy", "Quick"
]
ANIMALS = [
    "Tiger", "Wolf", "Panther", "Eagle", "Fox", "Bear", "Lion", "Leopard", "Falcon", "Otter", "Hawk", "Dolphin", "Rabbit", "Moose", "Panda", "Swan", "Horse", "Shark", "Owl", "Lynx"
]

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "user_config.json")

def get_or_create_username():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "user_name" in data:
            return data["user_name"]
    # Generate friendly username
    username = f"{random.choice(ADJECTIVES)}{random.choice(ANIMALS)}{random.randint(10, 99)}"
    # Save to config
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump({"user_name": username}, f)
    return username

if __name__ == "__main__":
    print(get_or_create_username())
