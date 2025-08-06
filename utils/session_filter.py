from datetime import datetime, time, timezone
import pytz
import logging

# Your Telegram and Discord credentials
TELEGRAM_TOKEN = "8123034561:AAFUmL-YVT2uybFNDdl4U9eKQtz2w1f1dPo"
TELEGRAM_CHAT_ID = "5689209090"
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1402201260857233470/mwzakXPNjf6S_BPG4ZbK_1MmtivoO2AZKtzYFTrVtAm-68X0MW2HJ1naKCD33Hh2E8Zp"

# Define trading session times in UTC
SESSIONS = {
    "Asian": (time(23, 0), time(8, 0)),    # 23:00 - 08:00 UTC
    "London": (time(8, 0), time(17, 0)),   # 08:00 - 17:00 UTC
    "New York": (time(13, 0), time(22, 0)) # 13:00 - 22:00 UTC
}

def get_current_session():
    now_utc = datetime.now(timezone.utc).time()

    for session_name, (start, end) in SESSIONS.items():
        if start < end:
            if start <= now_utc < end:
                return session_name
        else:
            # Overnight session (e.g., Asian)
            if now_utc >= start or now_utc < end:
                return session_name
    return "Off-session"

def is_session_active(session_name):
    current = get_current_session()
    return current == session_name

def send_session_alert(session_name):
    # Placeholder to send alert via Telegram or Discord if needed
    logging.info(f"Current trading session: {session_name}")

# Example usage
if __name__ == "__main__":
    session = get_current_session()
    send_session_alert(session)
