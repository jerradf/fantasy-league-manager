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
# System auto-detects leagues 1-20 from environment variables

def _build_league_config(league_num: int) -> dict:
    """Build league config from environment variables"""
    prefix = f"LEAGUE{league_num}"
    league_id = os.environ.get(f"{prefix}_ID", "")
    
    if not league_id:
        return None  # League not configured
    
    platform = os.environ.get(f"{prefix}_PLATFORM", "sleeper_nfl")
    
    config = {
        "platform": platform,
        "league_id": league_id,
        "team_name": os.environ.get(f"{prefix}_TEAM_NAME", f"Team {league_num}"),
        "roster_id": os.environ.get(f"{prefix}_ROSTER_ID", ""),
        "rules": {},
        "core_file": CORE_DIR / f"league{league_num}_core.json",
        "state_file": STATE_DIR / f"league{league_num}_state.json",
        "log_file": LOGS_DIR / f"league{league_num}.log"
    }
    
    # Platform-specific rules
    if platform == "yahoo_nba":
        config["rules"] = {
            "adds_per_week": int(os.environ.get(f"{prefix}_ADDS_PER_WEEK", "4")),
            "il_slots": int(os.environ.get(f"{prefix}_IL_SLOTS", "3")),
            "scoring": os.environ.get(f"{prefix}_SCORING", "category")
        }
        config["inactive_league_id"] = os.environ.get(f"{prefix}_INACTIVE_ID", "")
    
    elif platform == "sleeper_nfl":
        config["rules"] = {
            "waiver_day": os.environ.get(f"{prefix}_WAIVER_DAY", "Tuesday"),
            "trade_deadline_week": int(os.environ.get(f"{prefix}_TRADE_DEADLINE", "12")),
        }
        
        # Optional rules
        if os.environ.get(f"{prefix}_NO_TE_SLOT"):
            config["rules"]["no_te_slot"] = os.environ.get(f"{prefix}_NO_TE_SLOT", "").lower() == "true"
            config["rules"]["te_flex_only"] = os.environ.get(f"{prefix}_TE_FLEX_ONLY", "").lower() == "true"
        
        if os.environ.get(f"{prefix}_INSTANT_TRADES"):
            config["rules"]["instant_trades"] = os.environ.get(f"{prefix}_INSTANT_TRADES", "").lower() == "true"
        
        if os.environ.get(f"{prefix}_TRADE_REVIEW_DAYS"):
            config["rules"]["trade_review_days"] = int(os.environ.get(f"{prefix}_TRADE_REVIEW_DAYS", "1"))
        
        if os.environ.get(f"{prefix}_PLAYOFF_TEAMS"):
            config["rules"]["playoff_teams"] = int(os.environ.get(f"{prefix}_PLAYOFF_TEAMS", "8"))
            config["rules"]["total_teams"] = int(os.environ.get(f"{prefix}_TOTAL_TEAMS", "12"))
    
    return config

# Auto-discover leagues from environment variables (supports up to 20 leagues)
LEAGUES = {}
for i in range(1, 21):
    league_config = _build_league_config(i)
    if league_config:
        LEAGUES[f"league{i}"] = league_config

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
