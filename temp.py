from crud import crear_grupo, crear_integrante, obtener_grupos_con_integrantes
from app import app  # Asegúrate de que aquí se importe tu Flask app correctamente
from models import db

# Datos de grupos
nombres_grupos = (
    [f"Grupo #{i}" for i in range(1, 11)] +
    [f"Duelo #{i}" for i in range(1, 5)] +
    [f"Semifinal #{i}" for i in range(1, 3)] +
    ["Final"]
)

# Integrantes por grupo
integrantes_por_grupo = {
    "Grupo #1": ["Kira Molero", "Ayzen Peña", "Isaac Rivera", "Jeremy Mora"],
    "Grupo #2": ["Jeremy Ortez", "Joel Ortez", "Eder Alvarez", "Marcos Alvarado"],
    "Grupo #3": ["Anahi Zamora", "Iliana Rugama", "Hans Chicaza", "Erick Salazar"],
    "Grupo #4": ["Kendall Ramirez", "Kristel Rugama", "Daniel Hamilton", "Valeska Alfaro"],
    "Grupo #5": ["Santiago Otoya", "Brandon Lange", "Emmanuel Obando", "Miguel Rosales"],
    "Grupo #6": ["Bradly Sosa", "Sebastian Romero", "Yair Aguilera", "Beison Toruño"]
}

with app.app_context():
    db.drop_all()
    db.create_all()

    print("🌱 Creando grupos...")
    grupos = {}
    for nombre in nombres_grupos:
        grupo = crear_grupo(nombre)
        grupos[nombre] = grupo.id
        print(f"✅ {nombre} creado con ID {grupo.id}")

    print("\n👥 Añadiendo integrantes...")
    for nombre_grupo, integrantes in integrantes_por_grupo.items():
        grupo_id = grupos[nombre_grupo]
        for nombre in integrantes:
            crear_integrante(nombre, grupo_id)
            print(f"➕ {nombre} añadido a {nombre_grupo}")
    print(obtener_grupos_con_integrantes())
    print("\n✅ Base de datos poblada correctamente.")
