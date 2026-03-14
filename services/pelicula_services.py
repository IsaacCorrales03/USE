from sqlalchemy.exc import IntegrityError
from flask_sqlalchemy import SQLAlchemy
from models.pelicula import Pelicula, VotoPelicula
from extensions import db
from sqlalchemy import func
# ── PELÍCULAS ─────────────────────────────────────────────────────────────────

def agregar_pelicula(titulo, descripcion=None, agregada_por=None):
    """Crea una nueva película propuesta. Retorna la película creada."""
    pelicula = Pelicula(
        titulo=titulo,
        descripcion=descripcion,
        agregada_por=agregada_por
    )
    db.session.add(pelicula)
    db.session.commit()
    return pelicula


def votar_pelicula(pelicula_id, voter_ip):

    voto = VotoPelicula.query.filter_by(
        pelicula_id=pelicula_id,
        voter_ip=voter_ip
    ).first()

    if voto:
        db.session.delete(voto)
        voted = False
    else:
        db.session.add(
            VotoPelicula(
                pelicula_id=pelicula_id,
                voter_ip=voter_ip
            )
        )
        voted = True

    db.session.commit()

    total = db.session.query(func.count(VotoPelicula.id))\
        .filter_by(pelicula_id=pelicula_id)\
        .scalar()

    return total, voted

def obtener_peliculas(voter_ip=None):

    votos_sub = db.session.query(
        VotoPelicula.pelicula_id,
        func.count(VotoPelicula.id).label("total_votos")
    ).group_by(VotoPelicula.pelicula_id).subquery()

    query = db.session.query(
        Pelicula.id,
        Pelicula.titulo,
        Pelicula.descripcion,
        Pelicula.agregada_por,
        func.coalesce(votos_sub.c.total_votos, 0).label("total_votos")
    ).outerjoin(
        votos_sub,
        Pelicula.id == votos_sub.c.pelicula_id
    )

    peliculas = query.order_by(
        func.coalesce(votos_sub.c.total_votos, 0).desc()
    ).all()

    resultado = []

    for p in peliculas:
        ya_vote = False

        if voter_ip:
            ya_vote = db.session.query(VotoPelicula.id)\
                .filter_by(
                    pelicula_id=p.id,
                    voter_ip=voter_ip
                ).first() is not None

        resultado.append({
            "id": p.id,
            "titulo": p.titulo,
            "descripcion": p.descripcion,
            "agregada_por": p.agregada_por,
            "total_votos": p.total_votos,
            "ya_vote": ya_vote
        })

    return resultado

def eliminar_pelicula(pelicula_id):
    """Elimina una película y sus votos (cascade)."""
    pelicula = Pelicula.query.get(pelicula_id)
    if not pelicula:
        return False
    db.session.delete(pelicula)
    db.session.commit()
    return True