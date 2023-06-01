from flask import Blueprint, jsonify

from firebase_admin import firestore

# utils
from utils.firebase import init_firebase

mvp = Blueprint("mvp", __name__)

db = init_firebase()


@mvp.route("/test", methods=["GET"])
def test_route():
    return jsonify(message="MVP endpoint works")


@mvp.route("/test/<id>", methods=["GET"])
def get_test(id):
    collection = db.collection("test")

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


# @mvp.route("test")
# def put_test
