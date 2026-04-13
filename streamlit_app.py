import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# CONFIGURACIÓN DE PÁGINA "FACHA"
st.set_page_config(page_title="Pupi & Sofi | Elite Analytics", layout="wide", page_icon="💪")

st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    [data-testid="stMetricValue"] { font-size: 2.2rem; font-weight: 700; color: #58a6ff; }
    .stMetric { background-color: #161b22; padding: 20px; border-radius: 12px; border: 1px solid #30363d; }
    h1, h2, h3 { color: #f0f6fc; font-family: 'Inter', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# CONFIGURACIÓN DE DATOS (URL de tu Google Sheet)
SHEET_URL = "TU_URL_CON_COMILLAS_AQUI"

@st.cache_data(ttl=300)
def load_and_clean_data(url):
    df = pd.read_csv(url, decimal=',')
    df.columns = df.columns.str.strip()
    # Conversión forzada a numérico
    cols = ['Peso_Pupi', 'Peso_Sofi', 'Cintura_Pupi', 'Cintura_Sofi']
    for c in cols:
        df[c] = pd.to_numeric(df[c].astype(str).str.replace(',', '.'), errors='coerce')
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    return df.dropna(subset=['Fecha'])

try:
    df = load_and_clean_data(SHEET_URL)
    
    # SIDEBAR - CONTROL DE PERFIL
    st.sidebar.title("🧬 Perfil de Atleta")
    user = st.sidebar.selectbox("Seleccionar Atleta", ["Pupi", "Sofi"])
    altura = 1.75 if user == "Pupi" else 1.62 # Ajustá según real
    
    # ASIGNACIÓN DE COLUMNAS
    peso_col = f'Peso_{user}'
    cint_col = f'Cintura_{user}'
    
    # CÁLCULOS AVANZADOS (BI LOGIC)
    df['Media_Movil'] = df[peso_col].rolling(window=3, min_periods=1).mean()
    df['ICA'] = (df[cint_col] / (altura * 100)).round(3)
    
    # Lógica de Coach (Insights)
    delta_peso_total = round(df[peso_col].iloc[-1] - df[peso_col].iloc[0], 2)
    delta_cint_total = round(df[cint_col].iloc[-1] - df[cint_col].iloc[0], 2)
    
    # TÍTULO
    st.title(f"Elite Performance Dashboard: {user}")
    
    # FILA 1: KPIs (RESUMEN EJECUTIVO)
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Peso Actual", f"{df[peso_col].iloc[-1]} kg", f"{round(df[peso_col].diff().iloc[-1], 2)} kg", delta_color="inverse")
    with k2:
        st.metric("Cintura Actual", f"{df[cint_col].iloc[-1]} cm", f"{round(df[cint_col].diff().iloc[-1], 2)} cm", delta_color="inverse")
    with k3:
        st.metric("ICA (Salud)", df['ICA'].iloc[-1], help="Índice Cintura/Altura. Meta: < 0.5")
    with k4:
        # Insight Dinámico
        status = "Recomposición" if delta_peso_total > 0 and delta_cint_total <= 0 else "En Proceso"
        st.metric("Status Coach", status)

    # FILA 2: GRÁFICOS APILADOS (VERTICAL STACK)
    # Creamos subplots: 2 filas, 1 columna, comparten eje X
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.1,
                        subplot_titles=(f"Tendencia de Peso (kg)", f"Dinámica de Cintura (cm)"))

    # Gráfico 1: Peso y Media Móvil
    fig.add_trace(go.Scatter(x=df['Fecha'], y=df[peso_col], name="Peso Diario", mode='lines+markers', line=dict(color='#58a6ff', width=1), opacity=0.5), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['Fecha'], y=df['Media_Movil'], name="Media Móvil (Tendencia)", line=dict(color='#3fb950', width=4)), row=1, col=1)

    # Gráfico 2: Cintura
    fig.add_trace(go.Scatter(x=df['Fecha'], y=df[cint_col], name="Cintura", fill='tozeroy', line=dict(color='#f85149', width=3)), row=2, col=1)

    # Estilo del Layout
    fig.update_layout(height=800, template="plotly_dark", showlegend=True,
                      margin=dict(l=20, r=20, t=60, b=20),
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    
    st.plotly_chart(fig, use_container_width=True)

    # FILA 3: INSIGHTS MÉDICOS/COACHING
    st.subheader("💡 Análisis del Coach")
    col_a, col_b = st.columns(2)
    with col_a:
        st.info(f"Desde el inicio, has cambiado **{delta_peso_total} kg** de peso corporal.")
    with col_b:
        if delta_cint_total < 0:
            st.success(f"¡Excelente! Tu cintura bajó **{abs(delta_cint_total)} cm**. Esto indica pérdida de grasa real.")
        else:
            st.warning(f"La cintura varió **{delta_cint_total} cm**. Vigilar calidad de nutrientes.")

except Exception as e:
    st.error("Error en el sistema de telemetría. Revisar conexión con Google Sheets.")
    st.exception(e)
