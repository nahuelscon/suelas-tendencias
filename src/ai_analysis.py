"""
Módulo de análisis con IA.
Usa Hugging Face Inference API (gratuita) para generar
recomendaciones de diseño de suelas basadas en tendencias.
"""

import os
import requests
import json


HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"


def llamar_ia(prompt, max_tokens=800):
    """
    Llama a la API gratuita de Hugging Face.

    Args:
        prompt: texto de instrucción para el modelo
        max_tokens: máximo de tokens en la respuesta

    Returns:
        texto generado por la IA
    """
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        raise ValueError("Falta la variable de entorno HF_TOKEN")

    headers = {"Authorization": f"Bearer {hf_token}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_tokens,
            "temperature": 0.7,
            "return_full_text": False,
        },
    }

    response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=60)

    if response.status_code == 503:
        # Modelo cargando, reintentar
        import time
        print("Modelo cargando, esperando 20 segundos...")
        time.sleep(20)
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=60)

    response.raise_for_status()
    result = response.json()

    if isinstance(result, list) and len(result) > 0:
        return result[0].get("generated_text", "").strip()

    return str(result)


def generar_concepto_suela(tendencias, temporada):
    """
    Genera un concepto de diseño de suela basado en las tendencias.

    Args:
        tendencias: dict con datos de tendencias de Google Trends
        temporada: string con la temporada actual

    Returns:
        dict con concepto de suela para dama y niño
    """

    # Extraer los términos más relevantes
    terminos_dama = sorted(
        tendencias.get("tendencias_dama", {}).items(),
        key=lambda x: x[1]["ultimo_valor"],
        reverse=True
    )[:3]

    terminos_nino = sorted(
        tendencias.get("tendencias_nino", {}).items(),
        key=lambda x: x[1]["ultimo_valor"],
        reverse=True
    )[:2]

    emergentes = tendencias.get("emergentes", [])[:3]

    # Formatear términos para el prompt
    top_dama = ", ".join([t[0] for t in terminos_dama]) if terminos_dama else "calzado de moda"
    top_nino = ", ".join([t[0] for t in terminos_nino]) if terminos_nino else "calzado infantil"
    top_emergentes = ", ".join(emergentes) if emergentes else "ninguno destacado"

    prompt = f"""<s>[INST] Eres un experto en diseño de calzado y suelas para una fábrica argentina.
Basándote en las siguientes tendencias actuales de búsqueda en Argentina para la temporada {temporada}:

TENDENCIAS DAMA MÁS BUSCADAS: {top_dama}
TENDENCIAS NIÑO MÁS BUSCADAS: {top_nino}
TÉRMINOS EMERGENTES: {top_emergentes}

Genera en español un reporte de diseño de suelas con este formato exacto:

## CONCEPTO DE SUELA DAMA
**Estilo:** [nombre del estilo]
**Tipo de suela:** [descripción del tipo: plataforma / taco stiletto / cuña / plana / etc.]
**Altura:** [altura aproximada en cm]
**Forma de punta:** [redonda / cuadrada / almendrada / punta fina]
**Material sugerido:** [goma / PVC / cuero / TR / EVA]
**Textura:** [lisa / estriada / antideslizante / diseño geométrico]
**Colores tendencia:** [2 o 3 colores]
**Justificación:** [1 oración explicando por qué este diseño responde a las tendencias]

## CONCEPTO DE SUELA NIÑO
**Estilo:** [nombre del estilo]
**Tipo de suela:** [descripción]
**Altura:** [altura aproximada en cm]
**Forma de punta:** [tipo de punta]
**Material sugerido:** [material]
**Textura:** [descripción de textura]
**Colores tendencia:** [2 o 3 colores]
**Justificación:** [1 oración explicando por qué este diseño responde a las tendencias]

## ALERTA DE TENDENCIA EMERGENTE
[1 párrafo describiendo qué estilo nuevo está apareciendo y qué tipo de suela necesitaría]
[/INST]"""

    try:
        print("Generando concepto de suela con IA...")
        concepto = llamar_ia(prompt)
        return {
            "concepto_dama": extraer_seccion(concepto, "CONCEPTO DE SUELA DAMA", "CONCEPTO DE SUELA NIÑO"),
            "concepto_nino": extraer_seccion(concepto, "CONCEPTO DE SUELA NIÑO", "ALERTA DE TENDENCIA EMERGENTE"),
            "alerta_emergente": extraer_seccion(concepto, "ALERTA DE TENDENCIA EMERGENTE", None),
            "texto_completo": concepto,
        }
    except Exception as e:
        print(f"Error en IA: {e}")
        return generar_concepto_fallback(temporada, top_dama, top_nino)


