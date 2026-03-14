from flask_sqlalchemy import SQLAlchemy
from extensions import db
from sqlalchemy import func

class Pelicula(db.Model):
    __tablename__ = 'peliculas'
 
    id          = db.Column(db.Integer, primary_key=True)
    titulo      = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.String(500), nullable=True)
    agregada_por = db.Column(db.String(100), nullable=True)   # nombre de quien la propuso
 
    # Relación con votos
    votos = db.relationship('VotoPelicula', backref='pelicula', cascade='all, delete-orphan')
 
    @property
    def total_votos(self):
        return db.session.query(func.count(VotoPelicula.id))\
            .filter(VotoPelicula.pelicula_id == self.id)\
            .scalar()

class VotoPelicula(db.Model):

    __tablename__ = 'votos_pelicula'

    id = db.Column(db.Integer, primary_key=True)
    pelicula_id = db.Column(db.Integer, db.ForeignKey('peliculas.id'), nullable=False)
    voter_ip = db.Column(db.String(45), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('pelicula_id', 'voter_ip', name='uq_voto_pelicula_ip'),
        db.Index('idx_votos_pelicula', 'pelicula_id')
    )