"""
Módulo de generación de conceptos de suela.
Genera reportes de diseño inteligentes basados en los datos de temporada.
No depende de APIs externas de IA para mayor confiabilidad.
"""

import os
import requests
from datetime import datetime


# Modelos gratuitos a intentar en orden
HF_MODELOS = [
    "google/flan-t5-large",
    "google/flan-t5-base",
]


def intentar_ia_huggingface(prompt_simple, temporada, contexto):
    """
    Intenta usar HuggingFace como mejora opcional.
    Si falla, retorna None y se usa el generador local.
    """
    hf_token = os.environ.get("HF_TOKEN", "")
    if not hf_token:
        return None

    headers = {"Authorization": f"Bearer {hf_token}"}

    for modelo in HF_MODELOS:
        try:
            url = f"https://api-inference.huggingface.co/models/{modelo}"
            payload = {
                "inputs": prompt_simple,
                "parameters": {"max_new_tokens": 200},
                "options": {"wait_for_model": True}
            }
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and result:
                    texto = result[0].get("generated_text", "").strip()
                    if texto and len(texto) > 20:
                        return texto
        except Exception:
            continue

    return None


def generar_concepto_suela(tendencias, temporada):
    """
    Genera el concepto de suela basado en tendencias y temporada.
    Usa lógica inteligente local sin depender de APIs externas.
    """
    contexto = tendencias.get("contexto_moda", {})

    estilos_dama = contexto.get("estilos_dama", [])
    estilos_nino = contexto.get("estilos_nino", [])
    colores = contexto.get("colores", [])
    materiales = contexto.get("materiales", [])
    novedades = contexto.get("novedades", [])
    tendencias_globales = contexto.get("tendencias_globales", [])
    emergentes = tendencias.get("emergentes", [])

    # Datos del concepto dama (top 1 estilo de temporada)
    estilo_dama = estilos_dama[0] if estilos_dama else "botín clásico"
    estilo_dama_2 = estilos_dama[1] if len(estilos_dama) > 1 else estilo_dama
    color_1 = colores[0] if colores else "negro"
    color_2 = colores[1] if len(colores) > 1 else "marrón"
    material_1 = materiales[0] if materiales else "TR"
    material_2 = materiales[1] if len(materiales) > 1 else "goma"

    # Datos del concepto niño
    estilo_nino = estilos_nino[0] if estilos_nino else "calzado escolar"
    color_nino_1 = colores[2] if len(colores) > 2 else colores[0] if colores else "negro"
    color_nino_2 = colores[3] if len(colores) > 3 else colores[1] if len(colores) > 1 else "blanco"

    # Definir características según temporada
    if temporada in ["verano", "primavera"]:
        tipo_dama = "Plataforma" if "plataforma" in estilo_dama else "Suela plana"
        altura_dama = "5-7 cm" if "plataforma" in estilo_dama else "1-2 cm"
        punta_dama = "Cuadrada" if temporada == "verano" else "Almendrada"
        textura_dama = "Lisa con ranuras laterales decorativas"
        tipo_nino = "Plana flexible antideslizante"
        altura_nino = "1.5 cm"
        punta_nino = "Redonda"
        textura_nino = "Estriada transversal en colores"
    else:
        tipo_dama = "Taco cuadrado bajo" if "botín" in estilo_dama or "bota" in estilo_dama else "Plataforma track"
        altura_dama = "3-4 cm" if "botín" in estilo_dama else "4-5 cm"
        punta_dama = "Cuadrada"
        textura_dama = "Antideslizante con relieve geométrico profundo"
        tipo_nino = "Plana gruesa impermeable"
        altura_nino = "2-3 cm"
        punta_nino = "Redonda"
        textura_nino = "Antideslizante con relieve profundo"

    # Armar concepto dama
    concepto_dama = f"""## CONCEPTO DE SUELA DAMA
**Estilo:** {estilo_dama.capitalize()}
**Tipo de suela:** {tipo_dama}
**Altura:** {altura_dama}
**Forma de punta:** {punta_dama}
**Material sugerido:** {material_1} + {material_2}
**Textura:** {textura_dama}
**Colores tendencia:** {color_1.capitalize()}, {color_2.capitalize()}
**Justificación:** El {estilo_dama} lidera las búsquedas de temporada {temporada} en Argentina, con tendencia hacia {tendencias_globales[0].lower() if tendencias_globales else 'mayor comodidad y estilo'}."""

    # Armar concepto niño
    concepto_nino = f"""## CONCEPTO DE SUELA NIÑO/NIÑA
**Estilo:** {estilo_nino.capitalize()}
**Tipo de suela:** {tipo_nino}
**Altura:** {altura_nino}
**Forma de punta:** {punta_nino}
**Material sugerido:** {material_1}
**Textura:** {textura_nino}
**Colores tendencia:** {color_nino_1.capitalize()}, {color_nino_2.capitalize()}
**Justificación:** Alta demanda de {estilo_nino} para la temporada {temporada}, priorizando durabilidad y seguridad antideslizante."""

    # Alerta emergente
    novedad_1 = novedades[0] if novedades else emergentes[0] if emergentes else "nuevos estilos en desarrollo"
    novedad_2 = novedades[1] if len(novedades) > 1 else ""
    emergente_extra = f" También se observa: {emergentes[0]}." if emergentes and emergentes[0] not in novedad_1 else ""

    alerta = f"""## ALERTA DE TENDENCIA EMERGENTE
Esta semana se detecta crecimiento en: **{novedad_1}**. {f'Además: {novedad_2}.' if novedad_2 else ''}{emergente_extra}

Tendencia global a monitorear: *{tendencias_globales[-1] if tendencias_globales else 'nuevas combinaciones de materiales'}*."""

    return {
        "concepto_dama": concepto_dama,
        "concepto_nino": concepto_nino,
        "alerta_emergente": alerta,
        "texto_completo": f"{concepto_dama}\n\n{concepto_nino}\n\n{alerta}",
    }
