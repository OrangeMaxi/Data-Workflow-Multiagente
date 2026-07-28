import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional, Dict, Any, Tuple

from data_workflow_team.config.settings import settings
from data_workflow_team.core.audit_logger import log_audit_event

def _send_email_notification(subject: str, message: str, recipient: str = None) -> Tuple[bool, str]:
    target_email = recipient or settings.NOTIFICATION_EMAIL_TO
    smtp_server = settings.SMTP_SERVER
    smtp_port = settings.SMTP_PORT
    smtp_user = settings.SMTP_USER
    smtp_pass = settings.SMTP_PASSWORD

    if not smtp_user or not smtp_pass:
        print(f"  [Notification Manager] [EMAIL SIMULATED -> {target_email}]: {subject}")
        return True, f"Notificación por Email a '{target_email}' registrada (Para envío en vivo por SMTP, configura SMTP_USER y SMTP_PASSWORD en .env)."

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"[Data Workflow Team] {subject}"
        msg["From"] = smtp_user
        msg["To"] = target_email

        body_text = f"Data Workflow Team - Alerta de Sistema\n\n{message}\n\nDestinatario: {target_email}"
        msg.attach(MIMEText(body_text, "plain", "utf-8"))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, [target_email], msg.as_string())

        return True, f"Correo enviado exitosamente a {target_email}."
    except Exception as e:
        return False, f"Error enviando correo a {target_email}: {str(e)}"

def _send_slack_notification(subject: str, message: str) -> Tuple[bool, str]:
    url = settings.SLACK_WEBHOOK_URL
    if not url:
        return False, "Slack Webhook URL no configurada."
    try:
        payload = {"text": f"*[{subject}]*\n{message}"}
        res = requests.post(url, json=payload, timeout=5)
        return res.status_code == 200, f"Notificación Slack enviada (Status {res.status_code})"
    except Exception as e:
        return False, f"Error Slack: {str(e)}"

def _send_teams_notification(subject: str, message: str) -> Tuple[bool, str]:
    url = settings.TEAMS_WEBHOOK_URL
    if not url:
        return False, "Microsoft Teams Webhook URL no configurada."
    try:
        payload = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "0076D7",
            "summary": subject,
            "sections": [{
                "activityTitle": f"Data Workflow Team: {subject}",
                "text": message
            }]
        }
        res = requests.post(url, json=payload, timeout=5)
        return res.status_code == 200, f"Notificación Microsoft Teams enviada (Status {res.status_code})"
    except Exception as e:
        return False, f"Error Teams: {str(e)}"

def _send_telegram_notification(subject: str, message: str) -> Tuple[bool, str]:
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    if not token or not chat_id:
        return False, "Telegram Bot Token o Chat ID no configurados."
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        text = f"<b>{subject}</b>\n\n{message}"
        payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
        res = requests.post(url, json=payload, timeout=5)
        return res.status_code == 200, f"Notificación Telegram enviada (Status {res.status_code})"
    except Exception as e:
        return False, f"Error Telegram: {str(e)}"

def send_alert_notification(
    event_type: str,
    subject: str,
    message: str,
    recipient: str = None,
    channels: List[str] = None
) -> str:
    """
    Despacha notificaciones y alertas multicanal (Email/Gmail, Slack, Teams, Telegram, Webhook).
    
    Args:
        event_type: Tipo de evento ('GIT_BRANCH', 'GIT_PR', 'RELEASE', 'KANBAN_DONE', 'SYSTEM_ALERT')
        subject: Título o asunto breve de la alerta.
        message: Detalle y cuerpo explicativo del evento.
        recipient: Dirección de correo destinatario si aplica (por defecto: maximilianonaranjo@gmail.com).
        channels: Lista de canales a utilizar (ej. ['email', 'slack', 'teams', 'telegram']).
        
    Returns:
        Resumen del despacho de la alerta multicanal.
    """
    target_channels = channels or ["email"]
    results = []
    
    target_email = recipient or settings.NOTIFICATION_EMAIL_TO
    print(f"  [Notification Dispatcher] Evento '{event_type}' -> Dispatching to {target_channels}...")
    
    for ch in target_channels:
        ch_lower = ch.lower()
        if ch_lower == "email" or ch_lower == "gmail":
            ok, msg = _send_email_notification(subject, message, target_email)
            results.append(f"Email: {msg}")
        elif ch_lower == "slack":
            ok, msg = _send_slack_notification(subject, message)
            results.append(f"Slack: {msg}")
        elif ch_lower == "teams":
            ok, msg = _send_teams_notification(subject, message)
            results.append(f"Teams: {msg}")
        elif ch_lower == "telegram":
            ok, msg = _send_telegram_notification(subject, message)
            results.append(f"Telegram: {msg}")
            
    log_audit_event("NotificationManager", f"ALERT_{event_type.upper()}", target_email, "SUCCESS", {"channels": target_channels, "subject": subject})
    return f"Alerta '{event_type}' procesada exitosamente.\nDetalle por Canal:\n- " + "\n- ".join(results)
