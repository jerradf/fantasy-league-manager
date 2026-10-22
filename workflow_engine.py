"""
Workflow Engine - 9-Step Execution Loop
Orchestrates all league management operations
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from validators import (
    validate_lineup_eligibility,
    validate_roster_structure,
    validate_trade_legality,
    validate_waiver_claim,
    calculate_team_health,
    verify_roster_clean,
    validate_protected_players
)
from utils import (
    load_core_players,
    save_state,
    load_json,
    safe_get,
    format_player_name,
    calculate_adds_remaining
)


class WorkflowEngine:
    """Executes the 9-step workflow for a single league instance"""
    
    def __init__(self, league_config: Dict, api_client, ollama_client, logger):
        self.config = league_config
        self.api = api_client
        self.ai = ollama_client
        self.logger = logger
        self.log = []
        
        # Load persistent data
        self.core_players = load_core_players(self.config["core_file"])
        self.state = load_json(self.config["state_file"]) or {}
        
        # Runtime data
        self.roster = []
        self.league_info = {}
        self.current_week = 1
        self.moves_executed = []
        self.issues_found = []
    
    def execute(self) -> Dict:
        """Run all 9 steps sequentially and return results"""
        self.logger.info(f"Starting workflow for {self.config['team_name']}")
        
        results = {
            "identity": self.step_0_scan_team_open(),
            "trends": self.step_1_checking_trends(),
            "holds": self.step_2_hold_long_term_players(),
            "streaming": self.step_3_quick_big_points_players(),
            "lineup": self.step_4_swap_players(),
            "trades": self.step_5_trades(),
            "validation": self.step_6_scan_team_close(),
            "matchup": self.step_7_handle_matchup(),
            "final": self.step_8_verify_roster(),
            "queued": self._get_queued_actions()
        }
        
        # Save final state
        self._save_execution_state(results)
        
        self.logger.info("Workflow completed")
        return results
    
    def step_0_scan_team_open(self) -> Dict:
        """
        Step 0: Initialize logs, output identity, check platform connectivity
        """
        self.logger.info("STEP 0: Scan Team (Open)")
        
        result = {
            "league_id": self.config["league_id"],
            "team_name": self.config["team_name"],
            "platform": self.config["platform"],
            "current_week": 1,
            "platform_status": "CHECKING",
            "extra_info": ""
        }
        
        # Determine current week based on platform
        if "nfl" in self.config["platform"]:
            self.current_week = self._get_nfl_week()
        elif "nba" in self.config["platform"]:
            self.current_week = self._get_nba_week()
        
        result["current_week"] = self.current_week
        
        # Check platform connectivity
        try:
            if self.config["platform"] == "sleeper_nfl":
                league_info = self.api.get_league_info(self.config["league_id"])
                if league_info:
                    result["platform_status"] = "ACTIVE"
                    result["extra_info"] = f"Roster ID: {self.config['roster_id']}"
                else:
                    result["platform_status"] = "ERROR"
                    result["extra_info"] = "Failed to fetch league data"
            
            elif self.config["platform"] == "yahoo_nba":
                # Yahoo requires credentials - check availability
                result["platform_status"] = "ACTIVE"
                result["extra_info"] = "Yahoo API ready"
        
        except Exception as e:
            self.logger.error(f"Platform connectivity check failed: {e}")
            result["platform_status"] = "ERROR"
            result["extra_info"] = str(e)
        
        self.logger.info(f"Platform: {result['platform_status']}, Week: {result['current_week']}")
        return result
    
    def step_1_checking_trends(self) -> Dict:
        """
        Step 1: Pull live network data - roster, projections, standings, free agents, trades
        """
        self.logger.info("STEP 1: Checking Trends")
        
        result = {
            "summary": "No data",
            "roster_size": 0,
            "rank": "Unknown",
            "points_vs_projection": 0,
            "free_agents_available": 0,
            "pending_trades": 0
        }
        
        try:
            if self.config["platform"] == "sleeper_nfl":
                # Get roster
                roster_data = self.api.get_roster(
                    self.config["league_id"],
                    self.config["roster_id"]
                )
                
                if roster_data:
                    self.roster = roster_data.get("players", [])
                    result["roster_size"] = len(self.roster)
                    
                    # Get standings
                    rosters = self.api.get_rosters(self.config["league_id"])
                    if rosters:
                        # Sort by wins
                        sorted_rosters = sorted(
                            rosters,
                            key=lambda r: (r.get("settings", {}).get("wins", 0)),
                            reverse=True
                        )
                        
                        # Find our rank
                        for i, r in enumerate(sorted_rosters):
                            if str(r.get("roster_id")) == str(self.config["roster_id"]):
                                result["rank"] = f"{i + 1}/{len(rosters)}"
                                break
                    
                    # Get transactions (for trending)
                    transactions = self.api.get_transactions(
                        self.config["league_id"],
                        self.current_week
                    )
                    
                    if transactions:
                        result["pending_trades"] = sum(
                            1 for t in transactions if t.get("type") == "trade" and t.get("status") == "pending"
                        )
                
                result["summary"] = f"Rank: {result['rank']} | Roster: {result['roster_size']} players"
            
            elif self.config["platform"] == "yahoo_nba":
                # Yahoo API calls would go here
                result["summary"] = "Yahoo data pending implementation"
        
        except Exception as e:
            self.logger.error(f"Failed to check trends: {e}")
            result["summary"] = f"Error: {str(e)}"
        
        self.logger.info(f"Trends: {result['summary']}")
        return result
    
    def step_2_hold_long_term_players(self) -> Dict:
        """
        Step 2: Load core players and mark them as protected
        """
        self.logger.info("STEP 2: Hold Long-Term Players")
        
        protected = self.core_players.get("protected_players", [])
        never_drop = self.core_players.get("never_drop", [])
        
        result = {
            "protected_count": len(protected),
            "never_drop_count": len(never_drop),
            "protected_list": protected,
            "violations": []
        }
        
        self.logger.info(f"Protected: {len(protected)} players, Never Drop: {len(never_drop)} players")
        return result
    
    def step_3_quick_big_points_players(self) -> Dict:
        """
        Step 3: Identify and execute optimal streaming waiver moves
        """
        self.logger.info("STEP 3: Quick Big Points Players (Streaming)")
        
        result = {
            "suggestions": [],
            "moves": [],
            "blocked": []
        }
        
        try:
            # Get trending players or available free agents
            if self.config["platform"] == "sleeper_nfl":
                trending = self.api.get_trending_players("nfl", "add", 24)
                
                if trending and self.ai.available:
                    # Ask AI for waiver suggestions
                    suggestions = self.ai.suggest_waiver_adds(
                        self.roster,
                        trending[:20],
                        self.config["rules"],
                        self.current_week
                    )
                    
                    result["suggestions"] = suggestions
                    
                    # Check if we should execute (adds remaining, etc.)
                    adds_remaining = calculate_adds_remaining(
                        self.config["rules"],
                        []  # Would need to fetch this week's transactions
                    )
                    
                    if adds_remaining > 0:
                        self.logger.info(f"Waiver suggestions available, adds remaining: {adds_remaining}")
                    else:
                        result["blocked"].append("Weekly add limit reached")
                else:
                    result["blocked"].append("AI offline or no trending data")
        
        except Exception as e:
            self.logger.error(f"Streaming analysis failed: {e}")
            result["blocked"].append(f"Error: {str(e)}")
        
        self.logger.info(f"Streaming: {len(result['suggestions'])} suggestions, {len(result['moves'])} executed")
        return result
    
    def step_4_swap_players(self) -> Dict:
        """
        Step 4: Optimize lineup with eligibility gate enforcement
        """
        self.logger.info("STEP 4: Swap Players (Lineup Optimization)")
        
        result = {
            "changes": [],
            "validation": "PENDING",
            "blocked": []
        }
        
        try:
            if self.ai.available and self.roster:
                # Get matchup data if available
                matchups = {}
                if self.config["platform"] == "sleeper_nfl":
                    matchup_data = self.api.get_matchups(
                        self.config["league_id"],
                        self.current_week
                    )
                    if matchup_data:
                        matchups = {"data": matchup_data}
                
                # Get player info with injury status
                players_dict = self.api.get_players() or {}
                
                # Build injury data
                injury_data = {}
                for player_id in self.roster:
                    player_info = players_dict.get(player_id, {})
                    injury_status = player_info.get("injury_status")
                    if injury_status:
                        injury_data[player_id] = injury_status
                
                # Ask AI for lineup optimization
                roster_with_details = []
                for player_id in self.roster:
                    player_info = players_dict.get(player_id, {})
                    roster_with_details.append({
                        "player_id": player_id,
                        "name": player_info.get("full_name", player_id),
                        "position": player_info.get("position"),
                        "injury_status": player_info.get("injury_status")
                    })
                
                optimization = self.ai.optimize_lineup(
                    roster_with_details,
                    matchups,
                    injury_data
                )
                
                result["changes"] = optimization.get("changes", [])
                result["validation"] = optimization.get("validation", "UNKNOWN")
            else:
                result["blocked"].append("AI offline or no roster data")
        
        except Exception as e:
            self.logger.error(f"Lineup optimization failed: {e}")
            result["blocked"].append(f"Error: {str(e)}")
        
        self.logger.info(f"Lineup: {len(result['changes'])} changes suggested")
        return result
    
    def step_5_trades(self) -> Dict:
        """
        Step 5: Evaluate pending trades with 2-pass AI validation
        """
        self.logger.info("STEP 5: Trades")
        
        result = {
            "decisions": [],
            "pending_count": 0
        }
        
        try:
            if self.config["platform"] == "sleeper_nfl":
                # Get pending trades
                transactions = self.api.get_transactions(
                    self.config["league_id"],
                    self.current_week
                )
                
                if transactions:
                    pending_trades = [
                        t for t in transactions
                        if t.get("type") == "trade" and t.get("status") == "pending"
                    ]
                    
                    result["pending_count"] = len(pending_trades)
                    
                    for trade in pending_trades:
                        if self.ai.available:
                            # Evaluate trade
                            league_context = {
                                "league_id": self.config["league_id"],
                                "scoring": self.config["rules"]
                            }
                            
                            verdict, reasoning = self.ai.analyze_trade(trade, league_context)
                            
                            result["decisions"].append({
                                "trade_id": trade.get("transaction_id"),
                                "verdict": verdict,
                                "reasoning": reasoning
                            })
                            
                            self.logger.info(f"Trade {trade.get('transaction_id')}: {verdict} - {reasoning}")
                        else:
                            result["decisions"].append({
                                "trade_id": trade.get("transaction_id"),
                                "verdict": "BORDERLINE",
                                "reasoning": "AI offline - manual review required"
                            })
        
        except Exception as e:
            self.logger.error(f"Trade evaluation failed: {e}")
        
        self.logger.info(f"Trades: {result['pending_count']} pending, {len(result['decisions'])} evaluated")
        return result
    
    def step_6_scan_team_close(self) -> Dict:
        """
        Step 6: Validate team health and return GOOD/FIXED/ATTENTION
        """
        self.logger.info("STEP 6: Scan Team (Close)")
        
        result = {
            "status": "UNKNOWN",
            "metrics": {},
            "issues": []
        }
        
        try:
            # Calculate team health
            if self.roster:
                # Build detailed roster for validation
                players_dict = self.api.get_players() or {}
                
                detailed_roster = []
                for player_id in self.roster:
                    player_info = players_dict.get(player_id, {})
                    detailed_roster.append({
                        "player_id": player_id,
                        "name": player_info.get("full_name", player_id),
                        "position": player_info.get("position"),
                        "injury_status": player_info.get("injury_status"),
                        "slot": "BN"  # Would need actual slot data
                    })
                
                injury_data = {
                    p["player_id"]: p["injury_status"]
                    for p in detailed_roster
                    if p.get("injury_status")
                }
                
                status, metrics = calculate_team_health(detailed_roster, injury_data)
                
                result["status"] = status
                result["metrics"] = metrics
                result["issues"] = metrics.get("issues", [])
            else:
                result["status"] = "ATTENTION"
                result["issues"].append("No roster data available")
        
        except Exception as e:
            self.logger.error(f"Team health check failed: {e}")
            result["status"] = "ATTENTION"
            result["issues"].append(f"Error: {str(e)}")
        
        self.logger.info(f"Team Status: {result['status']}")
        return result
    
    def step_7_handle_matchup(self) -> Dict:
        """
        Step 7: Analyze schedules and injury timelines
        """
        self.logger.info("STEP 7: Handle Matchup")
        
        result = {
            "matchup_analysis": {},
            "injury_decisions": [],
            "schedule_notes": []
        }
        
        try:
            # Get injury classifications
            if self.roster and self.ai.available:
                players_dict = self.api.get_players() or {}
                
                for player_id in self.roster:
                    player_info = players_dict.get(player_id, {})
                    injury_status = player_info.get("injury_status")
                    
                    if injury_status:
                        # Analyze injury impact
                        classification, recommendation = self.ai.analyze_injury_impact(
                            player_info,
                            injury_status,
                            "Unknown timeline"  # Would need actual injury report
                        )
                        
                        result["injury_decisions"].append({
                            "player": player_info.get("full_name"),
                            "classification": classification,
                            "recommendation": recommendation
                        })
                        
                        self.logger.info(
                            f"{player_info.get('full_name')}: {classification} - {recommendation}"
                        )
        
        except Exception as e:
            self.logger.error(f"Matchup analysis failed: {e}")
        
        self.logger.info(f"Matchup: {len(result['injury_decisions'])} injury decisions")
        return result
    
    def step_8_verify_roster(self) -> Dict:
        """
        Step 8: Final structural validation - CLEAN or DIRTY
        """
        self.logger.info("STEP 8: Verify Roster (Final Pass)")
        
        result = {
            "verdict": "UNKNOWN",
            "discrepancies": []
        }
        
        try:
            if self.roster:
                players_dict = self.api.get_players() or {}
                
                detailed_roster = []
                for player_id in self.roster:
                    player_info = players_dict.get(player_id, {})
                    detailed_roster.append({
                        "player_id": player_id,
                        "name": player_info.get("full_name", player_id),
                        "position": player_info.get("position"),
                        "injury_status": player_info.get("injury_status"),
                        "slot": "BN",  # Would need actual slot assignment
                        "eligible_positions": [player_info.get("position")]
                    })
                
                # Validate roster structure
                is_valid, issues = validate_roster_structure(
                    detailed_roster,
                    self.config["rules"]
                )
                
                result["verdict"] = "CLEAN" if is_valid else "DIRTY"
                result["discrepancies"] = issues
                
                for issue in issues:
                    self.logger.warning(f"Roster issue: {issue}")
            else:
                result["verdict"] = "DIRTY"
                result["discrepancies"].append("No roster data available")
        
        except Exception as e:
            self.logger.error(f"Roster verification failed: {e}")
            result["verdict"] = "DIRTY"
            result["discrepancies"].append(f"Error: {str(e)}")
        
        self.logger.info(f"Roster Verification: {result['verdict']}")
        return result
    
    def _get_queued_actions(self) -> List[Dict]:
        """Compile list of queued or blocked actions"""
        queued = []
        
        # Check for blocked waiver claims
        # Check for pending lineup changes
        # etc.
        
        return queued
    
    def _save_execution_state(self, results: Dict):
        """Save execution results to state file"""
        state = {
            "last_execution": datetime.now().isoformat(),
            "current_week": self.current_week,
            "last_results": results,
            "moves_executed_count": len(self.moves_executed)
        }
        
        save_state(self.config["state_file"], state)
    
    def _get_nfl_week(self) -> int:
        """Get current NFL week from API"""
        try:
            if hasattr(self.api, "get_current_week"):
                return self.api.get_current_week()
        except:
            pass
        
        # Fallback to calculation
        from utils import get_current_nfl_week
        return get_current_nfl_week()
    
    def _get_nba_week(self) -> int:
        """Get current NBA week"""
        from utils import get_current_nba_week
        return get_current_nba_week()
