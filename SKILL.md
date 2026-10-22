# Fantasy League Manager Skill

## Overview

The Fantasy League Manager is an autonomous Python-based system that orchestrates three fantasy sports league instances through a deterministic 9-step workflow. It integrates with Sleeper NFL and Yahoo NBA APIs, leveraging local Ollama AI (Qwen 2.5 7B model) for intelligent trade analysis, lineup optimization, and waiver recommendations.

## Privacy-First Architecture Design

### Problem
Fantasy sports management involves:
- Embarrassing league names you don't want recruiters to see
- Personal strategies and protected player lists
- Detailed logs with team names and player decisions
- API credentials and league IDs

### Solution: Three-Layer Separation

**Layer 1: Public Code (GitHub)**
- Generic, reusable fantasy sports framework
- Environment variable based configuration
- Zero hardcoded personal information
- Portfolio and resume safe

**Layer 2: Local Credentials (~/.zshrc)**
- API keys and authentication tokens
- League IDs and roster IDs
- Team names and league names
- Never leaves your machine
- Not backed up to cloud

**Layer 3: Personal Data (iCloud Drive)**
- Detailed execution logs with full context
- Protected player lists and strategies
- State history and execution results
- Automatically backed up and synced
- Accessible across your devices

### Benefits

1. **Career Safe:** Share your GitHub repo without exposing "GoonBoys" league names
2. **Secure:** Credentials never committed or synced to cloud
3. **Convenient:** Personal data backed up via iCloud automatically
4. **Maintainable:** Update strategies in iCloud without touching code
5. **Portable:** Clone repo on any Mac, set env vars, run instantly

### What Goes Where?

```
❌ NEVER in Git:
   - League names (use environment variables)
   - Team names (use environment variables)
   - Player strategies (stored in iCloud)
   - API credentials (in ~/.zshrc)
   - Execution logs (written to iCloud)

✅ Safe for Git:
   - Generic league management code
   - Workflow engine logic
   - API client implementations
   - Validation and utility functions
   - Documentation and README
```

## Architecture

### Data Separation Model

**CRITICAL DESIGN PRINCIPLE:** This system separates public code from private data.

**GitHub Repository (Public):**
- Contains ONLY generic league management framework
- Zero hardcoded league names, team names, or IDs
- Safe to share in portfolios and with recruiters
- No embarrassing league names visible 😉

**iCloud Drive (Private):**
```
~/Library/Mobile Documents/com~apple~CloudDocs/FantasyLeague/
├── logs/           # Detailed execution logs with real team names
├── state/          # Execution history and results
├── core/           # Protected player lists and strategies
└── README.txt      # Personal data documentation
```

**Environment Variables (Local ~/.zshrc):**
- All league IDs, team names, and API credentials
- Never committed to version control
- Loaded at runtime

### Why This Architecture?

1. **Portfolio Safety:** Repository is completely generic - no "GoonBoys" league names visible to recruiters
2. **iCloud Sync:** Personal data backed up and synced across devices automatically
3. **Security:** Credentials and sensitive info never leave your machine
4. **Shareability:** Code is open-source ready without exposing personal strategies

### System Components

**GitHub Repository:**
```
league_manager.py          # Main orchestration script
├── config.py             # Generic league configs (loads from env vars)
├── api_client.py         # Sleeper and Yahoo API integrations
├── ollama_client.py      # Local AI model integration
├── workflow_engine.py    # 9-step execution engine
├── validators.py         # Roster and lineup validation logic
├── utils.py             # Helper functions and utilities
└── setup_icloud.py       # One-time iCloud structure setup
```

**iCloud Drive Structure:**
```
FantasyLeague/
├── logs/
│   ├── league1.log       # Full execution logs with real names
│   ├── league2.log
│   └── league3.log
├── state/
│   ├── league1_state.json    # Last execution results
│   ├── league2_state.json
│   └── league3_state.json
├── core/
│   ├── league1_core.json     # Protected players (your strategy)
│   ├── league2_core.json
│   └── league3_core.json
└── README.txt            # Personal data documentation
```

### Data Flow

```
User Execution (Terminal)
     ↓
Load Environment Variables (~/.zshrc)
     ↓
Main Script (league_manager.py)
     ↓
Load Config from Env Vars
     ↓
Initialize Clients (API + Ollama)
     ↓
For Each League Instance:
     ↓
Load Personal Data from iCloud:
     ├→ Protected Players (core/*.json)
     └→ Previous State (state/*.json)
     ↓
Workflow Engine (9 steps)
     ├→ API Calls (read roster, standings, etc.)
     ├→ AI Analysis (trade eval, lineup opt, waiver)
     ├→ Validators (eligibility, legality checks)
     └→ Write to iCloud:
         ├→ Detailed Logs (logs/*.log)
         └→ State Updates (state/*.json)
     ↓
Format & Output Summary (stdout - generic)
```

