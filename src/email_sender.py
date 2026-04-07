"""
Módulo de envío de email.
Usa Gmail SMTP con contraseña de aplicación (gratuito).
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime


def construir_html(reporte_tendencias, conceptos_ia):
    """
    Construye el HTML del email con el reporte semanal.

    Args:
        reporte_tendencias: dict con datos de Google Trends
        conceptos_ia: dict con conceptos generados por IA

    Returns:
        string HTML del email
    """
    fecha = reporte_tendencias.get("fecha", datetime.now().strftime("%d/%m/%Y"))
    temporada = reporte_tendencias.get("temporada", "").capitalize()

    # Top tendencias dama
    tendencias_dama = reporte_tendencias.get("tendencias_dama", {})
    top_dama = sorted(tendencias_dama.items(), key=lambda x: x[1]["ultimo_valor"], reverse=True)[:5]

    # Top tendencias niño
    tendencias_nino = reporte_tendencias.get("tendencias_nino", {})
    top_nino = sorted(tendencias_nino.items(), key=lambda x: x[1]["ultimo_valor"], reverse=True)[:3]

    # Emergentes
    emergentes = reporte_tendencias.get("emergentes", [])

    # Construir filas de tabla dama
    filas_dama = ""
    for keyword, datos in top_dama:
        emoji = "🔺" if datos["tendencia"] == "subiendo" else "🔻"
        filas_dama += f"""
        <tr>
            <td style="padding:8px; border-bottom:1px solid #eee;">{keyword}</td>
            <td style="padding:8px; border-bottom:1px solid #eee; text-align:center;">{datos['ultimo_valor']}/100</td>
            <td style="padding:8px; border-bottom:1px solid #eee; text-align:center;">{emoji} {datos['tendencia'].capitalize()}</td>
        </tr>"""

    filas_nino = ""
    for keyword, datos in top_nino:
        emoji = "🔺" if datos["tendencia"] == "subiendo" else "🔻"
        filas_nino += f"""
        <tr>
            <td style="padding:8px; border-bottom:1px solid #eee;">{keyword}</td>
            <td style="padding:8px; border-bottom:1px solid #eee; text-align:center;">{datos['ultimo_valor']}/100</td>
            <td style="padding:8px; border-bottom:1px solid #eee; text-align:center;">{emoji} {datos['tendencia'].capitalize()}</td>
        </tr>"""

    emergentes_html = ""
    for term in emergentes:
        emergentes_html += f'<span style="background:#f0e6ff; padding:4px 10px; border-radius:20px; margin:3px; display:inline-block;">{term}</span>'

    # Convertir markdown básico a HTML para los conceptos
    def md_a_html(texto):
        if not texto:
            return ""
        lineas = texto.split("\n")
        html = ""
        for linea in lineas:
            linea = linea.strip()
            if linea.startswith("## "):
                html += f'<h3 style="color:#6a1b9a; margin-top:15px;">{linea[3:]}</h3>'
            elif linea.startswith("**") and ":**" in linea:
                partes = linea.split(":**", 1)
                clave = partes[0].replace("**", "").strip()
                valor = partes[1].strip() if len(partes) > 1 else ""
                html += f'<p style="margin:5px 0;"><strong style="color:#555;">{clave}:</strong> {valor}</p>'
            elif linea:
                html += f'<p style="margin:5px 0; color:#444;">{linea}</p>'
        return html

    concepto_dama_html = md_a_html(conceptos_ia.get("concepto_dama", ""))
    concepto_nino_html = md_a_html(conceptos_ia.get("concepto_nino", ""))
    alerta_html = md_a_html(conceptos_ia.get("alerta_emergente", ""))

    html = f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="font-family: Arial, sans-serif; max-width: 650px; margin: 0 auto; background: #f9f9f9; padding: 20px;">

    <!-- Header -->
    <div style="background: linear-gradient(135deg, #6a1b9a, #ab47bc); padding: 30px; border-radius: 12px; text-align: center; margin-bottom: 20px;">
        <h1 style="color: white; margin: 0; font-size: 24px;">Reporte Semanal de Tendencias</h1>
        <p style="color: #f3e5f5; margin: 8px 0 0 0;">Calzado Dama & Niño · {fecha} · Temporada: {temporada}</p>
    </div>

    <!-- Tendencias Dama -->
    <div style="background: white; border-radius: 10px; padding: 20px; margin-bottom: 15px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">
        <h2 style="color: #6a1b9a; margin-top: 0; font-size: 18px;">Tendencias Dama en Argentina</h2>
        <table style="width:100%; border-collapse:collapse;">
            <thead>
                <tr style="background:#f3e5f5;">
                    <th style="padding:8px; text-align:left; color:#6a1b9a;">Término</th>
                    <th style="padding:8px; text-align:center; color:#6a1b9a;">Popularidad</th>
                    <th style="padding:8px; text-align:center; color:#6a1b9a;">Tendencia</th>
                </tr>
            </thead>
            <tbody>{filas_dama}</tbody>
        </table>
    </div>

    <!-- Tendencias Niño -->
    <div style="background: white; border-radius: 10px; padding: 20px; margin-bottom: 15px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">
        <h2 style="color: #6a1b9a; margin-top: 0; font-size: 18px;">Tendencias Calzado Niño/Niña</h2>
        <table style="width:100%; border-collapse:collapse;">
            <thead>
                <tr style="background:#f3e5f5;">
                    <th style="padding:8px; text-align:left; color:#6a1b9a;">Término</th>
                    <th style="padding:8px; text-align:center; color:#6a1b9a;">Popularidad</th>
                    <th style="padding:8px; text-align:center; color:#6a1b9a;">Tendencia</th>
                </tr>
            </thead>
            <tbody>{filas_nino}</tbody>
        </table>
    </div>

    <!-- Términos Emergentes -->
    {"" if not emergentes else f'''
    <div style="background: white; border-radius: 10px; padding: 20px; margin-bottom: 15px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">
        <h2 style="color: #6a1b9a; margin-top: 0; font-size: 18px;">Búsquedas Emergentes</h2>
        <p style="color: #666; font-size: 13px;">Términos que están creciendo rápidamente esta semana:</p>
        <div>{emergentes_html}</div>
    </div>
    '''}

    <!-- Concepto IA - Dama -->
    <div style="background: white; border-radius: 10px; padding: 20px; margin-bottom: 15px; box-shadow: 0 2px 6px rgba(0,0,0,0.08); border-left: 4px solid #6a1b9a;">
        <h2 style="color: #6a1b9a; margin-top: 0; font-size: 18px;">Concepto de Suela Sugerido - Dama</h2>
        <p style="color: #888; font-size: 12px; margin-top: -5px;">Generado por IA basado en tendencias actuales</p>
        {concepto_dama_html}
    </div>

    <!-- Concepto IA - Niño -->
    <div style="background: white; border-radius: 10px; padding: 20px; margin-bottom: 15px; box-shadow: 0 2px 6px rgba(0,0,0,0.08); border-left: 4px solid #ab47bc;">
        <h2 style="color: #6a1b9a; margin-top: 0; font-size: 18px;">Concepto de Suela Sugerido - Niño/Niña</h2>
        <p style="color: #888; font-size: 12px; margin-top: -5px;">Generado por IA basado en tendencias actuales</p>
        {concepto_nino_html}
    </div>

    <!-- Alerta Emergente -->
    {"" if not alerta_html else f'''
    <div style="background: #fff8e1; border-radius: 10px; padding: 20px; margin-bottom: 15px; box-shadow: 0 2px 6px rgba(0,0,0,0.08); border-left: 4px solid #ffc107;">
        <h2 style="color: #f57f17; margin-top: 0; font-size: 18px;">Alerta de Tendencia Emergente</h2>
        {alerta_html}
    </div>
    '''}

    <!-- Footer -->
    <div style="text-align: center; padding: 15px; color: #aaa; font-size: 12px;">
        <p>Reporte generado automáticamente · Suelas Argentina</p>
        <p>Próximo reporte: el lunes que viene</p>
    </div>

</body>
</html>
"""
    return html


