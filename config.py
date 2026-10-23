import os

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b")

LEAGUES = {
    "league1": {
        "name": "National Natty League",
        "id": "1389329423609643008",
        "roster_id": "8"
    },
    "league2": {
        "name": "Fantasy Fellowship League",
        "id": "1389389459547500544",
        "roster_id": "8"
    }
}

def get_credential(key, default=None):
    return os.environ.get(key, default)
