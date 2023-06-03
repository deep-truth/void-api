from flask import Blueprint, request, jsonify
import torch

from firebase_admin import firestore

# utils
from utils.firebase import init_firebase
from utils.score import process_and_score

mvp = Blueprint("mvp", __name__)

db = init_firebase()

users = db.collection("users")

# PUT /mvp/label/add -- Add new label or replace existing 
# POST /mvp/label/add -- Update existing labels
@mvp.route("/label/add", methods=["PUT", "POST"])
def add_blob_paths_to_label():
    """Add list of blob urls to a label (name of the speaker in the blob audio files) created by an admin

    Always have `admin` (str), `label` (str), and `blob_paths` (List[str]) in your request.
    """
    blob_paths = request.json.get("blob_paths")
    label = request.json.get("label")
    admin = request.json.get("admin")

    if not (blob_paths and label and admin):
        return jsonify(status=400, message="Missing admin, blob_paths, or label in request body.")

    # if isinstance(blob_paths, list):
    #     return jsonify(status=400, message="blob_paths is expected to be a list.")

    data = dict(blob_paths=blob_paths)
    labels_doc = users.document(admin).collection("labels")
    try:
        if request.method == "PUT":
            # create or replace - PUT
            labels_doc.document(label).set(data)
        else:
            # update - POST
            doc_ref = users.document(label).get()
            if doc_ref.exists:
                current_blob_paths = doc_ref.get("blob_paths")
                combined_blob_paths = list(set(current_blob_paths).union(set(blob_paths)))
                data = dict(blob_paths=combined_blob_paths)
            labels_doc.document(label).set(data, merge=True)
    except Exception as e:
        return jsonify(
            status=500,
            message="Error caught",
            error=str(e),
        )

    return jsonify(status=201, message="Data created successfully!")


@mvp.route("/score", methods=["GET"])
def score():
    blob_path = request.args.get("blob_path")
    label = request.args.get("label")

    if not blob_path or not label:
        return jsonify(status=400, message="Missing url or label in request body.")

    doc_ref = users.document(label).get()
    if not doc_ref.exists:
        return jsonify(
            status=404, message='There are no labels "{}" in our records.'.format(label)
        )

    label_blob_paths = doc_ref.get("blob_paths")
    score = 0
    for label_url in label_blob_paths:
        new_score = process_and_score(blob_path, label_url)
        print(f"new score {new_score}")
        score += new_score

    score = score / len(label_blob_paths)
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
