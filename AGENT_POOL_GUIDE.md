# TradingAgents - Agent Pool System

## Overview

The Agent Pool system provides a modular way to initialize and manage TradingAgents. Select exactly which agents you need, create custom workflows, and easily add/remove agents.

## Quick Start

### Initialize All Agents

```bash
python examples/initialize_all_agents.py
```

This will create one instance of each available agent type.

### Interactive Agent Selector

```bash
python examples/agent_selector_interface.py
```

Interactive menu to:
- Browse all available agents
- Add/remove agents from active pool
- Quick setup configurations
- Export/import configurations

## Available Agent Types

### Analysts (Data Collection)
- **market** - Technical indicators and trends
- **fundamentals** - Financial statements analysis
- **news** - News and current events
- **social** - Social media sentiment

### Researchers (Debate)
- **bull** - Builds bullish investment cases
- **bear** - Builds bearish counter-arguments

### Managers (Decision Making)
- **research** - Makes final investment decisions
- **risk** - Final risk assessment

### Risk Analysts (Risk Debate)
- **risky** - Argues for aggressive positioning
- **safe** - Argues for conservative approach
- **neutral** - Balanced perspective

### Trader
- **trader** - Creates executable trade plans

## Using Agent Pool in Code

### Example 1: Initialize Specific Agents

```python
from tradingagents.agent_pool import AgentPool
from tradingagents.config import DEFAULT_CONFIG

pool = AgentPool(DEFAULT_CONFIG)

# Add only the agents you need
pool.add_agent("analysts", "market")
pool.add_agent("analysts", "fundamentals")
pool.add_agent("researchers", "bull")
pool.add_agent("researchers", "bear")
pool.add_agent("managers", "research")

# Get active agents
active = pool.get_active_agents()
print(f"Active agents: {len(active)}")
```

### Example 2: Browse Available Agents

```python
from tradingagents.agent_pool import AgentRegistry

# Get all agents
all_agents = AgentRegistry.list_all_agents()

for agent in all_agents:
    print(f"{agent['category']} / {agent['id']}: {agent['name']}")
    print(f"  {agent['description']}")
```

### Example 3: Get Specific Agent

```python
pool = AgentPool(DEFAULT_CONFIG)

pool.add_agent("analysts", "market")

# Get the agent instance
market_analyst = pool.get_agent("analysts", "market")

# Use it
state = {"messages": [], "company_of_interest": "AAPL"}
result = market_analyst(state)
```

### Example 4: Custom Configuration

```python
custom_config = {
    "llm_provider": "google",
    "quick_think_llm": "gemini-2.0-flash-exp",
    "deep_think_llm": "gemini-1.5-pro",
    "max_debate_rounds": 3
}

pool = AgentPool(custom_config)
```

## Quick Setup Configurations

The interface provides pre-configured setups:

### 1. Full Analysis
All agents for comprehensive analysis:
- All 4 analysts
- Bull & bear researchers
- Research manager
- Trader
- All 3 risk analysts
- Risk manager

### 2. Basic Analysis
Quick analysis:
- Market analyst
- Fundamentals analyst

### 3. Research Debate
Focus on debate:
- Market analyst
- Fundamentals analyst
- Bull researcher
- Bear researcher
- Research manager

## Export/Import Configurations

### Export Current Setup

```python
# In interface
> export
Export filename: my_config.json

# Creates:
{
  "agents": [
    {"category": "analysts", "id": "market"},
    {"category": "analysts", "id": "fundamentals"}
  ]
}
```

### Import Configuration

```python
# In interface
> import
Import filename: my_config.json
```

Or programmatically:

```python
import json

with open("my_config.json") as f:
    config = json.load(f)

pool = AgentPool()
for agent in config["agents"]:
    pool.add_agent(agent["category"], agent["id"])
```

## Adding Custom Agents

### Step 1: Create Agent File

```python
# tradingagents/agents/analysts/my_analyst.py

def create_my_analyst(llm):
    def my_analyst_node(state):
        # Your logic here
        return {"messages": [...]}
    return my_analyst_node
```

### Step 2: Register in Agent Pool

Edit `tradingagents/agent_pool.py`:

```python
from tradingagents.agents.analysts.my_analyst import create_my_analyst

class AgentRegistry:
    AGENT_TYPES = {
        "analysts": {
            # ... existing analysts
            "my_analyst": {
                "name": "My Custom Analyst",
                "description": "Does custom analysis",
                "factory": create_my_analyst,
                "requires_memory": False
            }
        }
    }
```

### Step 3: Use It

```python
pool.add_agent("analysts", "my_analyst")
```

## Memory System

Agents that require memory (researchers, managers, trader) automatically get memory instances:

```python
pool.add_agent("researchers", "bull")

# Bull researcher now has its own memory
bull_memory = pool.memories.get("bull_memory")
```

Memory is shared across runs to help agents learn from past decisions.

## Architecture

```
AgentRegistry
├── Stores all agent definitions
├── Factory functions for creation
└── Metadata (name, description, requirements)

AgentPool
├── Manages LLM instances (quick/deep)
├── Creates and tracks active agents
├── Handles memory allocation
└── Provides add/remove/clear operations
```

## Best Practices

1. **Start Small**: Begin with 2-3 agents, add more as needed
2. **Match Use Case**:
   - Quick analysis → Basic setup (2 analysts)
   - Investment decision → Research debate (5 agents)
   - Full workflow → Full analysis (12 agents)
3. **Consider Cost**: More agents = more API calls
4. **Test Incrementally**: Add one agent at a time to understand behavior
5. **Save Configs**: Export successful configurations for reuse

## Troubleshooting

### Missing Dependencies

```bash
pip install langchain-google-genai python-dotenv
```

### API Key Error

```bash
cp .env.example .env
# Add GOOGLE_API_KEY=your_key
```

### Agent Creation Fails

Check that:
- API key is set
- Dependencies are installed
- Agent category/id are valid

## Next Steps

1. Run `python examples/initialize_all_agents.py` to see all agents
2. Run `python examples/agent_selector_interface.py` for interactive selection
3. Create your own configuration
4. Build custom workflows using selected agents

See `COMPLETE_GUIDE.md` for full TradingAgents documentation.
