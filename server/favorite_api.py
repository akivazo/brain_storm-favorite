from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient



server = Flask(__name__)
CORS(server)
collection = None

def set_mongo_client(mongo_client: MongoClient):
    global collection
    collection = mongo_client.get_database("brain_storm").get_collection("favorite")

@server.route("/")
def root():
    return "Favorite Api"

@server.route("/favorite/<user_name>/<idea_id>", methods=["POST"])
def add_favorite(user_name, idea_id):
    collection.update_one(
        {"Name": user_name},
        {"$addToSet": {"Ideas": idea_id}},  # $addToSet ensures no duplicates
        upsert=True  # Create the document if it doesn't exist
    )
    return jsonify("Idea added succefully"), 200

@server.route("/favorite/<user_name>/<idea_id>", methods=["DELETE"])
def remove_favorite(user_name, idea_id):
    collection.update_one(
        {"Name": user_name},
        {"$pull": {"Ideas": idea_id}},  # $addToSet ensures no duplicates
        upsert=True  # Create the document if it doesn't exist
    )
    return jsonify("Idea removed succefully"), 200


@server.route("/favorite/<user_name>", methods=["GET"])
def get_user_favorites(user_name):
    ideas = collection.find_one({"Name": user_name}, {"_id": 0, "Ideas": 1})
    if ideas:
        return jsonify({"ideas": list(ideas["Ideas"])}), 200
    return jsonify({"ideas": []}), 200
    
if __name__ == "__main__":
    import os, dotenv
    dotenv.load_dotenv()
    mongo_client = MongoClient(os.environ["FAVORITE_MONGODB_URI"])
    set_mongo_client(mongo_client)
    server.run(debug=True, port=5000)
    mongo_client.close()