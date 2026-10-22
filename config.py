"""
League Manager Configuration
Generic league instances loaded from environment variables
All personal data stored in iCloud Drive
"""

import os
from pathlib import Path

# Base directories
# Use iCloud Drive for all personal data, logs, and league-specific info
ICLOUD_DIR = Path.home() / "Library" / "Mobile Documents" / "com~apple~CloudDocs"
FANTASY_DATA_DIR = ICLOUD_DIR / "FantasyLeague"
LOGS_DIR = FANTASY_DATA_DIR / "logs"
STATE_DIR = FANTASY_DATA_DIR / "state"
CORE_DIR = FANTASY_DATA_DIR / "core"

# Ensure directories exist
FANTASY_DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)
STATE_DIR.mkdir(parents=True, exist_ok=True)
CORE_DIR.mkdir(parents=True, exist_ok=True)

# League configurations
# ALL personal data loaded from environment variables
# League names are generic - actual names stored in iCloud only
LEAGUES = {
    "league1": {
        "platform": os.environ.get("LEAGUE1_PLATFORM", "yahoo_nba"),
        "league_id": os.environ.get("LEAGUE1_ID", ""),
        "team_name": os.environ.get("LEAGUE1_TEAM_NAME", "Team 1"),
        "rules": {
            "adds_per_week": int(os.environ.get("LEAGUE1_ADDS_PER_WEEK", "4")),
            "il_slots": int(os.environ.get("LEAGUE1_IL_SLOTS", "3")),
            "scoring": os.environ.get("LEAGUE1_SCORING", "category")
        },
        "inactive_league_id": os.environ.get("LEAGUE1_INACTIVE_ID", ""),
        "core_file": CORE_DIR / "league1_core.json",
        "state_file": STATE_DIR / "league1_state.json",
        "log_file": LOGS_DIR / "league1.log"
    },
    "league2": {
        "platform": os.environ.get("LEAGUE2_PLATFORM", "sleeper_nfl"),
        "league_id": os.environ.get("LEAGUE2_ID", ""),
        "roster_id": os.environ.get("LEAGUE2_ROSTER_ID", "8"),
        "team_name": os.environ.get("LEAGUE2_TEAM_NAME", "Team 2"),
        "rules": {
            "no_te_slot": os.environ.get("LEAGUE2_NO_TE_SLOT", "true").lower() == "true",
            "te_flex_only": os.environ.get("LEAGUE2_TE_FLEX_ONLY", "true").lower() == "true",
            "waiver_day": os.environ.get("LEAGUE2_WAIVER_DAY", "Tuesday"),
            "trade_deadline_week": int(os.environ.get("LEAGUE2_TRADE_DEADLINE", "12")),
            "trade_review_days": int(os.environ.get("LEAGUE2_TRADE_REVIEW_DAYS", "1")),
            "playoff_teams": int(os.environ.get("LEAGUE2_PLAYOFF_TEAMS", "8")),
            "total_teams": int(os.environ.get("LEAGUE2_TOTAL_TEAMS", "12"))
        },
        "core_file": CORE_DIR / "league2_core.json",
        "state_file": STATE_DIR / "league2_state.json",
        "log_file": LOGS_DIR / "league2.log"
    },
    "league3": {
        "platform": os.environ.get("LEAGUE3_PLATFORM", "sleeper_nfl"),
        "league_id": os.environ.get("LEAGUE3_ID", ""),
        "roster_id": os.environ.get("LEAGUE3_ROSTER_ID", "8"),
        "team_name": os.environ.get("LEAGUE3_TEAM_NAME", "Team 3"),
        "rules": {
            "waiver_day": os.environ.get("LEAGUE3_WAIVER_DAY", "Tuesday"),
            "trade_deadline_week": int(os.environ.get("LEAGUE3_TRADE_DEADLINE", "11")),
            "instant_trades": os.environ.get("LEAGUE3_INSTANT_TRADES", "true").lower() == "true"
        },
        "core_file": CORE_DIR / "league3_core.json",
        "state_file": STATE_DIR / "league3_state.json",
        "log_file": LOGS_DIR / "league3.log"
    }
}

# API Configuration
SLEEPER_BASE_URL = "https://api.sleeper.app/v1"
SLEEPER_MOBILE_USER_AGENT = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"

YAHOO_BASE_URL = "https://fantasysports.yahooapis.com/fantasy/v2"

# Ollama Configuration
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "qwen2.5:7b"
OLLAMA_TIMEOUT = 120  # seconds

# Environment variable keys (DO NOT store values here)
ENV_KEYS = {
    "yahoo_client_id": "YAHOO_CLIENT_ID",
    "yahoo_client_secret": "YAHOO_CLIENT_SECRET",
    "yahoo_refresh_token": "YAHOO_REFRESH_TOKEN",
    "sleeper_cookie": "SLEEPER_COOKIE"
}

def get_credential(key):
    """Safely retrieve credentials from environment variables"""
    env_key = ENV_KEYS.get(key)
    if not env_key:
        raise ValueError(f"Unknown credential key: {key}")
    
    value = os.environ.get(env_key)
    if not value:
        raise ValueError(f"Environment variable {env_key} not set")
    
    return value

# Request timeouts
DEFAULT_TIMEOUT = 30
API_RETRY_ATTEMPTS = 3
API_RETRY_DELAY = 2  # seconds
