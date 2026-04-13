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

# ---------------------------------------------------------------------------
# 🛠️ CONFIGURACIÓN DE DATOS - ¡PEGÁ TU LINK AQUÍ!
# Debe terminar exactamente en /export?format=csv
SHEET_URL = "https://docs.google.com/spreadsheets/d/1MeXs_qGTPT57Gpf5IfFJvsy0CCINXNe9i8JGaH8f-FY/export?format=csv"
# ---------------------------------------------------------------------------

@st.cache_data(ttl=300)
def load_and_clean_data(url):
    try:
        # Intento de lectura robusta para configuración regional Argentina
        df = pd.read_csv(url, decimal=',', sep=',')
        if len(df.columns) <= 1:
            df = pd.read_csv(url, decimal=',', sep=';')
            
        # Detección de error de Link (HTML en lugar de CSV)
        if '<!DOCTYPE html>' in str(df.columns) or 'html' in str(df.columns).lower():
            st.error("🚨 Error de Link: Google mandó una página web en vez de datos.")
            st.info("Asegurate de que el link termine en /export?format=csv y que la Sheet sea pública.")
            st.stop()
            
    except Exception as e:
        st.error(f"Falla crítica al conectar con la base de datos: {e}")
        st.stop()

    # Limpieza profunda de encabezados
    df.columns = [str(c).strip().replace('\ufeff', '') for c in df.columns]
    
    # Conversión forzada a numérico de todas las columnas de interés
    cols_necesarias = ['Peso_Pupi', 'Peso_Sofi', 'Cintura_Pupi', 'Cintura_Sofi']
    for c in cols_necesarias:
        if c in df.columns:
            # Limpiamos posibles strings y forzamos float
            df[c] = pd.to_numeric(df[c].astype(str).str.replace(',', '.'), errors='coerce')
    
    # Parseo de fecha flexible
    df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True, errors='coerce')
    return df.dropna(subset=['Fecha']).sort_values('Fecha')

try:
    df = load_and_clean_data(SHEET_URL)
    
    # SIDEBAR - CONTROL DE PERFIL
    st.sidebar.title("🧬 Perfil de Atleta")
    user = st.sidebar.selectbox("Seleccionar Atleta", ["Pupi", "Sofi"])
    
    # Alturas reales para el cálculo del ICA (Ajustalas aquí)
    altura = 1.75 if user == "Pupi" else 1.62 
    
    peso_col = f'Peso_{user}'
    cint_col = f'Cintura_{user}'
    
    # CÁLCULOS DE BUSINESS INTELLIGENCE
    df['Media_Movil'] = df[peso_col].rolling(window=3, min_periods=1).mean()
    df['ICA'] = (df[cint_col] / (altura * 100)).round(3)
    
    # KPIs de Magnitud
    peso_actual = df[peso_col].iloc[-1]
    peso_anterior = df[peso_col].iloc[-2] if len(df) > 1 else peso_actual
    var_semanal = round(peso_actual - peso_anterior, 2)
    cambio_total = round(peso_actual - df[peso_col].iloc[0], 2)
    
    st.title(f"Elite Performance Dashboard: {user}")
    
    # --- FILA 1: SCORECARD PRINCIPAL ---
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Peso Actual", f"{peso_actual} kg", f"{var_semanal} kg", delta_color="inverse")
    with k2:
        st.metric("Promedio Hist.", f"{round(df[peso_col].mean(), 2)} kg", help="Tu peso real sin picos.")
    with k3:
        st.metric("Cintura Actual", f"{df[cint_col].iloc[-1]} cm", f"{round(df[cint_col].diff().iloc[-1], 2)} cm", delta_color="inverse")
    with k4:
        st.metric("ICA (Salud)", df['ICA'].iloc[-1], help="Meta: < 0.5")

    # ESTADÍSTICAS DE VARIABILIDAD (Expander)
    with st.expander("📊 Ver Análisis de Récords y Variabilidad"):
        e1, e2, e3, e4 = st.columns(4)
        e1.metric("Máximo", f"{df[peso_col].max()} kg")
        e2.metric("Mínimo", f"{df[peso_col].min()} kg")
        rango = round(df[peso_col].max() - df[peso_col].min(), 2)
        e3.metric("Rango Var.", f"{rango} kg")
        e4.metric("Cambio Neto", f"{cambio_total} kg")

    # --- FILA 2: GRÁFICOS APILADOS (BI STYLE) ---
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.1,
                        subplot_titles=("Tendencia de Peso (kg)", "Dinámica de Cintura (cm)"))

    # Gráfico Peso
    fig.add_trace(go.Scatter(x=df['Fecha'], y=df[peso_col], name="Peso Real", mode='markers+lines', 
                             line=dict(color='#58a6ff', width=1), opacity=0.4), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['Fecha'], y=df['Media_Movil'], name="Tendencia (Media Móvil)", 
                             line=dict(color='#3fb950', width=4)), row=1, col=1)
    
    # Gráfico Cintura (Con Zoom)
    fig.add_trace(go.Scatter(x=df['Fecha'], y=df[cint_col], name="Cintura", mode='lines+markers',
                             line=dict(color='#f85149', width=3), marker=dict(size=8, symbol='diamond')), row=2, col=1)
    fig.add_hline(y=df[cint_col].mean(), line_dash="dash", line_color="#ffffff", opacity=0.3, row=2, col=1)

    # Configuración de Ejes
    fig.update_layout(height=800, template="plotly_dark", showlegend=True, margin=dict(l=20, r=20, t=60, b=20))
    fig.update_yaxes(title_text="Peso (kg)", row=1, col=1, range=[df[peso_col].min() - 1, df[peso_col].max() + 1])
    fig.update_yaxes(title_text="Cintura (cm)", row=2, col=1, range=[df[cint_col].min() - 3, df[cint_col].max() + 3])
    
    st.plotly_chart(fig, use_container_width=True)

    # --- FILA 3: INSIGHTS DEL COACH ---
    st.subheader("💡 Análisis del Coach")
    col_a, col_b = st.columns(2)
    with col_a:
        if cambio_total > 0:
            st.info(f"Ganancia de **{cambio_total} kg**. Si la cintura no sube, es músculo puro.")
        else:
            st.success(f"Pérdida de **{abs(cambio_total)} kg**. ¡Vas por el buen camino!")
    with col_b:
        delta_cint = round(df[cint_col].iloc[-1] - df[cint_col].iloc[0], 2)
        if delta_cint <= 0:
            st.success(f"Cintura controlada (**{delta_cint} cm**). Composición corporal mejorando.")
        else:
            st.warning(f"La cintura subió **{delta_cint} cm**. Ajustar la calidad de la comida.")

except Exception as e:
    st.error("Error en la telemetría. Verificá tu Google Sheet y el link.")
    st.exception(e)
