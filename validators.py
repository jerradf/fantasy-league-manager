"""
Validation Logic for Fantasy Rosters and Lineups
Enforces league rules and roster integrity
"""

import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


def validate_lineup_eligibility(player: Dict, slot: str, injury_status: str, 
                                bye_week: Optional[int], current_week: int) -> Tuple[bool, str]:
    """
    Validate if a player can be placed in an active lineup slot
    
    CRITICAL RULE: Never place injured/bye/zero-projection players in active slots
    
    Returns: (is_valid, reason)
    """
    # Check injury status
    if injury_status and injury_status.upper() in ["OUT", "IR", "DOUBTFUL", "SUSPENDED"]:
        return (False, f"Player is {injury_status}")
    
    # Check bye week
    if bye_week and bye_week == current_week:
        return (False, "Player on bye week")
    
    # Check zero projection (if available)
    projected_points = player.get("projected_points", 0)
    if projected_points == 0 and injury_status:
        return (False, "Zero projection with injury concern")
    
    # Check slot eligibility
    eligible_positions = player.get("eligible_positions", [])
    if slot not in ["FLEX", "BN", "IR"] and slot not in eligible_positions:
        return (False, f"Player not eligible for {slot}")
    
    return (True, "Eligible")


def validate_roster_structure(roster: List[Dict], league_rules: Dict) -> Tuple[bool, List[str]]:
    """
    Verify roster meets league requirements
    
    Returns: (is_valid, list_of_issues)
    """
    issues = []
    
    # Check roster size limits
    total_players = len(roster)
    max_roster = league_rules.get("roster_size", 16)
    
    if total_players > max_roster:
        issues.append(f"Roster exceeds limit: {total_players}/{max_roster}")
    
    # Check position requirements
    position_counts = {}
    for player in roster:
        position = player.get("position", "UNKNOWN")
        position_counts[position] = position_counts.get(position, 0) + 1
    
    # Platform-specific validation
    if league_rules.get("no_te_slot") and league_rules.get("te_flex_only"):
        # NNL rule: TEs can only be in FLEX
        te_in_te_slot = any(
            p.get("position") == "TE" and p.get("slot") == "TE" 
            for p in roster
        )
        if te_in_te_slot:
            issues.append("TE in TE slot (should be FLEX only)")
    
    # Check IL/IR slot usage
    il_slots = league_rules.get("il_slots", 0)
    players_on_il = sum(1 for p in roster if p.get("slot") in ["IR", "IL"])
    
    if players_on_il > il_slots:
        issues.append(f"Too many IL players: {players_on_il}/{il_slots}")
    
    # Verify IL players are actually injured
    for player in roster:
        if player.get("slot") in ["IR", "IL"]:
            injury_status = player.get("injury_status", "")
            if not injury_status or injury_status.upper() not in ["OUT", "IR", "SUSPENDED"]:
                issues.append(f"{player.get('name')} in IL but not injured")
    
    return (len(issues) == 0, issues)


def validate_trade_legality(trade: Dict, league_rules: Dict, current_week: int) -> Tuple[bool, str]:
    """
    Check if trade is legal per league rules
    
    Returns: (is_legal, reason)
    """
    # Check trade deadline
    trade_deadline = league_rules.get("trade_deadline_week")
    if trade_deadline and current_week >= trade_deadline:
        return (False, f"Past trade deadline (Week {trade_deadline})")
    
    # Check roster limits after trade
    # (Simplified - would need full roster data)
    
    # Check for locked players (on bench during games, etc.)
    # Platform-specific logic would go here
    
    return (True, "Trade is legal")


