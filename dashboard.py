import streamlit as st
import pandas as pd
import plotly.express as px

st.title("BCG Cytokine Dashboard")

ruta = "CONCATENADO_TOTAL.xlsx"
df = pd.read_excel(ruta)

# --------------------------
# LIMPIEZA
# --------------------------

df["Tiempo"] = df["Tiempo"].astype(str).str.lower().str.strip()

for col in ["score","riesgo","intolerancia","fumador","respuesta1/26"]:
    if col in df.columns:
        df[col] = df[col].astype(str).str.lower().str.strip()

df["resp"] = df["respuesta1/26"]

# --------------------------
# SIDEBAR
# --------------------------

st.sidebar.header("Filtros")

sample = st.sidebar.selectbox("Tipo de muestra", ["PlasmaPaciente","OrinaPaciente"])
strat = st.sidebar.selectbox("Colorear por", ["resp","score","riesgo","intolerancia","fumador"])

unir_pacientes = st.sidebar.checkbox("Unir muestras del mismo paciente")

# --------------------------
# FILTRADO
# --------------------------

df_use = df[df["TipoMuestra"] == sample].copy()

# Orden correcto del tiempo
orden_tiempo = ["basal","post","mantenimiento"]
df_use["Tiempo"] = pd.Categorical(df_use["Tiempo"], categories=orden_tiempo, ordered=True)

# Selección variable
cytokines = [c for c in df.columns if c.endswith("_ESC")]
variable = st.selectbox("Variable", cytokines)

# --------------------------
# GRAFICO
# --------------------------

if unir_pacientes:

    fig = px.line(
        df_use,
        x="Tiempo",
        y=variable,
        color=strat,
        line_group="Paciente",
        markers=True,
        facet_col=strat,
        category_orders={"Tiempo": orden_tiempo}
    )

else:

    fig = px.scatter(
        df_use,
        x="Tiempo",
        y=variable,
        color=strat,
        facet_col=strat,
        hover_data=["Paciente"],
        category_orders={"Tiempo": orden_tiempo}
    )

fig.update_layout(
    xaxis_title="Tiempo",
    yaxis_title=variable,
    template="simple_white"
)

fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

st.plotly_chart(fig, use_container_width=True, key="main_plot")


