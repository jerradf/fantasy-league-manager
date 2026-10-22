# Fantasy League Manager

Autonomous Python-based fantasy sports manager for Mac with local Ollama AI integration.

## Architecture Overview

**Public Repository (GitHub):**
- Generic league management code
- No personal information, team names, or league IDs
- Completely shareable and portfolio-safe

**Private Data (iCloud Drive):**
- All personal league information stored in: `~/Library/Mobile Documents/com~apple~CloudDocs/FantasyLeague/`
- League names, team names, player strategies
- Detailed execution logs
- Protected player lists
- State and execution history

**Security Model:**
- League configurations loaded from environment variables
- All credentials in `~/.zshrc` (never committed)
- Logs and personal data synced via iCloud (never committed)
- Repository contains only generic framework

## Quick Start

### 1. Install Dependencies
```bash
pip3 install requests python-dotenv pyyaml
```

### 2. Install and Start Ollama
```bash
brew install ollama
ollama serve
```

In another terminal:
```bash
ollama pull qwen2.5:7b
```

### 3. Set Environment Variables
Copy `.env.example` and add to `~/.zshrc`:
```bash
# API Credentials
export YAHOO_CLIENT_ID="your_client_id"
export YAHOO_CLIENT_SECRET="your_client_secret"
export YAHOO_REFRESH_TOKEN="your_refresh_token"
export SLEEPER_COOKIE="your_sleeper_cookie"

# League IDs and Team Names
export GOONBOYS_LEAGUE_ID="your_yahoo_league_id"
export GOONBOYS_TEAM_NAME="Your Team Name"
export NNL_LEAGUE_ID="your_sleeper_league_id"
export NNL_ROSTER_ID="your_roster_id"
export NNL_TEAM_NAME="Your Team Name"
export FELLOWSHIP_LEAGUE_ID="your_sleeper_league_id"
export FELLOWSHIP_ROSTER_ID="your_roster_id"
export FELLOWSHIP_TEAM_NAME="Your Team Name"
```

Reload:
```bash
source ~/.zshrc
```

### 4. Run (THE COMMAND THAT ACTUALLY WORKS)

**EASY WAY - Double-click on Desktop:**
```
RUN_LEAGUE_MANAGER.sh
```

**OR Terminal:**
```bash
~/Desktop/RUN_LEAGUE_MANAGER.sh
```

This script loads all environment variables and runs the manager.

### 5. Optional: Model Management
Check and optimize your AI model:
```bash
python3 ~/workspace/custom-skills/league-manager/model_manager.py
```

## What It Does

**FULLY AUTONOMOUS** fantasy league management - zero human intervention required.

Manages three fantasy league instances:
- **League 1** (configurable - e.g., Yahoo NBA)
- **League 2** (configurable - e.g., Sleeper NFL)
- **League 3** (configurable - e.g., Sleeper NFL)

Each instance runs through a 9-step autonomous workflow:
0. Platform connectivity check
1. Pull live roster/standings data
2. Protect core players
3. **Execute optimal waiver moves automatically**
4. **Optimize and set starting lineup automatically**
5. **Evaluate and execute/reject trades automatically** (including counter-offers)
6. Validate team health
7. **Analyze injuries and execute roster moves** (IR, drops, pickups)
8. Final roster verification

## Features

- ✅ **Fully Autonomous** - Set it and forget it
- ✅ **No Human Review** - AI makes all decisions deterministically
- ✅ **Auto-Accept/Reject Trades** - With counter-trade generation
- ✅ **Auto-Execute Waivers** - Optimal streaming based on matchups
- ✅ **Auto-Set Lineups** - Respects injury/bye rules
- ✅ **Auto-Manage Injuries** - IR placement, drops, replacements
- ✅ **Calculated Risk Taking** - Uses mathematical thresholds
- ✅ Local AI analysis (no external data leakage)
- ✅ Protected player management (stars never dropped)
- ✅ Detailed logging per instance

## Output Example

```
=== NNL ===
(0) Week 8 | Platform: ACTIVE | Roster ID: 8
(1) Trends: Rank: 6/12 | Roster: 16 players
(2) Moves: Added Kyren Williams
(3) Trades: PASS - Accepted Kelce for Andrews
(4) Status: CLEAN
(5) Queued: None
```

## Documentation

See [SKILL.md](SKILL.md) for comprehensive documentation including:
- Complete architecture details
- API integration guide
- 9-step workflow specifications
- Security protocols
- Troubleshooting guide

## Requirements

- Python 3.9+
- Ollama with qwen2.5:7b model
- macOS (tested on macOS)
- Internet connection for API calls

## File Structure

```
~/workspace/custom-skills/league-manager/
├── league_manager.py      # Main script
├── config.py             # League configs
├── api_client.py         # API integrations
├── ollama_client.py      # AI client
├── workflow_engine.py    # 9-step engine
├── validators.py         # Validation logic
├── utils.py             # Helpers
├── model_manager.py     # Ollama model tools
├── setup_icloud.py      # iCloud setup
├── SKILL.md             # Full documentation
├── README.md            # This file
├── KIRO_INDEX_PROMPT.md # AI development guide
└── requirements.txt     # Dependencies

~/Library/Mobile Documents/com~apple~CloudDocs/FantasyLeague/
├── logs/                # Execution logs
├── state/               # State history
└── core/                # Protected players
```

## Troubleshooting

**Ollama not available:**
```bash
ollama serve
ollama pull qwen2.5:7b
```

**Missing credentials:**
```bash
echo $YAHOO_CLIENT_ID
echo $SLEEPER_COOKIE
```

**Check logs:**
```bash
tail -f ~/workspace/goals/fantasy-football-trade-rebuild/hidden_files/nnl.log
```

## License

Personal use only.
