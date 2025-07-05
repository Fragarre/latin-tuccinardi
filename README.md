
# SPI Author Verification Tool (Streamlit App)

Este proyecto implementa un sistema de verificación de autoría basado en el método SPI (Simplified Profile Intersection) según el enfoque descrito por Potha & Stamatatos (2014), y aplicado por Enrico Tuccinardi en su análisis estilométrico. Está desarrollado en Python y cuenta con una interfaz en Streamlit que permite cargar textos, ajustar parámetros y obtener una conclusión automática sobre la probabilidad de autoría común.

---

## 🧠 Fundamentos Teóricos

### SPI (Simplified Profile Intersection)
SPI es una técnica que compara perfiles estilométricos construidos a partir de n-gramas de caracteres. Cada texto se representa mediante un perfil de frecuencia relativo de sus n-gramas más comunes. La comparación se hace entre:
- Fragmentos del texto de referencia (autor conocido)
- El perfil general del autor conocido
- El perfil del texto de autoría dudosa

Se mide la similitud entre cada fragmento y los perfiles mencionados usando una métrica (coseno o distancia euclídea). La idea es que si el texto dudoso tiene alta similitud con los fragmentos del autor conocido, podría ser del mismo autor.

---

## ⚙️ Estructura del Proyecto

```
stamatatos/
│
├── app.py                    # Interfaz principal de usuario en Streamlit
├── analisis_spi.py          # Lógica central del análisis SPI
├── data/
│   ├── textos_ciertos/      # Textos del autor conocido (cargados desde .zip)
│   └── texto_dudoso/        # Texto de autoría dudosa (un solo archivo .txt)
├── resultados/
│   └── tablas/              # Tabla resumen de similitudes
├── requirements.txt         # Dependencias necesarias
└── README.md                # Este archivo
```

---

## 🖥️ Instrucciones de Uso

### 1. Carga de Archivos

- **Textos conocidos**: Debe cargarse un único archivo `.zip` que contenga **solo** archivos `.txt` del autor conocido.
- **Texto dudoso**: Un único archivo `.txt`. El nombre del archivo no importa.

### 2. Parámetros

- **n-grama (n)**: Longitud del n-grama de caracteres a usar (valores típicos: 3–6).
- **Tamaño del perfil (s)**: Cuántos n-gramas más frecuentes usar. Si se deja vacío, no se trunca.
- **Métrica de similitud**: `'cosine'` o `'euclidean'`.
- **Margen de tolerancia (%)**: Define el rango ±% alrededor de la media de similitudes Fragmento–Known. Se evalúa cuántos valores Fragmento–Unknown caen dentro de ese rango.

### 3. Interpretación de Resultados

La aplicación muestra:

- Distribución de similitudes en boxplot y gráfico de barras.
- Tabla `.csv` con todas las similitudes por fragmento.
- Conclusión automática:
  - **Alta probabilidad**: ≥ 70% de fragmentos están dentro del margen.
  - **Moderada**: entre 40% y 70%
  - **Baja**: < 40%
- Además, se da una **estimación porcentual de probabilidad** basada en los datos.

---

## 🚀 Deployment en Streamlit Cloud

1. Crea un repositorio en GitHub y sube todo el proyecto (`app.py`, `analisis_spi.py`, `README.md`, `requirements.txt`, etc.)
2. Asegúrate de tener este contenido en `requirements.txt`:

```
streamlit
scikit-learn
matplotlib
pandas
numpy
```
3. Ve a [https://streamlit.io/cloud](https://streamlit.io/cloud) e inicia sesión con tu cuenta GitHub.
4. Selecciona tu repositorio y haz click en **Deploy**.
5. La app quedará accesible vía URL.

---

## 🧩 Recomendaciones sobre Parámetros

| Tamaño textos conocidos | Tamaño texto dudoso | Parámetro recomendado |
|-------------------------|---------------------|------------------------|
| Muy largos              | Medio o largo       | `n=4`, `s=1000`, `margen=5%` |
| Cortos o medianos       | Muy corto           | `n=3`, `s=None`, `margen=10–15%` |
| Estilo muy marcado      | Estilo dudoso claro | `n=5`, `s=500`         |

> Si obtienes 0% de coincidencia, prueba aumentar el margen o no truncar el perfil (`s=None`).

---

## 📚 Referencias

- Potha, N., & Stamatatos, E. (2014). A Profile-Based Method for Authorship Verification. *CLEF*.
- Tuccinardi, E. (2017). A Stylometric Approach to the Letter of Pliny on Christians.

---

Desarrollado con ❤️ para proyectos de análisis estilométrico y humanidades digitales.
