from flask import Flask

# routes
from routes.mvp import mvp

# utils
from utils.firebase import init_firebase


app = Flask(__name__)
app.register_blueprint(mvp, url_prefix="/mvp")


@app.route("/", methods=["GET", "POST"])
def main():
    return "Hello Worlds!"


if __name__ == "__main__":
    init_firebase()

    app.run()
