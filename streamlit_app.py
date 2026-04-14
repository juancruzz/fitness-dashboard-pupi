import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA ELITE
st.set_page_config(
    page_title="PUPI & SOFI | Performance Lab",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. INYECCIÓN DE CSS PROFESIONAL (UI/UX Premium)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
        background-color: #050505;
    }
    
    /* Tarjetas estilo Glassmorphism */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 25px 20px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: transform 0.3s ease;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        border-color: #58a6ff;
    }

    /* Personalización de Títulos */
    h1 { font-weight: 800; letter-spacing: -1px; color: #ffffff; margin-bottom: 0px; }
    h3 { color: #8b949e; font-weight: 400; font-size: 1.1rem; }

    /* Estilo de los Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 0px 20px;
        color: white;
        border: none;
    }
    
    .stTabs [data-baseweb="tab"]:hover { background-color: rgba(255, 255, 255, 0.1); }
    .stTabs [aria-selected="true"] { background-color: #58a6ff !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 3. MOTOR DE DATOS (Backend)
# 🛠️ PEGA TU LINK ACÁ
SHEET_URL = "https://docs.google.com/spreadsheets/d/1MeXs_qGTPT57Gpf5IfFJvsy0CCINXNe9i8JGaH8f-FY/export?format=csv"

@st.cache_data(ttl=60)
def get_performance_data(url):
    try:
        df = pd.read_csv(url, decimal=',', sep=',')
        if len(df.columns) <= 1: df = pd.read_csv(url, decimal=',', sep=';')
        df.columns = [str(c).strip().replace('\ufeff', '') for c in df.columns]
        num_cols = ['Peso_Pupi', 'Peso_Sofi', 'Cintura_Pupi', 'Cintura_Sofi']
        for c in num_cols:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c].astype(str).str.replace(',', '.'), errors='coerce')
        df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True, errors='coerce')
        return df.dropna(subset=['Fecha']).sort_values('Fecha')
    except:
        return pd.DataFrame()

# 4. DASHBOARD LOGIC
df = get_performance_data(SHEET_URL)

if not df.empty:
    # --- HEADER PROFESIONAL ---
    st.markdown(f"<h3>{datetime.now().strftime('%A, %d de %B')}</h3>", unsafe_allow_html=True)
    st.title("Performance Lab: Composición Corporal")
    
    # --- SIDEBAR ELITE ---
    with st.sidebar:
        st.markdown("## ⚡ Menú de Atleta")
        user = st.radio("Atleta en foco:", ["Pupi", "Sofi"], label_visibility="collapsed")
        st.divider()
        st.info("💡 Este dashboard utiliza telemetría en tiempo real desde Google Sheets.")
        altura = 1.75 if user == "Pupi" else 1.62
    
    peso_col, cint_col = f'Peso_{user}', f'Cintura_{user}'
    
    # Procesamiento de Métricas
    actual_p, actual_c = df[peso_col].iloc[-1], df[cint_col].iloc[-1]
    prev_p, prev_c = df[peso_col].iloc[-2], df[cint_col].iloc[-2]
    media_m = df[peso_col].rolling(window=3).mean().iloc[-1]
    ica = round(actual_c / (altura * 100), 3)
    
    # --- INTERFAZ DE TABS (Navegación Pro) ---
    tab_resumen, tab_detalles, tab_metas = st.tabs(["🚀 Resumen Ejecutivo", "📈 Análisis Profundo", "🎯 Metas y Control"])
    
    with tab_resumen:
        # Fila de KPIs con diseño superior
        st.markdown("<br>", unsafe_allow_html=True)
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("PESO ACTUAL", f"{actual_p} kg", f"{round(actual_p - prev_p, 2)} kg", delta_color="inverse")
        k2.metric("PROMEDIO MÓVIL", f"{round(media_m, 2)} kg", "Tendencia real")
        k3.metric("CINTURA", f"{actual_c} cm", f"{round(actual_c - prev_c, 2)} cm", delta_color="inverse")
        k4.metric("ÍNDICE ICA", ica, help="ICA ideal < 0.5")
        
        # Gráfico de Tendencia Unificado (Compacto)
        st.markdown("### Tendencia de Performance")
        fig_main = go.Figure()
        fig_main.add_trace(go.Scatter(x=df['Fecha'], y=df[peso_col].rolling(window=3).mean(), 
                                    name="Peso (Media)", line=dict(color='#58a6ff', width=4), fill='tozeroy'))
        fig_main.update_layout(
            height=400, template="plotly_dark", 
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=20, b=0)
        )
        st.plotly_chart(fig_main, use_container_width=True)

    with tab_detalles:
        st.markdown("### Correlación Peso vs Cintura")
        fig_deep = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05)
        
        # Peso
        fig_deep.add_trace(go.Scatter(x=df['Fecha'], y=df[peso_col], name="Peso", line=dict(color='#58a6ff')), row=1, col=1)
        fig_deep.add_trace(go.Scatter(x=df['Fecha'], y=df[peso_col].rolling(window=3).mean(), name="Tendencia", line=dict(color='#3fb950', dash='dot')), row=1, col=1)
        
        # Cintura
        fig_deep.add_trace(go.Scatter(x=df['Fecha'], y=df[cint_col], name="Cintura", line=dict(color='#f85149')), row=2, col=1)
        
        fig_deep.update_layout(height=600, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        fig_deep.update_yaxes(range=[df[peso_col].min()-1, df[peso_col].max()+1], row=1, col=1)
        fig_deep.update_yaxes(range=[df[cint_col].min()-2, df[cint_col].max()+2], row=2, col=1)
        
        st.plotly_chart(fig_deep, use_container_width=True)

    with tab_metas:
        c_a, c_b = st.columns(2)
        with c_a:
            st.markdown("### 🏆 Récords del Periodo")
            st.write(f"**Máximo Histórico:** {df[peso_col].max()} kg")
            st.write(f"**Mínimo Histórico:** {df[peso_col].min()} kg")
            st.write(f"**Variación Neta:** {round(actual_p - df[peso_col].iloc[0], 2)} kg")
        
        with c_b:
            st.markdown("### 🧬 Insights del Coach")
            if ica < 0.5:
                st.success(f"ICA de {ica}: Estás en rango de salud metabólica óptima.")
            else:
                st.warning(f"ICA de {ica}: Objetivo primordial bajar cintura.")
            
            delta_p = actual_p - df[peso_col].iloc[0]
            delta_c = actual_c - df[cint_col].iloc[0]
            
            if delta_p > 0 and delta_c <= 0:
                st.info("ESTADO: RECOMPOSICIÓN ELITE. Ganando masa sin grasa.")
            elif delta_p < 0 and delta_c < 0:
                st.success("ESTADO: DÉFICIT EFICIENTE. Perdiendo grasa corporal.")
            else:
                st.info("ESTADO: MANTENIMIENTO / AJUSTE.")

else:
    st.error("⚠️ No se pudo conectar con la base de datos. Verificá la URL de Google Sheets.")
