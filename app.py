# app.py
import streamlit as st
import os
import io
import shutil
import zipfile
from analisis_spi import ejecutar_analisis

st.set_page_config(page_title="Análisis de Autoría SPI", layout="wide")
st.subheader("Análisis de Autoría por N-gramas (SPI no Normalizado) V 1.02")

# ------------------- SIDEBAR -------------------
st.sidebar.header("Parámetros")

n = st.sidebar.selectbox("Tamaño de n-grama (n)", [3, 4, 5, 6], index=1)

s_input = st.sidebar.text_input("Tamaño del perfil (s) — vacío para no truncar", value="1000")
try:
    s = int(s_input.strip()) if s_input.strip() else None
except ValueError:
    st.sidebar.error("El tamaño del perfil debe ser un número o estar vacío.")
    st.stop()

metodo = st.sidebar.selectbox("Métrica de similitud", ["cosine", "euclidean"], index=0)
margen = st.sidebar.slider("Margen de tolerancia (%)", min_value=1, max_value=20, value=5) / 100

# ------------------- CARGA DE ARCHIVOS -------------------
st.sidebar.header("Carga de archivos")
zip_conocidos = st.sidebar.file_uploader("Textos conocidos (.zip)", type="zip")
txt_dudoso = st.sidebar.file_uploader("Texto dudoso (.txt)", type="txt")

ejecutar = st.sidebar.button("Ejecutar análisis", disabled=not (zip_conocidos and txt_dudoso))

if ejecutar:
    # Limpiar directorios de ejecuciones anteriores
    # for folder in [CONOCIDOS_DIR, DUDOSO_DIR, os.path.join(BASE_DIR, "resultados", "tablas")]:
    #     shutil.rmtree(folder, ignore_errors=True)
    #     os.makedirs(folder, exist_ok=True)
    with st.spinner("Procesando análisis..."):

        # Directorio base relativo al archivo actual (más seguro en cloud)
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        DATA_DIR = os.path.join(BASE_DIR, "data")
        CONOCIDOS_DIR = os.path.join(DATA_DIR, "textos_ciertos")
        DUDOSO_DIR = os.path.join(DATA_DIR, "texto_dudoso")

        # Limpiar directorios
        shutil.rmtree(CONOCIDOS_DIR, ignore_errors=True)
        shutil.rmtree(DUDOSO_DIR, ignore_errors=True)
        os.makedirs(CONOCIDOS_DIR, exist_ok=True)
        os.makedirs(DUDOSO_DIR, exist_ok=True)

        # Guardar y descomprimir ZIP
        try:
            zip_path = os.path.join(CONOCIDOS_DIR, "temp.zip")
            with open(zip_path, "wb") as f:
                f.write(zip_conocidos.read())
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(CONOCIDOS_DIR)
            os.remove(zip_path)
        except Exception as e:
            st.error(f"Error al descomprimir el ZIP: {e}")
            st.stop()

        # Guardar el TXT dudoso
        try:
            dudoso_path = os.path.join(DUDOSO_DIR, "dudoso.txt")
            with open(dudoso_path, "wb") as f:
                f.write(txt_dudoso.read())
                f.flush()
                os.fsync(f.fileno())

            # 🔍 DEPURACIÓN: verificar que se ha guardado
            if not os.path.exists(dudoso_path):
                st.error("⚠️ El archivo dudoso no se encuentra después de guardarlo.")
                st.stop()
            
        except Exception as e:
            st.error(f"❌ Error al guardar el archivo dudoso: {e}")
            st.stop()

        # Ejecutar análisis
        try:
            resumen_md, fig_box, fig_bar = ejecutar_analisis(n=n, s=s, metodo=metodo, margen=margen)
        except FileNotFoundError as fnfe:
            st.error(f"Error de archivo: {fnfe}")
            st.stop()
        except Exception as e:
            st.error(f"Error durante el análisis: {e}")
            st.stop()

        # Mostrar resultados
        st.markdown(resumen_md)
        st.subheader("Distribución de similitudes")
        st.pyplot(fig_box)

        st.subheader("Similitud por fragmento")
        st.pyplot(fig_bar)

        st.success("Análisis completado.")

        # Ruta del CSV generado por el análisis
        csv_path = os.path.join(BASE_DIR, "resultados", "tablas", f"resumen_similitudes_{metodo}.csv")

        # Verificar que el archivo existe antes de ofrecer la descarga
        if os.path.exists(csv_path):
            with open(csv_path, "rb") as f:
                st.download_button(
                    label=f"📥 Descargar resumen de similitudes ({metodo})",
                    data=f,
                    file_name=f"resumen_similitudes_{metodo}.csv",
                    mime="text/csv"
                )
        else:
            st.warning("No se encontró el archivo de resumen de similitudes para descargar.")
