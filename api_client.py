"""
API Clients for Fantasy Sports Platforms
Handles Sleeper and Yahoo API interactions
"""

import requests
import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class SleeperClient:
    """Client for Sleeper Fantasy Football API"""
    
    def __init__(self, base_url: str = "https://api.sleeper.app/v1", timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        self.mobile_user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15"
        self._players_cache = None
        self._players_cache_time = None
    
    def _get(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Execute GET request with retry logic"""
        url = f"{self.base_url}/{endpoint}"
        
        for attempt in range(3):
            try:
                response = self.session.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                logger.warning(f"Sleeper GET failed (attempt {attempt + 1}): {e}")
                if attempt < 2:
                    time.sleep(2 ** attempt)
                else:
                    logger.error(f"Sleeper GET failed after retries: {endpoint}")
                    return None
    
    def _post(self, endpoint: str, data: Dict, cookie: str = None) -> Optional[Dict]:
        """Execute authenticated POST request"""
        url = f"{self.base_url}/{endpoint}"
        headers = {"User-Agent": self.mobile_user_agent}
        
        if cookie:
            headers["Cookie"] = cookie
        
        try:
            response = self.session.post(
                url, 
                json=data, 
                headers=headers, 
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Sleeper POST failed: {e}")
            return None
    
    def get_league_info(self, league_id: str) -> Optional[Dict]:
        """Get league settings and info"""
        return self._get(f"league/{league_id}")
    
    def get_rosters(self, league_id: str) -> Optional[List[Dict]]:
        """Get all rosters in league"""
        return self._get(f"league/{league_id}/rosters")
    
    def get_roster(self, league_id: str, roster_id: str) -> Optional[Dict]:
        """Get specific roster"""
        rosters = self.get_rosters(league_id)
        if rosters:
            for roster in rosters:
                if str(roster.get("roster_id")) == str(roster_id):
                    return roster
        return None
    
    def get_users(self, league_id: str) -> Optional[List[Dict]]:
        """Get league users"""
        return self._get(f"league/{league_id}/users")
    
    def get_matchups(self, league_id: str, week: int) -> Optional[List[Dict]]:
        """Get matchups for specific week"""
        return self._get(f"league/{league_id}/matchups/{week}")
    
    def get_players(self, force_refresh: bool = False) -> Optional[Dict]:
        """Get all NFL players (cached for 24 hours)"""
        now = time.time()
        
        if not force_refresh and self._players_cache and self._players_cache_time:
            if now - self._players_cache_time < 86400:  # 24 hours
                return self._players_cache
        
        players = self._get("players/nfl")
        if players:
            self._players_cache = players
            self._players_cache_time = now
        
        return players
    
    def get_trending_players(self, sport: str = "nfl", trend_type: str = "add", hours: int = 24) -> Optional[List[Dict]]:
        """Get trending players"""
        return self._get(f"players/{sport}/trending/{trend_type}", params={"lookback_hours": hours})
    
    def get_transactions(self, league_id: str, week: int) -> Optional[List[Dict]]:
        """Get transactions for specific week"""
        return self._get(f"league/{league_id}/transactions/{week}")
    
    def get_traded_picks(self, league_id: str) -> Optional[List[Dict]]:
        """Get traded draft picks"""
        return self._get(f"league/{league_id}/traded_picks")
    
    def get_current_week(self) -> int:
        """Get current NFL week"""
        state = self._get("state/nfl")
        if state:
            return state.get("week", 1)
        return 1
    
    def post_waiver_add(self, league_id: str, roster_id: str, add_player_id: str, 
                       drop_player_id: str, cookie: str) -> Optional[Dict]:
        """Submit waiver claim (requires authentication)"""
        data = {
            "type": "waiver",
            "settings": {
                "waiver_bid": 0
            },
            "roster_ids": [roster_id],
            "adds": {add_player_id: roster_id},
            "drops": {drop_player_id: roster_id}
        }
        return self._post(f"league/{league_id}/transactions", data, cookie)
    
    def post_trade_accept(self, league_id: str, transaction_id: str, cookie: str) -> Optional[Dict]:
        """Accept a trade offer"""
        # Note: Sleeper trade acceptance typically done via app
        # This is a placeholder for the structure
        logger.warning("Trade acceptance may require app interaction")
        return None
    
    def post_trade_reject(self, league_id: str, transaction_id: str, cookie: str) -> Optional[Dict]:
        """Reject a trade offer"""
        # Note: Sleeper trade rejection typically done via app
        logger.warning("Trade rejection may require app interaction")
        return None


class YahooClient:
    """Client for Yahoo Fantasy Sports API"""
    
    def __init__(self, base_url: str = "https://fantasysports.yahooapis.com/fantasy/v2", timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        self.access_token = None
        self.token_expiry = None
    
    def _refresh_token(self, client_id: str, client_secret: str, refresh_token: str) -> bool:
        """Refresh OAuth2 access token"""
        token_url = "https://api.login.yahoo.com/oauth2/get_token"
        
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret
        }
        
        try:
            response = requests.post(token_url, data=data, timeout=self.timeout)
            response.raise_for_status()
            token_data = response.json()
            
            self.access_token = token_data.get("access_token")
            expires_in = token_data.get("expires_in", 3600)
            self.token_expiry = time.time() + expires_in
            
            logger.info("Yahoo OAuth token refreshed")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Yahoo token refresh failed: {e}")
            return False
    
    def _ensure_token(self, client_id: str, client_secret: str, refresh_token: str):
        """Ensure we have a valid access token"""
        if not self.access_token or (self.token_expiry and time.time() >= self.token_expiry - 300):
            self._refresh_token(client_id, client_secret, refresh_token)
    
    def _get(self, endpoint: str, client_id: str, client_secret: str, refresh_token: str) -> Optional[Any]:
        """Execute authenticated GET request"""
        self._ensure_token(client_id, client_secret, refresh_token)
        
        if not self.access_token:
            logger.error("No valid Yahoo access token")
            return None
        
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Yahoo GET failed: {e}")
            return None
    
    def get_league_settings(self, league_id: str, credentials: Dict) -> Optional[Dict]:
        """Get league settings"""
        endpoint = f"league/nba.l.{league_id}/settings"
        return self._get(endpoint, **credentials)
    
    def get_team_roster(self, league_id: str, team_id: str, credentials: Dict) -> Optional[Dict]:
        """Get team roster"""
        endpoint = f"team/nba.l.{league_id}.t.{team_id}/roster"
        return self._get(endpoint, **credentials)
    
    def get_league_standings(self, league_id: str, credentials: Dict) -> Optional[Dict]:
        """Get league standings"""
        endpoint = f"league/nba.l.{league_id}/standings"
        return self._get(endpoint, **credentials)
    
    def get_free_agents(self, league_id: str, position: str, credentials: Dict) -> Optional[Dict]:
        """Get available free agents"""
        endpoint = f"league/nba.l.{league_id}/players;status=A;position={position}"
        return self._get(endpoint, **credentials)
    
    def get_player_stats(self, player_id: str, credentials: Dict) -> Optional[Dict]:
        """Get player statistics"""
        endpoint = f"player/nba.p.{player_id}/stats"
        return self._get(endpoint, **credentials)
    
    def get_pending_trades(self, league_id: str, credentials: Dict) -> Optional[Dict]:
        """Get pending trade offers"""
        endpoint = f"league/nba.l.{league_id}/transactions;type=pending_trade"
        return self._get(endpoint, **credentials)


def create_api_client(platform: str, config: Dict = None):
    """Factory function to create appropriate API client"""
    if platform == "sleeper_nfl":
        return SleeperClient()
    elif platform == "yahoo_nba":
        return YahooClient()
    else:
        raise ValueError(f"Unknown platform: {platform}")
