# app.py
import streamlit as st
import os
import shutil
import zipfile
from analisis_spi import ejecutar_analisis

st.set_page_config(page_title="Análisis de Autoría SPI", layout="wide")
st.title("Análisis de Autoría por N-gramas (SPI sin normalizar)")

# ------------------- SIDEBAR -------------------
st.sidebar.header("Parámetros")

# Selección de n-grama
n = st.sidebar.selectbox("Tamaño de n-grama (n)", [3, 4, 5, 6], index=1)

# Entrada manual para tamaño del perfil (s)
s_input = st.sidebar.text_input("Tamaño del perfil (s) — vacío para no truncar", value="1000")
try:
    s = int(s_input.strip()) if s_input.strip() else None
except ValueError:
    st.sidebar.error("El tamaño del perfil debe ser un número o estar vacío.")
    st.stop()

metodo = st.sidebar.selectbox("Métrica de similitud", ["cosine", "euclidean"], index=0)
margen = st.sidebar.slider("Margen de tolerancia (%)", min_value=1, max_value=20, value=5) / 100

try:
    s = int(s_input) if s_input.strip() else None
except ValueError:
    st.sidebar.error("El tamaño del perfil debe ser un número o estar vacío.")
    st.stop()

# ------------------- CARGA DE ARCHIVOS -------------------
st.sidebar.header("Carga de archivos")
zip_conocidos = st.sidebar.file_uploader("Textos conocidos (.zip)", type="zip")
txt_dudoso = st.sidebar.file_uploader("Texto dudoso (.txt)", type="txt")

if st.sidebar.button("Ejecutar análisis"):

    with st.spinner("Procesando análisis..."):

        # Preparar directorios
        base_dir = os.getcwd()
        data_dir = os.path.join(base_dir, "data")
        conocidos_dir = os.path.join(data_dir, "textos_ciertos")
        dudoso_dir = os.path.join(data_dir, "texto_dudoso")

        shutil.rmtree(conocidos_dir, ignore_errors=True)
        shutil.rmtree(dudoso_dir, ignore_errors=True)
        os.makedirs(conocidos_dir, exist_ok=True)
        os.makedirs(dudoso_dir, exist_ok=True)

        # Guardar y descomprimir ZIP
        if zip_conocidos:
            zip_path = os.path.join(conocidos_dir, "temp.zip")
            with open(zip_path, "wb") as f:
                f.write(zip_conocidos.read())
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(conocidos_dir)
            os.remove(zip_path)

        # Guardar TXT y renombrar como dudoso.txt
        if txt_dudoso:
            with open(os.path.join(dudoso_dir, "dudoso.txt"), "wb") as f:
                f.write(txt_dudoso.read())

        # Ejecutar análisis
        resumen_md, fig_box, fig_bar = ejecutar_analisis(n=n, s=s, metodo=metodo, margen=margen)

        # Mostrar resultados
        st.markdown(resumen_md)

        st.subheader("Distribución de similitudes")
        st.pyplot(fig_box)

        st.subheader("Similitud por fragmento")
        st.pyplot(fig_bar)

        st.success("Análisis completado.")
