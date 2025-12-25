# System Architecture

## Overview

GeminiTrader follows a multi-layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE LAYER                     │
│  ┌──────────────┐  ┌────────────────────────────────────┐   │
│  │   GUI (Tk)   │  │   CLI (Typer)                      │   │
│  │  main.py     │  │   cli/main.py                      │   │
│  └──────────────┘  └────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  ORCHESTRATION LAYER                         │
│  ┌──────────────────────┐  ┌──────────────────────────┐     │
│  │  ConversationManager │  │  AgentPool               │     │
│  │  (Debate Logic)      │  │  (Agent Lifecycle)       │     │
│  └──────────────────────┘  └──────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    AGENT LAYER                               │
│  ┌────────────┐ ┌──────────┐ ┌─────────┐ ┌────────────┐    │
│  │ Analysts   │ │Researchers│ │Managers │ │Risk Analysts│   │
│  │ (4 types)  │ │ (2 types) │ │(2 types)│ │  (3 types)  │   │
│  └────────────┘ └──────────┘ └─────────┘ └────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     DATA LAYER                               │
│  ┌──────────┐  ┌───────────┐  ┌─────────┐  ┌──────────┐    │
│  │ YFinance │  │ Alpha V   │  │ Google  │  │  Local   │    │
│  └──────────┘  └───────────┘  └─────────┘  └──────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. User Interface Layer

#### main.py - GUI Application
**Purpose**: Desktop application for agent management and conversations

**Key Components**:
- `AgentSelectorGUI`: Main application class
  - `setup_ui()`: Creates tabbed interface
  - `setup_pool_tab()`: Agent selection and configuration
  - `setup_conversation_tab()`: Query input and debate display

**Communication**:
- → `AgentRegistry`: Lists available agents
- → `AgentPool`: Initializes selected agents
- → `ConversationManager`: Sends queries and receives results
- ← User: Receives input, displays output

**State Management**:
- `self.registry`: AgentRegistry instance
- `self.pool`: AgentPool instance (null until initialized)
- `self.conversation_manager`: ConversationManager instance

#### cli/main.py - Command Line Interface
**Purpose**: Terminal-based interface for analysis

**Key Components**:
- `app`: Typer application
- Commands: analyze, config, list-agents

**Communication**:
- → `TradingAgentsGraph`: Runs full analysis workflow
- → Configuration system
- ← User: CLI commands and arguments

### 2. Orchestration Layer

#### AgentPool (tradingagents/agent_pool.py)
**Purpose**: Manages agent lifecycle and initialization

**Key Classes**:

##### `AgentRegistry`
**Static registry of all available agents**

Methods:
- `get_all_agents()`: Returns complete agent catalog
- `get_agent_info(category, agent_id)`: Get specific agent metadata
- `list_all_agents()`: Flatten registry to list format

Data Structure:
```python
AGENT_TYPES = {
    "analysts": {
        "market": {
            "name": "Market Analyst",
            "description": "...",
            "factory": create_market_analyst,
            "requires_memory": False
        },
        # ... more analysts
    },
    # ... more categories
}
```

##### `AgentPool`
**Manages active agent instances**

Methods:
- `__init__(config)`: Initialize LLMs and memory
- `_initialize_llms()`: Create Gemini model instances
- `add_agent(category, agent_id)`: Instantiate agent
- `remove_agent(category, agent_id)`: Deactivate agent
- `get_agent(category, agent_id)`: Retrieve agent instance
- `clear()`: Remove all agents

State:
- `llm_quick`: gemini-2.0-flash-exp instance
- `llm_deep`: gemini-1.5-pro instance
- `memories`: Dict of FinancialSituationMemory instances
- `active_agents`: Dict of agent instances

Communication:
- → Agent factories: Creates agent instances
- → LLM providers: Initializes language models
- → Memory system: Creates memory instances for stateful agents

#### ConversationManager (tradingagents/conversation_manager.py)
**Purpose**: Orchestrates multi-agent conversations and debates

