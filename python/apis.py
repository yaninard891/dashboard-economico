
import requests
import urllib3
 
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
 
HEADERS = {"Accept": "application/json"}
 
 
def obtener_inflacion():

    try:
        url = (
            "https://apis.datos.gob.ar/series/api/series/"
            "?ids=103.1_I2N_2016_M_15"
            "&limit=13"
            "&sort=desc"
            "&format=json"
        )
        respuesta = requests.get(url, headers=HEADERS, timeout=10)
        respuesta.raise_for_status()
        datos = respuesta.json()
 
        serie = datos.get("data", [])
 
        inflacion = []
        for i in range(len(serie) - 1):
            fecha       = serie[i][0]
            indice_act  = serie[i][1]
            indice_ant  = serie[i + 1][1]
 
            if indice_act and indice_ant:
                variacion = round(((indice_act - indice_ant) / indice_ant) * 100, 2)
                inflacion.append({
                    "fecha": fecha[:7],
                    "valor": variacion,
                    "indice": round(indice_act, 2),
                    "tipo": "ipc_mensual"
                })
 
        print(f" Inflación: {len(inflacion)} registros obtenidos")
        return inflacion
 
    except requests.exceptions.RequestException as e:
        print(f"✗ Error al obtener inflación: {e}")
        return []
 
 



def obtener_tipo_cambio_oficial():
    try:
        from datetime import datetime, timedelta
        fecha_hasta = datetime.today()
        fecha_desde = fecha_hasta - timedelta(days=24*30)

        url = (
            f"https://api.bcra.gob.ar/estadisticas/v2.0/datosvariable/4/"
            f"{fecha_desde.strftime('%Y-%m-%d')}/{fecha_hasta.strftime('%Y-%m-%d')}"
        )
        print("URL BCRA:", url)

        respuesta = requests.get(url, headers=HEADERS, timeout=10, verify=False)
        respuesta.raise_for_status()
        datos = respuesta.json()
        resultados = datos.get("results", [])

        if not resultados:
            print("  No hay datos disponibles para tipo de cambio oficial")
            return []

        
        por_mes = {}
        for item in resultados:
            mes = item.get("fecha", "")[:7]
            por_mes[mes] = round(item.get("valor", 0), 2)

       
        meses_disponibles = sorted(por_mes.keys(), reverse=True)[:12]
        cambio_oficial = [{"fecha": mes, "valor": por_mes[mes], "tipo": "oficial"} for mes in meses_disponibles]

        print(f" Tipo de cambio oficial: {len(cambio_oficial)} registros obtenidos")
        return cambio_oficial

    except requests.exceptions.RequestException as e:
        print(f"  Error al obtener tipo de cambio oficial: {e}")
        return []
def obtener_tipo_cambio_blue():

    try:
        resultado = {}
 
        url_blue = "https://dolarapi.com/v1/dolares/blue"
        r = requests.get(url_blue, headers=HEADERS, timeout=10)
        r.raise_for_status()
        blue = r.json()
        resultado["blue_compra"] = blue.get("compra")
        resultado["blue_venta"]  = blue.get("venta")
 
        
        url_ccl = "https://dolarapi.com/v1/dolares/contadoconliqui"
        r2 = requests.get(url_ccl, headers=HEADERS, timeout=10)
        r2.raise_for_status()
        ccl = r2.json()
        resultado["ccl_venta"] = ccl.get("venta")
 
        url_mep = "https://dolarapi.com/v1/dolares/bolsa"
        r3 = requests.get(url_mep, headers=HEADERS, timeout=10)
        r3.raise_for_status()
        mep = r3.json()
        resultado["mep_venta"] = mep.get("venta")
 
        resultado["tipo"] = "blue_ccl"
 
        print(f" Dólar blue: ${resultado['blue_venta']} | CCL: ${resultado['ccl_venta']}")
        return resultado
 
    except requests.exceptions.RequestException as e:
        print(f" Error al obtener dólar blue: {e}")
        return {}
 
 
def obtener_empleo():
    try:
        params = {
            "ids": "41.1_TDESOCUPADOS_D_T_26,41.1_TASA_EMPLEO_D_T_39,41.1_TACTIVIDAD_D_T_36",
            "limit": 8,
            "sort": "desc",
            "format": "json"
        }
        url = "https://apis.datos.gob.ar/series/api/series/"
        respuesta = requests.get(url, params=params, headers=HEADERS, timeout=10)
        respuesta.raise_for_status()
        datos = respuesta.json()

        serie = datos.get("data", [])
 
        empleo = []
        for item in serie:
            fecha        = item[0]
            desocupacion = item[1]
            tasa_empleo  = item[2]
            actividad    = item[3]
 
            empleo.append({
                "fecha":        fecha[:7],
                "desocupacion": round(desocupacion, 1) if desocupacion else None,
                "empleo":       round(tasa_empleo,  1) if tasa_empleo  else None,
                "actividad":    round(actividad,    1) if actividad    else None,
                "tipo": "eph"
            })
 
        print(f" Empleo/Desempleo: {len(empleo)} trimestres obtenidos")
        return empleo
 
    except requests.exceptions.RequestException as e:
        print(f" Error al obtener datos de empleo: {e}")
        return []
 
 
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