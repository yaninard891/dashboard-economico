from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "economic_dashboard"

def conectar():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    print("✓ Conectado a MongoDB")
    return db


def guardar_datos(db, datos):
    # Inflación
    if datos.get("inflacion"):
        db["inflacion"].insert_many(datos["inflacion"])
        print(f"✓ Inflación guardada: {len(datos['inflacion'])}")

    # Dólar
    if datos.get("dolar"):
        db["dolar"].insert_many(datos["dolar"])
        print(f"✓ Dólar guardado: {len(datos['dolar'])}")

    # Empleo
    if datos.get("empleo"):
        db["empleo"].insert_many(datos["empleo"])
        print(f"✓ Empleo guardado: {len(datos['empleo'])}")