def enviar_reporte(reporte_tendencias, conceptos_ia):
    """
    Envía el reporte semanal por email via Gmail SMTP.

    Args:
        reporte_tendencias: dict con datos de tendencias
        conceptos_ia: dict con conceptos generados por IA
    """
    gmail_user = os.environ.get("GMAIL_USER")
    gmail_app_password = os.environ.get("GMAIL_APP_PASSWORD")
    destinatario = os.environ.get("EMAIL_DESTINATARIO", gmail_user)

    if not gmail_user or not gmail_app_password:
        raise ValueError("Faltan variables GMAIL_USER o GMAIL_APP_PASSWORD")

    fecha = reporte_tendencias.get("fecha", datetime.now().strftime("%d/%m/%Y"))
    temporada = reporte_tendencias.get("temporada", "").capitalize()

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Reporte de Tendencias Calzado · {fecha} · {temporada}"
    msg["From"] = gmail_user
    msg["To"] = destinatario

    html_content = construir_html(reporte_tendencias, conceptos_ia)
    msg.attach(MIMEText(html_content, "html"))

    # Quitar espacios de la contraseña de app (por si se cargó con espacios)
    gmail_app_password = gmail_app_password.replace(" ", "")

    print(f"Enviando reporte a {destinatario}...")
    try:
        # Intentar primero con STARTTLS (puerto 587)
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(gmail_user, gmail_app_password)
            server.sendmail(gmail_user, destinatario, msg.as_string())
    except Exception:
        # Fallback con SSL (puerto 465)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, gmail_app_password)
            server.sendmail(gmail_user, destinatario, msg.as_string())

    print("Email enviado correctamente.")
