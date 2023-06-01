from flask import Blueprint, request, jsonify
import torch

from firebase_admin import firestore

# utils
from utils.firebase import init_firebase
from utils.score import process_and_score

mvp = Blueprint("mvp", __name__)

db = init_firebase()

users = db.collection("users")


@mvp.route("/label/add", methods=["PUT", "POST"])
def add_urls_to_label():
    urls = request.json.get("urls")
    label = request.json.get("label")

    if not (urls and label):
        return jsonify(status=400, message="Missing urls or label in request body.")

    # if isinstance(urls, list):
    #     return jsonify(status=400, message="urls is expected to be a list.")

    data = dict(urls=urls)
    try:
        if request.method == "PUT":
            # create or replace - PUT
            users.document(label).set(data)
        else:
            # update - POST
            doc_ref = users.document(label).get()
            if doc_ref.exists:
                current_urls = doc_ref.get("urls")
                combined_urls = list(set(current_urls).union(set(urls)))
                data = dict(urls=combined_urls)
            users.document(label).set(data, merge=True)
    except Exception as e:
        return jsonify(
            status=500,
            message="Error caught",
            error=str(e),
        )

    return jsonify(status=201, message="Data created successfully!")


@mvp.route("/score", methods=["GET"])
def score():
    url = request.args.get("url")
    label = request.args.get("label")

    if not url or not label:
        return jsonify(status=400, message="Missing url or label in request body.")

    doc_ref = users.document(label).get()
    if not doc_ref.exists:
        return jsonify(
            status=404, message='There are no labels "{}" in our records.'.format(label)
        )

    label_urls = doc_ref.get("urls")
    score = 0
    for label_url in label_urls:
        new_score = process_and_score(url, label_url)
        print(f"new score {new_score}")
        score += new_score

    score = score / len(label_urls)
    score = round(float(score), 4)

    return jsonify(status=200, data=dict(score=score))


"""
Test Routes
"""
test_collection = db.collection("test")


@mvp.route("/test", methods=["GET"])
def test_route():
    return jsonify(message="MVP endpoint works")


@mvp.route("/test/<id>", methods=["GET"])
def get_test(id):
    try:
        data = test_collection.document(id).get()

        return jsonify(
            status=200,
            message="Data grabbed!",
            data=data.to_dict(),
        )
    except Exception as e:
        return jsonify(
            status=500,
            message="Error caught",
            error=str(e),
        )


@mvp.route("/test", methods=["PUT", "POST"])
def update_test():
    if "id" not in request.json or "data" not in request.json:
        return jsonify(status=400, message="Missing id or data in request body.")
    id = request.json["id"]
    data = request.json["data"]
    try:
        if request.method == "PUT":
            # create or replace - PUT
            test_collection.document(id).set(data)
        else:
            # update - POST
            test_collection.document(id).set(data, merge=True)
    except Exception as e:
        return jsonify(
            status=500,
            message="Error caught",
            error=str(e),
        )

    return jsonify(status=201, message="Data created successfully!")
