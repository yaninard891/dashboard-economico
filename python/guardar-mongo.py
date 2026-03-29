

from pymongo import MongoClient, UpdateOne
from pymongo.errors import ConnectionFailure, BulkWriteError
from datetime import datetime, timezone

MONGO_URI = "mongodb://localhost:27017"
DB_NAME   = "dashboard_economico"


def conectar():
    try:
        cliente = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
        cliente.admin.command("ping")
        print(f" MongoDB conectado → {MONGO_URI} / {DB_NAME}")
        return cliente[DB_NAME]
    except ConnectionFailure as e:
        raise ConnectionFailure(f"No se pudo conectar a MongoDB: {e}")



def upsert_muchos(coleccion, documentos, clave_filtro):
    if not documentos:
        return 0
    operaciones = [
        UpdateOne(
            {k: doc[k] for k in clave_filtro if k in doc},
            {"$set": doc},
            upsert=True
        )
        for doc in documentos
    ]
    try:
        r = coleccion.bulk_write(operaciones, ordered=False)
        return r.upserted_count + r.modified_count
    except BulkWriteError as e:
        print(f"  Error bulk_write: {e.details}")
        return 0


def timestamp_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")



def guardar_inflacion(db, datos: list):
    n = upsert_muchos(db["inflacion"], datos, ["fecha", "tipo"])
    print(f" Inflación guardada:       {n} docs upserted en 'inflacion'")

def guardar_cambio_oficial(db, datos: list):
    n = upsert_muchos(db["cambio_oficial"], datos, ["fecha", "tipo"])
    print(f" Cambio oficial guardado:  {n} docs upserted en 'cambio_oficial'")

def guardar_cambio_blue(db, datos: dict):
    if not datos:
        print("  Sin datos de cambio blue para guardar")
        return
    snapshot = {**datos, "fecha_registro": timestamp_utc()}
    db["cambio_blue"].insert_one(snapshot)
    print(f" Cambio blue guardado:     blue=${datos.get('blue_venta')} CCL=${datos.get('ccl_venta')}")

def guardar_empleo(db, datos: list):
    n = upsert_muchos(db["empleo"], datos, ["fecha", "tipo"])
    print(f" Empleo guardado:          {n} docs upserted en 'empleo'")



def crear_indices(db):
    db["inflacion"].create_index([("fecha", 1), ("tipo", 1)], unique=True)
    db["cambio_oficial"].create_index([("fecha", 1), ("tipo", 1)], unique=True)
    db["cambio_blue"].create_index([("fecha_registro", -1)])
    db["empleo"].create_index([("fecha", 1), ("tipo", 1)], unique=True)
    print(" Índices creados/verificados")



def guardar_todo(datos_apis: dict):
   
    print("\n Conectando a MongoDB...")
    db = conectar()
    crear_indices(db)

    print("\n Guardando datos...")

    
    guardar_inflacion(db, datos_apis.get("inflacion", []))

   
    guardar_cambio_oficial(db, datos_apis.get("cambio_oficial", []))

   
    guardar_cambio_blue(db, datos_apis.get("cambio_blue", {}))

   
    guardar_empleo(db, datos_apis.get("empleo", []))

    print("\n Todo guardado correctamente.")



if __name__ == "__main__":
    try:
        from apis import obtener_todos_los_datos

        print("1) Obteniendo datos de las APIs...")
        datos = obtener_todos_los_datos()

        print("\n2) Guardando en MongoDB...")
        guardar_todo(datos)

    except ImportError as e:
        print(f"Módulo no encontrado: {e}")
        print("Corré este script desde la carpeta python/")
    except ConnectionFailure as e:
        print(f"\n {e}")
        print("¿Está corriendo MongoDB? Ejecutá: mongod")