from flask import (
    Flask,
    jsonify,
    request,
    render_template,
    send_from_directory,
    abort,
    redirect,
    make_response
)
from models.propuesta import Propuesta
from dotenv import load_dotenv
import json, os
from services.pelicula_services import obtener_peliculas
from extensions import db
load_dotenv()
EVENTOS = {
    "votar-pelicula": {
        "nombre": "Votación de películas",
        "descripcion": "Votá por la película que querés ver en el próximo evento del colegio.",
        "icono": "fas fa-film",
        "handler": "eventos.votar_pelicula",
        "template": "/votar_pelicula.html",
    }
}

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("sql_uri", None)
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "connect_args": {
        "sslmode": "require"
    }
}

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
from routes.pelicula_routes import votar_pelicula_bp
app.register_blueprint(votar_pelicula_bp)
db.init_app(app)
with app.app_context():
    db.create_all()
# Fetch the proposals from the DB
@app.route("/propuestas", methods=["GET"])
def propuestas():
    propuestas = Propuesta.query.order_by(Propuesta.votos.desc()).all()
    return render_template("propuestas.html", propuestas=propuestas)

# Let users submit a new idea
@app.route("/propuestas/crear", methods=["POST"])
def crear_propuesta():
    descripcion = request.form.get("descripcion")

    if not descripcion:
        return redirect("/propuestas")
    
    propuesta = Propuesta(descripcion=descripcion)

    db.session.add(propuesta)
    db.session.commit()

    return redirect("/propuestas")

# Vote for proposal
# IP Limitations
vote_timestamps = {}
RATE_LIMIT_SECONDS = 30

def check_ip_rate_limit(ip, propuesta_id):
    key = (ip, propuesta_id)
    last = vote_timestamps.get(key, 0)

    if time.time() - last < RATE_LIMIT_SECONDS:
        return False
    
    vote_timestamps[key] = time.time()
    return True

# Cookie tracking
@app.route("/propuestas/<int:id>/votar", methods=["POST"])
def votar_propuesta(id):
    propuesta = Propuesta.query.get_or_404(id)
    ip = request.remote_addr

    if not check_ip_rate_limit(ip, id):
        return redirect("/propuestas")
    
    raw = request.cookies.get("voted_proposals", "[]")
    voted = json.loads(raw)

    if id in voted:
        return redirect("/propuestas")
    
    propuestas.votos += 1
    db.session.commit()

    voted.append(id)

    response = make_response(redirect("/propuestas"))
    response.set_cookie(
        "voted_proposals",
        json.dump(voted),
        max_age=60*60*24*365
    )

    return response

# Endpoint de bienvenida
@app.route("/")
def index():
    return render_template('index.html', EVENTOS= EVENTOS)


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

    return render_template(evento["template"], evento=evento, slug=slug)
# Ver todos los grupos y sus integrantes (Smash)
@app.route("/torneo_smash", methods=["GET"])
def torneo_smash():
    datos = obtener_grupos_con_integrantes()
    return render_template('torneo_smash.html', grupos=datos)

# Ver todos los grupos y sus integrantes (MK)
@app.route("/torneo_mk", methods=["GET"])
def torneo_mk():
    return render_template('torneo_mk.html')

# Endpoint para descargar el cronograma
@app.route('/download_cronograma', methods=['GET'])
def download_cronograma():
    return send_from_directory(
        directory='static/assets',
        path='cronograma.pdf',
        as_attachment=True
    )

# Página de administración
@app.route("/admin")
def admin():
    datos_smash = obtener_grupos_con_integrantes()
    datos_mk = obtener_grupos_con_integrantes_mk()
    return render_template('admin.html', 
                           grupos_smash=datos_smash, 
                           grupos_mk=datos_mk)

