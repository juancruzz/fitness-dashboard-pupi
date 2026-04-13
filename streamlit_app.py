import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# CONFIGURACIÓN
st.set_page_config(page_title="Fitness Analytics | Pupi & Sofi", layout="wide")

# URL de tu Google Sheet (Copiá el link de "Compartir" y cambialo para que termine en /export?format=csv)
# Ejemplo: https://docs.google.com/spreadsheets/d/TU_ID_DE_PLANILLA/export?format=csv
SHEET_URL = "https://docs.google.com/spreadsheets/d/1MeXs_qGTPT57Gpf5IfFJvsy0CCINXNe9i8JGaH8f-FY/export?format=csv"

@st.cache_data(ttl=600) # Se actualiza cada 10 minutos
def load_data(url):
    # 1. Leemos el CSV avisando que la coma es el separador decimal (típico de Arg)
    df = pd.read_csv(url, decimal=',') 
    
    # 2. Limpieza de seguridad: nos aseguramos que las columnas sean números reales
    # A veces Sheets manda datos con espacios o formatos raros que confunden a Python
    cols_numericas = ['Peso_Pupi', 'Peso_Sofi', 'Cintura_Pupi', 'Cintura_Sofi']
    
    for col in cols_numericas:
        if col in df.columns:
            # Pasamos a string, reemplazamos coma por punto por las dudas, y forzamos a número
            # 'coerce' transforma lo que no sea número en vacío (NaN) para que no rompa el código
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')
    
    # 3. Quitamos filas que hayan quedado totalmente vacías
    df = df.dropna(subset=['Fecha'])
    
    return df

try:
    df = load_data(SHEET_URL)
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    
    # --- Mantenemos toda la lógica anterior de cálculos ---
    ALTURA_PUPI = 1.66
    ALTURA_SOFI = 1.56

    st.sidebar.title("Configuración")
    perfil = st.sidebar.radio("Usuario:", ["Pupi", "Sofi"])
    altura = ALTURA_PUPI if perfil == "Pupi" else ALTURA_SOFI
    col_peso = f'Peso_{perfil}'
    col_cintura = f'Cintura_{perfil}'

    # Cálculos automáticos
    df[f'Var_{perfil}'] = df[col_peso].diff()
    df[f'Media_{perfil}'] = df[col_peso].rolling(window=3).mean()
    df[f'ICA_{perfil}'] = (df[col_cintura] / (altura * 100)).round(3)

    # --- DASHBOARD ---
    st.title(f"📊 Dashboard Fitness Pro: {perfil}")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Peso Actual", f"{df[col_peso].iloc[-1]} kg", f"{round(df[f'Var_{perfil}'].iloc[-1], 2)} kg", delta_color="inverse")
    with c2:
        st.metric("Media Móvil", f"{round(df[f'Media_{perfil}'].iloc[-1], 2)} kg")
    with c3:
        st.metric("ICA", df[f'ICA_{perfil}'].iloc[-1])
    with c4:
        cambio = round(df[col_peso].iloc[-1] - df[col_peso].iloc[0], 2)
        st.metric("Cambio Total", f"{cambio} kg")

    # Gráfico
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=df['Fecha'], y=df[col_peso], name="Peso Real", line=dict(color='#58a6ff')), secondary_y=False)
    fig.add_trace(go.Scatter(x=df['Fecha'], y=df[f'Media_{perfil}'], name="Tendencia", line=dict(color='#3fb950', dash='dot')), secondary_y=False)
    fig.add_trace(go.Scatter(x=df['Fecha'], y=df[col_cintura], name="Cintura (cm)", line=dict(color='#f85149')), secondary_y=True)
    
    fig.update_layout(template="plotly_dark", hovermode="x unified", height=600)
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error("Error cargando los datos. Verificá la URL de Google Sheets.")
    st.exception(e) # Esto te va a mostrar el "Traceback" completo en la web
