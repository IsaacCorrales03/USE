from flask import (
    Flask,
    jsonify,
    request,
    render_template,
    send_from_directory,
    abort
)

from dotenv import load_dotenv
import os
import threading
import time
import requests

from extensions import db

# blueprints
from routes.pelicula_routes import votar_pelicula_bp
from routes.propuesta_routes import propuesta_bp

# services
from services.pelicula_services import obtener_peliculas


load_dotenv()

EVENTOS = {
    "votar-pelicula": {
        "nombre": "Votación de películas",
        "descripcion": "Votá por la película que querés ver en el próximo evento del colegio.",
        "icono": "fas fa-film",
        "template": "/votar_pelicula.html",
    }
}

app = Flask(__name__)

# ─────────────────────────────────────────
# DATABASE CONFIG
# ─────────────────────────────────────────

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("sql_uri")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "connect_args": {
        "sslmode": "require"
    }
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# ─────────────────────────────────────────
# BLUEPRINTS
# ─────────────────────────────────────────

app.register_blueprint(votar_pelicula_bp)
app.register_blueprint(propuesta_bp)

# ─────────────────────────────────────────
# CREATE TABLES
# ─────────────────────────────────────────

with app.app_context():
    db.create_all()

# ─────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html", EVENTOS=EVENTOS)


@app.route("/evento/<slug>")
def evento_detalle(slug):

    evento = EVENTOS.get(slug)

    if not evento:
        abort(404)

    ip = request.remote_addr

    if slug == "votar-pelicula":

        peliculas = obtener_peliculas(ip)

        return render_template(
            evento["template"],
            evento=evento,
            slug=slug,
            peliculas=peliculas
        )

    return render_template(
        evento["template"],
        evento=evento,
        slug=slug
    )


# ─────────────────────────────────────────
# STATIC DOWNLOAD
# ─────────────────────────────────────────

@app.route("/download_cronograma", methods=["GET"])
def download_cronograma():

    return send_from_directory(
        directory="static/assets",
        path="cronograma.pdf",
        as_attachment=True
    )


# ─────────────────────────────────────────
# KEEP RENDER SERVER AWAKE
# ─────────────────────────────────────────

def ping_periodico():

    while True:
        try:
            print("Haciendo ping a la URL...")
            requests.get(
                "https://union-social-estudiantil.onrender.com/",
                timeout=10
            )
        except Exception as e:
            print(f"Error al hacer ping: {e}")

        time.sleep(30)


# ─────────────────────────────────────────
# RUN APP
# ─────────────────────────────────────────

if __name__ == "__main__":

    threading.Thread(
        target=ping_periodico,
        daemon=True
    ).start()

    app.run(
        host="0.0.0.0",
        port=8080,
        debug=True
    )
