# Kiro AI Agent Indexing Prompt

Use this prompt in Kiro to index the entire Fantasy League Manager codebase for future development work.

## Indexing Command

Run this in your Kiro chat:

```
Please index the entire Fantasy League Manager project for future development work.

Project location: ~/workspace/custom-skills/league-manager/

This is a Python-based autonomous fantasy sports manager with the following architecture:

**Core Components:**
- league_manager.py: Main orchestration script
- workflow_engine.py: 9-step execution loop for each league
- api_client.py: Sleeper NFL and Yahoo NBA API integrations
- ollama_client.py: Local AI model integration (Qwen 2.5 7B)
- validators.py: Roster and lineup validation logic
- utils.py: Helper functions and utilities
- config.py: Environment-based configuration
- model_manager.py: Ollama model management and benchmarking
- setup_icloud.py: iCloud Drive personal data setup

**Key Features:**
1. **FULLY AUTONOMOUS OPERATION:** Zero human intervention - all decisions made by AI
2. Privacy-first design: All personal data (league names, logs, strategies) stored in iCloud Drive
3. Generic codebase safe for GitHub portfolios (no hardcoded personal info)
4. Three configurable league instances loaded from environment variables
5. 9-step deterministic workflow with auto-execution per league
6. Local AI-powered trade analysis with auto-accept/reject and counter-offer generation
7. Automatic waiver execution based on optimal streaming strategy
8. Automatic lineup optimization and injury management
9. Protected player management
10. Comprehensive validation and calculated risk-taking logic

**Architecture Highlights:**
- Environment variable configuration (~/.zshrc)
- iCloud Drive storage: ~/Library/Mobile Documents/com~apple~CloudDocs/FantasyLeague/
- Logs, state, and core player files in iCloud (not Git)
- Ollama integration for local AI without external API calls

**Technologies:**
- Python 3.9+
- Ollama (local LLM)
- Sleeper API (fantasy football)
- Yahoo Fantasy API (fantasy basketball)
- iCloud Drive for personal data storage

Index this entire codebase including:
- All Python modules and their relationships
- Configuration patterns and environment variable usage
- API integration patterns
- Workflow engine logic
- Validation rules
- iCloud Drive integration
- Documentation (SKILL.md, README.md)

This will enable me to ask you to make changes, add features, debug issues, and extend functionality in future sessions.
```

## Example Future Development Prompts

Once indexed, you can ask Kiro:

### Add New Feature
```
Add pre-emptive trade generation - system should scan league rosters weekly and 
auto-generate profitable trade offers to send to other teams based on their needs.
```

### Debug Issue
```
The auto-waiver execution is not working on Sleeper. Check the cookie authentication 
in api_client.py and fix the POST request headers.
```

### Extend Platform Support
```
Add support for ESPN Fantasy Football. Create a new ESPN API client following the 
same pattern as Sleeper and Yahoo clients, with auto-execution capabilities.
```

### Optimize Performance
```
The trade evaluation AI is slow. Optimize the Ollama prompts and consider 
using a faster model for real-time decision making.
```

### Add Advanced Logic
```
Create a multi-week lookahead for waiver streaming - system should plan pickups 
2-3 weeks in advance based on playoff schedules and matchup data.
```

## Benefits of Indexing

✅ Kiro understands the entire codebase structure
✅ Can make changes across multiple files coherently
✅ Respects the privacy-first architecture
✅ Maintains coding patterns and conventions
✅ Suggests improvements based on full context
✅ Debug with complete understanding of data flow

## Updating the Index

After major changes, re-index:
```
Update the Fantasy League Manager knowledge base at ~/workspace/custom-skills/league-manager/
```

## Notes

- Personal data (league names, IDs) in environment variables and iCloud
- Never index the iCloud directory itself (contains sensitive info)
- Focus on code structure, patterns, and public documentation
- API credentials are in ~/.zshrc (never indexed)