**Data Storage Locations:**

| Data Type | Location | Committed to Git? | Contains Personal Info? |
|-----------|----------|-------------------|-------------------------|
| Source Code | GitHub Repo | ✅ Yes | ❌ No |
| League IDs | ~/.zshrc | ❌ Never | ✅ Yes |
| Team Names | ~/.zshrc | ❌ Never | ✅ Yes |
| API Credentials | ~/.zshrc | ❌ Never | ✅ Yes |
| Protected Players | iCloud/core/ | ❌ Never | ✅ Yes |
| Execution Logs | iCloud/logs/ | ❌ Never | ✅ Yes |
| State History | iCloud/state/ | ❌ Never | ✅ Yes |

## League Instances

### 1. GoonBoys (Yahoo NBA)
- **Platform:** Yahoo Fantasy Basketball
- **League ID:** 216278
- **Team Name:** Jerrad's Incredible Team
- **Rules:**
  - 4 adds per week cap
  - 3 IL (Injured List) slots
  - Category scoring
- **Inactive League:** Goonaholics (137495) - DO NOT TOUCH

### 2. NNL (Sleeper NFL)
- **Platform:** Sleeper Fantasy Football
- **League ID:** 1389329423609643008
- **Roster ID:** 8
- **Team Name:** Its Our Year
- **Special Rules:**
  - No dedicated TE slot (TEs must use FLEX)
  - Waivers clear Tuesdays
  - Trade deadline: Week 12 with 1-day review
  - Playoffs: Top 8 of 12 teams

### 3. Fellowship (Sleeper NFL)
- **Platform:** Sleeper Fantasy Football
- **League ID:** 1389389459547500544
- **Roster ID:** 8
- **Team Name:** Roster 8
- **Special Rules:**
  - Waivers clear Tuesdays
  - Trade deadline: Week 11
  - Instant trade execution (no review period)

## The 9-Step Workflow

Each league instance executes these steps sequentially:

### Step 0: Scan Team (Open)
**Purpose:** Initialize execution, verify platform connectivity

**Actions:**
- Output instance identity (league ID, team name, platform)
- Determine current scoring week
- Check API connectivity status
- Log execution start

**Output:** Platform status (ACTIVE/ERROR), current week

---

### Step 1: Checking Trends
**Purpose:** Pull live network data matrices

**Actions:**
- Fetch current roster composition
- Pull league standings and rankings
- Retrieve projected vs actual points
- Identify trending free agents
- Check for pending trade offers

**Output:** Roster size, league rank, points differential

---

### Step 2: Hold Long-Term Players
**Purpose:** Load and protect core players from automated actions

**Actions:**
- Load `{instance}_core.json` file
- Mark protected players (never drop/trade without heavy analysis)
- Validate core roster integrity

**Output:** Protected player count, violation checks

---

### Step 3: Quick Big Points Players
**Purpose:** Identify optimal streaming waiver additions

**Actions:**
- Analyze roster gaps and weaknesses
- Pull trending add candidates
- Route data through Ollama AI for matchup projections
- Validate against weekly add limits
- Generate prioritized waiver suggestions

**Output:** Waiver add/drop recommendations

---

### Step 4: Swap Players
**Purpose:** Optimize starting lineup deterministically

**Critical Rule:** **NEVER place injured, bye week, or zero-projection players in active slots**

**Actions:**
- Pull current lineup configuration
- Fetch injury reports and bye weeks
- Route through AI for lineup optimization
- Apply eligibility gate validation
- Suggest lineup swaps

**Output:** Lineup change recommendations with reasoning

---

### Step 5: Trades
**Purpose:** Evaluate pending trade offers with 2-pass AI validation

**Pass 1 - Mathematical Value:**
- Compare projected points over season
- Analyze consistency metrics
- Evaluate schedule strength
- Calculate positional scarcity impact

**Pass 2 - Sanity Baseline:**
- Check for lopsided trades
- Verify injury risk levels
- Validate roster construction post-trade
- Flag unusual patterns

**Verdicts:**
- **PASS:** Auto-accept (clear mathematical win)
- **FAIL:** Auto-reject (clear mathematical loss)
- **BORDERLINE:** Flag for manual review with 1-sentence synopsis

**Output:** Trade decisions with reasoning

