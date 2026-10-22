"""
Deep Analysis Engine
Performs comprehensive player evaluation across entire league
Compares every player against league averages and recommends actions
"""

import logging
from typing import Dict, List, Tuple, Optional
from statistics import mean, median

logger = logging.getLogger(__name__)


class DeepAnalyzer:
    """Performs deep analytical research on roster vs entire league"""
    
    def __init__(self, api_client, league_id: str, roster_id: str):
        self.api = api_client
        self.league_id = league_id
        self.roster_id = roster_id
        self.all_rosters = []
        self.all_players = {}
        self.player_stats = {}
        self.league_averages = {}
    
    def run_deep_analysis(self) -> Dict:
        """
        Execute comprehensive league-wide analysis
        
        Steps:
        1. Pull ALL rosters from league
        2. Get player stats for everyone
        3. Calculate league-wide averages by position
        4. Compare YOUR players vs league averages
        5. Identify underperformers to drop
        6. Identify upgrade targets on waivers
        7. Suggest trades based on roster construction
        """
        logger.info("🔍 Starting DEEP ANALYSIS - Full league scan...")
        
        results = {
            "your_roster": [],
            "underperformers": [],
            "league_stars": [],
            "trade_targets": [],
            "drop_candidates": [],
            "waiver_upgrades": [],
            "position_analysis": {}
        }
        
        # Step 1: Pull all league rosters
        logger.info("📊 Scanning all 12 rosters in league...")
        self.all_rosters = self.api.get_rosters(self.league_id) or []
        
        if not self.all_rosters:
            logger.warning("Failed to get league rosters")
            return results
        
        # Step 2: Get all player data
        logger.info("📈 Loading comprehensive player statistics...")
        self.all_players = self.api.get_players() or {}
        
        # Step 3: Analyze your roster
        your_roster = None
        for roster in self.all_rosters:
            if str(roster.get("roster_id")) == str(self.roster_id):
                your_roster = roster
                break
        
        if not your_roster:
            logger.warning("Could not find your roster")
            return results
        
        your_player_ids = your_roster.get("players", [])
        logger.info(f"📋 Analyzing {len(your_player_ids)} players on your roster...")
        
        # Step 4: Calculate league-wide averages
        logger.info("🧮 Computing league-wide performance metrics...")
        self._calculate_league_averages()
        
        # Step 5: Analyze each of YOUR players
        logger.info("🔬 Deep dive on each player...")
        for player_id in your_player_ids:
            player_data = self.all_players.get(player_id, {})
            analysis = self._analyze_player(player_id, player_data)
            results["your_roster"].append(analysis)
            
            # Classify player
            if analysis["performance_rating"] == "DROP":
                results["drop_candidates"].append(analysis)
            elif analysis["performance_rating"] == "UNDERPERFORMER":
                results["underperformers"].append(analysis)
        
        # Step 6: Find upgrade targets
        logger.info("🎯 Scanning league for upgrade opportunities...")
        results["waiver_upgrades"] = self._find_waiver_upgrades(your_player_ids)
        
        # Step 7: Identify trade targets
        logger.info("💼 Analyzing other rosters for trade opportunities...")
        results["trade_targets"] = self._find_trade_targets(your_player_ids)
        
        # Step 8: Position-by-position analysis
        logger.info("📊 Position-by-position breakdown...")
        results["position_analysis"] = self._analyze_positions(your_player_ids)
        
        logger.info(f"✅ Deep analysis complete:")
        logger.info(f"   - Drop candidates: {len(results['drop_candidates'])}")
        logger.info(f"   - Underperformers: {len(results['underperformers'])}")
        logger.info(f"   - Waiver upgrades: {len(results['waiver_upgrades'])}")
        logger.info(f"   - Trade targets: {len(results['trade_targets'])}")
        
        return results
    
    def _calculate_league_averages(self):
        """Calculate average points per position across ALL rosters"""
        position_stats = {}
        
        for roster in self.all_rosters:
            player_ids = roster.get("players", [])
            for player_id in player_ids:
                player = self.all_players.get(player_id, {})
                position = player.get("position", "UNKNOWN")
                
                # Get fantasy points (simplified - would use actual stats)
                points = player.get("fantasy_points_ppr", 0)
                
                if position not in position_stats:
                    position_stats[position] = []
                
                if points > 0:
                    position_stats[position].append(points)
        
        # Calculate averages
        for position, points_list in position_stats.items():
            if points_list:
                self.league_averages[position] = {
                    "average": mean(points_list),
                    "median": median(points_list),
                    "max": max(points_list),
                    "min": min(points_list)
                }
    
    def _analyze_player(self, player_id: str, player_data: Dict) -> Dict:
        """
        Deep analysis of single player vs league benchmarks
        
        Returns performance rating: STAR | SOLID | AVERAGE | UNDERPERFORMER | DROP
        """
        name = player_data.get("full_name", player_id)
        position = player_data.get("position", "UNKNOWN")
        team = player_data.get("team", "FA")
        injury_status = player_data.get("injury_status", "")
        
        # Get player stats (simplified - would pull actual stats)
        player_points = player_data.get("fantasy_points_ppr", 0)
        
        # Compare to position average
        position_avg = self.league_averages.get(position, {}).get("average", 0)
        position_max = self.league_averages.get(position, {}).get("max", 0)
        
        # Calculate performance percentile
        if position_avg > 0:
            performance_pct = (player_points / position_avg) * 100
        else:
            performance_pct = 0
        
        # Rating logic
        if performance_pct >= 150:
            rating = "STAR"
            action = "KEEP - Elite performer"
        elif performance_pct >= 110:
            rating = "SOLID"
            action = "KEEP - Above average"
        elif performance_pct >= 80:
            rating = "AVERAGE"
            action = "HOLD - Monitor performance"
        elif performance_pct >= 50:
            rating = "UNDERPERFORMER"
            action = "CONSIDER UPGRADE - Below average"
        else:
            rating = "DROP"
            action = "DROP IMMEDIATELY - Wasting roster spot"
        
        # Injury considerations
        if injury_status in ["Out", "IR", "Doubtful"]:
            action = f"INJURED ({injury_status}) - {action}"
        
        return {
            "player_id": player_id,
            "name": name,
            "position": position,
            "team": team,
            "points": player_points,
            "position_avg": position_avg,
            "performance_pct": performance_pct,
            "performance_rating": rating,
            "recommended_action": action,
            "injury_status": injury_status
        }
    
    def _find_waiver_upgrades(self, your_player_ids: List[str]) -> List[Dict]:
        """Find available players better than your worst players"""
        upgrades = []
        
        # Find unrostered players
        all_rostered = set()
        for roster in self.all_rosters:
            all_rostered.update(roster.get("players", []))
        
        # Sample top unrostered players (would do full scan)
        for player_id, player_data in list(self.all_players.items())[:100]:
            if player_id not in all_rostered and player_id not in your_player_ids:
                position = player_data.get("position")
                if position in ["QB", "RB", "WR", "TE"]:
                    points = player_data.get("fantasy_points_ppr", 0)
                    position_avg = self.league_averages.get(position, {}).get("average", 0)
                    
                    if points > position_avg * 1.2:  # 20% above average
                        upgrades.append({
                            "name": player_data.get("full_name", player_id),
                            "position": position,
                            "points": points,
                            "advantage": f"+{int((points/position_avg - 1) * 100)}% vs avg"
                        })
        
        return upgrades[:5]  # Top 5
    
    def _find_trade_targets(self, your_player_ids: List[str]) -> List[Dict]:
        """Identify high-value players on other teams to target"""
        targets = []
        
        # Scan all rosters for stars
        for roster in self.all_rosters:
            if str(roster.get("roster_id")) == str(self.roster_id):
                continue  # Skip your own roster
            
            roster_players = roster.get("players", [])
            for player_id in roster_players:
                player_data = self.all_players.get(player_id, {})
                position = player_data.get("position")
                points = player_data.get("fantasy_points_ppr", 0)
                position_avg = self.league_averages.get(position, {}).get("average", 0)
                
                # High performers worth trading for
                if points > position_avg * 1.5:
                    targets.append({
                        "name": player_data.get("full_name", player_id),
                        "position": position,
                        "points": points,
                        "owner": f"Roster {roster.get('roster_id')}",
                        "value": "HIGH - Consider offering package deal"
                    })
        
        return sorted(targets, key=lambda x: x["points"], reverse=True)[:10]
    
    def _analyze_positions(self, your_player_ids: List[str]) -> Dict:
        """Position-by-position strength analysis"""
        position_breakdown = {}
        
        for player_id in your_player_ids:
            player = self.all_players.get(player_id, {})
            position = player.get("position", "UNKNOWN")
            
            if position not in position_breakdown:
                position_breakdown[position] = {
                    "count": 0,
                    "total_points": 0,
                    "players": []
                }
            
            points = player.get("fantasy_points_ppr", 0)
            position_breakdown[position]["count"] += 1
            position_breakdown[position]["total_points"] += points
            position_breakdown[position]["players"].append(player.get("full_name", player_id))
        
        # Add analysis
        for position, data in position_breakdown.items():
            avg = data["total_points"] / data["count"] if data["count"] > 0 else 0
            league_avg = self.league_averages.get(position, {}).get("average", 0)
            
            if avg > league_avg * 1.2:
                data["strength"] = "STRONG"
            elif avg > league_avg * 0.8:
                data["strength"] = "AVERAGE"
            else:
                data["strength"] = "WEAK - NEEDS UPGRADE"
        
        return position_breakdown
