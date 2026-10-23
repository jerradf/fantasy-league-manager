#!/Users/jrdmf/opt/anaconda3/bin/python3
"""
Fantasy League Manager
Orchestrates three fantasy league instances with deterministic 9-step workflow
Execute: python3 ~/workspace/custom-skills/league-manager/league_manager.py
"""

import sys
import os
import json
import logging
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import LEAGUES, OLLAMA_BASE_URL, OLLAMA_MODEL, get_credential
from api_client import SleeperClient, YahooClient, create_api_client
from ollama_client import OllamaClient
from workflow_engine import WorkflowEngine
from utils import format_summary, setup_logging
from run_log import write_run_log, commit_and_push_log


# Configure root logger
logging.basicConfig(
    level=logging.WARNING,
    format='%(levelname)s - %(message)s'
)


def initialize_clients():
    """Initialize API and AI clients"""
    
    # Initialize Ollama client
    ollama = OllamaClient(
        base_url=OLLAMA_BASE_URL,
        model=OLLAMA_MODEL
    )
    
    if not ollama.available:
        print("⚠️  WARNING: Ollama AI not available - running in limited mode")
        print(f"   Make sure Ollama is running: ollama serve")
        print(f"   And model is installed: ollama pull {OLLAMA_MODEL}")
        print()
    
    return ollama


def process_league(instance_name: str, league_config: dict, ollama: OllamaClient) -> dict:
    """
    Process a single league instance through the 9-step workflow
    
    Returns: workflow results dict
    """
    # Read actual league name from iCloud core file (NEVER from code!)
    league_display_name = instance_name
    try:
        core_data = json.load(open(league_config["core_file"]))
        league_display_name = core_data.get("league_display_name", league_config["team_name"])
    except:
        league_display_name = league_config["team_name"]
    
    # Setup instance-specific logging
    logger = setup_logging(
        instance_name,
        league_config["log_file"]
    )
    
    logger.info(f"="*60)
    logger.info(f"Processing {instance_name.upper()}: {league_display_name}")
    logger.info(f"="*60)
    
    try:
        # Create API client for platform
        api_client = create_api_client(
            league_config["platform"],
            league_config
        )
        
        # Create workflow engine
        workflow = WorkflowEngine(
            league_config=league_config,
            api_client=api_client,
            ollama_client=ollama,
            logger=logger
        )
        
        # Execute 9-step workflow
        results = workflow.execute()
        
        return results
    
    except Exception as e:
        logger.error(f"Failed to process {instance_name}: {e}", exc_info=True)
        return {
            "error": str(e),
            "identity": {
                "league_id": league_config["league_id"],
                "team_name": league_config["team_name"],
                "platform_status": "ERROR"
            }
        }


def main():
    """
    Main execution entry point
    Processes all three league instances and outputs summary
    """
    print("🏈 Fantasy League Manager - Starting...")
    print(f"🤖 AI Model: {OLLAMA_MODEL}")
    print()
    
    # Initialize shared clients
    ollama = initialize_clients()
    
    if not ollama.available:
        print("💡 TIP: Want to try a different model? Run: python3 model_manager.py")
        print()
    
    # Process each league instance
    all_results = {}
    run_log_lines = []
    
    for instance_name, league_config in LEAGUES.items():
        print(f"Processing {instance_name}...")
        
        try:
            results = process_league(instance_name, league_config, ollama)
            all_results[instance_name] = results
            
            # Output summary for this instance
            summary = format_summary(instance_name, results)
            print(summary)
            print()
            run_log_lines.append(summary)
            run_log_lines.append('```json')
            run_log_lines.append(json.dumps(results, indent=2, default=str))
            run_log_lines.append('```')
        
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted by user")
            sys.exit(1)
        
        except Exception as e:
            print(f"❌ Error processing {instance_name}: {e}")
            print()
    
    # Final summary
    print("="*60)
    print("✅ League Manager execution completed")
    print(f"Processed {len(all_results)} league instances")
    print("="*60)
    
    try:
        log_path = write_run_log(run_log_lines)
        print(f'Run log written: {log_path}')
        commit_and_push_log(log_path)
    except Exception as e:
        print(f'Run log failed: {e}')

    # Return appropriate exit code
    errors = sum(1 for r in all_results.values() if "error" in r)
    if errors > 0:
        print(f"⚠️  {errors} instances had errors - check logs for details")
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        logging.error("Fatal error", exc_info=True)
        sys.exit(1)