**Key Methods**:

##### Core Workflow
- `send_query_to_agents(query, context)`: Main entry point
  - Returns: Full conversation with responses, debate, verdict

##### Phase 1: Individual Analysis
- `_collect_individual_responses(query, context)`:
  - Iterates through all active agents
  - Creates specialized prompts per agent type
  - Collects individual perspectives
  - Returns: List of agent responses

- `_create_specialized_prompt(query, agent_name, category, description)`:
  - Generates context-aware prompts
  - Focuses agent on their expertise area

- `_get_agent_response(agent_data, prompt, context)`:
  - **Currently**: Returns mock responses by agent type
  - **TODO**: Call actual agent LLM with proper state

##### Phase 2: Debate Orchestration
- `_orchestrate_debate(query, responses, context)`:
  - Runs 3 debate rounds
  - Returns: List of debate exchanges

- `_generate_position_statements(responses)`:
  - Groups agents by sentiment (bullish/bearish/neutral)
  - Creates coalition statements

- `_generate_challenges(responses)`:
  - Generates cross-examination between viewpoints

- `_generate_consensus(responses)`:
  - Builds common ground and action items

##### Phase 3: Verdict Generation
- `_generate_final_verdict(query, responses, debate)`:
  - Aggregates agent sentiments
  - Calculates confidence levels
  - Generates actionable recommendations
  - Returns: Verdict dictionary

State Management:
- `conversation_history`: List of all past conversations
- `agent_pool`: Reference to AgentPool instance

### 3. Agent Layer

All agents follow a common pattern:

```python
def create_<agent_name>(llm, memory=None):
    def <agent_name>_node(state):
        # Extract state variables
        # Define tools
        # Create system message
        # Bind tools to LLM
        # Invoke LLM
        # Update state
        return state
    return <agent_name>_node
```

#### Analysts (tradingagents/agents/analysts/)

##### Market Analyst (market_analyst.py)
**Specialization**: Technical analysis and price action

Tools Used:
- `get_stock_data(ticker, period)`: OHLCV data
- `get_indicators(ticker, indicators, period)`: Technical indicators

Analyzes:
- Moving averages (SMA, EMA)
- MACD and momentum indicators
- Volume patterns
- Support/resistance levels

Returns: Technical outlook and chart setup analysis

##### Fundamentals Analyst (fundamentals_analyst.py)
**Specialization**: Financial statements and valuation

Tools Used:
- `get_fundamentals(ticker)`: Company fundamentals
- `get_balance_sheet(ticker)`: Balance sheet data
- `get_cashflow(ticker)`: Cash flow statement
- `get_income_statement(ticker)`: P&L data
- `get_insider_sentiment(ticker)`: Insider trading patterns

Analyzes:
- P/E ratios and valuation metrics
- Revenue and profit trends
- Balance sheet strength
- Insider activity

Returns: Fundamental assessment and valuation opinion

##### News Analyst (news_analyst.py)
**Specialization**: News sentiment and catalysts

Tools Used:
- `get_news(ticker)`: Company-specific news
- `get_global_news()`: Market-wide news

Analyzes:
- Recent news sentiment
- Upcoming catalysts
- Earnings announcements
- Regulatory changes

Returns: News-based outlook and catalyst timeline

##### Social Media Analyst (social_media_analyst.py)
**Specialization**: Retail sentiment and social trends

Tools Used:
- `get_news(ticker)`: Social media mentions
- Reddit/Twitter sentiment (via news aggregation)

Analyzes:
- Retail investor sentiment
- Discussion volume trends
- Influencer opinions
- Options flow (if available)

Returns: Social sentiment summary and crowd psychology

#### Researchers (tradingagents/agents/researchers/)

##### Bull Researcher (bull_researcher.py)
**Specialization**: Building bullish investment cases

Uses Memory: YES
- Stores successful bullish patterns
- Retrieves similar past situations

