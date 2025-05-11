from flask import Flask, jsonify, request, render_template, send_from_directory
from models import db
from crud import (
    crear_integrante, cambiar_estado_integrante,
    cambiar_integrante_de_grupo, crear_grupo,
    obtener_grupos_con_integrantes,
    crear_integrante_mk, cambiar_estado_integrante_mk,
    cambiar_integrante_de_grupo_mk, crear_grupo_mk,
    obtener_grupos_con_integrantes_mk
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://avnadmin:AVNS_M4d5uHlTqavp-NKx7l4@newrali-zenithai.k.aivencloud.com:24527/defaultdb'
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "connect_args": {
        "ssl": {}
    }
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Endpoint de bienvenida
@app.route("/")
def index():
    return render_template('index.html')

# Ver todos los grupos y sus integrantes (Smash)
@app.route("/torneo_smash", methods=["GET"])
def torneo_smash():
    datos = obtener_grupos_con_integrantes()
    return render_template('torneo_smash.html', grupos=datos)

# Ver todos los grupos y sus integrantes (MK)
@app.route("/torneo_mk", methods=["GET"])
def torneo_mk():
    datos = obtener_grupos_con_integrantes_mk()
    return render_template('torneo_mk.html', grupos=datos)

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

if __name__ == '__main__':
    app.run(port=8080, debug=True)
