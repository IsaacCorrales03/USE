from sqlalchemy import func
from extensions import db
from models.propuesta import Propuesta, VotoPropuesta


def agregar_propuesta(descripcion):

    propuesta = Propuesta(descripcion=descripcion)

    db.session.add(propuesta)
    db.session.commit()

    return propuesta


def votar_propuesta(propuesta_id, voter_ip):

    voto = VotoPropuesta.query.filter_by(
        propuesta_id=propuesta_id,
        voter_ip=voter_ip
    ).first()

    if voto:
        db.session.delete(voto)
        voted = False
    else:
        db.session.add(
            VotoPropuesta(
                propuesta_id=propuesta_id,
                voter_ip=voter_ip
            )
        )
        voted = True

    db.session.commit()

    total = db.session.query(func.count(VotoPropuesta.id))\
        .filter_by(propuesta_id=propuesta_id)\
        .scalar()

    return total, voted


def obtener_propuestas(voter_ip=None):

    votos_sub = db.session.query(
        VotoPropuesta.propuesta_id,
        func.count(VotoPropuesta.id).label("total_votos")
    ).group_by(VotoPropuesta.propuesta_id).subquery()

    query = db.session.query(
        Propuesta.id,
        Propuesta.descripcion,
        func.coalesce(votos_sub.c.total_votos, 0).label("total_votos")
    ).outerjoin(
        votos_sub,
        Propuesta.id == votos_sub.c.propuesta_id
    )

    propuestas = query.order_by(
        func.coalesce(votos_sub.c.total_votos, 0).desc()
    ).all()

    resultado = []

    for p in propuestas:

        ya_vote = False

        if voter_ip:
            ya_vote = db.session.query(VotoPropuesta.id)\
                .filter_by(
                    propuesta_id=p.id,
                    voter_ip=voter_ip
                ).first() is not None

        resultado.append({
            "id": p.id,
            "descripcion": p.descripcion,
            "total_votos": p.total_votos,
            "ya_vote": ya_vote
        })

    return resultado


def eliminar_propuesta(propuesta_id):

    propuesta = Propuesta.query.get(propuesta_id)

    if not propuesta:
        return False

    db.session.delete(propuesta)
    db.session.commit()

    return True
