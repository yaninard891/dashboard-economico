
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

DATOS_GOB_URL = "https://apis.datos.gob.ar/series/api/series/"



def obtener_inflacion():
    try:
        url = (
            f"{DATOS_GOB_URL}"
            "?ids=103.1_I2N_2016_M_15"
            "&limit=13&sort=desc&format=json"
        )
        respuesta = requests.get(url, headers=HEADERS, timeout=10)
        respuesta.raise_for_status()
        serie = respuesta.json().get("data", [])

        inflacion = []
        for i in range(len(serie) - 1):
            fecha      = serie[i][0]
            indice_act = serie[i][1]
            indice_ant = serie[i + 1][1]
            if indice_act and indice_ant:
                variacion = round(((indice_act - indice_ant) / indice_ant) * 100, 2)
                inflacion.append({
                    "fecha":  fecha[:7],
                    "valor":  variacion,
                    "indice": round(indice_act, 2),
                    "tipo":   "ipc_mensual"
                })

        print(f" Inflación: {len(inflacion)} registros obtenidos")
        return inflacion

    except requests.exceptions.RequestException as e:
        print(f"✗ Error al obtener inflación: {e}")
        return []



def obtener_tipo_cambio_oficial():
    try:
        from datetime import datetime, timedelta
        fecha_desde = (datetime.today() - timedelta(days=400)).strftime("%Y-%m-%d")

       
        url = (
            f"{DATOS_GOB_URL}"
            "?ids=168.1_T_CAMBIOR_D_0_0_26"
            f"&start_date={fecha_desde}"
            "&limit=500&sort=asc&format=json"
        )
        print(f"URL dólar oficial: {url}")

        respuesta = requests.get(url, headers=HEADERS, timeout=15)
        respuesta.raise_for_status()
        serie = respuesta.json().get("data", [])

        
        por_mes = {}
        for item in serie:
            if item[1] is not None:
                mes = item[0][:7]
                por_mes[mes] = round(item[1], 2)

        meses = sorted(por_mes.keys(), reverse=True)[:12]
        cambio_oficial = [
            {"fecha": mes, "valor": por_mes[mes], "tipo": "oficial"}
            for mes in meses
        ]

        print(f" Tipo de cambio oficial: {len(cambio_oficial)} registros obtenidos")
        return cambio_oficial

    except requests.exceptions.RequestException as e:
        print(f"  Error al obtener tipo de cambio oficial: {e}")
        return []



def obtener_tipo_cambio_blue():
    try:
        resultado = {}

        r = requests.get("https://dolarapi.com/v1/dolares/blue", headers=HEADERS, timeout=10)
        r.raise_for_status()
        blue = r.json()
        resultado["blue_compra"] = blue.get("compra")
        resultado["blue_venta"]  = blue.get("venta")

        r2 = requests.get("https://dolarapi.com/v1/dolares/contadoconliqui", headers=HEADERS, timeout=10)
        r2.raise_for_status()
        resultado["ccl_venta"] = r2.json().get("venta")

        r3 = requests.get("https://dolarapi.com/v1/dolares/bolsa", headers=HEADERS, timeout=10)
        r3.raise_for_status()
        resultado["mep_venta"] = r3.json().get("venta")

        resultado["tipo"] = "blue_ccl"
        print(f" Dólar blue: ${resultado['blue_venta']} | CCL: ${resultado['ccl_venta']}")
        return resultado

    except requests.exceptions.RequestException as e:
        print(f" Error al obtener dólar blue: {e}")
        return {}


def obtener_empleo():
    """
    La EPH no tiene API REST pública activa.
    Datos hardcodeados del INDEC — actualizar manualmente cada trimestre.
    Fuente: https://www.indec.gob.ar (Mercado de trabajo, tasas e indicadores)
    """
    empleo = [
        {"fecha": "2025-07", "desocupacion": 6.6, "empleo": 45.4, "actividad": 48.6, "tipo": "eph"},
        {"fecha": "2025-04", "desocupacion": 7.6, "empleo": 44.5, "actividad": 48.1, "tipo": "eph"},
        {"fecha": "2025-01", "desocupacion": 8.4, "empleo": 44.0, "actividad": 48.0, "tipo": "eph"},
        {"fecha": "2024-10", "desocupacion": 6.4, "empleo": 44.8, "actividad": 47.8, "tipo": "eph"},
        {"fecha": "2024-07", "desocupacion": 6.9, "empleo": 44.5, "actividad": 47.8, "tipo": "eph"},
        {"fecha": "2024-04", "desocupacion": 7.7, "empleo": 44.2, "actividad": 47.8, "tipo": "eph"},
        {"fecha": "2024-01", "desocupacion": 7.7, "empleo": 43.9, "actividad": 47.6, "tipo": "eph"},
        {"fecha": "2023-10", "desocupacion": 5.7, "empleo": 44.8, "actividad": 47.3, "tipo": "eph"},
    ]
    print(f" Empleo/Desempleo: {len(empleo)} trimestres (hardcoded INDEC)")
    return empleo

# ─────────────────────────────────────────────────────────────
# FUNCIÓN PRINCIPAL
# ─────────────────────────────────────────────────────────────
def obtener_todos_los_datos():
    print("\n Iniciando consulta a las APIs...\n")

    datos = {
        "inflacion":      obtener_inflacion(),
        "cambio_oficial": obtener_tipo_cambio_oficial(),
        "cambio_blue":    obtener_tipo_cambio_blue(),
        "empleo":         obtener_empleo(),
    }

    print("\n Consulta finalizada.")
    return datos


if __name__ == "__main__":
    resultado = obtener_todos_los_datos()

    print("\n" + "─" * 40)
    print("RESUMEN:")
    print(f"  Inflación:      {len(resultado['inflacion'])} registros")
    print(f"  Cambio oficial: {len(resultado['cambio_oficial'])} registros")
    print(f"  Cambio blue:    {resultado['cambio_blue']}")
    print(f"  Empleo:         {len(resultado['empleo'])} trimestres")