# Ruta para cambiar un integrante de grupo (Smash)
@app.route("/integrante/<int:id>/cambiar_grupo", methods=["PUT"])
def cambiar_grupo(id):
    datos = request.get_json()
    nuevo_grupo_id = datos.get("grupo_id")
    
    if not nuevo_grupo_id:
        return jsonify({"error": "ID de grupo es requerido"}), 400
    
    try:
        integrante = cambiar_integrante_de_grupo(id, nuevo_grupo_id)
        if not integrante:
            return jsonify({"error": "Integrante no encontrado"}), 404
        return jsonify({"mensaje": f"Integrante cambiado al grupo {nuevo_grupo_id}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Descalificar o habilitar a un integrante (Smash)
@app.route("/integrante/<int:id>/estado", methods=["PUT"])
def editar_estado_integrante(id):
    datos = request.get_json()
    nuevo_estado = datos.get("descalificado", True)
    integrante = cambiar_estado_integrante(id, descalificado=nuevo_estado)
    if not integrante:
        return jsonify({"error": "Integrante no encontrado"}), 404
    return jsonify({"mensaje": f"Estado actualizado a descalificado={nuevo_estado}"})

# Añadir integrante a grupo (Smash)
@app.route("/grupo/<int:grupo_id>/integrante", methods=["POST"])
def agregar_integrante_a_grupo(grupo_id):
    datos = request.get_json()
    nombre = datos.get("nombre")
    if not nombre:
        return jsonify({"error": "Nombre es requerido"}), 400
    integrante = crear_integrante(nombre, grupo_id)
    return jsonify({
        "mensaje": f"{nombre} agregado al grupo {grupo_id}",
        "integrante_id": integrante.id
    })

# Ruta para cambiar un integrante de grupo (MK)
@app.route("/integrante_mk/<int:id>/cambiar_grupo", methods=["PUT"])
def cambiar_grupo_mk(id):
    datos = request.get_json()
    nuevo_grupo_id = datos.get("grupo_id")
    
    if not nuevo_grupo_id:
        return jsonify({"error": "ID de grupo es requerido"}), 400
    
    try:
        integrante = cambiar_integrante_de_grupo_mk(id, nuevo_grupo_id)
        if not integrante:
            return jsonify({"error": "Integrante no encontrado"}), 404
        return jsonify({"mensaje": f"Integrante cambiado al grupo {nuevo_grupo_id}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Descalificar o habilitar a un integrante (MK)
@app.route("/integrante_mk/<int:id>/estado", methods=["PUT"])
def editar_estado_integrante_mk(id):
    datos = request.get_json()
    nuevo_estado = datos.get("descalificado", True)
    integrante = cambiar_estado_integrante_mk(id, descalificado=nuevo_estado)
    if not integrante:
        return jsonify({"error": "Integrante no encontrado"}), 404
    return jsonify({"mensaje": f"Estado actualizado a descalificado={nuevo_estado}"})

# Añadir integrante a grupo (MK)
@app.route("/grupo_mk/<int:grupo_id>/integrante", methods=["POST"])
def agregar_integrante_a_grupo_mk(grupo_id):
    datos = request.get_json()
    nombre = datos.get("nombre")
    if not nombre:
        return jsonify({"error": "Nombre es requerido"}), 400
    integrante = crear_integrante_mk(nombre, grupo_id)
    return jsonify({
        "mensaje": f"{nombre} agregado al grupo {grupo_id}",
        "integrante_id": integrante.id
    })

@app.route("/eventos", methods=["GET"])
def eventos():
    return "hello"
import threading
import time
import requests

def ping_periodico():
    while True:
        try:
            print("Haciendo ping a la URL...")
            requests.get("https://union-social-estudiantil.onrender.com/")
        except Exception as e:
            print(f"Error al hacer ping: {e}")
        time.sleep(30)

if __name__ == '__main__':
    threading.Thread(target=ping_periodico, daemon=True).start()
    app.run(host='0.0.0.0', port=8080, debug=True)

# Let's begin