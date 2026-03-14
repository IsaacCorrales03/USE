from flask import Blueprint, request, jsonify, render_template
from services.propuesta_services import (
    agregar_propuesta,
    votar_propuesta,
    obtener_propuestas,
    eliminar_propuesta
)

propuesta_bp = Blueprint(
    "propuestas",
    __name__,
    url_prefix="/propuestas"
)


def get_ip():

    if request.headers.get("X-Forwarded-For"):
        return request.headers["X-Forwarded-For"].split(",")[0].strip()

    return request.remote_addr


@propuesta_bp.route("/")
def index():

    ip = get_ip()

    propuestas = obtener_propuestas(ip)

    return render_template(
        "propuestas.html",
        propuestas=propuestas
    )


@propuesta_bp.route("/agregar", methods=["POST"])
def agregar():

    data = request.get_json(silent=True) or {}

    descripcion = (data.get("descripcion") or "").strip()

    if not descripcion:
        return jsonify({"error": "Descripción requerida"}), 400

    propuesta = agregar_propuesta(descripcion)

    return jsonify({
        "id": propuesta.id,
        "descripcion": propuesta.descripcion,
        "total_votos": 0
    }), 201


@propuesta_bp.route("/votar/<int:propuesta_id>", methods=["POST"])
def votar(propuesta_id):

    ip = get_ip()

    try:

        total, ya_vote = votar_propuesta(propuesta_id, ip)

        return jsonify({
            "total_votos": total,
            "ya_vote": ya_vote
        })

    except Exception as e:

        return jsonify({"error": str(e)}), 500


@propuesta_bp.route("/eliminar/<int:propuesta_id>", methods=["DELETE"])
def eliminar(propuesta_id):

    eliminado = eliminar_propuesta(propuesta_id)

    if not eliminado:
        return jsonify({"error": "Propuesta no encontrada"}), 404

    return jsonify({
        "ok": True,
        "propuesta_id": propuesta_id
    })