---

### Step 6: Scan Team (Close)
**Purpose:** Validate team health and roster integrity

**Actions:**
- Count injured players
- Verify IL/IR slot usage
- Check roster construction rules
- Calculate bench depth
- Identify lineup violations

**Verdicts:**
- **GOOD:** Healthy roster, no issues
- **FIXED:** Issues found and corrected automatically
- **ATTENTION:** Issues requiring manual intervention

**Output:** Team health status and metrics

---

### Step 7: Handle Matchup
**Purpose:** Analyze schedules and injury timelines

**Injury Classifications:**
- **RETURNING:** Back within 1-2 weeks (stash on roster)
- **EXTENDED:** Out 3+ weeks (move to IR/IL)
- **SEASON_ENDING:** Done for season (drop candidate)

**Actions:**
- Pull weekly matchup data
- Analyze upcoming schedule difficulty
- Route injury data through AI for classification
- Generate stash/drop recommendations

**Output:** Injury decisions, schedule notes

---

### Step 8: Verify Roster (Final Pass)
**Purpose:** Final structural validation against live platform

**Actions:**
- Verify all position slots are filled correctly
- Check for illegal lineup configurations
- Validate against platform-specific rules
- Confirm no duplicate players
- Check roster size limits

**Verdicts:**
- **CLEAN:** Roster passes all validation checks
- **DIRTY:** Discrepancies found (logged with details)

**Output:** Final verdict with specific discrepancies

---

## API Integration

### Sleeper API
- **Base URL:** `https://api.sleeper.app/v1`
- **Authentication:** 
  - Read operations: No auth required
  - Write operations: Cookie-based with mobile User-Agent
- **Rate Limits:** Generous, no explicit limit documented
- **Key Endpoints:**
  - `GET /league/{league_id}` - League info
  - `GET /league/{league_id}/rosters` - All rosters
  - `GET /league/{league_id}/matchups/{week}` - Weekly matchups
  - `GET /players/nfl` - All NFL players (cached 24h)
  - `GET /players/nfl/trending/add` - Trending adds

### Yahoo API
- **Base URL:** `https://fantasysports.yahooapis.com/fantasy/v2`
- **Authentication:** OAuth2 with refresh token flow
- **Credentials Required:**
  - `YAHOO_CLIENT_ID`
  - `YAHOO_CLIENT_SECRET`
  - `YAHOO_REFRESH_TOKEN`
- **Token Refresh:** Automatic before expiry
- **Key Endpoints:**
  - `/league/nba.l.{league_id}/settings` - League settings
  - `/team/nba.l.{league_id}.t.{team_id}/roster` - Team roster
  - `/league/nba.l.{league_id}/standings` - Standings

## Ollama Integration

### Local AI Model
- **Model:** Qwen 2.5 7B (`qwen2.5:7b`)
- **Endpoint:** `http://localhost:11434/api/generate`
- **Timeout:** 120 seconds
- **Temperature:** 0.3 (deterministic)
- **Top P:** 0.9

### AI-Powered Features

1. **Trade Analysis**
   - Two-pass validation (value + sanity)
   - League context integration
   - Returns verdict with reasoning

2. **Waiver Suggestions**
   - Analyzes roster gaps
   - Evaluates matchup projections
   - Prioritizes streaming candidates

3. **Lineup Optimization**
   - Maximizes projected points
   - Enforces eligibility rules
   - Avoids injured/bye players

4. **Injury Classification**
   - Categorizes injury timelines
   - Provides stash/drop recommendations
   - Conservative approach by default

### Graceful Degradation
If Ollama is offline:
- System continues execution
- AI steps return BORDERLINE/manual review flags
- Validation steps still enforce rules
- Logs warnings for offline AI

## Security & Credentials

### Environment Variables Required

```bash
# Yahoo API (for GoonBoys)
export YAHOO_CLIENT_ID="your_client_id"
export YAHOO_CLIENT_SECRET="your_client_secret"
export YAHOO_REFRESH_TOKEN="your_refresh_token"

# Sleeper API (for write operations)
export SLEEPER_COOKIE="your_sleeper_cookie"
```

### Security Protocols
- All credentials pulled from `os.environ`
- Never logged or printed to stdout
- Cookie-based auth for Sleeper writes
- OAuth2 token auto-refresh for Yahoo
- Secure HTTPS for all API calls

### Getting Credentials

**Yahoo OAuth:**
1. Register app at: https://developer.yahoo.com/apps/
2. Get Client ID and Client Secret
3. Complete OAuth flow to get refresh token
4. Set environment variables

