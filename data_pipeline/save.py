from data_pipeline.apis import obtener_todos_los_datos
from database.mongo import conectar, guardar_datos

def main():
    print("Obteniendo datos...")
    datos = obtener_todos_los_datos()

    print("Conectando a MongoDB...")
    db = conectar()

    print("Guardando datos...")
    guardar_datos(db, datos)

    print("✓ Todo guardado correctamente")

if __name__ == "__main__":
    main()