def extraer_seccion(texto, inicio, fin):
    """Extrae una sección del texto entre dos encabezados."""
    try:
        idx_inicio = texto.find(f"## {inicio}")
        if idx_inicio == -1:
            idx_inicio = texto.find(inicio)
        if idx_inicio == -1:
            return texto

        if fin:
            idx_fin = texto.find(f"## {fin}")
            if idx_fin == -1:
                idx_fin = texto.find(fin)
            if idx_fin != -1:
                return texto[idx_inicio:idx_fin].strip()

        return texto[idx_inicio:].strip()
    except Exception:
        return texto


def generar_concepto_fallback(temporada, top_dama, top_nino):
    """
    Genera un concepto básico sin IA en caso de error.
    Útil como respaldo cuando la API no está disponible.
    """
    if temporada in ["verano", "primavera"]:
        concepto_dama = """## CONCEPTO DE SUELA DAMA
**Estilo:** Sandalia plataforma verano
**Tipo de suela:** Plataforma
**Altura:** 5-7 cm
**Forma de punta:** Abierta / destalonada
**Material sugerido:** EVA / TR
**Textura:** Lisa con diseño geométrico lateral
**Colores tendencia:** Beige, blanco, terracota
**Justificación:** Las búsquedas indican alta demanda de sandalias con altura para la temporada."""

        concepto_nino = """## CONCEPTO DE SUELA NIÑO
**Estilo:** Sandalia infantil sport
**Tipo de suela:** Plana flexible
**Altura:** 1-2 cm
**Forma de punta:** Redonda
**Material sugerido:** TR antideslizante
**Textura:** Estriada con motivos de colores
**Colores tendencia:** Rosa, lila, turquesa
**Justificación:** Alta búsqueda de calzado infantil cómodo y colorido para verano."""
    else:
        concepto_dama = """## CONCEPTO DE SUELA DAMA
**Estilo:** Botín urbano invierno
**Tipo de suela:** Taco cuadrado bajo
**Altura:** 3-4 cm
**Forma de punta:** Cuadrada
**Material sugerido:** TR / goma
**Textura:** Antideslizante estriada
**Colores tendencia:** Negro, marrón, bordeaux
**Justificación:** Las búsquedas de botines y borcegos lideran las tendencias de invierno."""

        concepto_nino = """## CONCEPTO DE SUELA NIÑO
**Estilo:** Bota infantil impermeable
**Tipo de suela:** Plana gruesa
**Altura:** 2-3 cm
**Forma de punta:** Redonda
**Material sugerido:** PVC / EVA
**Textura:** Antideslizante con relieve
**Colores tendencia:** Negro, azul marino, verde militar
**Justificación:** Alta demanda de calzado abrigado y resistente para niños en invierno."""

    return {
        "concepto_dama": concepto_dama,
        "concepto_nino": concepto_nino,
        "alerta_emergente": f"## ALERTA DE TENDENCIA EMERGENTE\nSe detectan búsquedas crecientes relacionadas a: {top_dama}. Monitorear la próxima semana.",
        "texto_completo": f"{concepto_dama}\n\n{concepto_nino}",
    }
