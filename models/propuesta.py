from extensions import db
from sqlalchemy import func

class Propuesta(db.Model):

    __tablename__ = "propuestas"

    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.Text, nullable=False)
    
    votos = db.relationship(
        "VotoPropuesta",
        backref="propuesta",
        cascade="all, delete-orphan"
    )

    @property
    def total_votos(self):
        return db.session.query(func.count(VotoPropuesta.id))\
            .filter(VotoPropuesta.propuesta_id == self.id)\
            .scalar()


class VotoPropuesta(db.Model):

    __tablename__ = "votos_propuesta"

    id = db.Column(db.Integer, primary_key=True)

    propuesta_id = db.Column(
        db.Integer,
        db.ForeignKey("propuestas.id"),
        nullable=False
    )

    voter_ip = db.Column(db.String(45), nullable=False)

    __table_args__ = (
        db.UniqueConstraint(
            "propuesta_id",
            "voter_ip",
            name="uq_voto_propuesta_ip"
        ),
        db.Index("idx_votos_propuesta", "propuesta_id"),
    )
