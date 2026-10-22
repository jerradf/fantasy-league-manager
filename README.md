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

### 🚀 ONE-CLICK SETUP (Automated)

Double-click on Desktop:
```
ONE_CLICK_SETUP.sh
```

This automatically:
1. Downloads AI model (qwen2.5:7b)
2. Opens browser to get your Sleeper cookie
3. Configures everything for write actions
4. Verifies setup

### Manual Setup (If Needed)

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

The system uses environment variables for all league-specific configuration. Add to `~/.zshrc`:

```bash
# Fantasy League Manager Configuration

# API Credentials
export YAHOO_CLIENT_ID="<yahoo_oauth_client_id>"
export YAHOO_CLIENT_SECRET="<yahoo_oauth_secret>"
export YAHOO_REFRESH_TOKEN="<yahoo_oauth_refresh_token>"
export SLEEPER_COOKIE="<sleeper_session_cookie>"

# League Configuration
export LEAGUE1_PLATFORM="yahoo_nba"
export LEAGUE1_ID="<league_identifier>"
export LEAGUE1_TEAM_NAME="<team_name>"
export LEAGUE1_ADDS_PER_WEEK="4"
export LEAGUE1_IL_SLOTS="3"

export LEAGUE2_PLATFORM="sleeper_nfl"
export LEAGUE2_ID="<league_identifier>"
export LEAGUE2_ROSTER_ID="<roster_number>"
export LEAGUE2_TEAM_NAME="<team_name>"
export LEAGUE2_TRADE_DEADLINE="12"

export LEAGUE3_PLATFORM="sleeper_nfl"
export LEAGUE3_ID="<league_identifier>"
export LEAGUE3_ROSTER_ID="<roster_number>"
export LEAGUE3_TEAM_NAME="<team_name>"
export LEAGUE3_INSTANT_TRADES="true"
```

Reload:
```bash
source ~/.zshrc
```

**Note:** The included `RUN_LEAGUE_MANAGER.sh` handles this automatically.

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
