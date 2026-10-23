#!/usr/bin/env python3
import os
import sys
import json
import requests

class BackdoorAuthException(Exception):
    """Raised when the internal GraphQL gateway session token is invalid or expired."""
    pass

def get_roster(league_id, roster_id):
    """
    Retrieves real active player arrays from the backdoor workspace pipeline.
    Utilizes the SLEEPER_SESSION_TOKEN environment variable injected from local_env.sh.
    """
    token = os.getenv("SLEEPER_SESSION_TOKEN")
    if not token:
        print("[-] Missing SLEEPER_SESSION_TOKEN in environment variables.", file=sys.stderr)
        raise BackdoorAuthException("No backdoor token available.")

    # Sleeper internal gateway endpoint matching the custom tool spec
    url = "https://sleeper.app"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
    }

    # GraphQL payload targeting the specific roster identity sequence
    query = """
    query getRoster($league_id: String!, $roster_id: Int!) {
        roster(league_id: $league_id, roster_id: $roster_id) {
            status
            players
            starters
        }
    }
    """
    
    variables = {
        "league_id": str(league_id),
        "roster_id": int(roster_id)
    }

    try:
        # Gateway request execution block
        response = requests.post(url, json={"query": query, "variables": variables}, headers=headers, timeout=15)
        
        # Explicit detection for redirection/authentication gateway errors
        if response.status_code in (401, 403) or "unauthorized" in response.text.lower():
            raise BackdoorAuthException("SLEEPER SESSION EXPIRED")
            
        response.raise_for_status()
        res_json = response.json()
        
        if "errors" in res_json:
            error_msg = res_json["errors"].get("message", "")
            if "auth" in error_msg.lower() or "token" in error_msg.lower():
                raise BackdoorAuthException("SLEEPER SESSION EXPIRED")
            return {"status": "DIRTY", "players": [], "starters": []}

        data = res_json.get("data", {})
        roster_node = data.get("roster")
        
        if not roster_node:
            return {"status": "DIRTY", "players": [], "starters": []}
            
        return {
            "status": roster_node.get("status", "CLEAN"),
            "players": roster_node.get("players", []),
            "starters": roster_node.get("starters", [])
        }

    except requests.exceptions.HTTPError as http_err:
        if http_err.response.status_code in (401, 403):
            raise BackdoorAuthException("SLEEPER SESSION EXPIRED")
        raise http_err
