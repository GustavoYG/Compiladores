from flask import Flask, send_from_directory
import threading
import os

def run_server(html_file="index.html", css_file="style.css", port=5000):
    app = Flask(__name__, static_folder='.')

    @app.route("/")
    def index():
        return send_from_directory('.', html_file)
    @app.route("/style.css")
    def style():
        return send_from_directory('.', css_file)

    print(f"Servidor en http://localhost:{port}")
    app.run(port=port)