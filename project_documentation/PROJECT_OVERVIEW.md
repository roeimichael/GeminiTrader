# GeminiTrader - Project Overview

## Executive Summary

GeminiTrader is a sophisticated multi-agent trading analysis system that leverages Google's Gemini AI models to provide comprehensive stock market analysis through specialized agents. The system employs a debate-driven consensus mechanism where multiple AI agents analyze stocks from different perspectives, discuss their findings, and reach a unified recommendation.

## Core Capabilities

### 1. Multi-Agent Analysis System
- **12 Specialized Agents** across 5 categories:
  - **Analysts (4)**: Market, Fundamentals, News, Social Media
  - **Researchers (2)**: Bull Case Builder, Bear Case Builder
  - **Managers (2)**: Research Manager, Risk Manager
  - **Risk Analysts (3)**: Aggressive, Conservative, Neutral
  - **Trader (1)**: Trade Execution Planner

### 2. Intelligent Orchestration
- LangGraph-based workflow engine
- State management for multi-step analysis
- Conditional routing based on agent recommendations
- Memory systems for learning from past analyses

### 3. Conversation & Debate Interface
- Interactive query system where users can ask trading questions
- Three-phase analysis workflow:
  - **Phase 1**: Individual agent analysis from specialized perspectives
  - **Phase 2**: Multi-round debate between agents with conflicting views
  - **Phase 3**: Consensus verdict with actionable recommendations

### 4. Modular Agent Management
- Visual GUI for selecting and configuring agents
- Agent pool system for dynamic agent initialization
- Support for custom agent combinations
- Quick setup templates (Full, Basic, Research Debate)

## Technology Stack

### AI & ML
- **Primary LLM**: Google Gemini (gemini-2.0-flash-exp, gemini-1.5-pro)
- **Framework**: LangChain + LangGraph for agent orchestration
- **Memory**: ChromaDB for situation-based learning (OpenAI embeddings)

### Data Sources
- **Technical Data**: Yahoo Finance, Alpha Vantage
- **Fundamental Data**: Alpha Vantage, SimFin
- **News Data**: Alpha Vantage, Google News, Finnhub
- **Social Data**: Reddit sentiment analysis

### UI & Interface
- **GUI**: Tkinter with tabbed interface (dark theme)
- **CLI**: Typer-based command-line interface
- **Export/Import**: JSON configuration management

### Architecture
- **Language**: Python 3.11+
- **Pattern**: Multi-agent system with pub-sub communication
- **State Management**: LangGraph StateGraph
- **Configuration**: Environment-based (.env) + runtime config

## Project Structure

```
GeminiTrader/
├── main.py                              # GUI application entry point
├── tradingagents/                       # Core trading agents library
│   ├── agent_pool.py                    # Agent registry & pool management
│   ├── conversation_manager.py          # Debate orchestration
│   ├── config.py                        # System configuration
│   ├── agents/                          # All 12 agent implementations
│   │   ├── analysts/                    # 4 data analysis agents
│   │   ├── researchers/                 # Bull & Bear debate agents
│   │   ├── managers/                    # Decision-making agents
│   │   ├── risk_mgmt/                   # 3 risk perspective agents
│   │   ├── trader/                      # Trade execution agent
│   │   └── utils/                       # Tools, memory, state management
│   ├── dataflows/                       # Data source integrations
│   │   ├── interface.py                 # Vendor routing
│   │   ├── alpha_vantage*.py            # Alpha Vantage APIs
│   │   ├── y_finance.py                 # Yahoo Finance
│   │   ├── google.py                    # Google News
│   │   └── local.py                     # Local/cached data
│   └── graph/                           # LangGraph workflow engine
│       ├── trading_graph.py             # Main workflow definition
│       ├── conditional_logic.py         # Decision routing
│       ├── propagation.py               # State propagation
│       └── setup.py                     # Graph construction
├── cli/                                 # Command-line interface
├── agent_prompts.json                   # Centralized agent prompts
└── project_documentation/               # This documentation

```

## Key Design Principles

### 1. Modularity
- Agents are independent and swappable
- Each agent has a single responsibility
- Easy to add new agents without modifying existing code

### 2. Debate-Driven Consensus
- Multiple perspectives prevent single-point-of-view bias
- Agents challenge each other's assumptions
- Final recommendation reflects collective wisdom

### 3. Transparency
- All agent reasoning is visible to users
- Clear separation of individual opinions vs. consensus
- Audit trail of debate rounds and decision points

### 4. Flexibility
- Users choose which agents to activate
- Configurable debate rounds and discussion depth
- Support for both quick analysis and deep research

