from flask import Flask

# routes
from routes.mvp import mvp

app = Flask(__name__)
app.register_blueprint(mvp, url_prefix="/mvp")


@app.route("/", methods=["GET", "POST"])
def main():
    return "Hello Worlds!"


if __name__ == "__main__":
    app.run()
