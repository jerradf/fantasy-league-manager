import os

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b")                  

LEAGUES = {
    "league1": {
        "name": "National Natty League",
        "team_name": "National Natty League",
        "id": "1389329423609643008",    
        "league_id": "1389329423609643008",
        "roster_id": "8",
        "platform": "sleeper",
        "log_file": "logs/2026/sleeper/league1_run.log"
    },                  
    "league2": {
        "name": "Fantasy Fellowship League",
        "team_name": "Fantasy Fellowship League",
        "id": "1389389459547500544",        
        "league_id": "1389389459547500544",
        "roster_id": "8",
        "platform": "sleeper",
        "log_file": "logs/2026/sleeper/league2_run.log"
    }                   
}    

def get_credential(key, default=None):
    return os.environ.get(key, default)
