"""
Módulo para guardar reportes de tendencias en Supabase.
Usa la REST API directamente (sin dependencias extra).
"""

import os
import requests
from datetime import datetime


def guardar_reporte_en_supabase(reporte_tendencias: dict, conceptos_ia: dict) -> bool:
    """
    Guarda el reporte generado en la tabla reportes_tendencias de Supabase.

    Args:
        reporte_tendencias: Dict con fecha, temporada, tendencias, etc.
        conceptos_ia: Dict con concepto_dama, concepto_nino, alerta_emergente, texto_completo.

    Returns:
        True si se guardó correctamente, False si hubo error.
    """
    supabase_url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    supabase_key = os.environ.get("SUPABASE_ANON_KEY", "")

    if not supabase_url or not supabase_key:
        print("  ⚠️  SUPABASE_URL o SUPABASE_ANON_KEY no configurados. Saltando guardado en DB.")
        return False

    endpoint = f"{supabase_url}/rest/v1/reportes_tendencias"

    fecha = reporte_tendencias.get("fecha", datetime.now().strftime("%Y-%m-%d"))
    temporada = reporte_tendencias.get("temporada", "verano")

    payload = {
        "fecha": fecha,
        "temporada": temporada,
        "concepto_dama": conceptos_ia.get("concepto_dama", ""),
        "concepto_nino": conceptos_ia.get("concepto_nino", ""),
        "alerta_emergente": conceptos_ia.get("alerta_emergente", ""),
        "texto_completo": conceptos_ia.get("texto_completo", ""),
    }

    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }

    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=15)
        if response.status_code in (200, 201):
            print("  ✅ Reporte guardado en Supabase correctamente.")
            return True
        else:
            print(f"  ❌ Error al guardar en Supabase: {response.status_code} - {response.text[:200]}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Error de conexión con Supabase: {e}")
        return False
