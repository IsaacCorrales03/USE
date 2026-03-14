from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Grupo(db.Model):
    __tablename__ = 'grupos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    integrantes = db.relationship('Integrante', backref='grupo', cascade='all, delete-orphan')

class Integrante(db.Model):
    __tablename__ = 'integrantes'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descalificado = db.Column(db.Boolean, default=False, nullable=False)
    
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupos.id'), nullable=False)

class Grupo_mk(db.Model):
    __tablename__ = 'grupos_mk'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    
    # Relación con la tabla Integrante_mk
    integrantes = db.relationship('Integrante_mk', backref='grupo_mk', cascade='all, delete-orphan')

class Integrante_mk(db.Model):
    __tablename__ = 'integrantes_mk'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descalificado = db.Column(db.Boolean, default=False, nullable=False)
    
    # Corregir la clave foránea para apuntar a 'grupos_mk'
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupos_mk.id'), nullable=False)