**Sleeper Cookie:**
1. Log into Sleeper web app
2. Open browser DevTools → Application → Cookies
3. Copy cookie value
4. Set `SLEEPER_COOKIE` environment variable

## File Structure

### Configuration Files
```
~/workspace/goals/fantasy-football-trade-rebuild/hidden_files/
├── goonboys_core.json          # Protected players
├── goonboys_state.json         # Execution state
├── goonboys.log                # Detailed logs
├── nnl_core.json
├── nnl_state.json
├── nnl.log
├── fellowship_core.json
├── fellowship_state.json
└── fellowship.log
```

### Core JSON Structure
```json
{
  "protected_players": ["player_id_1", "player_id_2"],
  "never_drop": ["star_player_name"],
  "trade_block": ["tradeable_player"],
  "last_updated": "2026-10-21T21:00:00"
}
```

### State JSON Structure
```json
{
  "last_execution": "2026-10-21T21:30:00",
  "current_week": 8,
  "last_results": { /* workflow results */ },
  "moves_executed_count": 3
}
```

## Usage

### Basic Execution
```bash
python3 ~/workspace/custom-skills/league-manager/league_manager.py
```

### Expected Output
```
🏈 Fantasy League Manager - Starting...

Processing goonboys...

=== GOONBOYS ===
(0) Week 3 | Platform: ACTIVE | Yahoo API ready
(1) Trends: Rank: 4/12 | Roster: 13 players
(2) Moves: Added Coby White, Dropped Troy Brown Jr.
(3) Trades: PASS - Accepted Haliburton for Maxey (value +12%)
(4) Status: CLEAN
(5) Queued: None

Processing nnl...

=== NNL ===
(0) Week 8 | Platform: ACTIVE | Roster ID: 8
(1) Trends: Rank: 6/12 | Roster: 16 players
(2) Moves: None executed
(3) Trades: BORDERLINE - Review Kelce for Andrews (flag: positional scarcity)
(4) Status: DIRTY - TE in TE slot (corrected)
(5) Queued: Waiver claim Tuesday for Chuba Hubbard

Processing fellowship...

=== FELLOWSHIP ===
(0) Week 8 | Platform: ACTIVE | Roster ID: 8
(1) Trends: Rank: 3/12 | Roster: 16 players
(2) Moves: Moved CMC to IR, Added Kyren Williams
(3) Trades: FAIL - Rejected Tyreek for Waddle (value -18%)
(4) Status: CLEAN
(5) Queued: Monitor CMC return timeline

============================================================
✅ League Manager execution completed
Processed 3 league instances
============================================================
```

## Installation

### Prerequisites
```bash
# Python 3.9+
python3 --version

# Ollama with Qwen model
brew install ollama
ollama serve
ollama pull qwen2.5:7b
```

### Dependencies
```bash
pip3 install requests python-dotenv pyyaml
```

### Step 1: Set Up iCloud Storage
Run the setup script to create the personal data directory structure:

```bash
cd ~/workspace/custom-skills/league-manager
python3 setup_icloud.py
```

This creates:
- `~/Library/Mobile Documents/com~apple~CloudDocs/FantasyLeague/`
- Subdirectories for logs, state, and core files
- Initial JSON files for 3 league instances

### Step 2: Configure Environment Variables
Copy `.env.example` and add your personal configuration to `~/.zshrc`:

```bash
# API Credentials
export YAHOO_CLIENT_ID="your_client_id"
export YAHOO_CLIENT_SECRET="your_client_secret"
export YAHOO_REFRESH_TOKEN="your_refresh_token"
export SLEEPER_COOKIE="your_sleeper_cookie"

# League 1 Configuration (e.g., Yahoo NBA)
export LEAGUE1_PLATFORM="yahoo_nba"
export LEAGUE1_ID="your_league_id"
export LEAGUE1_TEAM_NAME="Your Team Name"  # SAFE - not in git
export LEAGUE1_ADDS_PER_WEEK="4"
export LEAGUE1_IL_SLOTS="3"

# League 2 Configuration (e.g., Sleeper NFL)
export LEAGUE2_PLATFORM="sleeper_nfl"
export LEAGUE2_ID="your_league_id"
export LEAGUE2_ROSTER_ID="your_roster_id"
export LEAGUE2_TEAM_NAME="Your Team Name"  # SAFE - not in git
export LEAGUE2_NO_TE_SLOT="true"
export LEAGUE2_TRADE_DEADLINE="12"

# League 3 Configuration
export LEAGUE3_PLATFORM="sleeper_nfl"
export LEAGUE3_ID="your_league_id"
export LEAGUE3_ROSTER_ID="your_roster_id"
export LEAGUE3_TEAM_NAME="Your Team Name"  # SAFE - not in git
export LEAGUE3_INSTANT_TRADES="true"
```

