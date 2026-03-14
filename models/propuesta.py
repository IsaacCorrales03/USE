from models import db

class Propuesta(db.Model):
    __table__name = "propuestas"

    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.Text, nullable=False)
    votos = db.Column(db.Integer, nullable=False, default=0)
    