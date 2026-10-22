# Contributing Guidelines

## 🔒 CRITICAL: Privacy Guardrails

This repository is **portfolio-safe** and must remain free of personal information.

### NEVER COMMIT TO PYTHON FILES:

❌ Actual league names in `.py` files
❌ Team names in `.py` files  
❌ League IDs hardcoded in `.py` files
❌ API credentials in any files
❌ Player names from your actual rosters in code

### DOCUMENTATION CAN REFERENCE (for examples):

✅ League name examples in `.md` documentation
✅ Example league names in `CONTRIBUTING.md`
✅ References in comments explaining the system

### ALWAYS USE:

✅ Generic placeholders: `<league_identifier>`, `<team_name>`, `<roster_number>`
✅ Read league names from iCloud: `core_data.get("league_display_name")`
✅ Environment variable references: `LEAGUE1_ID`, `LEAGUE2_TEAM_NAME`
✅ Documentation examples: "League 1", "League 2", "League 3"

## 📁 Where Personal Data Belongs:

**iCloud Drive ONLY:**
- `~/Library/Mobile Documents/com~apple~CloudDocs/FantasyLeague/core/*.json`
  - Contains: `league_display_name`, protected players, notes
- `~/Library/Mobile Documents/com~apple~CloudDocs/FantasyLeague/logs/*.log`
  - Contains: Execution logs with real names
- `~/Library/Mobile Documents/com~apple~CloudDocs/FantasyLeague/state/*.json`
  - Contains: Execution history

**Environment Variables (~/.zshrc):**
- League IDs
- Team names
- API credentials
- Platform configurations

**RUN Scripts (Local only):**
- `RUN_LEAGUE_MANAGER.sh` on Desktop
- Any local wrapper scripts

## 🛡️ Pre-Commit Hook

A pre-commit hook is installed to block commits containing personal data patterns.

**Blocked patterns:**
- League names (GoonBoys, NNL, Fellowship, etc.)
- Team names
- Specific player references from your rosters

**If blocked:**
1. Remove the personal reference
2. Use generic placeholder or iCloud reference
3. Commit again

## 💻 Code Changes

### Before Submitting Changes:

1. **Test locally** with your actual data (in iCloud/env vars)
2. **Verify privacy** - no personal data in code
3. **Check placeholders** - use angle bracket format `<value>`
4. **Run pre-commit** - it will catch leaks
5. **Review diff** - manually scan for personal info

### Making League-Specific Decisions:

❌ **WRONG:**
```python
if league_name == "GoonBoys":
    # Special logic for my league
```

✅ **RIGHT:**
```python
core_data = load_core_players(config["core_file"])
league_name = core_data.get("league_display_name", "")
if core_data.get("custom_rule_enabled"):
    # Special logic based on iCloud config
```

## 🔄 Adding Features

### Workflow for New Features:

1. **Design** - Plan the feature generically
2. **Implement** - Use configurable parameters
3. **Test** - With your real leagues (iCloud data)
4. **Document** - With generic examples only
5. **Commit** - Pre-commit hook validates privacy

### Feature Suggestions:

Before implementing trade/waiver logic, ask:
- "Should this auto-execute or just suggest?"
- "Does this need league-specific configuration?"
- "Will this work for all platforms (Sleeper/Yahoo/ESPN)?"

**The system should tell you when your leagues need attention, not make assumptions about what's best.**

## 📊 Performance Guardrails

When league ranks are poor (bottom 25% of league):
- System logs: "⚠️  League performance below average"
- Suggests: More aggressive waiver strategy
- Asks: "Review protected players - are they actually performing?"

The AI should challenge decisions, not blindly execute.

## ✅ Checklist Before Commit:

- [ ] No league names in code
- [ ] No team names in code
- [ ] No league IDs in code (use env vars)
- [ ] Placeholders use `<angle_brackets>`
- [ ] League names read from iCloud when needed
- [ ] Pre-commit hook passes
- [ ] Changes work with generic configuration
- [ ] Documentation uses professional examples

## 🚫 Auto-Reject Commits Containing:

- Specific league names from your actual leagues
- Team names from your actual teams
- League IDs hardcoded in Python files
- API credentials in any form
- Player names from your actual rosters (in docs/examples)

## ✨ Good Commit Examples:

✅ "Add trade counter-offer generation"
✅ "Implement injury timeline analysis"
✅ "Update waiver priority algorithm"
✅ "Fix roster validation for custom rules"

## ❌ Bad Commit Examples:

❌ "Fix GoonBoys IL slot issue"
❌ "Update NNL trade logic"
❌ "Add protection for CMC and Tyreek"
❌ "League 216278 roster fixes"

---

**Remember:** This repo is safe for recruiters to see. Keep it that way.
