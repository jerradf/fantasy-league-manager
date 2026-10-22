"""
Utility Functions for League Manager
File operations, logging, formatting, and helpers
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


def load_core_players(filepath: Path) -> Dict:
    """
    Load protected players from JSON file
    
    Returns dict with keys: protected_players, never_drop, trade_block
    """
    if not filepath.exists():
        # Create default structure
        default_core = {
            "protected_players": [],
            "never_drop": [],
            "trade_block": [],
            "last_updated": None
        }
        save_json(filepath, default_core)
        return default_core
    
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load core players from {filepath}: {e}")
        return {
            "protected_players": [],
            "never_drop": [],
            "trade_block": [],
            "last_updated": None
        }


def save_state(filepath: Path, state_data: Dict):
    """Persist execution state to JSON file"""
    state_data["last_updated"] = datetime.now().isoformat()
    save_json(filepath, state_data)


def save_json(filepath: Path, data: Dict):
    """Save data to JSON file with pretty formatting"""
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logging.error(f"Failed to save JSON to {filepath}: {e}")


def load_json(filepath: Path) -> Optional[Dict]:
    """Load data from JSON file"""
    if not filepath.exists():
        return None
    
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load JSON from {filepath}: {e}")
        return None


def format_summary(instance_name: str, results: Dict) -> str:
    """
    Generate concise stdout summary for single league instance
    
    Format:
    === INSTANCE_NAME ===
    📊 STANDINGS: X/Y (Percentile) - Performance Status
    🎯 ACTIONS NEEDED: Critical issues and recommendations
    (0) Identity & Status
    (1) Trends
    (2) Moves
    (3) Trades
    (4) Status
    (5) Queued
    """
    # Get trends for standing analysis
    trends = results.get("trends", {})
    rank = trends.get("rank", "Unknown")
    performance_alert = trends.get("performance_alert")
    rank_percentile = trends.get("rank_percentile")
    
    # Build header with standings
    lines = [f"\n{'='*70}"]
    lines.append(f"  {instance_name.upper()}")
    lines.append(f"{'='*70}")
    
    # Prominent standings display
    if rank != "Unknown":
        lines.append(f"")
        lines.append(f"📊 LEAGUE STANDING: {rank}")
        if rank_percentile:
            if rank_percentile >= 75:
                lines.append(f"   ⚠️  BOTTOM 25% - URGENT ACTION NEEDED")
            elif rank_percentile >= 50:
                lines.append(f"   📊 Middle of Pack - Can Improve")
            elif rank_percentile >= 25:
                lines.append(f"   ✅ Top Half - Maintain Strategy")
            else:
                lines.append(f"   🏆 TOP 25% - Playoff Bound!")
    
    # Actions needed section
    actions_needed = []
    
    # Check roster issues
    final_validation = results.get("final", {})
    discrepancies = final_validation.get("discrepancies", [])
    if discrepancies:
        for issue in discrepancies[:3]:  # Top 3 issues
            actions_needed.append(f"❌ {issue}")
    
    # Check performance
    if performance_alert:
        if "BOTTOM 25%" in performance_alert:
            actions_needed.append("⚡ More aggressive waiver strategy needed")
            actions_needed.append("⚡ Review protected players - are they performing?")
            actions_needed.append("⚡ Consider trade offers to upgrade roster")
    
    # Check trades
    trades = results.get("trades", {})
    trade_decisions = trades.get("decisions", [])
    if trade_decisions:
        for decision in trade_decisions[:2]:
            verdict = decision.get("verdict", "")
            reasoning = decision.get("reasoning", "")
            if verdict == "BORDERLINE":
                actions_needed.append(f"🤔 Review trade offer: {reasoning}")
    
    # Display actions
    if actions_needed:
        lines.append(f"")
        lines.append(f"🎯 ACTIONS NEEDED:")
        for action in actions_needed[:5]:  # Max 5 actions
            lines.append(f"   {action}")
    else:
        lines.append(f"")
        lines.append(f"✅ NO CRITICAL ACTIONS - Team is optimized")
    
    # Check for deep analysis results
    trends = results.get("trends", {})
    deep_analysis = trends.get("deep_analysis")
    
    if deep_analysis:
        lines.append(f"")
        lines.append(f"🔬 DEEP ANALYSIS RESULTS:")
        lines.append(f"{'─'*70}")
        
        # Drop candidates
        drop_candidates = deep_analysis.get("drop_candidates", [])
        if drop_candidates:
            lines.append(f"")
            lines.append(f"❌ DROP IMMEDIATELY ({len(drop_candidates)} players):")
            for player in drop_candidates[:3]:
                lines.append(f"   • {player['name']} ({player['position']}) - {player['recommended_action']}")
                lines.append(f"     Performance: {player['performance_pct']:.0f}% of position average")
        
        # Underperformers
        underperformers = deep_analysis.get("underperformers", [])
        if underperformers:
            lines.append(f"")
            lines.append(f"⚠️  UNDERPERFORMERS ({len(underperformers)} players):")
            for player in underperformers[:3]:
                lines.append(f"   • {player['name']} ({player['position']}) - {player['recommended_action']}")
        
        # Waiver upgrades
        waiver_upgrades = deep_analysis.get("waiver_upgrades", [])
        if waiver_upgrades:
            lines.append(f"")
            lines.append(f"⬆️  WAIVER UPGRADES AVAILABLE ({len(waiver_upgrades)}):")
            for player in waiver_upgrades[:3]:
                lines.append(f"   • {player['name']} ({player['position']}) - {player['advantage']}")
        
        # Trade targets
        trade_targets = deep_analysis.get("trade_targets", [])
        if trade_targets[:2]:
            lines.append(f"")
            lines.append(f"💼 TOP TRADE TARGETS:")
            for player in trade_targets[:2]:
                lines.append(f"   • {player['name']} ({player['position']}) on {player['owner']}")
        
        # Position analysis
        position_analysis = deep_analysis.get("position_analysis", {})
        if position_analysis:
            lines.append(f"")
            lines.append(f"📊 POSITION STRENGTH:")
            for pos, data in sorted(position_analysis.items()):
                strength = data.get("strength", "")
                count = data.get("count", 0)
                lines.append(f"   • {pos}: {strength} ({count} players)")
        
        lines.append(f"")
        lines.append(f"{'─'*70}")
    
    lines.append(f"")
    lines.append(f"{'─'*70}")
    
    # Original summary details
    identity = results.get("identity", {})
    week = identity.get("current_week", "?")
    platform_status = identity.get("platform_status", "UNKNOWN")
    extra_info = identity.get("extra_info", "")
    
    lines.append(f"(0) Week {week} | Platform: {platform_status} | {extra_info}")
    
    # Trends
    trend_summary = trends.get("summary", "No trend data")
    lines.append(f"(1) Trends: {trend_summary}")
    
    # Moves
    moves = []
    streaming = results.get("streaming", {})
    lineup = results.get("lineup", {})
    
    if streaming.get("moves"):
        for move in streaming["moves"]:
            moves.append(move.get("summary", str(move)))
    
    if lineup.get("changes"):
        for change in lineup["changes"]:
            moves.append(change.get("summary", str(change)))
    
    if moves:
        moves_str = ", ".join(moves)
        lines.append(f"(2) Moves: {moves_str}")
    else:
        lines.append("(2) Moves: None executed")
    
    # Trades
    if trade_decisions:
        first_trade = trade_decisions[0]
        verdict = first_trade.get("verdict", "UNKNOWN")
        reasoning = first_trade.get("reasoning", "")
        trade_summary = f"{verdict} - {reasoning}"
        lines.append(f"(3) Trades: {trade_summary}")
    else:
        lines.append("(3) Trades: None pending")
    
    # Validation status
    verdict = final_validation.get("verdict", "UNKNOWN")
    issues = final_validation.get("discrepancies", [])
    
    if issues:
        first_issue = issues[0]
        lines.append(f"(4) Status: {verdict} - {first_issue}")
    else:
        lines.append(f"(4) Status: {verdict}")
    
    # Queued actions
    queued = results.get("queued", [])
    if queued:
        queued_summary = queued[0].get("summary", "Tasks queued")
        lines.append(f"(5) Queued: {queued_summary}")
    else:
        lines.append("(5) Queued: None")
    
    lines.append(f"{'='*70}")
    
    return "\n".join(lines)


def setup_logging(instance_name: str, log_file: Path, level=logging.INFO):
    """
    Configure logging for a league instance
    
    Returns logger instance
    """
    logger = logging.getLogger(f"league_manager.{instance_name}")
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # File handler - detailed logs
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    fh.setFormatter(file_formatter)
    logger.addHandler(fh)
    
    # Console handler - warnings and errors only
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    ch.setFormatter(console_formatter)
    logger.addHandler(ch)
    
    return logger


def get_current_nfl_week() -> int:
    """
    Calculate current NFL week based on date
    
    NFL season starts first Thursday of September
    This is a simplified calculation
    """
    now = datetime.now()
    year = now.year
    
    # Approximate NFL season start (first Thursday of September)
    # Week 1 typically starts around Sept 7-10
    season_start = datetime(year, 9, 7)
    
    if now < season_start:
        # Pre-season or previous season
        return 1
    
    # Calculate weeks since season start
    delta = now - season_start
    week = (delta.days // 7) + 1
    
    # Cap at week 18
    return min(week, 18)


def get_current_nba_week() -> int:
    """
    Calculate current NBA week based on date
    
    NBA season starts mid-October
    """
    now = datetime.now()
    year = now.year
    
    # NBA season typically starts around Oct 15
    if now.month < 10:
        # Off-season - use previous season
        year -= 1
    
    season_start = datetime(year, 10, 15)
    
    if now < season_start:
        # Pre-season
        return 1
    
    # Calculate weeks since season start
    delta = now - season_start
    week = (delta.days // 7) + 1
    
    # NBA regular season is ~26 weeks
    return min(week, 26)


def safe_get(dictionary: Dict, *keys, default=None):
    """
    Safely get nested dictionary value
    
    Example: safe_get(data, "player", "stats", "points", default=0)
    """
    result = dictionary
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key)
            if result is None:
                return default
        else:
            return default
    return result if result is not None else default


def truncate_string(text: str, max_length: int = 50) -> str:
    """Truncate string with ellipsis if too long"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def format_player_name(player: Dict) -> str:
    """Format player name consistently"""
    name = player.get("name", player.get("full_name", "Unknown"))
    position = player.get("position", "")
    
    if position:
        return f"{name} ({position})"
    return name


def calculate_adds_remaining(league_rules: Dict, transactions_this_week: List[Dict]) -> int:
    """Calculate how many adds are remaining this week"""
    max_adds = league_rules.get("adds_per_week")
    
    if max_adds is None:
        return 999  # Unlimited
    
    # Count add transactions this week
    adds_count = sum(1 for t in transactions_this_week if t.get("type") == "waiver" or t.get("type") == "free_agent")
    
    return max(0, max_adds - adds_count)
