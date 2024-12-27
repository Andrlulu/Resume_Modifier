# app/main.py

from flask import Flask
from markupsafe import escape

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the Resume Modifier API!"

@app.route("/<name>")
def hello(name):
    return f"Hello, {escape(name)}!"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
