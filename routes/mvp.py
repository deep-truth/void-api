from flask import Blueprint, request, jsonify

from firebase_admin import firestore

# utils
from utils.firebase import init_firebase

mvp = Blueprint("mvp", __name__)

db = init_firebase()
collection = db.collection("test")


@mvp.route("/test", methods=["GET"])
def test_route():
    return jsonify(message="MVP endpoint works")


@mvp.route("/test/<id>", methods=["GET"])
def get_test(id):
    try:
        data = collection.document(id).get()

        return jsonify(
            code=200,
            message="Data grabbed!",
            data=data.to_dict(),
        )
    except Exception as e:
        return jsonify(
            code=500,
            message="Error caught",
            error=str(e),
        )


@mvp.route("/test", methods=["PUT", "POST"])
def update_test():
    if "id" not in request.json or "data" not in request.json:
        return jsonify(code=400, message="Missing id or data in request body.")
    id = request.json["id"]
    data = request.json["data"]
    # create or replace
    try:
        if request.method == "PUT":
            collection.document(id).set(data)
        else:
            collection.document(id).set(data, merge=True)
    except Exception as e:
        return jsonify(
            code=500,
            message="Error caught",
            error=str(e),
        )

    return jsonify(code=201, message="Data created successfully!")
