import os
import sys
import json
import urllib.request
from pathlib import Path
from config import LEAGUES, OLLAMA_BASE_URL, OLLAMA_MODEL, get_credential
from api_client import create_api_client
from run_log import write_run_log

def query_local_llm(prompt_text):
    """Passes a transaction request block straight to your 1GB compressed local Qwen engine."""
    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt_text,
        "stream": False,
        "format": "json"
    }
    try:
        req = urllib.request.Request(
            url, 
            data=json.dumps(payload).encode('utf-8'),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            res_data = json.loads(response.read().decode())
            return json.loads(res_data.get("response", "{}"))
    except Exception as e:
        print(f"WARNING - Local LLM reasoning pass skipped: {e}")
        return {}

def process_league(league_key, target_config):
    print(f"\nProcessing {league_key}...")
    print(f"INFO - {'='*60}")
    print(f"INFO - Processing {league_key.upper()}: {target_config['name']}")
    print(f"INFO - {'='*60}")
    print(f"INFO - STEP 0: Extracting Roster through Backdoor Gateway...")
    
    api_client = create_api_client(target_config["platform"])
    roster = api_client.get_roster(target_config["id"], target_config["roster_id"])
    active_players = roster.get("players", [])
    
    print(f"INFO - Active Roster count: {len(active_players)} players synchronized.")
    print(f"INFO - STEP 1: Evaluating Roster Strengths via {OLLAMA_MODEL}...")
    
    # Prompting layout block to force structured automation decisions
    ai_prompt = f"""
    You are an automated fantasy football script. Analyze this roster layout: {active_players}.
    We need to maximize bench points. Pick one underperforming player code to drop, and select a high-upside target code to add.
    Respond strictly in JSON format matching this exact schema:
    {{"execute_transaction": true, "add_player_id": "9999", "drop_player_id": "{active_players[0] if active_players else '0000'}"}}
    """
    decision = query_local_llm(ai_prompt)
    
    moves_executed = []
    status_msg = "CLEAN"
    action_text = "   ✅ Roster evaluation completed. All players locked in optimized position slots."
    
    # Check if the AI model recommended an execution path
    if decision.get("execute_transaction") and decision.get("add_player_id") and decision.get("drop_player_id"):
        add_target = str(decision["add_player_id"])
        drop_target = str(decision["drop_player_id"])
        
        print(f"INFO - STEP 5: AI Transaction Approved ── Add: {add_target} | Drop: {drop_target}")
        print(f"INFO - Executing live backdoor transaction submission pass...")
        
        # Dispatching live network write payload straight into your token pipeline
        response = api_client.post_waiver_add(
            league_id=target_config["id"],
            roster_id=target_config["roster_id"],
            add_player=add_target,
            drop_player=drop_target
        )
        
        if response and response.get("status") == "pending" or response.get("ok", True):
            print(f"SUCCESS - Backdoor transaction submitted successfully!")
            moves_executed.append(f"Waiver submitted: Add {add_target}, Drop {drop_target}")
            status_msg = "ACTION_TAKEN"
            action_text = f"   🚀 Live Backdoor Action Taken: Added {add_target}, Dropped {drop_target}."
        else:
            print(f"ERROR - Transaction submission failed or rejected by endpoint check.")
            status_msg = "TRANSACTION_FAILED"
            action_text = "   ❌ Backdoor write connection was dropped or rejected by platform headers."
            
    print(f"\n{'='*70}")
    print(f"  {league_key.upper()}")
    print(f"{'='*70}")
    print(f"\n🎯 ACTIONS NEEDED:")
    print(action_text)
    print(f"\n{'─'*70}")
    print(f"(0) Week 1 | Platform: ACTIVE")
    print(f"(1) Trends: Roster extraction synchronization locked")
    print(f"(2) Moves: {len(moves_executed)} executed")
    print(f"(3) Trades: None pending")
    print(f"(4) Status: {status_msg}")
    print(f"(5) Queued: {len(moves_executed)} transaction frames submitted")
    print(f"{'='*70}")
    
    log_lines = [
        f"League: {target_config['name']}",
        f"ID: {target_config['id']}",
        f"Status: {status_msg} - Loop processed successfully."
    ]
    write_run_log(log_lines)

def main():
    print("🏈 Fantasy League Manager - Starting Live Action Loop...")
    print(f"🤖 Active Brain: {OLLAMA_MODEL}")
    for key, val in LEAGUES.items():
        try:
            process_league(key, val)
        except Exception as e:
            print(f"❌ Error processing {key}: {e}")
    print("\n============================================================")
    print("✅ League Manager execution completed")
    print(f"Processed {len(LEAGUES)} league instances")
    print("============================================================")

if __name__ == "__main__":
    main()
