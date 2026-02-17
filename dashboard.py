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
# LIMPIAR NaN en grupo
# --------------------------
df_use = df_use[df_use[strat].notna()]

# ordenar tiempo
orden_tiempo = ["basal","post","mantenimiento"]
df_use["Tiempo"] = pd.Categorical(df_use["Tiempo"],
                                   categories=orden_tiempo,
                                   ordered=True)

# crear variable combinada Tiempo + Grupo
df_use["Tiempo_Grupo"] = df_use["Tiempo"].astype(str) + "_" + df_use[strat].astype(str)

# orden manual
grupos = sorted(df_use[strat].unique())
orden_combinado = []

for t in orden_tiempo:
    for g in grupos:
        orden_combinado.append(f"{t}_{g}")

df_use["Tiempo_Grupo"] = pd.Categorical(
    df_use["Tiempo_Grupo"],
    categories=orden_combinado,
    ordered=True
)

# --------------------------
# GRAFICO
# --------------------------

if unir_pacientes:

    fig = px.line(
        df_use,
        x="Tiempo_Grupo",
        y=variable,
        color=strat,
        line_group="Paciente",
        markers=True,
        category_orders={"Tiempo_Grupo": orden_combinado}
    )

else:

    fig = px.scatter(
        df_use,
        x="Tiempo_Grupo",
        y=variable,
        color=strat,
        hover_data=["Paciente"],
        category_orders={"Tiempo_Grupo": orden_combinado}
    )

fig.update_layout(
    xaxis_title="Tiempo",
    yaxis_title=variable,
    template="simple_white"
)

st.plotly_chart(fig, use_container_width=True, key="main_plot")
