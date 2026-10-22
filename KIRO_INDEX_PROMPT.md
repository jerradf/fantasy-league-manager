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
1. Privacy-first design: All personal data (league names, logs, strategies) stored in iCloud Drive
2. Generic codebase safe for GitHub portfolios (no hardcoded personal info)
3. Three configurable league instances loaded from environment variables
4. 9-step deterministic workflow per league execution
5. Local AI-powered trade analysis, lineup optimization, waiver recommendations
6. Protected player management
7. Comprehensive validation and safety checks

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
Add a feature to automatically propose trades based on roster needs and available players. 
Update the workflow engine to include this in step 5, and create a new trade_proposer.py module.
```

### Debug Issue
```
The Yahoo API authentication is failing. Check the api_client.py Yahoo OAuth flow and 
fix any token refresh issues.
```

### Extend Platform Support
```
Add support for ESPN Fantasy Football. Create a new ESPN API client following the 
same pattern as Sleeper and Yahoo clients.
```

### Optimize Performance
```
The workflow is taking too long. Profile the code and optimize the API calls and 
AI inference. Consider caching strategies.
```

### Add Testing
```
Create comprehensive unit tests for the validators.py module. Cover all validation 
functions with edge cases.
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
