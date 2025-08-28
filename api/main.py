import db
from chains import make_response
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/users", methods=["POST"])
def post_user():
    data = request.json
    if db.get_user_registered(data["telegram_id"]):
        return {"message": "already registered"}, 409
    if "telegram_id" in data and "name" in data:
        db.insert_user(data)
    else:
        return jsonify({"message": "Invalid data"}), 400
    return {"message": "success"}, 201


@app.route("/prompt", methods=["POST"])
def prompt():
    data = request.json
    user_id = db.get_user_registered(data["user_id"])
    if user_id:
        return make_response(user_id=user_id, question=data["prompt"])
    return {"message": "Not registered"}, 401


if __name__ == "__main__":
    app.run()