### 5. Extensibility
- Plugin architecture for new data sources
- Custom agent creation support
- Multiple LLM backends supported (Google, OpenAI, Anthropic, local)

## Workflow Example

```
User Query: "Should I invest in MSFT? They're releasing earnings next week."

PHASE 1: Individual Analysis
  ├─ Market Analyst: Technical indicators show bullish pattern
  ├─ Fundamentals Analyst: Strong revenue growth, healthy balance sheet
  ├─ News Analyst: Positive pre-earnings sentiment
  └─ Social Media Analyst: Retail investors moderately bullish

PHASE 2: Debate
  Round 1 - Position Statements
    ├─ Bullish Coalition: Multiple positive indicators align
    └─ Bearish Coalition: Valuation concerns, macro headwinds

  Round 2 - Challenging Assumptions
    ├─ Bears: "Market may have priced in positive news"
    └─ Bulls: "Technical support provides favorable risk/reward"

  Round 3 - Consensus Building
    └─ Agreement: Take position with risk management

PHASE 3: Final Verdict
  ├─ Recommendation: BUY
  ├─ Confidence: Moderate
  ├─ Sentiment: 75% bullish
  └─ Action Items:
      - Position size: Moderate based on risk tolerance
      - Stop loss: Below key support
      - Monitor: Earnings release closely
      - Review: Post-earnings for adjustment
```

## Current Status

### ✅ Completed Features
- [x] Multi-agent system with 12 specialized agents
- [x] GUI for agent selection and pool management
- [x] Conversation interface with query input
- [x] Three-phase debate orchestration
- [x] Visual output formatting
- [x] Configuration export/import
- [x] Agent registry and factory pattern
- [x] Multiple data source integrations
- [x] LangGraph workflow engine
- [x] Memory system for learning

### 🚧 In Progress / Mock Implementation
- [ ] **Agent-LLM Integration**: Currently using mock responses
  - Need to connect ConversationManager to actual agent LLM calls
  - Implement proper state object creation for each agent
  - Parse and process actual agent responses

### 📋 Planned Features
- [ ] Real-time data fetching during conversations
- [ ] Historical backtesting of agent recommendations
- [ ] Portfolio management integration
- [ ] Trade execution capabilities
- [ ] Performance analytics dashboard
- [ ] Web-based interface (currently desktop only)
- [ ] Multi-language support
- [ ] Custom agent builder UI
- [ ] Automated trading strategies
- [ ] Risk monitoring and alerts

## Use Cases

### 1. Individual Investors
- Get multi-perspective analysis before making trades
- Understand different viewpoints (bull vs. bear)
- Learn from agent reasoning and debate process

### 2. Research & Education
- Study different analytical approaches
- Compare technical vs. fundamental analysis
- Understand market sentiment dynamics

### 3. Strategy Development
- Test hypotheses against multiple agent perspectives
- Identify blind spots in analysis
- Refine trading strategies through debate insights

### 4. Risk Management
- Evaluate risk from multiple angles (aggressive, conservative, neutral)
- Get balanced recommendations
- Understand potential downside scenarios

## Performance Considerations

### LLM Model Selection
- **Quick Thinking (gemini-2.0-flash-exp)**:
  - Used for: Analysts, Researchers, Risk Analysts
  - Fast responses, lower cost
  - Suitable for data analysis and pattern recognition

- **Deep Thinking (gemini-1.5-pro)**:
  - Used for: Managers, Trader
  - More thoughtful reasoning
  - Better for complex decision-making and synthesis

### Memory Management
- Selective memory for agents that benefit from historical context
- ChromaDB for efficient similarity search
- Separate memory spaces per agent to prevent cross-contamination

### Cost Optimization
- Tiered LLM usage (fast vs. deep thinking models)
- Caching for repeated queries
- Configurable debate rounds to control API calls
- Local data sources where possible

## Security & Privacy

### API Key Management
- Environment variable-based configuration (.env)
- No hardcoded credentials
- Separate keys for different services

### Data Handling
- No personal data collection
- Query history stored locally only
- Export/import for user-controlled backups

## Next Steps for Development

See `MISSING_FEATURES.md` for detailed roadmap and priorities.

## Getting Started

1. **Installation**:
   ```bash
   pip install -r requirements.txt
   cp .env.example .env
   # Add your GOOGLE_API_KEY to .env
   ```

2. **Run GUI**:
   ```bash
   python main.py
   ```

3. **Select Agents**: Choose agents in Pool Setup tab
4. **Initialize Pool**: Click "Initialize Pool" button
5. **Start Conversation**: Switch to Conversation tab and ask questions

For detailed usage, see individual documentation files in this folder.
