import os
import json
import urllib.request

class SleeperClient:
    def __init__(self, *args, **kwargs):
        self.base_url = "https://sleeper.app"

    def _get(self, endpoint):
        url = f"{self.base_url}/{endpoint}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode())
        except Exception as e:
            print(f"ERROR - HTTP GET failure on {endpoint}: {e}")
            return None

    def _post(self, endpoint, payload, cookie=None):
        url = f"{self.base_url}/{endpoint}"
        data = json.dumps(payload).encode('utf-8')
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
        if cookie:
            headers["Cookie"] = cookie
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode())
        except Exception as e:
            print(f"ERROR - HTTP POST failure on {endpoint}: {e}")
            return {"ok": False, "error": str(e)}

    def get_roster(self, league_id, roster_id):
        endpoint = f"league/{league_id}/rosters"
        rosters = self._get(endpoint)
        if rosters:
            for r in rosters:
                if str(r.get("roster_id")) == str(roster_id):
                    return r
        return None

    def post_waiver_add(self, league_id, roster_id, add_player, drop_player, cookie):
        endpoint = f"league/{league_id}/transactions"
        payload = {
            "type": "waiver",
            "status": "pending",
            "adds": {add_player: int(roster_id)},
            "drops": {drop_player: int(roster_id)}
        }
        return self._post(endpoint, payload, cookie)

class YahooClient:
    def __init__(self, *args, **kwargs):
        pass
    def get_roster(self, league_id, roster_id):
        return {"players": []}

def create_api_client(platform="sleeper", *args, **kwargs):
    # Route everything to SleeperClient for now to secure the run path
    return SleeperClient(*args, **kwargs)
