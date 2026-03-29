

from datetime import datetime



def limpiar_numero(valor):
    
    if valor is None:
        return None
    try:
        return float(valor)
    except (ValueError, TypeError):
       
        limpio = str(valor).replace("$", "").replace("%", "").replace(" ", "")
        
        if "," in limpio and "." in limpio:
            if limpio.index(".") < limpio.index(","):
                
                limpio = limpio.replace(".", "").replace(",", ".")
            else:
                
                limpio = limpio.replace(",", "")
        elif "," in limpio:
            limpio = limpio.replace(",", ".")
        try:
            return float(limpio)
        except ValueError:
            return None


def limpiar_fecha(valor, formatos=None):
    """Intenta parsear una fecha en varios formatos. Retorna string ISO o None."""
    if valor is None:
        return None
    if isinstance(valor, datetime):
        return valor.strftime("%Y-%m-%d")
    formatos = formatos or [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%Y/%m/%d",
        "%d/%m/%y",
    ]
    for fmt in formatos:
        try:
            return datetime.strptime(str(valor).strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None  


def timestamp_ahora():
    """Retorna el timestamp actual en ISO para marcar cuándo se actualizó el dato."""
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")



def limpiar_dolar(datos_crudos: dict) -> list:
  
    if not datos_crudos or "error" in datos_crudos:
        return []

    resultado = []
    fecha_hoy = timestamp_ahora()

    for tipo, valores in datos_crudos.items():
        if not isinstance(valores, dict):
            continue
        doc = {
            "tipo": tipo.lower().strip(),
            "compra": limpiar_numero(valores.get("compra")),
            "venta": limpiar_numero(valores.get("venta")),
            "fecha": fecha_hoy,
            "fuente": "dolarito",
        }
       
        if doc["compra"] and doc["venta"]:
            doc["spread"] = round(doc["venta"] - doc["compra"], 2)
        resultado.append(doc)

    return resultado


def limpiar_inflacion(datos_crudos: list) -> list:
   
    if not datos_crudos or not isinstance(datos_crudos, list):
        return []

    resultado = []
    for item in datos_crudos:
        if not isinstance(item, dict):
            continue

        
        periodo_raw = str(item.get("periodo", "")).strip()
        if len(periodo_raw) == 6 and periodo_raw.isdigit():
           
            periodo = f"{periodo_raw[:4]}-{periodo_raw[4:]}"
        else:
            periodo = periodo_raw

        doc = {
            "periodo": periodo,
            "valor": limpiar_numero(item.get("valor")),
            "fuente": "indec",
            "fecha_actualizacion": timestamp_ahora(),
        }
        if doc["valor"] is not None:
            resultado.append(doc)

    return resultado


def limpiar_tasa_bcra(datos_crudos: list) -> list:
 
    if not datos_crudos or not isinstance(datos_crudos, list):
        return []

    resultado = []
    for item in datos_crudos:
        if not isinstance(item, dict):
            continue
        doc = {
            "fecha": limpiar_fecha(item.get("fecha")),
            "valor": limpiar_numero(item.get("valor")),
            "fuente": "bcra",
            "fecha_actualizacion": timestamp_ahora(),
        }
        if doc["fecha"] and doc["valor"] is not None:
            resultado.append(doc)

    
    resultado.sort(key=lambda x: x["fecha"])
    return resultado


def limpiar_todo(datos: dict) -> dict:
  
    return {
        "dolar": limpiar_dolar(datos.get("dolar", {})),
        "inflacion": limpiar_inflacion(datos.get("inflacion", [])),
        "tasa_bcra": limpiar_tasa_bcra(datos.get("tasa_bcra", [])),
    }



if __name__ == "__main__":
    import json

    try:
        from apis import obtener_todos_los_datos
        print("Obteniendo datos de las APIs...")
        crudos = obtener_todos_los_datos()
        limpios = limpiar_todo(crudos)
        print(json.dumps(limpios, indent=2, ensure_ascii=False))
    except ImportError:
        
        print("apis.py no encontrado. Probando con datos de ejemplo...\n")
        ejemplo = {
            "dolar": {
                "oficial": {"compra": "980,50", "venta": "1.020,00"},
                "blue":    {"compra": "1.250",  "venta": "1.270"},
            },
            "inflacion": [
                {"periodo": "202401", "valor": "20.6"},
                {"periodo": "202402", "valor": "13.2"},
            ],
            "tasa_bcra": [
                {"fecha": "15/01/2024", "valor": "100"},
                {"fecha": "15/02/2024", "valor": "110"},
            ],
        }
        limpios = limpiar_todo(ejemplo)
        print(json.dumps(limpios, indent=2, ensure_ascii=False))