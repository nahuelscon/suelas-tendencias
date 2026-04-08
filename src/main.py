"""
Orquestador principal del módulo de tendencias.
Ejecuta el flujo completo: tendencias → IA → email.
"""

import sys
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env (solo en desarrollo local)
load_dotenv()


def ejecutar_reporte():
    """Ejecuta el flujo completo del reporte semanal."""
    print("=" * 50)
    print("REPORTE SEMANAL DE TENDENCIAS - SUELAS ARGENTINA")
    print("=" * 50)

    # Paso 1: Obtener tendencias de Google Trends
    print("\n[1/4] Obteniendo tendencias de Google Trends Argentina...")
    try:
        from trends import obtener_reporte_tendencias
        reporte_tendencias = obtener_reporte_tendencias()
        print(f"Temporada detectada: {reporte_tendencias['temporada']}")
        print(f"Tendencias dama encontradas: {len(reporte_tendencias['tendencias_dama'])}")
        print(f"Tendencias niño encontradas: {len(reporte_tendencias['tendencias_nino'])}")
        print(f"Términos emergentes: {len(reporte_tendencias['emergentes'])}")
    except Exception as e:
        print(f"Error obteniendo tendencias: {e}")
        sys.exit(1)

    # Paso 2: Generar conceptos de suela con IA
    print("\n[2/4] Generando conceptos de suela con IA...")
    try:
        from ai_analysis import generar_concepto_suela
        conceptos_ia = generar_concepto_suela(reporte_tendencias, reporte_tendencias["temporada"])
        print("Conceptos generados correctamente.")
    except Exception as e:
        print(f"Error en análisis IA: {e}")
        print("Usando conceptos de respaldo...")
        from ai_analysis import generar_concepto_fallback
        conceptos_ia = generar_concepto_fallback(
            reporte_tendencias["temporada"],
            "calzado dama",
            "calzado niño"
        )

    # Paso 3: Guardar reporte en Supabase (para la app móvil)
    print("\n[3/4] Guardando reporte en Supabase...")
    try:
        from supabase_sender import guardar_reporte_en_supabase
        guardar_reporte_en_supabase(reporte_tendencias, conceptos_ia)
    except Exception as e:
        print(f"  ⚠️  Error guardando en Supabase (no crítico): {e}")

    # Paso 4: Enviar email con el reporte
    print("\n[4/4] Enviando reporte por email...")
    try:
        from email_sender import enviar_reporte
        enviar_reporte(reporte_tendencias, conceptos_ia)
        print("Reporte enviado exitosamente.")
    except Exception as e:
        print(f"Error enviando email: {e}")
        # Si falla el email, imprimir el reporte en consola
        print("\n--- REPORTE (salida a consola por error de email) ---")
        print(conceptos_ia.get("texto_completo", "Sin contenido"))
        sys.exit(1)

    print("\n" + "=" * 50)
    print("REPORTE COMPLETADO EXITOSAMENTE")
    print("=" * 50)


if __name__ == "__main__":
    ejecutar_reporte()