Then reload:
```bash
source ~/.zshrc
```

### Step 3: Customize Protected Players (Optional)
Edit the core JSON files in iCloud to add protected players:

```bash
# Open in your favorite editor
open ~/Library/Mobile\ Documents/com~apple~CloudDocs/FantasyLeague/core/league1_core.json
```

Add player IDs or names you never want to drop/trade:
```json
{
  "protected_players": ["player_id_123"],
  "never_drop": ["Christian McCaffrey", "Your Star Player"],
  "trade_block": []
}
```

### Verify Installation
```bash
# Check Ollama
curl http://localhost:11434/api/tags

# Check environment variables
echo $YAHOO_CLIENT_ID
echo $SLEEPER_COOKIE

# Test execution
python3 ~/workspace/custom-skills/league-manager/league_manager.py
```

## Troubleshooting

### Ollama Not Available
**Symptom:** "WARNING: Ollama AI not available"

**Solution:**
```bash
# Start Ollama server
ollama serve

# In another terminal, verify model
ollama list | grep qwen2.5

# If not installed
ollama pull qwen2.5:7b
```

### Yahoo Authentication Failures
**Symptom:** "No valid Yahoo access token"

**Solution:**
1. Check environment variables are set
2. Verify refresh token hasn't expired
3. Re-authenticate via Yahoo Developer Console
4. Update `YAHOO_REFRESH_TOKEN` environment variable

### Sleeper Write Operations Fail
**Symptom:** POST requests return 401/403

**Solution:**
1. Get fresh cookie from Sleeper web app
2. Update `SLEEPER_COOKIE` environment variable
3. Ensure cookie includes all session data
4. Try from same IP as web login

### Missing Roster Data
**Symptom:** "No roster data available"

**Solution:**
1. Verify league IDs are correct
2. Check roster IDs for Sleeper leagues
3. Confirm API connectivity
4. Check detailed logs in `hidden_files/`

### TE in TE Slot (NNL)
**Symptom:** Status shows "DIRTY - TE in TE slot"

**Solution:**
- This is expected validation for NNL league rules
- System should auto-flag for correction
- Manually move TE to FLEX slot via Sleeper app
- Next execution will validate as CLEAN

## Advanced Configuration

### Modifying Protected Players
Edit `~/workspace/goals/fantasy-football-trade-rebuild/hidden_files/{instance}_core.json`:

```json
{
  "protected_players": ["player_id_123", "player_id_456"],
  "never_drop": ["Christian McCaffrey", "Tyreek Hill"],
  "trade_block": ["injury_prone_player"],
  "last_updated": "2026-10-21T21:00:00"
}
```

### Adjusting AI Parameters
Edit `ollama_client.py`:
```python
"options": {
    "temperature": 0.3,  # Lower = more deterministic
    "top_p": 0.9         # Nucleus sampling threshold
}
```

### Adding New League Rules
Edit `config.py` and add to league's `rules` dict:
```python
"rules": {
    "custom_rule": "value",
    # ... existing rules
}
```

Then update validators in `validators.py` to enforce.

## Maintenance

### Log Rotation
Logs grow over time. Rotate manually:
```bash
cd ~/workspace/goals/fantasy-football-trade-rebuild/hidden_files/
mv goonboys.log goonboys.log.$(date +%Y%m%d)
mv nnl.log nnl.log.$(date +%Y%m%d)
mv fellowship.log fellowship.log.$(date +%Y%m%d)
```

### State Reset
To reset execution state:
```bash
rm ~/workspace/goals/fantasy-football-trade-rebuild/hidden_files/*_state.json
```
State files will be recreated on next run.

### Clear Protected Players
```bash
# Edit core files or delete to reset
nano ~/workspace/goals/fantasy-football-trade-rebuild/hidden_files/nnl_core.json
```

## Future Enhancements

Potential additions (not currently implemented):
- Automated waiver claim execution
- Trade proposal generation
- Multi-week projection analysis
- Playoff probability calculations
- Email/SMS notifications for ATTENTION status
- Web dashboard for results visualization
- Historical performance tracking

## License

Personal use only. Not licensed for distribution.

## Support

For issues or questions:
1. Check detailed logs in `hidden_files/`
2. Verify all credentials are set correctly
3. Ensure Ollama is running with correct model
4. Review this documentation for troubleshooting steps
