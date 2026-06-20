import subprocess
import sys


def show_notification(title, message):
    try:
        from plyer import notification

        notification.notify(title=title, message=message, timeout=3, app_icon=None)
    except Exception:
        _toast_fallback(title, message)


def _toast_fallback(title, message):
    try:
        subprocess.run(
            [
                "powershell",
                "-Command",
                f"""
                [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
                $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
                $textNodes = $template.GetElementsByTagName("text")
                $textNodes.Item(0).AppendChild($template.CreateTextNode("{title}")) > $null
                $textNodes.Item(1).AppendChild($template.CreateTextNode("{message}")) > $null
                $toast = [Windows.UI.Notifications.ToastNotification]::new($template)
                [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Whisper").Show($toast)
                """,
            ],
            capture_output=True,
            timeout=5,
        )
    except Exception:
        pass
