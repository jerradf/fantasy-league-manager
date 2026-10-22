"""
Ollama Local LLM Client
Handles all AI-driven analysis using local Qwen model
"""

import requests
import json
import logging
from typing import Dict, List, Tuple, Any

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for local Ollama AI model integration"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "qwen2.5:7b", timeout: int = 120):
        self.base_url = base_url
        self.model = model
        self.timeout = timeout
        self.available = self._check_availability()
    
    def _check_availability(self) -> bool:
        """Check if Ollama is running and model is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                if self.model in model_names or self.model.replace(":", "_") in str(model_names):
                    logger.info(f"Ollama available with model {self.model}")
                    return True
                else:
                    logger.warning(f"Ollama running but {self.model} not found. Available: {model_names}")
                    return False
            return False
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
            return False
    
    def _generate(self, prompt: str, system_prompt: str = None) -> str:
        """Send prompt to Ollama and get response"""
        if not self.available:
            logger.warning("Ollama not available, skipping AI analysis")
            return None
        
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9
                }
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                logger.error(f"Ollama generation failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            return None
    
    def analyze_trade(self, trade_data: Dict, league_context: Dict) -> Tuple[str, str]:
        """
        Two-pass trade validation system
        Pass 1: Mathematical value projection against league
        Pass 2: Sanity baseline check
        
        Returns: (verdict, reasoning)
        verdict: "PASS" | "FAIL" | "BORDERLINE"
        """
        if not self.available:
            return ("BORDERLINE", "AI offline - manual review required")
        
        system_prompt = """You are a fantasy sports trade analyzer. Evaluate trades using:
1. Mathematical value: Compare projected points, consistency, schedule strength
2. Sanity check: Avoid lopsided trades, positional scarcity issues, injury risks

Return verdict as: PASS (clear win), FAIL (clear loss), or BORDERLINE (needs review)
Keep reasoning to 1-2 sentences."""
        
        prompt = f"""Analyze this fantasy sports trade:

TRADE OFFER:
{json.dumps(trade_data, indent=2)}

LEAGUE CONTEXT:
{json.dumps(league_context, indent=2)}

Evaluate both value projection and sanity. Return format:
VERDICT: [PASS/FAIL/BORDERLINE]
REASONING: [1-2 sentence explanation]"""
        
        response = self._generate(prompt, system_prompt)
        
        if not response:
            return ("BORDERLINE", "AI analysis failed - manual review required")
        
        # Parse response
        verdict = "BORDERLINE"
        reasoning = response
        
        if "VERDICT:" in response:
            lines = response.split("\n")
            for line in lines:
                if line.startswith("VERDICT:"):
                    verdict_text = line.replace("VERDICT:", "").strip().upper()
                    if "PASS" in verdict_text:
                        verdict = "PASS"
                    elif "FAIL" in verdict_text:
                        verdict = "FAIL"
                    else:
                        verdict = "BORDERLINE"
                elif line.startswith("REASONING:"):
                    reasoning = line.replace("REASONING:", "").strip()
        
        return (verdict, reasoning)
    
    def suggest_waiver_adds(self, roster: List[Dict], available_players: List[Dict], 
                           scoring_rules: Dict, current_week: int) -> List[Dict]:
        """
        Analyze roster gaps and identify high-projection streaming candidates
        Returns prioritized list of add/drop recommendations
        """
        if not self.available:
            logger.warning("Ollama offline - skipping waiver analysis")
            return []
        
        system_prompt = """You are a fantasy sports waiver wire expert. Identify optimal streaming adds based on:
1. Roster gaps and weaknesses
2. Upcoming matchups and projections
3. Injury replacements needed
4. Schedule advantages

Return top 3 add/drop suggestions with brief reasoning."""
        
        prompt = f"""Analyze waiver wire opportunities:

CURRENT ROSTER:
{json.dumps(roster[:10], indent=2)}

TOP AVAILABLE PLAYERS:
{json.dumps(available_players[:20], indent=2)}

SCORING RULES:
{json.dumps(scoring_rules, indent=2)}

