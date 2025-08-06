# utils/session_filter.py

from datetime import datetime, time, timezone, timedelta
import logging

def get_current_utc_time():
    return datetime.utcnow().time()

def is_time_between(begin, end, current):
    if begin < end:
        return begin <= current < end
    else:  # crosses midnight
        return current >= begin or current < end

def get_trading_session():
    """
    Determines current trading session based on UTC time.
    Returns session name and emoji.
    Sessions (UTC times):
      - Asian: 23:00 - 08:00
      - London: 08:00 - 17:00
      - New York: 13:00 - 22:00
      - Off: otherwise
    """
    now = get_current_utc_time()
    if is_time_between(time(23,0), time(8,0), now):
        session = "Asian Session 🟣"
        open_market = True
    elif is_time_between(time(8,0), time(17,0), now):
        session = "London Session 🟢"
        open_market = True
    elif is_time_between(time(13,0), time(22,0), now):
        session = "New York Session 🔵"
        open_market = True
    else:
        session = "Off Session ⚪"
        open_market = False

    logging.info(f"⏰ Current trading session: {session}")
    return session, open_market

def session_filter(min_session="London Session 🟢"):
    """
    Allows signal only if current session is in allowed sessions.
    min_session can be set to "Asian", "London", or "New York" to allow those or later sessions.
    """
    session_order = ["Asian Session 🟣", "London Session 🟢", "New York Session 🔵", "Off Session ⚪"]
    session, open_market = get_trading_session()

    if session_order.index(session) >= session_order.index(min_session):
        logging.info(f"✅ Session filter passed: {session} >= {min_session}")
        return True, session
    else:
        logging.warning(f"❌ Session filter failed: {session} < {min_session}")
        return False, session
