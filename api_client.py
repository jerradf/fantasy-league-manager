import os
import json
import urllib.request
from config import get_credential

class SleeperClient:
    def __init__(self, *args, **kwargs):
        # Point straight to the private internal web app gate endpoint 
        self.base_url = "https://sleeper.app"

    def _authenticated_request(self, endpoint, method="GET", payload=None):
        url = f"{self.base_url}/{endpoint}"
        token = get_credential("SLEEPER_TOKEN") or get_credential("SLEEPER_COOKIE")
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*"
        }
        if token:
            headers["Authorization"] = str(token)
            headers["cookie"] = f"token={token}"

        data = json.dumps(payload).encode('utf-8') if payload else None
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=12) as response:
                return json.loads(response.read().decode())
        except Exception as e:
            print(f"BACKDOOR ERROR - Failure accessing {endpoint} via {method}: {e}")
            return None

    def get_user_id_from_token(self):
        # Backdoor pass: Call token validation loop to pull your unique user metadata
        res = self._authenticated_request("user", method="GET")
        if res and isinstance(res, dict):
            return res.get("user_id")
        return None

    def get_roster(self, league_id, roster_id):
        # 1. Pull down the full league structure using authenticated session rules
        endpoint = f"league/{league_id}/rosters"
        rosters = self._authenticated_request(endpoint, method="GET")
        if not rosters or not isinstance(rosters, list):
            return {"players": []}

        # 2. Attempt to resolve by internal user_id backdoor match first
        my_uid = self.get_user_id_from_token()
        if my_uid:
            for r in rosters:
                if str(r.get("owner_id")) == str(my_uid):
                    return r

        # 3. Fallback: match based on your explicit roster assignment sequence slot
        for r in rosters:
            if str(r.get("roster_id")) == str(roster_id):
                return r

        return rosters[0] if len(rosters) > 0 else {"players": []}

    def post_waiver_add(self, league_id, roster_id, add_player, drop_player, cookie=None):
        # Authenticated backdoor transaction post gate routing
        endpoint = f"league/{league_id}/transactions"
        payload = {
            "type": "waiver",
            "status": "pending",
            "adds": {add_player: int(roster_id)},
            "drops": {drop_player: int(roster_id)}
        }
        return self._authenticated_request(endpoint, method="POST", payload=payload)

class YahooClient:
    def __init__(self, *args, **kwargs):
        pass
    def get_roster(self, league_id, roster_id):
        return {"players": []}

def create_api_client(platform="sleeper", *args, **kwargs):
    return SleeperClient(*args, **kwargs)
