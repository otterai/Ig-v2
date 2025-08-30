import os
import random
import requests
from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://PythonBotz:Baddie@cluster0.xunylzo.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
client = MongoClient(MONGO_URI)
db = client["ig_api"]
collection = db["users"]

# Method Types
METHOD_TYPES = [
    "Spam", "Harassment", "Hate Speech", "Violence",
    "False Information", "Nudity", "Bullying",
    "Impersonation", "Copyright", "Self-Harm"
]

def generate_random_methods(username: str):
    """Generate & cache random methods in DB"""
    existing = collection.find_one({"username": username})
    if existing and "methods" in existing:
        return existing["methods"]

    num_methods = random.randint(3, 5)
    selected = random.sample(METHOD_TYPES, num_methods)

    formatted = []
    for method in selected:
        qty = random.randint(1, 5)
        formatted.append(f"{qty}x {method}")

    return formatted


@app.route("/api/meth", methods=["GET"])
def get_instagram_info():
    username = request.args.get("user", "").strip()
    if not username:
        return jsonify({
            "success": False,
            "message": "⚠️ Please provide a valid Instagram username!",
            "credits": "TG @PythonBotz × @DrSudo"
        }), 400

    # Check cache
    cached = collection.find_one({"username": username})
    if cached:
        return jsonify({
            "success": True,
            "data": cached["data"],
            "methods": cached["methods"],
            "credits": "TG @PythonBotz × @DrSudo"
        })

    try:
        resp = requests.get(f"https://ig-info-drsudo.vercel.app/api/ig?user={username}", timeout=8)
        if resp.status_code != 200:
            return jsonify({
                "success": False,
                "message": "🚨 Failed to fetch Instagram data. Please try again later!",
                "credits": "TG @PythonBotz × @DrSudo"
            }), 502

        data = resp.json()
        if not data.get("success"):
            return jsonify({
                "success": False,
                "message": f"❌ No Instagram account found for username: <b>{username}</b>",
                "hint": "Double-check spelling or try another account.",
                "credits": "TG @PythonBotz × @DrSudo"
            }), 404

        methods = generate_random_methods(username)

        # Save to DB
        collection.insert_one({
            "username": username,
            "data": data,
            "methods": methods
        })

        return jsonify({
            "success": True,
            "data": data,
            "methods": methods,
            "credits": "TG @PythonBotz × @DrSudo"
        })

    except requests.Timeout:
        return jsonify({
            "success": False,
            "message": "⏳ Request timed out. Please try again later.",
            "credits": "TG @PythonBotz × @DrSudo"
        }), 504
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"⚠️ Unexpected error: {str(e)}",
            "credits": "TG @PythonBotz × @DrSudo"
        }), 500


# Vercel handler
def handler(request, *args, **kwargs):
    return app(request, *args, **kwargs)