def validate_waiver_claim(add_player: Dict, drop_player: Dict, roster: List[Dict], 
                         league_rules: Dict) -> Tuple[bool, str]:
    """
    Validate waiver add/drop transaction
    
    Returns: (is_valid, reason)
    """
    # Check adds remaining this week
    adds_this_week = league_rules.get("adds_this_week", 0)
    max_adds = league_rules.get("adds_per_week")
    
    if max_adds and adds_this_week >= max_adds:
        return (False, f"Weekly add limit reached ({adds_this_week}/{max_adds})")
    
    # Check if drop player is on roster
    drop_on_roster = any(p.get("player_id") == drop_player.get("player_id") for p in roster)
    if not drop_on_roster:
        return (False, "Drop player not on roster")
    
    # Check if add player is available
    if add_player.get("status") == "rostered":
        return (False, "Player already rostered")
    
    # Check roster limits
    if len(roster) >= league_rules.get("roster_size", 16):
        # Need to drop someone
        if not drop_player:
            return (False, "Roster full, must drop a player")
    
    return (True, "Waiver claim valid")


def calculate_team_health(roster: List[Dict], injury_data: Dict) -> Tuple[str, Dict]:
    """
    Assess overall team health and return status
    
    Returns: (status, health_metrics)
    status: "GOOD" | "FIXED" | "ATTENTION"
    """
    metrics = {
        "total_players": len(roster),
        "injured_players": 0,
        "on_bye": 0,
        "active_slots_filled": 0,
        "bench_depth": 0,
        "issues": []
    }
    
    for player in roster:
        slot = player.get("slot", "BN")
        injury_status = player.get("injury_status", "")
        
        # Count injuries
        if injury_status and injury_status.upper() in ["OUT", "DOUBTFUL", "QUESTIONABLE", "IR"]:
            metrics["injured_players"] += 1
            
            # Check if injured player is in active slot
            if slot not in ["BN", "IR", "IL"]:
                metrics["issues"].append(f"{player.get('name')} injured in active slot")
        
        # Count active slots
        if slot not in ["BN", "IR", "IL"]:
            metrics["active_slots_filled"] += 1
        else:
            metrics["bench_depth"] += 1
    
    # Determine status
    if len(metrics["issues"]) == 0 and metrics["injured_players"] <= 2:
        status = "GOOD"
    elif len(metrics["issues"]) > 0:
        status = "ATTENTION"
    else:
        status = "FIXED"
    
    return (status, metrics)


def verify_roster_clean(roster: List[Dict], expected_structure: Dict) -> Tuple[str, List[str]]:
    """
    Final validation pass against live platform layout
    
    Returns: (verdict, discrepancies)
    verdict: "CLEAN" | "DIRTY"
    """
    discrepancies = []
    
    # Check active lineup slots are filled
    required_slots = expected_structure.get("required_slots", [])
    roster_slots = [p.get("slot") for p in roster]
    
    for req_slot in required_slots:
        if req_slot not in roster_slots:
            discrepancies.append(f"Missing required slot: {req_slot}")
    
    # Check for invalid slot assignments
    for player in roster:
        slot = player.get("slot")
        eligible = player.get("eligible_positions", [])
        
        if slot not in ["BN", "IR", "IL", "FLEX"] and slot not in eligible:
            discrepancies.append(
                f"{player.get('name')} in {slot} but only eligible for {eligible}"
            )
    
    # Check for empty starting slots
    for player in roster:
        slot = player.get("slot")
        if slot not in ["BN", "IR", "IL"]:
            if not player.get("player_id"):
                discrepancies.append(f"Empty starting slot: {slot}")
    
    verdict = "CLEAN" if len(discrepancies) == 0 else "DIRTY"
    
    return (verdict, discrepancies)


def validate_protected_players(drop_candidate: Dict, protected_list: List[str]) -> Tuple[bool, str]:
    """
    Check if player is protected from being dropped
    
    Returns: (is_protected, reason)
    """
    player_id = drop_candidate.get("player_id")
    player_name = drop_candidate.get("name", "")
    
    if player_id in protected_list or player_name in protected_list:
        return (True, "Player is on protected/core list")
    
    return (False, "Not protected")
