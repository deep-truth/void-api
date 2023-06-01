from flask import Blueprint, jsonify

mvp = Blueprint("mvp", __name__)


@mvp.route("/test", methods=["GET"])
def test_route():
    return jsonify(message="MVP endpoint works")
