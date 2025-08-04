# utils/session_filter.py
from datetime import datetime

def get_current_session():
    now = datetime.utcnow().hour
    if 6 <= now < 14:
        return 'London'
    elif 13 <= now < 22:
        return 'New York'
    else:
        return 'Off Hours'