Process:
1. Query memory for comparable bull cases
2. Analyze current positive catalysts
3. Build comprehensive bullish thesis
4. Estimate upside potential

Returns: Bull case with probability and upside targets

##### Bear Researcher (bear_researcher.py)
**Specialization**: Finding risks and bearish scenarios

Uses Memory: YES
- Stores historical bear cases
- Identifies risk patterns

Process:
1. Query memory for similar risk scenarios
2. Identify current headwinds
3. Build bearish counter-argument
4. Estimate downside risk

Returns: Bear case with probability and downside targets

#### Managers (tradingagents/agents/managers/)

##### Research Manager (research_manager.py)
**Specialization**: Synthesizing research into decisions

Uses Memory: YES
Uses LLM: Deep thinking (gemini-1.5-pro)

Process:
1. Review all analyst inputs
2. Weigh bull vs. bear arguments
3. Make initial investment recommendation
4. Store decision rationale in memory

Returns: BUY/SELL/HOLD recommendation with reasoning

##### Risk Manager (risk_manager.py)
**Specialization**: Final risk assessment

Uses Memory: YES
Uses LLM: Deep thinking (gemini-1.5-pro)

Process:
1. Review research manager recommendation
2. Assess risk analyst perspectives
3. Evaluate risk/reward ratio
4. Make final recommendation

Returns: Final verdict with position sizing guidance

#### Risk Analysts (tradingagents/agents/risk_mgmt/)

##### Aggressive Debator (aggresive_debator.py)
**Specialization**: High risk tolerance perspective

Advocates for:
- Larger position sizes
- Momentum plays
- Taking advantage of opportunities
- Higher risk/reward ratios

##### Conservative Debator (conservative_debator.py)
**Specialization**: Capital preservation

Advocates for:
- Smaller positions
- Waiting for confirmation
- Protecting capital
- Lower risk exposure

##### Neutral Debator (neutral_debator.py)
**Specialization**: Balanced approach

Advocates for:
- Moderate position sizing
- Diversified entry points
- Balanced risk management
- Flexible strategies

#### Trader (tradingagents/agents/trader/)

##### Trader (trader.py)
**Specialization**: Executable trade plans

Uses Memory: YES
Uses LLM: Deep thinking (gemini-1.5-pro)

Creates:
- Entry price levels
- Stop loss placements
- Profit target zones
- Position sizing recommendations
- Execution strategy (market/limit orders)

### 4. Data Layer

#### Interface (tradingagents/dataflows/interface.py)
**Purpose**: Route data requests to appropriate vendors

Key Function:
- `route_to_vendor(tool_name, **params)`:
  - Checks configuration for tool-specific vendor
  - Falls back to category-level vendor
  - Calls appropriate vendor implementation
  - Returns data or error

Configuration Priority:
1. `tool_vendors[specific_tool]`
2. `data_vendors[category]`
3. Default vendor

#### Vendor Implementations

All vendors follow interface pattern:
```python
def get_<data_type>(ticker, **params):
    # Fetch from external API
    # Parse and format
    # Return standardized data structure
    # or raise exception
```

##### Yahoo Finance (y_finance.py)
Provides:
- Stock prices (OHLCV)
- Technical indicators
- Basic fundamentals

Advantages:
- Free, no API key required
- Real-time data
- Wide coverage

##### Alpha Vantage (alpha_vantage_*.py)
Provides:
- Advanced technical indicators
- Fundamental data
- News and sentiment
- Company financials

Requires: API key (free tier available)

##### Google (google.py)
Provides:
- News aggregation
- Search-based sentiment

Requires: API key

##### Local (local.py)
Provides:
- Cached data
- Historical datasets
- Testing fixtures

Use Cases:
- Offline development
- Backtesting
- Rate limit avoidance

### 5. Memory System

#### FinancialSituationMemory (tradingagents/agents/utils/memory.py)

**Purpose**: Enable agents to learn from past analyses

