from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Propuesta(db.Model):
    __tablename__ = "propuestas"

    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.Text, nullable=False)
    votos = db.Column(db.Integer, nullable=False, default=0)