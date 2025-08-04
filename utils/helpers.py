# utils/helpers.py

def get_ticker(asset):
    mapping = {
        "Gold": "GC=F",
        "EURUSD": "EURUSD=X",
        "USDJPY": "JPY=X",
    }
    return mapping.get(asset, "")
