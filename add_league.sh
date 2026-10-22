#!/bin/bash

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║        🏈 ADD NEW LEAGUE TO FANTASY MANAGER 🏈                ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Find next available league number
max_num=0
for i in {1..20}; do
    var_name="LEAGUE${i}_ID"
    if [ -z "${!var_name}" ]; then
        max_num=$i
        break
    fi
done

if [ $max_num -eq 0 ]; then
    echo "❌ All 20 league slots full! Edit config.py manually."
    exit 1
fi

echo "📝 Adding League $max_num"
echo ""

# Platform selection
echo "Select platform:"
echo "1) Sleeper NFL"
echo "2) Yahoo NBA"
echo "3) ESPN (coming soon)"
read -p "Choice (1-3): " platform_choice

case $platform_choice in
    1)
        platform="sleeper_nfl"
        ;;
    2)
        platform="yahoo_nba"
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

# Get league details
echo ""
read -p "League ID: " league_id
read -p "Team Name: " team_name

if [ "$platform" == "sleeper_nfl" ]; then
    read -p "Roster ID: " roster_id
    read -p "Trade Deadline Week (e.g., 12): " trade_deadline
    read -p "Waiver Day (e.g., Tuesday): " waiver_day
fi

# Add to .zshrc
echo "" >> ~/.zshrc
echo "# League $max_num ($team_name) - Added $(date)" >> ~/.zshrc
echo "export LEAGUE${max_num}_PLATFORM=\"$platform\"" >> ~/.zshrc
echo "export LEAGUE${max_num}_ID=\"$league_id\"" >> ~/.zshrc
echo "export LEAGUE${max_num}_TEAM_NAME=\"$team_name\"" >> ~/.zshrc

if [ "$platform" == "sleeper_nfl" ]; then
    echo "export LEAGUE${max_num}_ROSTER_ID=\"$roster_id\"" >> ~/.zshrc
    echo "export LEAGUE${max_num}_TRADE_DEADLINE=\"$trade_deadline\"" >> ~/.zshrc
    echo "export LEAGUE${max_num}_WAIVER_DAY=\"$waiver_day\"" >> ~/.zshrc
fi

# Add to config.py
config_file=~/workspace/custom-skills/league-manager/config.py

# Create league entry
cat >> $config_file << EOFCONFIG

    "league${max_num}": {
        "platform": os.environ.get("LEAGUE${max_num}_PLATFORM", "$platform"),
        "league_id": os.environ.get("LEAGUE${max_num}_ID", ""),
        "team_name": os.environ.get("LEAGUE${max_num}_TEAM_NAME", "$team_name"),
EOFCONFIG

if [ "$platform" == "sleeper_nfl" ]; then
    cat >> $config_file << EOFCONFIG
        "roster_id": os.environ.get("LEAGUE${max_num}_ROSTER_ID", "$roster_id"),
        "rules": {
            "waiver_day": os.environ.get("LEAGUE${max_num}_WAIVER_DAY", "$waiver_day"),
            "trade_deadline_week": int(os.environ.get("LEAGUE${max_num}_TRADE_DEADLINE", "$trade_deadline")),
        },
EOFCONFIG
else
    cat >> $config_file << EOFCONFIG
        "rules": {
            "adds_per_week": int(os.environ.get("LEAGUE${max_num}_ADDS_PER_WEEK", "4")),
            "il_slots": int(os.environ.get("LEAGUE${max_num}_IL_SLOTS", "3")),
        },
EOFCONFIG
fi

cat >> $config_file << EOFCONFIG
        "core_file": CORE_DIR / "league${max_num}_core.json",
        "state_file": STATE_DIR / "league${max_num}_state.json",
        "log_file": LOGS_DIR / "league${max_num}.log"
    },
EOFCONFIG

# Create iCloud files
icloud_dir=~/Library/Mobile\ Documents/com~apple~CloudDocs/FantasyLeague

cat > "${icloud_dir}/core/league${max_num}_core.json" << EOFJSON
{
  "protected_players": [],
  "never_drop": [],
  "trade_block": [],
  "last_updated": null,
  "notes": "League ${max_num} ($team_name) - Protected player list"
}
EOFJSON

cat > "${icloud_dir}/state/league${max_num}_state.json" << EOFJSON
{
  "last_execution": null,
  "current_week": 1,
  "last_results": {},
  "moves_executed_count": 0
}
EOFJSON

# Reload
source ~/.zshrc

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║              ✅ LEAGUE $max_num ADDED SUCCESSFULLY! ✅              ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 League Details:"
echo "   - Platform: $platform"
echo "   - League ID: $league_id"
echo "   - Team Name: $team_name"
echo ""
echo "📁 Files Created:"
echo "   - iCloud: FantasyLeague/core/league${max_num}_core.json"
echo "   - iCloud: FantasyLeague/state/league${max_num}_state.json"
echo "   - Config: config.py updated"
echo ""
echo "🚀 Next time you run league_manager.py, it will include this league!"
echo ""
