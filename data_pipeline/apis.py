import requests
from datetime import datetime

HEADERS = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0"
}

DATOS_GOB_URL = "https://apis.datos.gob.ar/series/api/series/"

# ─────────────────────────────
# INFLACIÓN (CORREGIDA)
# ─────────────────────────────
def obtener_inflacion():
    try:
        url = (
            f"{DATOS_GOB_URL}"
            "?ids=103.1_I2N_2016_M_15"
            "&limit=13&sort=desc&format=json"
        )

        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        data = r.json().get("data", [])

        # 🔥 CORRECCIÓN CLAVE: invertir orden
        data = list(reversed(data))

        resultado = []

        for i in range(1, len(data)):
            actual = data[i][1]
            anterior = data[i - 1][1]

            if actual and anterior:
                variacion = round(((actual - anterior) / anterior) * 100, 2)

                resultado.append({
                    "fecha": data[i][0][:7],
                    "valor": variacion,
                    "tipo": "inflacion"
                })

        return resultado

    except Exception as e:
        print("Error inflación:", e)
        return []

# ─────────────────────────────
# DÓLAR
# ─────────────────────────────
def obtener_dolar():
    try:
        blue = requests.get("https://dolarapi.com/v1/dolares/blue", headers=HEADERS, timeout=10).json()
        ccl = requests.get("https://dolarapi.com/v1/dolares/contadoconliqui", headers=HEADERS, timeout=10).json()
        mep = requests.get("https://dolarapi.com/v1/dolares/bolsa", headers=HEADERS, timeout=10).json()

        return [{
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "blue_compra": blue.get("compra"),
            "blue_venta": blue.get("venta"),
            "ccl_venta": ccl.get("venta"),
            "mep_venta": mep.get("venta"),
            "tipo": "dolar"
        }]

    except Exception as e:
        print("Error dólar:", e)
        return []

# ─────────────────────────────
# EMPLEO (HARDCODED)
# ─────────────────────────────
def obtener_empleo():
    return [
        {"fecha": "2025-07", "valor": 6.6, "tipo": "desempleo"},
        {"fecha": "2025-04", "valor": 7.6, "tipo": "desempleo"},
        {"fecha": "2025-01", "valor": 8.4, "tipo": "desempleo"},
    ]

# ─────────────────────────────
# TODO JUNTO
# ─────────────────────────────
def obtener_todos_los_datos():
    return {
        "inflacion": obtener_inflacion(),
        "dolar": obtener_dolar(),
        "empleo": obtener_empleo()
    }

# ─────────────────────────────
# TEST
# ─────────────────────────────
if __name__ == "__main__":
    datos = obtener_todos_los_datos()
    print("\nRESULTADO:\n")
    print(datos)