import os
from pathlib import Path
from dotenv import dotenv_values

def get_setting(name: str, default: str = '') -> str:
    return os.environ.get(name, dotenv_values(Path(__file__).parent / '.env').get(name) or default)

def get_model() -> str:
    return get_setting('GEMINI_MODEL', 'gemini-3.8-flash')

def get_genai_client():
    import time
    from apishield.model_access import environment_connection, model_client
    return model_client(environment_connection(), time.monotonic() + 60)
