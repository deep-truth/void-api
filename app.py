from flask import Flask
from flask_cors import CORS

# routes
from routes.mvp import mvp

# utils
from utils.firebase import init_firebase

import random

app = Flask(__name__)
app.register_blueprint(mvp, url_prefix="/mvp")
CORS(app)


@app.route("/", methods=["GET", "POST"])
def main():
    return f"Hello Worlds! -- {random.randint(0, 100)}"


if __name__ == "__main__":
    init_firebase()

    app.run()
