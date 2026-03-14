from flask import Blueprint, render_template, request, jsonify
from services.pelicula_services import agregar_pelicula, votar_pelicula, obtener_peliculas

votar_pelicula_bp = Blueprint('votar_pelicula', __name__, url_prefix='/evento/votar_pelicula')

def get_ip():
    """Obtiene la IP real del visitante, considerando proxies."""
    if request.headers.get('X-Forwarded-For'):
        return request.headers['X-Forwarded-For'].split(',')[0].strip()
    return request.remote_addr


@votar_pelicula_bp.route('/')
def index():
    ip = get_ip()
    peliculas = obtener_peliculas(voter_ip=ip)
    return render_template('votar_pelicula.html', peliculas=peliculas)


@votar_pelicula_bp.route('/agregar', methods=['POST'])
def agregar():
    data = request.get_json(silent=True) or {}

    titulo = (data.get('titulo') or '').strip()
    if not titulo:
        return jsonify({'error': 'El título es obligatorio'}), 400

    descripcion  = (data.get('descripcion') or '').strip() or None
    agregada_por = (data.get('nombre') or '').strip() or None

    try:
        pelicula = agregar_pelicula(titulo, descripcion, agregada_por)
        return jsonify({
            'id':           pelicula.id,
            'titulo':       pelicula.titulo,
            'descripcion':  pelicula.descripcion,
            'agregada_por': pelicula.agregada_por,
            'total_votos':  0
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@votar_pelicula_bp.route('/votar/<int:pelicula_id>', methods=['POST'])
def votar(pelicula_id):
    ip = get_ip()
    try:
        total, ya_vote = votar_pelicula(pelicula_id, ip)
        return jsonify({'total_votos': total, 'ya_vote': ya_vote})
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@votar_pelicula_bp.route('/eliminar/<int:pelicula_id>', methods=['DELETE'])
def eliminar(pelicula_id):

    from services.pelicula_services import eliminar_pelicula

    try:
        eliminado = eliminar_pelicula(pelicula_id)

        if not eliminado:
            return jsonify({'error': 'Película no encontrada'}), 404

        return jsonify({
            'ok': True,
            'pelicula_id': pelicula_id
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500