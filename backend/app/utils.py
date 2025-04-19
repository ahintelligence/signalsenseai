import numpy as np
import pandas as pd
from datetime import datetime

def safe_serialize(obj):
    if isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    elif isinstance(obj, (np.ndarray,)):
        return obj.tolist()
    elif isinstance(obj, (pd.Timestamp, datetime)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: safe_serialize(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [safe_serialize(v) for v in obj]
    else:
        return obj
