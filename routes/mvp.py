from flask import Blueprint, request, jsonify
import torch

from firebase_admin import firestore

# utils
from utils.firebase import init_firebase
from utils.score import process_and_score

mvp = Blueprint("mvp", __name__)

db = init_firebase()

admins = db.collection("admins")

# GET /mvp/labels
@mvp.route("/labels", methods=["GET"])
def get_labels():
    admin = request.args.get("admin")

    if not admin:
        return jsonify(status=400, message="Missing `admin` in request.")
    labels = []
    doc_ref = admins.document(admin).collection("labels").get()

    for label in doc_ref:
        labels.append(label.id)

    return jsonify(status=200, data=labels, message="Retrieved data successfully!")
    

# PUT /mvp/labels -- Add new label or replace existing 
# POST /mvp/labels -- Update existing labels
@mvp.route("/labels", methods=["PUT", "POST"])
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
    labels_doc = admins.document(admin).collection("labels")
    try:
        if request.method == "PUT":
            # create or replace - PUT
            labels_doc.document(label).set(data)
        else:
            # update - POST
            doc_ref = admins.document(label).get()
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
    admin = request.args.get("admin")

    if not (blob_path and label and admin):
        return jsonify(status=400, message="Missing admin, blob_path, or label in request body.")

    labels_doc = admins.document(admin).collection("labels")
    label_doc_ref = labels_doc.document(label).get()
    if not label_doc_ref.exists:
        return jsonify(
            status=404, message='There are no labels "{}" in our records.'.format(label)
        )

    label_blob_paths = label_doc_ref.get("blob_paths")
    score = 0
    for label_url in label_blob_paths:
        new_score = process_and_score(blob_path, label_url)
        score += new_score

    score = score / len(label_blob_paths)
    score = round(float(score), 4)

    return jsonify(status=200, data=dict(score=score))