**Technology**: ChromaDB + OpenAI Embeddings

**Key Methods**:
- `__init__(name, config)`: Initialize collection
- `add_situations(situations_and_advice)`: Store learnings
- `get_relevant_situations(query, top_k)`: Retrieve similar cases
- `clear()`: Reset memory

**Storage Structure**:
```python
{
    "id": "unique_id",
    "situation": "Market conditions description",
    "advice": "What was recommended",
    "embedding": [0.123, 0.456, ...]  # OpenAI embedding
}
```

**Used By**:
- Bull Researcher: Past bullish patterns
- Bear Researcher: Historical risks
- Research Manager: Decision history
- Risk Manager: Risk assessment patterns
- Trader: Execution strategies

### 6. State Management

#### AgentState (tradingagents/agents/utils/agent_states.py)

**Purpose**: Shared state across agent workflow

**Key Fields**:
```python
{
    "company_of_interest": str,      # Ticker symbol
    "trade_date": str,               # YYYY-MM-DD
    "analyst_insights": dict,        # Analyst outputs
    "bull_case": str,                # Bull researcher output
    "bear_case": str,                # Bear researcher output
    "research_recommendation": str,  # Research manager decision
    "risk_recommendation": str,      # Risk manager final verdict
    "trade_plan": dict,              # Trader execution plan
    # ... more fields
}
```

**Flow Through Workflow**:
1. Initial state created with ticker and date
2. Analysts populate their sections
3. Researchers build cases
4. Managers make decisions
5. Trader creates execution plan

### 7. Graph Orchestration (tradingagents/graph/)

#### TradingAgentsGraph (trading_graph.py)

**Purpose**: Define and execute multi-agent workflow

**Key Components**:

##### Initialization
- `__init__(selected_analysts, config)`:
  - Initialize LLMs
  - Create memory instances
  - Setup selected agents
  - Build graph

##### Graph Construction
- `setup_graph()`:
  - Define nodes (one per agent)
  - Define edges (workflow paths)
  - Add conditional routing
  - Compile StateGraph

##### Execution
- `run(ticker, trade_date)`:
  - Create initial state
  - Execute graph
  - Return final state with recommendations

##### Workflow Paths
```
START
  ↓
Analysts (parallel execution)
  ├─ Market Analyst
  ├─ Fundamentals Analyst
  ├─ News Analyst
  └─ Social Media Analyst
  ↓
Bull Researcher ←→ Bear Researcher (debate)
  ↓
Research Manager (first decision)
  ↓
Risk Debate (parallel)
  ├─ Aggressive Debator
  ├─ Conservative Debator
  └─ Neutral Debator
  ↓
Risk Manager (final decision)
  ↓
Trader (execution plan)
  ↓
END
```

#### Conditional Logic (conditional_logic.py)

**Purpose**: Route workflow based on agent outputs

Key Functions:
- `should_continue_debate()`: Check if more debate needed
- `check_research_decision()`: Route based on recommendation strength
- `evaluate_risk_level()`: Determine risk path

#### Propagation (propagation.py)

**Purpose**: Propagate state changes through workflow

Ensures:
- State consistency
- Data flow between agents
- Error handling

## Data Flow Example

