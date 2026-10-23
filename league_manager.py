#!/usr/bin/env python3
import os
import sys
import json
import time
import requests
from datetime import datetime
import config
import api_client

def write_run_log(league_name, log_data):
    """
    Appends execution metrics, agent decisions, and transaction statuses
    to the specific run log designated in the league configuration.
    """
    log_file = config.LEAGUES.get(league_name, {}).get('log_file', 'run_manager.log')
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{league_name}] {json.dumps(log_data)}\n"
    
    try:
        with open(log_file, "a") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"[-] Failed to write to log file {log_file}: {e}", file=sys.stderr)

def query_local_ollama(system_prompt, user_prompt):
    """
    Dispatches the optimization context to the local Ollama instance running Qwen2.5:7b
    using a strict 60-second connection and read timeout.
    """
    url = f"{config.OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": config.OLLAMA_MODEL,
        "prompt": f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{user_prompt}<|im_end|>\n<|im_start|>assistant\n",
        "stream": False,
        "options": {
            "temperature": 0.2
        }
    }
    
    # 60-second timeout enforcement for local reasoning passes
    response = requests.post(url, json=payload, timeout=60)
    response.raise_for_status()
    return response.json().get("response", "").strip()

def run_optimization_cycle():
    print("[*] Initiating Fantasy League Manager Optimization Loop...")
    
    for league_name, league_meta in config.LEAGUES.items():
        print(f"\n[*] Processing Workspace: {league_name}")
        league_id = league_meta.get('id')
        roster_id = league_meta.get('roster_id')
        
        # ==========================================
        # PASS 1: ROSTER DATA EXTRACTION
        # ==========================================
        print(f"[+] Pass 1: Extracting roster data for Roster ID {roster_id}...")
        try:
            # Synchronize real player arrays from the backdoor gateway pipeline
            roster_data = api_client.get_roster(league_id, roster_id)
            if not roster_data or roster_data.get('status') == 'DIRTY':
                raise ValueError("Roster parsing returned incomplete or DIRTY structure.")
                
        except Exception as auth_err:
            print("\n###########################################################################")
            print("BACKDOOR CONNECTION EXCEPTION - SLEEPER SESSION EXPIRED - FRESH TOKEN REQUIRED")
            print("###########################################################################\n")
            write_run_log(league_name, {"status": "CRITICAL", "error": "Token expired or rejected"})
            continue

        players = roster_data.get("players", [])
        starters = roster_data.get("starters", [])
        bench = [p for p in players if p not in starters]
        
        print(f"[+] Successfully sync'd {len(players)} total rostered items ({len(starters)} Starters / {len(bench)} Bench).")

        # ==========================================
        # PASS 2: LOCAL AI REASONING LOOP (QWEN2.5)
        # ==========================================
        print(f"[+] Pass 2: Launching agentic optimization via local {config.OLLAMA_MODEL}...")
        
        system_prompt = (
            "You are an expert high-context fantasy football analyst and manager agent.\n"
            "Your objective is to maximize weekly projected scoring floors, optimize lineups, "
            "recommend logical bench-to-starter swaps, identify high-upside waiver targets, "
            "and propose point-generating trade frameworks based on player data arrays.\n"
            "Provide your final output as a valid JSON object containing specific execution steps "
            "under the keys: 'lineup_swaps', 'waiver_adds', and 'trade_proposals'."
        )
        
        user_prompt = f"League Context: {league_name}\nStarters: {starters}\nBench: {bench}\nOptimize this roster."
        
        try:
            reasoning_output = query_local_ollama(system_prompt, user_prompt)
            print("[+] Reasoning loop completed successfully.")
            
            try:
                decisions = json.loads(reasoning_output)
            except json.JSONDecodeError:
                decisions = {
                    "lineup_swaps": [],
                    "waiver_adds": [],
                    "trade_proposals": [],
                    "raw_reasoning": reasoning_output
                }
                
        except requests.exceptions.Timeout:
            print(f"[-] Local LLM reasoning pass timed out after 60 seconds on {league_name}.")
            write_run_log(league_name, {"status": "TIMEOUT", "error": "LLM threshold exceeded 60s"})
            continue
        except Exception as e:
            print(f"[-] Error during reasoning pass: {e}")
            write_run_log(league_name, {"status": "REASONING_ERROR", "error": str(e)})
            continue

        # ==========================================
        # PASS 3: COMPLETE STRUCTURAL RUN LOGS
        # ==========================================
        print(f"[+] Pass 3: Parsing decisions and writing transaction logs...")
        
        swaps = decisions.get("lineup_swaps", [])
        adds = decisions.get("waiver_adds", [])
        trades = decisions.get("trade_proposals", [])
        
        # Explicitly output every single decision line-by-line in stdout terminal logs
        for swap in swaps:
            print(f"    [SWAP ACTION] -> {swap}")
        for add in adds:
            print(f"    [WAIVER ACTION] -> {add}")
            # Automatically dispatch live write actions through backdoor engine if recommended
            if isinstance(add, dict) and "add_id" in add and "drop_id" in add:
                api_client.post_waiver_add(league_id, roster_id, add["add_id"], add["drop_id"])
        for trade in trades:
            print(f"    [TRADE EVAL] -> {trade}")
            
        write_run_log(league_name, {
            "status": "SUCCESS",
            "swaps_count": len(swaps),
            "adds_count": len(adds),
            "trades_count": len(trades)
        })
        
    print("\n============================================================")
    print("✅ League Manager execution completed")
    print("============================================================")

if __name__ == "__main__":
    run_optimization_cycle()
