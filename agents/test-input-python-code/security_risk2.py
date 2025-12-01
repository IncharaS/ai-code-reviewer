import os
import sqlite3
import subprocess
import flask
from flask import request

app = flask.Flask(__name__)

# 1. Hard‑coded secret (very insecure)
API_KEY = "12345-SECRET-KEY-DO-NOT-HARDCODE"

# 2. SQL Injection vulnerability
def get_user(username):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Vulnerable query
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)

    return cursor.fetchall()

# 3. Command injection vulnerability
def run_system_command(cmd):
    # Extremely unsafe: executing user input directly
    return subprocess.check_output(cmd, shell=True)

# 4. Path traversal vulnerability
def read_user_file(filename):
    # No validation on filename
    with open("/var/app/userfiles/" + filename, "r") as f:
        return f.read()

# 5. Unsafe Flask endpoint
@app.route("/run")
def run():
    cmd = request.args.get("cmd")
    return run_system_command(cmd)

# 6. XSS vulnerability
@app.route("/hello")
def hello():
    name = request.args.get("name", "world")
    return f"<h1>Hello {name}</h1>"  # unsafe, not escaped

# 7. Using eval on user input (critical)
@app.route("/eval")
def eval_code():
    user_code = request.args.get("code")
    return str(eval(user_code))  # VERY dangerous

if __name__ == "__main__":
    app.run(debug=True)
