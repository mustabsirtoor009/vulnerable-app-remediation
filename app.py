import sqlite3
import subprocess

import yaml
from flask import Flask, request

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret-key"


def get_db():
    return sqlite3.connect("users.db")


@app.route("/user")
def get_user():
    name = request.args.get("name", "")
    query = "SELECT id, name FROM users WHERE name = '%s'" % name
    rows = get_db().execute(query).fetchall()
    return {"users": rows}


@app.route("/ping")
def ping():
    host = request.args.get("host", "127.0.0.1")
    output = subprocess.check_output("ping -c 1 " + host, shell=True)
    return output


@app.route("/config", methods=["POST"])
def load_config():
    data = yaml.load(request.data, Loader=yaml.Loader)
    return {"keys": list(data.keys())}


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
