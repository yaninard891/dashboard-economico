import streamlit as st
import pandas as pd
from pymongo import MongoClient

# ─────────────────────────────
# CONFIG
# ─────────────────────────────
st.set_page_config(layout="wide")
st.title("📊 Dashboard Económico Argentina")

# ─────────────────────────────
# MONGO
# ─────────────────────────────
client = MongoClient("mongodb://localhost:27017")
db = client["economic_dashboard"]

inflacion = list(db["inflacion"].find())
dolar = list(db["dolar"].find().sort("fecha", -1))
empleo = list(db["empleo"].find())

# ─────────────────────────────
# DATAFRAMES
# ─────────────────────────────
df_inf = pd.DataFrame(inflacion)
df_dolar = pd.DataFrame(dolar)
df_emp = pd.DataFrame(empleo)

# ─────────────────────────────
# LIMPIEZA
# ─────────────────────────────
if not df_inf.empty:
    df_inf["valor"] = pd.to_numeric(df_inf["valor"], errors="coerce")
    df_inf = df_inf.sort_values("fecha")

if not df_emp.empty:
    df_emp["valor"] = pd.to_numeric(df_emp["valor"], errors="coerce")
    df_emp = df_emp.sort_values("fecha")

if not df_dolar.empty:
    df_dolar = df_dolar.sort_values("fecha")

# ─────────────────────────────
# PREDICCIÓN
# ─────────────────────────────
def predecir_inflacion(df):
    if df.empty or len(df) < 3:
        return None
    return df["valor"].tail(3).mean()

# ─────────────────────────────
# ÚLTIMOS DATOS
# ─────────────────────────────
last_inf = df_inf.iloc[-1] if not df_inf.empty else None
prev_inf = df_inf.iloc[-2] if len(df_inf) > 1 else None

last_dolar = df_dolar.iloc[0] if not df_dolar.empty else None

last_emp = df_emp.iloc[-1] if not df_emp.empty else None
prev_emp = df_emp.iloc[-2] if len(df_emp) > 1 else None

# ─────────────────────────────
# KPIs PRINCIPALES
# ─────────────────────────────
st.subheader(" Indicadores Clave")

c1, c2, c3, c4 = st.columns(4)

with c1:
    if last_inf is not None:
        delta = last_inf["valor"] - prev_inf["valor"] if prev_inf is not None else 0
        st.metric("Inflación", f"{last_inf['valor']} %", f"{delta:.2f} %")

with c2:
    if last_dolar is not None:
        st.metric("Dólar Blue", f"${last_dolar['blue_venta']}", last_dolar["fecha"])

with c3:
    if last_dolar is not None:
        st.metric("Dólar Oficial", f"${last_dolar['mep_venta']}", last_dolar["fecha"])

with c4:
    if last_emp is not None:
        delta_emp = last_emp["valor"] - prev_emp["valor"] if prev_emp is not None else 0
        st.metric("Desempleo", f"{last_emp['valor']} %", f"{delta_emp:.2f} %")

# ─────────────────────────────
# 💱 BRECHA CAMBIARIA
# ─────────────────────────────
st.subheader(" Brecha Cambiaria")

if last_dolar is not None:
    blue = last_dolar["blue_venta"]
    oficial = last_dolar["mep_venta"]

    brecha = ((oficial - blue) / blue) * 100

    if brecha > 10:
        st.error(f"Brecha alta: {brecha:.2f}% ")
    else:
        st.success(f"Brecha normal: {brecha:.2f}% ")

# ─────────────────────────────
# 🧠 INSIGHTS + PREDICCIÓN (DESPUÉS DE DATOS + BRECHA)
# ─────────────────────────────
st.subheader(" Análisis y proyecciones")

if last_inf is not None:
    # INSIGHT
    if last_inf["valor"] > 3:
        st.warning(" Inflación elevada (presión inflacionaria)")
    elif last_inf["valor"] > 2:
        st.info(" Inflación moderada")
    else:
        st.success(" Inflación controlada")

    # PREDICCIÓN
    pred = predecir_inflacion(df_inf)

    if pred:
        st.metric(
            "Inflación estimada próximo mes",
            f"{pred:.2f} %",
            f"{pred - last_inf['valor']:.2f} vs actual"
        )

st.divider()

# ─────────────────────────────
#  GRÁFICOS
# ─────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader(" Inflación")
    if not df_inf.empty:
        st.line_chart(df_inf.set_index("fecha")["valor"])

with col2:
    st.subheader(" Dólar (Blue vs Oficial)")
    if not df_dolar.empty:
        st.line_chart(df_dolar.set_index("fecha")[["blue_venta", "mep_venta"]])

# ─────────────────────────────
#  DESEMPLEO
# ─────────────────────────────
st.subheader(" Desempleo")

if not df_emp.empty:
    st.line_chart(df_emp.set_index("fecha")["valor"])