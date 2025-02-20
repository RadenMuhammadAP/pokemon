import sqlite3
import requests
from flask import Flask, jsonify, request

# Constants
POKEAPI_URL = "https://pokeapi.co/api/v2/pokemon?limit=10000"
DB_NAME = "pokemon.db"

# Initialize Flask app
app = Flask(__name__)

def init_db():
    """Initialize the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pokemon (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            url TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def fetch_and_store_pokemon():
    """Fetch Pokémon data and store it in the database."""
    response = requests.get(POKEAPI_URL)
    if response.status_code == 200:
        data = response.json()
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        for pokemon in data.get("results", []):
            cursor.execute("INSERT OR IGNORE INTO pokemon (name, url) VALUES (?, ?)", (pokemon["name"], pokemon["url"]))
        conn.commit()
        conn.close()

@app.route("/api/pokemon", methods=["GET"])
def get_pokemon():
    """Retrieve Pokémon data from the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name, url FROM pokemon")
    pokemons = cursor.fetchall()
    conn.close()
    
    jsonapi_response = {
        "data": [
            {
                "type": "pokemon",
                "id": name,
                "attributes": {"name": name, "url": url}
            }
            for name, url in pokemons
        ]
    }
    return jsonify(jsonapi_response)

if __name__ == "__main__":
    init_db()
    fetch_and_store_pokemon()
    app.run(debug=True)
