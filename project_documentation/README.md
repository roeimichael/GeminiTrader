# GeminiTrader Project Documentation

Welcome to the comprehensive documentation for the GeminiTrader multi-agent trading analysis system.

## Documentation Index

### 📋 Start Here

1. **[PROJECT_OVERVIEW.md](./PROJECT_OVERVIEW.md)**
   - Executive summary of the system
   - Core capabilities and features
   - Technology stack
   - Quick start guide
   - **Read this first** to understand what GeminiTrader does

2. **[ARCHITECTURE.md](./ARCHITECTURE.md)**
   - Detailed system architecture
   - Component diagrams and data flow
   - How all pieces fit together
   - **Read this** to understand how it works

3. **[FILES_INVENTORY.md](./FILES_INVENTORY.md)**
   - Complete listing of all files
   - Purpose and dependencies of each file
   - Function-level documentation
   - **Reference this** when working with specific files

4. **[MISSING_FEATURES.md](./MISSING_FEATURES.md)**
   - What's not implemented yet
   - Known issues and bugs
   - Development roadmap
   - Priority order for future work
   - **Read this** to see what needs to be done

## Quick Navigation

### By Role

#### For AI Generators / LLM Context
**Goal**: Understand the entire project to generate code, fix bugs, or add features

**Read in Order**:
1. PROJECT_OVERVIEW.md - Understand what it is
2. ARCHITECTURE.md - Understand how it works
3. FILES_INVENTORY.md - Know where everything is
4. MISSING_FEATURES.md - See what's incomplete

**You'll Learn**:
- System architecture and design patterns
- All agent types and their purposes
- Data flow and component interactions
- Current limitations and TODOs

---

#### For New Developers
**Goal**: Start contributing to the project

**Read in Order**:
1. PROJECT_OVERVIEW.md - High-level understanding
2. MISSING_FEATURES.md - See what needs work
3. FILES_INVENTORY.md - Find relevant files
4. ARCHITECTURE.md - Deep dive when needed

**You'll Learn**:
- How to set up the development environment
- Where to find specific functionality
- What needs to be built
- How to add new agents or data sources

---

#### For System Architects
**Goal**: Evaluate or modify the system architecture

**Read in Order**:
1. ARCHITECTURE.md - System design
2. PROJECT_OVERVIEW.md - Capabilities and constraints
3. MISSING_FEATURES.md - Scalability needs

**You'll Learn**:
- Multi-agent orchestration patterns
- State management approach
- Data layer abstraction
- LLM integration strategy

---

#### For Product Managers
**Goal**: Understand features and roadmap

**Read in Order**:
1. PROJECT_OVERVIEW.md - What's built
2. MISSING_FEATURES.md - What's next
3. ARCHITECTURE.md - Technical constraints

**You'll Learn**:
- Current capabilities
- Use cases and target users
- Development timeline estimates
- Resource requirements

---

### By Component

#### Understanding Agents
**Files to Read**:
- ARCHITECTURE.md → "Agent Layer" section
- FILES_INVENTORY.md → "tradingagents/agents/" section
- PROJECT_OVERVIEW.md → "Core Capabilities" → "Multi-Agent Analysis System"

**Learn About**:
- All 12 agent types
- Agent communication patterns
- Memory systems
- LLM model selection

---

#### Understanding Data Layer
**Files to Read**:
- ARCHITECTURE.md → "Data Layer" section
- FILES_INVENTORY.md → "tradingagents/dataflows/" section

**Learn About**:
- Vendor routing
- API integrations
- Caching strategies
- Fallback mechanisms

---

#### Understanding Conversations
**Files to Read**:
- ARCHITECTURE.md → "ConversationManager" section
- FILES_INVENTORY.md → "conversation_manager.py" entry
- MISSING_FEATURES.md → Issue #1 (Critical)

**Learn About**:
- Debate orchestration
- 3-phase workflow
- Response aggregation
- **Current limitations** (mock responses)

---

#### Understanding GUI
**Files to Read**:
- FILES_INVENTORY.md → "main.py" entry
- ARCHITECTURE.md → "User Interface Layer"

