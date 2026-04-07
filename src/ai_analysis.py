"""
Módulo de análisis con IA.
Usa Hugging Face Inference API (gratuita) para generar
recomendaciones de diseño de suelas basadas en tendencias.
"""

import os
import requests


# Modelos gratuitos disponibles en HuggingFace Inference API
HF_API_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"


def llamar_ia(prompt, max_tokens=600):
    """
    Llama a la API gratuita de Hugging Face.
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
            "do_sample": True,
        },
        "options": {
            "wait_for_model": True,
        }
    }

    response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=90)
    response.raise_for_status()
    result = response.json()

    if isinstance(result, list) and len(result) > 0:
        return result[0].get("generated_text", "").strip()

    return str(result)


def generar_concepto_suela(tendencias, temporada):
    """
    Genera un concepto de diseño de suela basado en las tendencias.
    """
    contexto = tendencias.get("contexto_moda", {})
    estilos_dama = ", ".join(contexto.get("estilos_dama", [])[:3])
    estilos_nino = ", ".join(contexto.get("estilos_nino", [])[:2])
    colores = ", ".join(contexto.get("colores", [])[:3])
    materiales = ", ".join(contexto.get("materiales", [])[:2])
    tendencias_globales = " | ".join(contexto.get("tendencias_globales", [])[:3])
    emergentes = ", ".join(tendencias.get("emergentes", [])[:3])

    prompt = f"""<|system|>
Eres un experto en diseño de calzado y suelas para una fábrica argentina. Respondés siempre en español, de forma técnica y concisa.</s>
<|user|>
Temporada actual en Argentina: {temporada}
Estilos dama en tendencia: {estilos_dama}
Estilos niño en tendencia: {estilos_nino}
Colores de temporada: {colores}
Materiales sugeridos: {materiales}
Tendencias globales: {tendencias_globales}
Búsquedas emergentes: {emergentes}

Generá un reporte de diseño de suelas con este formato:

## CONCEPTO DE SUELA DAMA
**Estilo:** [nombre]
**Tipo:** [plataforma / taco cuadrado / cuña / plana / etc]
**Altura:** [cm]
**Punta:** [redonda / cuadrada / almendrada]
**Material:** [tipo]
**Textura:** [descripción]
**Colores:** [2 colores]
**Por qué:** [1 oración]

## CONCEPTO DE SUELA NIÑO
**Estilo:** [nombre]
**Tipo:** [descripción]
**Altura:** [cm]
**Punta:** [tipo]
**Material:** [tipo]
**Textura:** [descripción]
**Colores:** [2 colores]
**Por qué:** [1 oración]

## ALERTA EMERGENTE
[1 párrafo breve sobre qué estilo nuevo está apareciendo]</s>
<|assistant|>"""

    try:
        print("Generando concepto de suela con IA...")
        concepto = llamar_ia(prompt)
        return {
            "concepto_dama": extraer_seccion(concepto, "CONCEPTO DE SUELA DAMA", "CONCEPTO DE SUELA NIÑO"),
            "concepto_nino": extraer_seccion(concepto, "CONCEPTO DE SUELA NIÑO", "ALERTA EMERGENTE"),
            "alerta_emergente": extraer_seccion(concepto, "ALERTA EMERGENTE", None),
            "texto_completo": concepto,
        }
    except Exception as e:
        print(f"Error en IA: {e}")
        return generar_concepto_fallback(temporada, estilos_dama, estilos_nino)


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


def generar_concepto_fallback(temporada, estilos_dama="", estilos_nino=""):
    """Genera un concepto de respaldo sin IA."""
    if temporada in ["verano", "primavera"]:
        concepto_dama = """## CONCEPTO DE SUELA DAMA
**Estilo:** Sandalia plataforma verano
**Tipo:** Plataforma
**Altura:** 5-7 cm
**Punta:** Abierta / destalonada
**Material:** EVA / TR
**Textura:** Lisa con diseño geométrico lateral
**Colores:** Beige, terracota
**Por qué:** Las búsquedas de sandalias con altura dominan la temporada en Argentina."""

        concepto_nino = """## CONCEPTO DE SUELA NIÑO
**Estilo:** Sandalia infantil sport
**Tipo:** Plana flexible
**Altura:** 1-2 cm
**Punta:** Redonda
**Material:** TR antideslizante
**Textura:** Estriada multicolor
**Colores:** Rosa, turquesa
**Por qué:** Alta búsqueda de calzado infantil cómodo y colorido para verano."""

        alerta = """## ALERTA EMERGENTE
Las ojotas y sandalias de tiras minimalistas están ganando terreno rápidamente esta temporada, con suelas ultrafinas de EVA de 1-2cm en colores neutros y traslúcidos."""

    else:
        concepto_dama = """## CONCEPTO DE SUELA DAMA
**Estilo:** Botín urbano invierno
**Tipo:** Taco cuadrado bajo
**Altura:** 3-4 cm
**Punta:** Cuadrada
**Material:** TR / goma
**Textura:** Antideslizante estriada
**Colores:** Negro, bordeaux
**Por qué:** Los botines y borcegos lideran las búsquedas de calzado de invierno."""

        concepto_nino = """## CONCEPTO DE SUELA NIÑO
**Estilo:** Bota infantil impermeable
**Tipo:** Plana gruesa
**Altura:** 2-3 cm
**Punta:** Redonda
**Material:** PVC / EVA
**Textura:** Antideslizante con relieve
**Colores:** Negro, azul marino
**Por qué:** Alta demanda de calzado abrigado y resistente para niños en invierno."""

        alerta = f"""## ALERTA EMERGENTE
Los borcegos con suela gruesa tipo work boot están emergiendo con fuerza esta temporada. Se busca suela de TR bicolor (negro con detalle en color) de 3-4cm, con textura marcada y punta ligeramente cuadrada."""

    return {
        "concepto_dama": concepto_dama,
        "concepto_nino": concepto_nino,
        "alerta_emergente": alerta,
        "texto_completo": f"{concepto_dama}\n\n{concepto_nino}\n\n{alerta}",
    }