```
User Query: "Analyze AAPL"
    ↓
┌─────────────────────────────────────┐
│ GUI / ConversationManager           │
│ - Parse query                       │
│ - Extract ticker: AAPL              │
│ - Prepare context                   │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ AgentPool                           │
│ - Get active agents                 │
│ - For each agent:                   │
│   - Call agent factory              │
│   - Pass LLM and memory             │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ Market Analyst Agent                │
│ - Call get_stock_data("AAPL")      │
│     ↓                               │
│   ┌─────────────────────────┐      │
│   │ Dataflows Interface     │      │
│   │ - Route to YFinance     │      │
│   └─────────────────────────┘      │
│     ↓                               │
│   ┌─────────────────────────┐      │
│   │ YFinance                │      │
│   │ - Fetch AAPL data       │      │
│   │ - Return OHLCV          │      │
│   └─────────────────────────┘      │
│     ↓                               │
│ - Call get_indicators("AAPL",      │
│   ["rsi", "macd"])                 │
│     ↓                               │
│   [Same routing process]            │
│     ↓                               │
│ - Analyze with LLM                  │
│ - Generate insights                 │
└─────────────────────────────────────┘
    ↓
[Same process for other agents]
    ↓
┌─────────────────────────────────────┐
│ ConversationManager                 │
│ - Collect all responses             │
│ - Orchestrate debate                │
│ - Generate verdict                  │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ GUI Display                         │
│ - Format output                     │
│ - Show to user                      │
└─────────────────────────────────────┘
```

## Configuration System

### Environment Variables (.env)
```
GOOGLE_API_KEY=<your_key>
OPENAI_API_KEY=<your_key>  # For embeddings
ALPHA_VANTAGE_KEY=<your_key>
```

### Runtime Configuration (tradingagents/config.py)
```python
DEFAULT_CONFIG = {
    "llm_provider": "google",
    "deep_think_llm": "gemini-1.5-pro",
    "quick_think_llm": "gemini-2.0-flash-exp",
    "max_debate_rounds": 1,
    "data_vendors": {
        "core_stock_apis": "yfinance",
        "technical_indicators": "yfinance",
        "fundamental_data": "alpha_vantage",
        "news_data": "alpha_vantage",
    },
    # ... more settings
}
```

### Dataflows Configuration (tradingagents/dataflows/config.py)
- Module-level configuration management
- Runtime override support
- Vendor selection per tool

## Error Handling

### Levels
1. **Data Layer**: API errors, rate limits, invalid tickers
2. **Agent Layer**: LLM errors, tool failures, invalid outputs
3. **Orchestration Layer**: State errors, workflow failures
4. **UI Layer**: User input validation, display errors

### Strategy
- Graceful degradation
- Fallback data sources
- Error propagation to user
- Logging for debugging

## Performance Optimization

### Caching
- API responses cached locally
- Repeated queries use cached data
- Configurable cache TTL

### Parallel Execution
- Analysts run in parallel
- Risk debators run in parallel
- LangGraph manages concurrency

### Rate Limiting
- Respect API limits
- Backoff strategies
- Local data fallback

## Security Considerations

### API Keys
- Never committed to version control
- Environment variable based
- .env.example as template

### Data Privacy
- No user data sent to LLMs except queries
- Local memory storage
- No cloud sync of sensitive data

### Input Validation
- Sanitize user queries
- Validate ticker symbols
- Limit query length

## Extensibility Points

### Adding New Agents
1. Create agent file in appropriate category folder
2. Implement `create_<agent_name>(llm, memory)` factory
3. Register in `AgentRegistry.AGENT_TYPES`
4. Add to agent_prompts.json (optional)

### Adding New Data Sources
1. Create vendor file in dataflows/
2. Implement required functions
3. Update `interface.py` routing
4. Add configuration options

### Adding New LLM Providers
1. Update LLM initialization in `AgentPool`
2. Add provider-specific configuration
3. Test with all agent types

## Testing Strategy

### Unit Tests
- Individual agent functions
- Data source connectors
- Utility functions

### Integration Tests
- Agent workflow end-to-end
- Data fetching and parsing
- State propagation

### UI Tests
- GUI interaction flows
- Configuration management
- Error handling

## Deployment

### Development
```bash
python main.py
```

### Production Considerations
- API key rotation
- Error monitoring
- Usage analytics
- Cost tracking (LLM API calls)

## Monitoring & Observability

### Metrics to Track
- API call count by vendor
- LLM token usage
- Response times
- Error rates
- User query patterns

### Logging
- Agent decisions
- API calls
- Errors and exceptions
- Performance metrics

---

For detailed component documentation, see individual files in this folder.