**Learn About**:
- Tabbed interface
- Agent selection
- Conversation display
- Configuration management

---

## File Summaries

| File | Purpose | Size | Priority |
|------|---------|------|----------|
| PROJECT_OVERVIEW.md | High-level introduction | ~500 lines | READ FIRST |
| ARCHITECTURE.md | Technical deep dive | ~800 lines | READ SECOND |
| FILES_INVENTORY.md | Complete file reference | ~1200 lines | REFERENCE |
| MISSING_FEATURES.md | Roadmap & TODOs | ~600 lines | FOR PLANNING |

## Key Concepts Explained

### Multi-Agent System
GeminiTrader uses **12 specialized AI agents** that each analyze stocks from their unique perspective:
- **Analysts** gather data (technical, fundamental, news, social)
- **Researchers** build bullish and bearish cases
- **Managers** make investment decisions
- **Risk Analysts** evaluate risk from multiple angles
- **Trader** creates executable plans

See ARCHITECTURE.md for complete workflow.

### Debate-Driven Consensus
Instead of a single AI opinion, agents **debate** their viewpoints:
1. Individual analysis (Phase 1)
2. Multi-round debate (Phase 2)
3. Consensus verdict (Phase 3)

This prevents single-perspective bias and produces more robust recommendations.

### LangGraph Orchestration
The system uses **LangGraph** (from LangChain) to orchestrate the multi-agent workflow:
- State-based execution
- Conditional routing
- Parallel agent execution
- Memory persistence

See ARCHITECTURE.md → "Graph Orchestration" for details.

### Memory System
Agents with `requires_memory: True` use **ChromaDB** to:
- Store past analyses
- Retrieve similar situations
- Learn from history
- Improve recommendations

See ARCHITECTURE.md → "Memory System" for implementation.

## Common Questions

### Q: How do I add a new agent?
**A**: See ARCHITECTURE.md → "Extensibility Points" → "Adding New Agents"

Steps:
1. Create agent file in appropriate category
2. Implement `create_<agent_name>(llm, memory)` factory
3. Register in `AgentRegistry.AGENT_TYPES`
4. Add prompts to `agent_prompts.json`

### Q: How do I add a new data source?
**A**: See ARCHITECTURE.md → "Extensibility Points" → "Adding New Data Sources"

Steps:
1. Create vendor file in `dataflows/`
2. Implement required functions
3. Update `interface.py` routing
4. Add configuration options

### Q: Why are conversation responses mocked?
**A**: See MISSING_FEATURES.md → Issue #1 "Agent-LLM Integration Not Connected"

The ConversationManager needs to be connected to actual agent LLM calls. This is the **top priority** fix.

