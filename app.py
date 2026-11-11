import os
import re
import sqlite3
import subprocess

import yaml
from flask import Flask, abort, request

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]

HOST_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.-]{0,252}$")


def get_db():
    return sqlite3.connect("users.db")


@app.route("/user")
def get_user():
    name = request.args.get("name", "")
    rows = get_db().execute(
        "SELECT id, name FROM users WHERE name = ?", (name,)
    ).fetchall()
    return {"users": rows}


@app.route("/ping")
def ping():
    host = request.args.get("host", "127.0.0.1")
    if not HOST_PATTERN.match(host):
        abort(400)
    output = subprocess.check_output(["ping", "-c", "1", host])
    return output


@app.route("/config", methods=["POST"])
def load_config():
    data = yaml.safe_load(request.data)
    return {"keys": list(data.keys())}


if __name__ == "__main__":
    app.run(host="127.0.0.1", debug=False)
