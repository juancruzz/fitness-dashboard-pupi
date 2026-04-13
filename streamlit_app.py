import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuración Estética
st.set_page_config(page_title="Fitness Dashboard | Pupi & Sofi", layout="wide")

st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 1.8rem; color: #00d1ff; }
    .main { background-color: #0e1117; }
    </style>
    """, unsafe_allow_html=True)

# 1. DATOS REALES (Los de tu imagen)
data = {
    'Fecha': ['2026-02-17', '2026-02-23', '2026-02-26', '2026-03-04', '2026-03-06', '2026-03-07', '2026-03-16', '2026-03-23', '2026-03-28', '2026-04-02', '2026-04-04', '2026-04-12'],
    'Peso_Sofi': [56.3, 56.2, 55.8, 55.6, 55.1, 55.3, 56.3, 57.3, 55.9, 55.4, 56.6, 56.2],
    'Peso_Pupi': [64.1, 67.2, 66.4, 65.9, 66.3, 65.9, 66.5, 66.3, 65.2, 65.3, 66.9, 65.9],
    'Cintura_Sofi': [70, 70, 69.8, 69.5, 69.2, 69.3, 70, 71, 70, 69.5, 70.2, 70],
    'Cintura_Pupi': [82, 82, 81.5, 81.8, 81, 80.8, 81.5, 82, 81, 80.5, 81.5, 81]
}
df = pd.DataFrame(data)
df['Fecha'] = pd.to_datetime(df['Fecha'])

# Interfaz
st.title("💪 Fitness Tracking Dashboard")
user = st.sidebar.radio("Ver datos de:", ["Pupi", "Sofi"])

col_p = f"Peso_{user}"
col_c = f"Cintura_{user}"

# Métricas Top
m1, m2, m3 = st.columns(3)
with m1:
    st.metric("Peso Actual", f"{df[col_p].iloc[-1]} kg", f"{round(df[col_p].iloc[-1] - df[col_p].iloc[-2], 2)} kg", delta_color="inverse")
with m2:
    st.metric("Cintura Actual", f"{df[col_c].iloc[-1]} cm", f"{round(df[col_c].iloc[-1] - df[col_c].iloc[-2], 2)} cm", delta_color="inverse")
with m3:
    ratio = round(df[col_c].iloc[-1] / df[col_p].iloc[-1], 2)
    st.metric("Ratio Cintura/Peso", ratio)

# Gráfico Pro
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Scatter(x=df['Fecha'], y=df[col_p], name="Peso (kg)", line=dict(color='#00d1ff', width=4)), secondary_y=False)
fig.add_trace(go.Scatter(x=df['Fecha'], y=df[col_c], name="Cintura (cm)", line=dict(color='#ff4b4b', width=4, dash='dot')), secondary_y=True)

fig.update_layout(title=f"Evolución Combinada - {user}", template="plotly_dark", hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

st.write("### Historial de Datos")
st.dataframe(df.sort_values(by='Fecha', ascending=False), use_container_width=True)
