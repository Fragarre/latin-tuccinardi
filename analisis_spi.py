# analisis_spi.py
# Análisis de autoría basado en perfiles de n-gramas y medidas de similitud

import os
import glob
import matplotlib.pyplot as plt
import pandas as pd
from collections import Counter, defaultdict
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial.distance import euclidean
import numpy as np

# --------------------------- CONFIGURACIÓN ---------------------------

# Ruta base absoluta al directorio donde está este script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Subcarpetas principales
DATA_DIR = os.path.join(BASE_DIR, "data")
TABLAS_DIR = os.path.join(BASE_DIR, "resultados", "tablas")
FIGURAS_DIR = os.path.join(BASE_DIR, "resultados", "figuras")

# Crear directorios de salida si no existen
os.makedirs(TABLAS_DIR, exist_ok=True)
os.makedirs(FIGURAS_DIR, exist_ok=True)

# Ruta del archivo dudoso
path_unknown = os.path.join(DATA_DIR, "texto_dudoso", "dudoso.txt")
if not os.path.exists(path_unknown):
    raise FileNotFoundError(f"No se encontró el archivo dudoso en '{path_unknown}'. Asegúrate de haber subido un archivo .txt.")


# --------------------------- FUNCIONES BÁSICAS ---------------------------

def leer_texto(path):
    with open(path, encoding="utf-8") as f:
        return f.read()

def obtener_ngramas(texto, n):
    return [texto[i:i+n] for i in range(len(texto) - n + 1)]

def perfil_ngramas(texto, n, s=None):
    ngrams = obtener_ngramas(texto, n)
    contador = Counter(ngrams)
    total = sum(contador.values())
    comunes = dict(contador.most_common(s)) if s else dict(contador)
    relativas = {k: v / total for k, v in comunes.items()}
    return comunes, relativas

def fragmentar_texto(texto, tam_fragmento):
    L = len(texto) // tam_fragmento
    return [texto[i*tam_fragmento:(i+1)*tam_fragmento] for i in range(L)]

def vector_frecuencias(ngr_common, freq_dict):
    return np.array([freq_dict.get(ng, 0) for ng in ngr_common])

def calcular_similitud(vec1, vec2, metodo="cosine"):
    vec1 = vec1.reshape(1, -1)
    vec2 = vec2.reshape(1, -1)
    if metodo == "cosine":
        return cosine_similarity(vec1, vec2)[0][0]
    elif metodo == "euclidean":
        return euclidean(vec1.flatten(), vec2.flatten())
    else:
        raise ValueError("Métrica no soportada")

# --------------------------- FUNCIÓN PRINCIPAL ---------------------------

def ejecutar_analisis(n=4, s=1000, metodo="cosine", margen=0.10):
    os.makedirs(TABLAS_DIR, exist_ok=True)

    path_unknown = os.path.join(DATA_DIR, "texto_dudoso", "dudoso.txt")
    if not os.path.exists(path_unknown):
        raise FileNotFoundError("No se encontró el archivo dudoso en 'data/texto_dudoso/dudoso.txt'. Asegúrate de haber subido un archivo .txt.")

    unknown_text = leer_texto(path_unknown)

    

    unknown_text = leer_texto(path_unknown)
    tam_unknown = len(unknown_text)
    _, freq_unknown_rel = perfil_ngramas(unknown_text, n, s=s)

    known_text = ""
    for file in glob.glob(os.path.join(DATA_DIR, "textos_ciertos", "*.txt")):
        known_text += leer_texto(file)

    _, freq_known_rel = perfil_ngramas(known_text, n, s=s)

    fragmentos = fragmentar_texto(known_text, tam_unknown)

    resumen = []
    for idx, frag in enumerate(fragmentos):
        _, freq_Fi_rel = perfil_ngramas(frag, n, s=s)
        ngramas = list(freq_Fi_rel.keys())

        vec_Fi = vector_frecuencias(ngramas, freq_Fi_rel)
        vec_known = vector_frecuencias(ngramas, freq_known_rel)
        vec_unknown = vector_frecuencias(ngramas, freq_unknown_rel)

        sim_known = calcular_similitud(vec_Fi, vec_known, metodo)
        sim_unknown = calcular_similitud(vec_Fi, vec_unknown, metodo)

        resumen.append({
            "fragmento": idx+1,
            f"{metodo}_Known": sim_known,
            f"{metodo}_Unknown": sim_unknown
        })

    resumen_df = pd.DataFrame(resumen)
    resumen_csv = os.path.join(TABLAS_DIR, f"resumen_similitudes_{metodo}.csv")
    resumen_df.to_csv(resumen_csv, index=False)

    # Evaluación proporcional
    mean_known = resumen_df[f"{metodo}_Known"].mean()
    delta = mean_known * margen
    lim_inf = mean_known - delta
    lim_sup = mean_known + delta

    valores_unknown = resumen_df[f"{metodo}_Unknown"]
    dentro = sum((lim_inf <= val <= lim_sup) for val in valores_unknown)
    porcentaje = dentro / len(valores_unknown) if len(valores_unknown) > 0 else 0

    if porcentaje >= 0.7:
        conclusion = "ALTA probabilidad de misma autoría."
    elif porcentaje >= 0.4:
        conclusion = "PROBABILIDAD MODERADA de misma autoría."
    else:
        conclusion = "BAJA probabilidad de misma autoría."

    # Texto con margen personalizado
    resumen_md = f"""## Conclusión del Análisis

**Métrica:** {metodo}  
**n-gramas:** {n}  
**Perfil truncado:** {s}  
**Fragmentos:** {len(fragmentos)}

---

**Similitudes promedio fragmento vs Known:** {mean_known:.4f}  
**Rango de tolerancia ±{int(margen*100)}%:** {mean_known:.4f} ± {delta:.4f} → [{lim_inf:.4f}, {lim_sup:.4f}]  
**Fragmentos en rango respecto a Unknown:** {dentro} de {len(valores_unknown)} ({porcentaje:.1%})

---

**{conclusion}**  
**PROBABILIDAD ESTIMADA:** {porcentaje*100:.1f}%
"""

    # Boxplot
    fig_box = plt.figure(figsize=(8, 5))
    plt.boxplot([resumen_df[f"{metodo}_Known"], resumen_df[f"{metodo}_Unknown"]],
                labels=["Fragmento vs Known", "Fragmento vs Unknown"],
                patch_artist=True)
    plt.title("Distribución de Similitudes")
    plt.grid(True, axis='y')

    # Barras
    fig_bar = plt.figure(figsize=(10, 5))
    x = resumen_df["fragmento"]
    plt.bar(x - 0.15, resumen_df[f"{metodo}_Known"], width=0.3, label="Known")
    plt.bar(x + 0.15, resumen_df[f"{metodo}_Unknown"], width=0.3, label="Unknown")
    plt.title("Similitud por Fragmento")
    plt.legend()
    plt.grid(True, axis='y')

    return resumen_md, fig_box, fig_bar
