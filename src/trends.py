"""
Módulo de tendencias de calzado.
Obtiene datos de Google Trends para Argentina y los procesa.
"""

from pytrends.request import TrendReq
import pandas as pd
from datetime import datetime


# Palabras clave de búsqueda por temporada
KEYWORDS_VERANO = [
    "sandalias mujer 2025",
    "calzado verano mujer",
    "zapatos plataforma mujer",
    "sandalias tiras mujer",
    "zapatos destalonados mujer",
]

KEYWORDS_INVIERNO = [
    "botas mujer 2025",
    "botines mujer invierno",
    "calzado invierno mujer",
    "borcegos mujer",
    "zapatos cerrados mujer",
]

KEYWORDS_NINO = [
    "zapatillas nena 2025",
    "calzado infantil niña",
    "sandalias nena verano",
    "botines nena invierno",
]


def obtener_temporada_actual():
    """Determina la temporada según el mes actual en Argentina (hemisferio sur)."""
    mes = datetime.now().month
    if mes in [12, 1, 2, 3]:
        return "verano"
    elif mes in [6, 7, 8, 9]:
        return "invierno"
    elif mes in [4, 5]:
        return "otoño"
    else:
        return "primavera"


def buscar_tendencias(keywords, geo="AR", periodo="today 3-m"):
    """
    Busca tendencias en Google Trends para Argentina.

    Args:
        keywords: lista de términos a buscar
        geo: código de país (AR = Argentina)
        periodo: rango de tiempo

    Returns:
        dict con datos de tendencias
    """
    pytrends = TrendReq(hl="es-AR", tz=-180)  # UTC-3 Argentina

    resultados = {}

    # Google Trends permite máximo 5 keywords por vez
    for i in range(0, len(keywords), 5):
        grupo = keywords[i:i+5]
        try:
            pytrends.build_payload(grupo, geo=geo, timeframe=periodo)
            data = pytrends.interest_over_time()

            if not data.empty:
                for keyword in grupo:
                    if keyword in data.columns:
                        promedio = data[keyword].mean()
                        ultimo = data[keyword].iloc[-1] if len(data) > 0 else 0
                        tendencia = "subiendo" if ultimo > promedio else "bajando"
                        resultados[keyword] = {
                            "promedio": round(promedio, 1),
                            "ultimo_valor": int(ultimo),
                            "tendencia": tendencia,
                        }
        except Exception as e:
            print(f"Error buscando '{grupo}': {e}")
            continue

    return resultados


def obtener_queries_relacionadas(keyword, geo="AR"):
    """Obtiene búsquedas relacionadas al término dado."""
    pytrends = TrendReq(hl="es-AR", tz=-180)
    try:
        pytrends.build_payload([keyword], geo=geo, timeframe="today 3-m")
        related = pytrends.related_queries()

        if keyword in related and related[keyword]["rising"] is not None:
            top = related[keyword]["rising"].head(5)
            return top["query"].tolist()
    except Exception as e:
        print(f"Error obteniendo queries relacionadas: {e}")

    return []


def obtener_reporte_tendencias():
    """
    Genera el reporte completo de tendencias de calzado.

    Returns:
        dict con tendencias organizadas por categoría
    """
    temporada = obtener_temporada_actual()
    print(f"Temporada actual: {temporada}")
    print("Buscando tendencias en Google Trends Argentina...")

    reporte = {
        "fecha": datetime.now().strftime("%d/%m/%Y"),
        "temporada": temporada,
        "tendencias_dama": {},
        "tendencias_nino": {},
        "emergentes": [],
    }

    # Tendencias según temporada
    if temporada in ["verano", "primavera"]:
        keywords_dama = KEYWORDS_VERANO
    else:
        keywords_dama = KEYWORDS_INVIERNO

    print("Buscando tendencias de dama...")
    reporte["tendencias_dama"] = buscar_tendencias(keywords_dama)

    print("Buscando tendencias de niño...")
    reporte["tendencias_nino"] = buscar_tendencias(KEYWORDS_NINO)

    # Término más buscado para obtener emergentes
    if reporte["tendencias_dama"]:
        top_keyword = max(
            reporte["tendencias_dama"],
            key=lambda k: reporte["tendencias_dama"][k]["ultimo_valor"]
        )
        print(f"Buscando términos emergentes relacionados a: {top_keyword}")
        reporte["emergentes"] = obtener_queries_relacionadas(top_keyword)

    return reporte