CURRENT WEEK: {current_week}

Suggest top 3 streaming adds with who to drop. Format:
1. ADD [player] / DROP [player] - [reason]"""
        
        response = self._generate(prompt, system_prompt)
        
        # Parse suggestions (simple extraction)
        suggestions = []
        if response:
            lines = response.split("\n")
            for line in lines:
                if "ADD" in line and "DROP" in line:
                    suggestions.append({"raw": line.strip()})
        
        return suggestions
    
    def optimize_lineup(self, roster: List[Dict], matchups: Dict, injury_data: Dict) -> Dict:
        """
        Deterministic lineup optimization
        Enforces: Never place injured/bye/zero-projection players in active slots
        """
        if not self.available:
            logger.warning("Ollama offline - skipping lineup optimization")
            return {"changes": [], "validation": "AI_OFFLINE"}
        
        system_prompt = """You are a fantasy lineup optimizer. Set optimal starting lineups based on:
1. Projected points for the week
2. Matchup quality
3. Player health status
4. Bye weeks

CRITICAL RULE: Never place injured, bye week, or zero-projection players in active slots.
Only suggest lineup changes if they improve projected points."""
        
        prompt = f"""Optimize starting lineup:

ROSTER:
{json.dumps(roster, indent=2)}

MATCHUPS:
{json.dumps(matchups, indent=2)}

INJURY DATA:
{json.dumps(injury_data, indent=2)}

Suggest lineup changes. Format each as:
MOVE: [Player] from [BENCH] to [ACTIVE_SLOT]
REASON: [brief explanation]"""
        
        response = self._generate(prompt, system_prompt)
        
        changes = []
        if response:
            lines = response.split("\n")
            for i, line in enumerate(lines):
                if line.startswith("MOVE:"):
                    reason = ""
                    if i + 1 < len(lines) and lines[i + 1].startswith("REASON:"):
                        reason = lines[i + 1].replace("REASON:", "").strip()
                    changes.append({
                        "move": line.replace("MOVE:", "").strip(),
                        "reason": reason
                    })
        
        return {
            "changes": changes,
            "validation": "PASS" if changes else "NO_CHANGES"
        }
    
    def analyze_injury_impact(self, player: Dict, injury_status: str, timeline: str) -> Tuple[str, str]:
        """
        Classify injury impact for roster decisions
        Returns: (classification, recommendation)
        classification: "RETURNING" | "EXTENDED" | "SEASON_ENDING"
        """
        if not self.available:
            return ("EXTENDED", "AI offline - assume extended absence")
        
        system_prompt = """You are a fantasy sports injury analyst. Classify injuries as:
- RETURNING: Player back within 1-2 weeks (stash on roster)
- EXTENDED: Player out 3+ weeks (move to IR/IL)
- SEASON_ENDING: Player done for season (drop)

Be conservative with classifications."""
        
        prompt = f"""Analyze player injury:

PLAYER: {player.get('name', 'Unknown')}
POSITION: {player.get('position', 'Unknown')}
INJURY: {injury_status}
TIMELINE: {timeline}

Classify as RETURNING, EXTENDED, or SEASON_ENDING with brief reasoning.
Format:
CLASSIFICATION: [type]
RECOMMENDATION: [1 sentence]"""
        
        response = self._generate(prompt, system_prompt)
        
        classification = "EXTENDED"  # Default to conservative
        recommendation = response if response else "Unable to analyze - monitor closely"
        
        if response:
            if "CLASSIFICATION:" in response:
                lines = response.split("\n")
                for line in lines:
                    if line.startswith("CLASSIFICATION:"):
                        class_text = line.replace("CLASSIFICATION:", "").strip().upper()
                        if "RETURNING" in class_text:
                            classification = "RETURNING"
                        elif "SEASON" in class_text or "ENDING" in class_text:
                            classification = "SEASON_ENDING"
                        else:
                            classification = "EXTENDED"
                    elif line.startswith("RECOMMENDATION:"):
                        recommendation = line.replace("RECOMMENDATION:", "").strip()
        
        return (classification, recommendation)
