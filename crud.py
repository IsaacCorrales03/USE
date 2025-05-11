from models import db, Grupo, Integrante, Grupo_mk, Integrante_mk


# Crear un nuevo integrante y asignarlo a un grupo
def crear_integrante_mk(nombre, grupo_id):
    nuevo = Integrante_mk(nombre=nombre, grupo_id=grupo_id)
    db.session.add(nuevo)
    db.session.commit()
    return nuevo

# Cambiar de grupo a un integrante existente
def cambiar_integrante_de_grupo_mk(integrante_id, nuevo_grupo_id):
    integrante = Integrante_mk.query.get(integrante_id)
    if not integrante:
        return None
    
    # Validar que el grupo exista
    grupo = Grupo_mk.query.get(nuevo_grupo_id)
    if not grupo:
        raise ValueError(f"El grupo con id {nuevo_grupo_id} no existe")
    
    # Cambiar el grupo
    integrante.grupo_id = nuevo_grupo_id
    db.session.commit()
    
    return integrante

# Crear un grupo para Mortal Kombat
def crear_grupo_mk(nombre):
    nuevo_grupo = Grupo_mk(nombre=nombre)
    db.session.add(nuevo_grupo)
    db.session.commit()
    return nuevo_grupo

# Cambiar el estado "descalificado" de un integrante
def cambiar_estado_integrante_mk(integrante_id, descalificado=True):
    integrante = Integrante_mk.query.get(integrante_id)
    if not integrante:
        return None
    integrante.descalificado = descalificado
    db.session.commit()
    return integrante

# Obtener todos los grupos con sus integrantes
def obtener_grupos_con_integrantes_mk():
    grupos = Grupo_mk.query.all()
    resultado = []
    for grupo in grupos:
        integrantes = [
            {
                "id": i.id,
                "nombre": i.nombre,
                "descalificado": i.descalificado
            }
            for i in grupo.integrantes
        ]
        resultado.append({
            "grupo_id": grupo.id,
            "grupo_nombre": grupo.nombre,
            "integrantes": integrantes
        })
    return resultado

# Crear un nuevo integrante y asignarlo a un grupo
def crear_integrante(nombre, grupo_id):
    nuevo = Integrante(nombre=nombre, grupo_id=grupo_id)
    db.session.add(nuevo)
    db.session.commit()
    return nuevo

# Cambiar de grupo a un integrante existente
def cambiar_integrante_de_grupo(integrante_id, nuevo_grupo_id):
    
    integrante = Integrante.query.get(integrante_id)
    if not integrante:
        return None
        
    # Validar que el grupo exista
    from models import Grupo
    grupo = Grupo.query.get(nuevo_grupo_id)
    if not grupo:
        raise ValueError(f"El grupo con id {nuevo_grupo_id} no existe")
    
    # Cambiar el grupo
    integrante.grupo_id = nuevo_grupo_id
    db.session.commit()
    
    return integrante

def crear_grupo(nombre):
    nuevo_grupo = Grupo(nombre=nombre)
    db.session.add(nuevo_grupo)
    db.session.commit()
    return nuevo_grupo
# Cambiar el estado "descalificado" de un integrante
def cambiar_estado_integrante(integrante_id, descalificado=True):
    integrante = Integrante.query.get(integrante_id)
    if not integrante:
        return None
    integrante.descalificado = descalificado
    db.session.commit()
    return integrante

def obtener_grupos_con_integrantes():
    grupos = Grupo.query.all()
    resultado = []
    for grupo in grupos:
        integrantes = [
            {
                "id": i.id,
                "nombre": i.nombre,
                "descalificado": i.descalificado
            }
            for i in grupo.integrantes
        ]
        resultado.append({
            "grupo_id": grupo.id,
            "grupo_nombre": grupo.nombre,
            "integrantes": integrantes
        })
    return resultado
