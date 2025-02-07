import pandas as pd
import streamlit as st

# -----------------------------
# CONFIGURACIÓN DE STREAMLIT
# -----------------------------
st.set_page_config(page_title="Análisis de Pipelines - Azure DevOps", layout="wide")

st.title("📊 Dashboard de Análisis de Pipelines en Azure DevOps")

# -----------------------------
# CARGA DEL ARCHIVO EXCEL
# -----------------------------
st.sidebar.title("📂 Cargar Archivo Excel")
archivo = st.sidebar.file_uploader("Sube un archivo Excel", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo, sheet_name=None)  # Cargar todas las hojas
    sheet_name = list(df.keys())[0]  # Tomar la primera hoja
    data = df[sheet_name]

    # Normalizar nombres de columnas (convertir a mayúsculas y eliminar espacios)
    data.columns = data.columns.str.strip().str.upper()

    # -----------------------------
    # VALIDACIÓN DE COLUMNAS
    # -----------------------------
    columnas_requeridas = {"BUILDNUMBER", "STARTTIME", "FINISHTIME", "QUEUETIME", "AGENT", "REQUESTEDFOR", "STATUS"}
    if not columnas_requeridas.issubset(set(data.columns)):
        st.error("⚠️ El archivo no tiene todas las columnas necesarias. Verifica los nombres en el Excel.")
        st.write("📌 Columnas detectadas en el archivo:", list(data.columns))
    else:
        # Convertir a formato de fecha/hora
        data["STARTTIME"] = pd.to_datetime(data["STARTTIME"], errors="coerce")
        data["FINISHTIME"] = pd.to_datetime(data["FINISHTIME"], errors="coerce")
        data["QUEUETIME"] = pd.to_datetime(data["QUEUETIME"], errors="coerce")

        # Calcular duración total de ejecución en segundos y minutos
        data["DURACION_SEGUNDOS"] = (data["FINISHTIME"] - data["STARTTIME"]).dt.total_seconds()
        data["DURACION_MINUTOS"] = data["DURACION_SEGUNDOS"] / 60

        # Calcular tiempo en cola antes de ejecución en segundos y minutos
        data["TIEMPO_ESPERA_SEGUNDOS"] = (data["STARTTIME"] - data["QUEUETIME"]).dt.total_seconds()
        data["TIEMPO_ESPERA_MINUTOS"] = data["TIEMPO_ESPERA_SEGUNDOS"] / 60

        # -----------------------------
        # INCLUSIÓN DE NUEVAS COLUMNAS
        # -----------------------------
        columnas_adicionales = ["SUBAREA", "PROYECTO", "NAME_REPO", "DEFINITION_NAME"]
        columnas_existentes = [col for col in columnas_adicionales if col in data.columns]

        # Definir las columnas a mostrar
        columnas_mostrar = [
            "BUILDNUMBER", "STARTTIME", "FINISHTIME", "QUEUETIME", 
            "TIEMPO_ESPERA_SEGUNDOS", "TIEMPO_ESPERA_MINUTOS", 
            "DURACION_SEGUNDOS", "DURACION_MINUTOS", 
            "AGENT", "REQUESTEDFOR"
        ] + columnas_existentes  # Agregar solo las que existan en el Excel

        # -----------------------------
        # MOSTRAR DATOS RELEVANTES
        # -----------------------------
        st.subheader("📌 Detalles de Ejecuciones de Pipelines")
        st.dataframe(data[columnas_mostrar].sort_values("STARTTIME", ascending=False).head(20))

        # -----------------------------
        # TOP 10 PIPELINES CON MAYOR DURACIÓN
        # -----------------------------
        st.subheader("🏆 Top 10 Pipelines con Mayor Duración")
        top_10_mayor = data.sort_values("DURACION_SEGUNDOS", ascending=False).head(10)
        st.table(top_10_mayor[columnas_mostrar])

        # -----------------------------
        # FRECUENCIA DE ERRORES POR DÍA
        # -----------------------------
        st.subheader("📅 Frecuencia de Errores por Día")
        errores_por_dia = data.groupby(data["STARTTIME"].dt.date)["STATUS"].value_counts().unstack().fillna(0)
        st.table(errores_por_dia)

        # -----------------------------
        # ANÁLISIS DE TIEMPOS DE ESPERA Y EJECUCIÓN
        # -----------------------------
        st.subheader("⏳ Análisis de Tiempos de Espera y Ejecución")
        resumen_tiempos = data[["TIEMPO_ESPERA_SEGUNDOS", "TIEMPO_ESPERA_MINUTOS", "DURACION_SEGUNDOS", "DURACION_MINUTOS"]].describe()
        st.table(resumen_tiempos)
else:
    st.warning("📌 Por favor, sube un archivo Excel para analizar los datos.")