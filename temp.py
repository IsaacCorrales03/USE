from crud import (
    crear_grupo_mk,
    crear_integrante_mk,
    obtener_grupos_con_integrantes_mk
)
from app import app
from models import db

# Lista de participantes (únicos, sin repetir)
participantes = [
    "Elkin García", "Jakel Brenes", "Luis Alberto", "Gerald", "Ian Chavarría",
    "Rachel Odette", "Juan David Mora", "Mattias Zeledón", "Diego Esquivel",
    "Christopher Mendoza", "Simón Azofifa", "Andrés Fonseca", "Keylor Nuñez",
    "Ibrahim Arguello", "Kevin Nicaragua", "Gabriel Obando", "Sebastián Moreno",
    "Bradley Abarca", "Alexander López", "Nelson Báez", "Brandon Smith",
    "Jeancarlo Hernández", "Elkin Gutiérrez", "Kenyet Arce", "María José Valledares",
    "Tiffany Vargas", "Samuel Pérez", "Wensy Castillo", "Julissa Carrillo",
    "Samuel Calderón", "Randy Cruz", "Cesar Medina", "Gleyner Alemán",
    "Jefferson Naranjo", "Moisés Martinez", "Esteban García", "Rachel Vazquez",
    "Sebastián Aguirres"
]

# Crear nombres de grupos
nombres_grupos_mk = [f"MK Grupo #{i}" for i in range(1, 9)]  # 8 grupos

with app.app_context():
    db.drop_all()
    db.create_all()

    print("🌱 Creando grupos MK...")
    grupos = {}
    for nombre in nombres_grupos_mk:
        grupo = crear_grupo_mk(nombre)
        grupos[nombre] = grupo.id
        print(f"✅ {nombre} creado con ID {grupo.id}")

    print("\n👥 Añadiendo integrantes a grupos MK...")
    grupo_nombres = list(grupos.keys())
    grupo_index = 0

    for i, participante in enumerate(participantes):
        grupo_actual = grupo_nombres[grupo_index]
        crear_integrante_mk(participante, grupos[grupo_actual])
        print(f"➕ {participante} añadido a {grupo_actual}")
        
        # Avanzar grupo (distribución equitativa, cada grupo recibe un integrante en ronda)
        grupo_index = (grupo_index + 1) % len(grupo_nombres)

    print("\n📋 Estructura actual de grupos MK:")
    print(obtener_grupos_con_integrantes_mk())

    print("\n✅ Base de datos MK poblada correctamente.")