### Q: How do I test the system?
**A**: Currently:
- Manual testing via GUI
- Unit tests: **Not implemented** (see MISSING_FEATURES.md #18)
- Integration tests: **Not implemented**

This is on the roadmap.

### Q: Can I use this for automated trading?
**A**: Not yet. See MISSING_FEATURES.md #10 "Automated Trading Integration"

**⚠️ Warning**: Automated trading requires extensive testing and risk management. Use at your own risk.

### Q: What LLMs does it support?
**A**: Currently:
- **Google Gemini** (primary, tested)
- OpenAI GPT (framework support, not tested in conversation mode)
- Anthropic Claude (framework support, not tested)
- Local LLMs (framework support, not tested)

See ARCHITECTURE.md → "Technology Stack" for details.

### Q: How much does it cost to run?
**A**: See MISSING_FEATURES.md → "Resource Requirements"

Estimated monthly costs:
- LLM API: $50-500 (depending on usage)
- Data APIs: $0-100 (Alpha Vantage free tier available)
- Infrastructure: $0 (runs locally) or $100-500 (cloud deployment)

## Critical Issues

### 🚨 Must Fix Before Production

1. **Agent-LLM Connection** (MISSING_FEATURES.md #1)
   - **Status**: Mock responses only
   - **Impact**: System doesn't work with real agents
   - **Priority**: CRITICAL
   - **Timeline**: 3-5 days

2. **State Management** (MISSING_FEATURES.md #2)
   - **Status**: Not implemented for conversations
   - **Impact**: Can't pass data between agents properly
   - **Priority**: CRITICAL
   - **Timeline**: 2-3 days

3. **Real-Time Data** (MISSING_FEATURES.md #3)
   - **Status**: Not fetched during conversations
   - **Impact**: Agents analyze without current data
   - **Priority**: HIGH
   - **Timeline**: 2-3 days

### 📋 Total Time to MVP
**Estimate**: 2-3 weeks to get conversation system fully functional

## Development Workflow

### Setting Up
```bash
# Clone repository
git clone <repo-url>
cd GeminiTrader

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env and add your API keys

# Run GUI
python main.py
```

### Making Changes
1. Read relevant documentation (use this index)
2. Find files in FILES_INVENTORY.md
3. Understand architecture from ARCHITECTURE.md
4. Make changes
5. Test manually (automated tests TODO)
6. Update documentation if needed

### Adding Features
1. Check MISSING_FEATURES.md for priorities
2. Read ARCHITECTURE.md for extensibility points
3. Follow existing patterns (see FILES_INVENTORY.md)
4. Add tests (when testing framework exists)
5. Update documentation

## Contributing

### Code Style
- Follow existing patterns
- Add docstrings to functions
- Use type hints
- Keep functions focused (single responsibility)

### Documentation
- Update FILES_INVENTORY.md for new files
- Update ARCHITECTURE.md for architectural changes
- Update MISSING_FEATURES.md when completing TODOs
- Update PROJECT_OVERVIEW.md for new capabilities

### Testing
- Manual testing required (no automated tests yet)
- Test with multiple agents
- Test error cases
- Verify API integrations

## Resources

### External Documentation
- [LangChain Docs](https://python.langchain.com/)
- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [Google Gemini API](https://ai.google.dev/)
- [Alpha Vantage API](https://www.alphavantage.co/)
- [Yahoo Finance (yfinance)](https://pypi.org/project/yfinance/)

### Related Projects
- LangChain
- LangGraph
- ChromaDB
- Tkinter

## Version History

### v0.2.0 (Current - 2024-12-25)
- ✅ Added conversation interface
- ✅ Added debate orchestration
- ✅ Created tabbed GUI
- ⚠️ Conversation uses mock responses (needs fixing)

### v0.1.0 (2024-12-23)
- ✅ Multi-agent system with 12 agents
- ✅ LangGraph workflow
- ✅ Data source integrations
- ✅ Memory system
- ✅ Basic GUI for agent selection

## License

[Add license information]

## Contact

[Add contact information]

---

**Last Updated**: 2024-12-25

**Maintainers**: [Add names]

**Status**: Active Development

---

## Quick Start for AI Generators

If you're an AI system reading this to generate code or understand the project:

1. **Read PROJECT_OVERVIEW.md** to understand what GeminiTrader does
2. **Read ARCHITECTURE.md** to understand the system design
3. **Reference FILES_INVENTORY.md** to find specific files and functions
4. **Check MISSING_FEATURES.md** to see what's not implemented

### Most Important Info for Code Generation:

**Agent Pattern**:
```python
def create_<agent_name>(llm, memory=None):
    def <agent_name>_node(state):
        # Extract from state
        # Define tools
        # Create prompt
        # Call LLM
        # Update state
        return state
    return <agent_name>_node
```

**State Structure**:
```python
{
    "company_of_interest": str,
    "trade_date": str,
    "analyst_insights": dict,
    "bull_case": str,
    "bear_case": str,
    ...
}
```

**Data Fetching**:
```python
from tradingagents.dataflows.interface import route_to_vendor
data = route_to_vendor("get_stock_data", ticker="AAPL", period="1mo")
```

**Critical TODO**:
The conversation system (ConversationManager) currently uses mock responses. Priority #1 is connecting it to actual agent LLM calls. See MISSING_FEATURES.md #1 for details.

Good luck! 🚀
