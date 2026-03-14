from models import db

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
        return len(self.votos) # type: ignore

class VotoPelicula(db.Model):
    """Un registro por like. Se identifica por IP para evitar doble voto."""
    __tablename__ = 'votos_pelicula'
 
    id          = db.Column(db.Integer, primary_key=True)
    pelicula_id = db.Column(db.Integer, db.ForeignKey('peliculas.id'), nullable=False)
    voter_ip    = db.Column(db.String(45), nullable=False)   # soporta IPv6
 
    __table_args__ = (
        db.UniqueConstraint('pelicula_id', 'voter_ip', name='uq_voto_pelicula_ip'),
    )