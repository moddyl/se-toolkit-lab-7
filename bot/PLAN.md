# Bot Development Plan

## Task 1: Scaffolding

- Create bot/ directory structure
- Implement test mode with --test flag
- Basic handlers (/start, /help, /health) returning placeholder text
- Configuration loading from .env.bot.secret
- Dependencies in pyproject.toml

## Task 2: Backend Integration

- Add API client to fetch real data from LMS backend
- Implement /items, /labs commands
- Integrate with actual endpoints

## Task 3: Intent Routing with LLM

- Add LLM client for natural language queries
- Implement intent detection
- Route natural language to appropriate commands

## Task 4: Deployment

- Deploy bot on VM
- Ensure it runs as a background service
- Verify with autochecker
