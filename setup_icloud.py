#!/usr/bin/env python3
"""
iCloud Setup Script
Initializes the personal data directory in iCloud Drive with league-specific files
Run this once to set up your personal configuration
"""

import json
from pathlib import Path
import sys

# iCloud path
ICLOUD_DIR = Path.home() / "Library" / "Mobile Documents" / "com~apple~CloudDocs"
FANTASY_DIR = ICLOUD_DIR / "FantasyLeague"

def setup_icloud_structure():
    """Create the iCloud directory structure for personal data"""
    
    print("🔧 Setting up iCloud Drive structure for Fantasy League Manager...")
    print(f"📁 Location: {FANTASY_DIR}")
    print()
    
    # Create directories
    dirs = {
        "logs": FANTASY_DIR / "logs",
        "state": FANTASY_DIR / "state",
        "core": FANTASY_DIR / "core"
    }
    
    for name, path in dirs.items():
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created {name} directory: {path}")
        else:
            print(f"✓  {name} directory exists: {path}")
    
    print()
    
    # Create initial JSON files for each league
    leagues = ["league1", "league2", "league3"]
    
    for league in leagues:
        core_file = dirs["core"] / f"{league}_core.json"
        state_file = dirs["state"] / f"{league}_state.json"
        
        # Create core file
        if not core_file.exists():
            core_data = {
                "protected_players": [],
                "never_drop": [],
                "trade_block": [],
                "last_updated": None,
                "notes": f"{league} - Protected player list (add player IDs or names here)"
            }
            with open(core_file, 'w') as f:
                json.dump(core_data, f, indent=2)
            print(f"✅ Created {league}_core.json")
        else:
            print(f"✓  {league}_core.json exists")
        
        # Create state file
        if not state_file.exists():
            state_data = {
                "last_execution": None,
                "current_week": 1,
                "last_results": {},
                "moves_executed_count": 0
            }
            with open(state_file, 'w') as f:
                json.dump(state_data, f, indent=2)
            print(f"✅ Created {league}_state.json")
        else:
            print(f"✓  {league}_state.json exists")
    
    print()
    
    # Create README in iCloud
    readme_path = FANTASY_DIR / "README.txt"
    if not readme_path.exists():
        readme_content = """Fantasy League Manager - Personal Data Directory

This directory contains all your personal fantasy league data:

📁 logs/    - Detailed execution logs for each league
📁 state/   - Current state and execution history
📁 core/    - Protected player lists (edit these to prevent drops/trades)

IMPORTANT:
- This data is NOT in the git repository
- Safe to include league names, team names, player strategies
- Synced via iCloud Drive
- Edit *_core.json files to add protected players

Protected Players Format:
{
  "protected_players": ["player_id_123", "player_name"],
  "never_drop": ["Star Player Name"],
  "trade_block": ["Tradeable Player"]
}

Logs will be written here automatically when you run the league manager.
"""
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        print(f"✅ Created README.txt")
    
    print()
    print("="*60)
    print("✅ iCloud setup complete!")
    print()
    print("Next steps:")
    print("1. Set your environment variables in ~/.zshrc (see .env.example)")
    print("2. Edit core files to add protected players:")
    print(f"   - {dirs['core']}/league1_core.json")
    print(f"   - {dirs['core']}/league2_core.json")
    print(f"   - {dirs['core']}/league3_core.json")
    print("3. Run: python3 league_manager.py")
    print("="*60)

if __name__ == "__main__":
    try:
        setup_icloud_structure()
    except Exception as e:
        print(f"❌ Error setting up iCloud structure: {e}")
        sys.exit(1)
