import streamlit as st
import pandas as pd
import plotly.express as px

ruta = "CONCATENADO_TOTAL.xlsx"


df = pd.read_excel(ruta)

df["Tiempo"] = df["Tiempo"].astype(str).str.lower()
df["resp"] = df["respuesta1/26"].astype(str).str.lower()

cytokines = [c for c in df.columns if c.endswith("_ESC")]

hemograma = [
    "GB-B","GB-R","HEMOGL","HEMATOCR","EOSIN","LINF","MONOC",
    "NEUTROFILOS","LINFOCITOS","SII INDEX","NLR"
]

hemograma = [h for h in hemograma if h in df.columns]

st.title("BCG – Dashboard exploratorio")

sample = st.selectbox("Muestra", ["OrinaPaciente","PlasmaPaciente"])
strat = st.selectbox("Color por", ["resp","score","riesgo","intolerancia","fumador"])
feature = st.selectbox("Variable", cytokines + hemograma)

df_use = df[df["TipoMuestra"] == sample]

fig = px.strip(
    df_use,
    x="Tiempo",
    y=feature,
    color=strat,
    hover_data=["Paciente"],
    stripmode="overlay"
)

st.plotly_chart(fig, use_container_width=True)

