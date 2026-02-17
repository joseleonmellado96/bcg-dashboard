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

import plotly.graph_objects as go
import numpy as np

# Orden correcto de tiempo
orden_tiempo = ["basal","post","mantenimiento"]
df_use = df_use[df_use["Tiempo"].isin(orden_tiempo)]
df_use["Tiempo"] = pd.Categorical(df_use["Tiempo"],
                                  categories=orden_tiempo,
                                  ordered=True)

# eliminar NaN reales
df_use = df_use[df_use[variable].notna()]

tipos = df_use["TipoMuestra"].unique()

# offsets para que no se solapen
offsets = np.linspace(-0.3, 0.3, len(tipos))

fig = go.Figure()

for offset, tipo in zip(offsets, tipos):

    df_tipo = df_use[df_use["TipoMuestra"] == tipo]

    for tiempo in orden_tiempo:

        sub = df_tipo[df_tipo["Tiempo"] == tiempo]
        if len(sub) == 0:
            continue

        # posición x base
        x_base = orden_tiempo.index(tiempo)

        # jitter
        x_vals = np.random.normal(
            x_base + offset,
            0.03,
            len(sub)
        )

        # puntos
        fig.add_trace(go.Scatter(
            x=x_vals,
            y=sub[variable],
            mode="markers",
            name=tipo,
            legendgroup=tipo,
            showlegend=(tiempo == "basal"),
            marker=dict(size=8),
            hovertext=sub["Paciente"]
        ))

        # línea media
        mean_val = sub[variable].mean()

        fig.add_trace(go.Scatter(
            x=[x_base + offset - 0.08, x_base + offset + 0.08],
            y=[mean_val, mean_val],
            mode="lines",
            line=dict(width=4),
            showlegend=False
        ))

fig.update_layout(
    xaxis=dict(
        tickmode="array",
        tickvals=[0,1,2],
        ticktext=["BASAL","POST","MANTENIMIENTO"]
    ),
    yaxis_title=variable,
    xaxis_title="Tiempo",
    template="simple_white",
    height=600
)

st.plotly_chart(fig, use_container_width=True, key="main_plot")
