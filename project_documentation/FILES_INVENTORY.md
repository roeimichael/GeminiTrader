# Complete Files Inventory

## Root Level Files

### main.py
**Purpose**: GUI application entry point
**Type**: Application
**Dependencies**: tradingagents.agent_pool, tradingagents.config, tradingagents.conversation_manager

**Classes**:
- `AgentSelectorGUI`: Main application class with tabbed interface

**Key Methods**:
- `setup_ui()`: Creates notebook with 2 tabs
- `setup_pool_tab()`: Agent selection interface
- `setup_conversation_tab()`: Conversation interface
- `initialize_pool()`: Creates agent pool and conversation manager
- `send_query()`: Sends user query to agents
- `display_conversation()`: Formats and displays results

**Communication**:
- → AgentRegistry: Lists available agents
- → AgentPool: Manages agent instances
- → ConversationManager: Orchestrates conversations
- ← User: GUI interactions

---

### .env.example
**Purpose**: Template for environment variables
**Type**: Configuration
**Contains**: API key placeholders

Required variables:
- `GOOGLE_API_KEY`
- `OPENAI_API_KEY`
- `ALPHA_VANTAGE_KEY`

---

### requirements.txt
**Purpose**: Python package dependencies
**Type**: Configuration
**Key Packages**:
- langchain-google-genai
- langgraph
- chromadb
- yfinance
- pandas
- tkinter (built-in)

---

### agent_prompts.json
**Purpose**: Centralized agent prompt templates
**Type**: Data
**Structure**:
```json
{
  "analysts": {...},
  "researchers": {...},
  "managers": {...},
  "risk_analysts": {...},
  "trader": {...}
}
```

**Used By**: Agents for system prompts

---

## tradingagents/ - Core Library

### tradingagents/config.py
**Purpose**: System-wide configuration
**Type**: Configuration Module
**Exports**: `DEFAULT_CONFIG` dictionary

**Key Settings**:
- `llm_provider`: "google"
- `deep_think_llm`: "gemini-1.5-pro"
- `quick_think_llm`: "gemini-2.0-flash-exp"
- `max_debate_rounds`: 1
- `data_vendors`: Data source routing config

**Used By**: All modules for configuration

---

### tradingagents/agent_pool.py
**Purpose**: Agent lifecycle management
**Type**: Orchestration Module
**Dependencies**: All agent factories, memory system

**Classes**:

#### `AgentRegistry`
**Purpose**: Static registry of all agents
**Type**: Class (no instances, all classmethods)

**Attributes**:
- `AGENT_TYPES`: Nested dict of all agent definitions

**Methods**:
- `get_all_agents()`: Returns full registry
- `get_agent_info(category, agent_id)`: Get specific agent metadata
- `list_all_agents()`: Flattened list of agents

**Data Structure**:
```python
{
  "category": {
    "agent_id": {
      "name": str,
      "description": str,
      "factory": callable,
      "requires_memory": bool
    }
  }
}
```

#### `AgentPool`
**Purpose**: Manage active agent instances
**Type**: Class (instantiated)

**Attributes**:
- `config`: Configuration dict
- `llm_quick`: ChatGoogleGenerativeAI instance (flash)
- `llm_deep`: ChatGoogleGenerativeAI instance (pro)
- `memories`: Dict of FinancialSituationMemory instances
- `active_agents`: Dict of active agent instances

**Methods**:
- `__init__(config)`: Initialize pool
- `_initialize_llms()`: Create LLM instances
- `_get_or_create_memory(name)`: Memory management
- `add_agent(category, agent_id)`: Instantiate and add agent
- `remove_agent(category, agent_id)`: Remove agent
- `get_agent(category, agent_id)`: Retrieve agent
- `get_active_agents()`: List active agents
- `clear()`: Remove all agents

**Communication**:
- → Agent factories: Creates instances
- → LLM providers: Initializes models
- → Memory system: Creates memories
- ← ConversationManager: Used for conversation
- ← TradingAgentsGraph: Used for workflow

---

### tradingagents/conversation_manager.py
**Purpose**: Multi-agent conversation orchestration
**Type**: Orchestration Module
**Dependencies**: agent_pool

**Classes**:

#### `ConversationManager`
**Purpose**: Orchestrate agent debates and consensus

**Attributes**:
- `agent_pool`: AgentPool instance
- `conversation_history`: List of past conversations

**Methods**:

##### Main Workflow
- `send_query_to_agents(query, context)`: Entry point
  - Returns: Complete conversation dict
  - Calls: All three phases

##### Phase 1: Collection
- `_collect_individual_responses(query, context)`: Get agent analyses
  - Returns: List of agent responses
  - Calls: _get_agent_response for each agent

- `_create_specialized_prompt(query, agent_name, category, description)`: Create prompts
  - Returns: Customized prompt string

- `_get_agent_response(agent_data, prompt, context)`: Get single agent response
  - **Current**: Returns mock response
  - **TODO**: Call actual agent with proper state
  - Returns: Agent analysis string

##### Phase 2: Debate
- `_orchestrate_debate(query, responses, context)`: Run debate rounds
  - Returns: List of debate rounds
  - Calls: _generate_* methods

- `_generate_position_statements(responses)`: Initial positions
  - Returns: List of coalition statements

- `_generate_challenges(responses)`: Cross-examination
  - Returns: List of challenges

- `_generate_consensus(responses)`: Build consensus
  - Returns: Common ground statements

##### Phase 3: Verdict
- `_generate_final_verdict(query, responses, debate)`: Create verdict
  - Returns: Verdict dict with recommendation
  - Calls: _generate_summary_text

- `_generate_summary_text(recommendation, bullish_pct, responses)`: Summary
  - Returns: Human-readable summary

##### Utility
- `get_conversation_history()`: Retrieve history
- `clear_history()`: Clear history

**Mock Response Methods** (TODO: Remove when real integration done):
- `_mock_market_analyst_response()`
- `_mock_fundamentals_analyst_response()`
- `_mock_news_analyst_response()`
- `_mock_social_analyst_response()`
- `_mock_bull_researcher_response()`
- `_mock_bear_researcher_response()`
- `_mock_risky_analyst_response()`
- `_mock_safe_analyst_response()`
- `_mock_neutral_analyst_response()`

**Communication**:
- → AgentPool: Get agent instances
- → Agents: Call for responses (TODO: not implemented yet)
- ← GUI: Receives queries, returns results

---

### tradingagents/prompt_manager.py
**Purpose**: Manage agent prompts
**Type**: Utility Module

**Functions**:
- Load prompts from agent_prompts.json
- Provide prompts to agents

**Used By**: Agents during initialization

---

## tradingagents/agents/ - Agent Implementations

### tradingagents/agents/__init__.py
**Purpose**: Agent package initialization
**Imports**: All agent creation functions and utilities

---

### tradingagents/agents/analysts/ - Data Analysis Agents

#### market_analyst.py
**Purpose**: Technical analysis expert
**Dependencies**: agent_utils, dataflows.config

**Function**: `create_market_analyst(llm)`
**Returns**: market_analyst_node function

**Agent Node**: `market_analyst_node(state)`
**Tools Used**:
- `get_stock_data(ticker, period)`: OHLCV data
- `get_indicators(ticker, indicators, period)`: Technical indicators

**Analyzes**:
- Moving averages (SMA, EMA)
- MACD, RSI, momentum
- Volume patterns
- Support/resistance
- Trend analysis

**State Updates**:
- `analyst_insights["market"]`: Technical analysis

**Output**: Technical outlook and setup analysis

---

#### fundamentals_analyst.py
**Purpose**: Fundamental analysis expert
**Dependencies**: agent_utils, dataflows.config

**Function**: `create_fundamentals_analyst(llm)`
**Returns**: fundamentals_analyst_node function

**Agent Node**: `fundamentals_analyst_node(state)`
**Tools Used**:
- `get_fundamentals(ticker)`: Company info
- `get_balance_sheet(ticker)`: Balance sheet
- `get_cashflow(ticker)`: Cash flow
- `get_income_statement(ticker)`: P&L
- `get_insider_sentiment(ticker)`: Insider trading
- `get_insider_transactions(ticker)`: Transaction details

**Analyzes**:
- P/E ratio, valuation metrics
- Revenue and profit growth
- Balance sheet strength
- Cash flow quality
- Insider activity

**State Updates**:
- `analyst_insights["fundamentals"]`: Fundamental analysis

**Output**: Valuation assessment and fundamental opinion

---

#### news_analyst.py
**Purpose**: News and sentiment analysis
**Dependencies**: agent_utils, dataflows.config

**Function**: `create_news_analyst(llm)`
**Returns**: news_analyst_node function

**Agent Node**: `news_analyst_node(state)`
**Tools Used**:
- `get_news(ticker)`: Company-specific news
- `get_global_news()`: Market-wide news

**Analyzes**:
- Recent news sentiment
- Upcoming catalysts
- Earnings announcements
- Regulatory changes
- Management commentary

**State Updates**:
- `analyst_insights["news"]`: News analysis

**Output**: News-based outlook and catalyst timeline

---

#### social_media_analyst.py
**Purpose**: Social sentiment analysis
**Dependencies**: agent_utils, dataflows.config

**Function**: `create_social_media_analyst(llm)`
**Returns**: social_media_analyst_node function

**Agent Node**: `social_media_analyst_node(state)`
**Tools Used**:
- `get_news(ticker)`: Social mentions (via news aggregation)
- Reddit/Twitter analysis

**Analyzes**:
- Retail sentiment
- Discussion volume
- Influencer opinions
- Options flow
- Crowd psychology

**State Updates**:
- `analyst_insights["social"]`: Social analysis

**Output**: Sentiment summary and crowd behavior

---

### tradingagents/agents/researchers/ - Bull/Bear Research

#### bull_researcher.py
**Purpose**: Build bullish investment cases
**Dependencies**: agent_utils, memory

**Function**: `create_bull_researcher(llm, memory)`
**Returns**: bull_researcher_node function
**Uses Memory**: YES

**Agent Node**: `bull_researcher_node(state)`
**Process**:
1. Query memory for similar bull cases
2. Analyze current positive catalysts
3. Build comprehensive bull thesis
4. Store in memory for future reference

**State Updates**:
- `bull_case`: Bullish investment thesis

**Output**: Bull case with upside potential

---

#### bear_researcher.py
**Purpose**: Identify risks and bearish scenarios
**Dependencies**: agent_utils, memory

**Function**: `create_bear_researcher(llm, memory)`
**Returns**: bear_researcher_node function
**Uses Memory**: YES

**Agent Node**: `bear_researcher_node(state)`
**Process**:
1. Query memory for similar risk scenarios
2. Identify current headwinds
3. Build bearish counter-argument
4. Store in memory

**State Updates**:
- `bear_case`: Bearish investment thesis

**Output**: Bear case with downside risk

---

### tradingagents/agents/managers/ - Decision Makers

#### research_manager.py
**Purpose**: Synthesize research into decisions
**Dependencies**: agent_utils, memory
**LLM**: Deep thinking (gemini-1.5-pro)

**Function**: `create_research_manager(llm, memory)`
**Returns**: research_manager_node function
**Uses Memory**: YES

**Agent Node**: `research_manager_node(state)`
**Process**:
1. Review all analyst insights
2. Weigh bull vs bear arguments
3. Make investment recommendation
4. Store decision rationale

**State Updates**:
- `research_recommendation`: BUY/SELL/HOLD with reasoning

**Output**: Investment recommendation with confidence

---

#### risk_manager.py
**Purpose**: Final risk assessment and verdict
**Dependencies**: agent_utils, memory
**LLM**: Deep thinking (gemini-1.5-pro)

**Function**: `create_risk_manager(llm, memory)`
**Returns**: risk_manager_node function
**Uses Memory**: YES

**Agent Node**: `risk_manager_node(state)`
**Process**:
1. Review research recommendation
2. Assess risk analyst perspectives
3. Evaluate risk/reward
4. Make final recommendation

**State Updates**:
- `risk_recommendation`: Final verdict

**Output**: Final recommendation with position sizing

---

### tradingagents/agents/risk_mgmt/ - Risk Perspectives

#### aggresive_debator.py
**Purpose**: High risk tolerance perspective

**Function**: `create_risky_debator(llm)`
**Returns**: risky_debator_node function

**Advocates For**:
- Larger positions
- Momentum plays
- Higher risk/reward

**State Updates**:
- `risk_insights["risky"]`: Aggressive perspective

---

#### conservative_debator.py
**Purpose**: Capital preservation perspective

**Function**: `create_safe_debator(llm)`
**Returns**: safe_debator_node function

**Advocates For**:
- Smaller positions
- Wait for confirmation
- Protect capital

**State Updates**:
- `risk_insights["safe"]`: Conservative perspective

---

#### neutral_debator.py
**Purpose**: Balanced risk perspective

**Function**: `create_neutral_debator(llm)`
**Returns**: neutral_debator_node function

**Advocates For**:
- Moderate sizing
- Diversified approach
- Balanced risk

**State Updates**:
- `risk_insights["neutral"]`: Balanced perspective

---

### tradingagents/agents/trader/ - Trade Execution

#### trader.py
**Purpose**: Create executable trade plans
**Dependencies**: agent_utils, memory
**LLM**: Deep thinking (gemini-1.5-pro)

**Function**: `create_trader(llm, memory)`
**Returns**: trader_node function
**Uses Memory**: YES

**Agent Node**: `trader_node(state)`
**Creates**:
- Entry price levels
- Stop loss placement
- Profit targets
- Position sizing
- Execution strategy

**State Updates**:
- `trade_plan`: Detailed execution plan

**Output**: Executable trade plan

---

### tradingagents/agents/utils/ - Utilities

#### agent_states.py
**Purpose**: State type definitions
**Type**: Type Definitions

**Classes/TypeDicts**:
- `AgentState`: Main workflow state
- `InvestDebateState`: Bull/Bear debate state
- `RiskDebateState`: Risk debate state

**Fields in AgentState**:
- `company_of_interest`: Ticker
- `trade_date`: Date
- `analyst_insights`: Dict of analyst outputs
- `bull_case`: Bull thesis
- `bear_case`: Bear thesis
- `research_recommendation`: Research manager output
- `risk_insights`: Risk analyst perspectives
- `risk_recommendation`: Final verdict
- `trade_plan`: Execution plan
- `messages`: LLM message history

**Used By**: All agents, graph workflow

---

#### agent_utils.py
**Purpose**: Tool exports and utilities
**Type**: Tool Aggregation

**Exports**:
- All stock data tools
- All indicator tools
- All fundamental tools
- All news tools

**Function**: `create_msg_delete()`
**Purpose**: Message management utility

---

#### memory.py
**Purpose**: Agent memory system
**Type**: Memory Management
**Technology**: ChromaDB + OpenAI Embeddings

**Class**: `FinancialSituationMemory`
**Purpose**: Store and retrieve past analyses

**Methods**:
- `__init__(name, config)`: Initialize collection
- `get_embedding(text)`: Get OpenAI embedding
- `add_situations(situations_and_advice)`: Store learnings
- `get_relevant_situations(query, top_k)`: Retrieve similar cases
- `clear()`: Reset memory

**Storage**:
- ChromaDB collection per agent
- OpenAI text-embedding-3-small
- Similarity search for retrieval

**Used By**:
- Bull Researcher
- Bear Researcher
- Research Manager
- Risk Manager
- Trader

---

#### core_stock_tools.py
**Purpose**: Basic stock data tools
**Dependencies**: dataflows.interface

**Functions**:
- `get_stock_data(ticker, period)`: OHLCV data
- Tool wrapper for LLM integration

**Data Flow**:
→ interface.route_to_vendor()
→ Vendor (YFinance/Alpha Vantage)
← Stock price data

---

#### technical_indicators_tools.py
**Purpose**: Technical indicator tools
**Dependencies**: dataflows.interface

**Functions**:
- `get_indicators(ticker, indicators, period)`: Calculate indicators
- Supports: RSI, MACD, SMA, EMA, etc.

**Data Flow**:
→ interface.route_to_vendor()
→ Vendor + local calculation
← Indicator values

---

#### fundamental_data_tools.py
**Purpose**: Fundamental analysis tools
**Dependencies**: dataflows.interface

**Functions**:
- `get_fundamentals(ticker)`: Company info
- `get_balance_sheet(ticker)`: Balance sheet
- `get_cashflow(ticker)`: Cash flow
- `get_income_statement(ticker)`: Income statement
- `get_insider_sentiment(ticker)`: Insider trading
- `get_insider_transactions(ticker)`: Transaction details

**Data Flow**:
→ interface.route_to_vendor()
→ Alpha Vantage / Local
← Financial data

---

#### news_data_tools.py
**Purpose**: News and sentiment tools
**Dependencies**: dataflows.interface

**Functions**:
- `get_news(ticker)`: Company news
- `get_global_news()`: Market news
- `get_reddit_company_news(ticker)`: Reddit sentiment
- `get_reddit_global_news()`: Reddit market sentiment

**Data Flow**:
→ interface.route_to_vendor()
→ Alpha Vantage / Google / Reddit
← News articles and sentiment

---

## tradingagents/dataflows/ - Data Sources

### interface.py
**Purpose**: Route data requests to vendors
**Type**: Routing Layer

**Function**: `route_to_vendor(tool_name, **params)`
**Purpose**: Select and call appropriate vendor

**Routing Logic**:
1. Check `tool_vendors[tool_name]` (specific override)
2. Check `data_vendors[category]` (category default)
3. Use hardcoded default

**Categories**:
- `core_stock_apis`: Stock prices
- `technical_indicators`: Indicators
- `fundamental_data`: Financials
- `news_data`: News and sentiment

**Vendors**:
- "yfinance": Yahoo Finance
- "alpha_vantage": Alpha Vantage
- "google": Google APIs
- "local": Local/cached data

**Communication**:
- ← Tools: Receive data requests
- → Vendors: Route to appropriate vendor
- ← Vendors: Return data
- → Tools: Pass data back

---

### config.py
**Purpose**: Dataflows configuration management
**Type**: Configuration Module
**Dependencies**: tradingagents.config

**Global Variables**:
- `_config`: Current configuration
- `DATA_DIR`: Data directory path

**Functions**:
- `initialize_config()`: Load DEFAULT_CONFIG
- `set_config(config)`: Override configuration
- `get_config()`: Retrieve current configuration

**Used By**: All dataflow modules

---

### y_finance.py
**Purpose**: Yahoo Finance data provider
**Type**: Vendor Implementation
**Technology**: yfinance library

**Functions**:
- `get_YFin_data(ticker, period, interval)`: OHLCV data
- `get_indicators_yfinance(ticker, indicators)`: Calculate indicators
- `get_fundamentals_yfinance(ticker)`: Basic fundamentals

**Advantages**:
- Free, no API key
- Real-time data
- Wide coverage

**Limitations**:
- Rate limits
- Limited historical data
- Basic fundamentals only

---

### alpha_vantage*.py
**Purpose**: Alpha Vantage data providers
**Type**: Vendor Implementation
**Technology**: Alpha Vantage API

**Files**:
- `alpha_vantage.py`: Core API wrapper
- `alpha_vantage_common.py`: Shared utilities
- `alpha_vantage_stock.py`: Stock data
- `alpha_vantage_indicator.py`: Technical indicators
- `alpha_vantage_fundamentals.py`: Financial statements
- `alpha_vantage_news.py`: News and sentiment

**Functions**:
- `get_alpha_vantage_stock_data()`: Price data
- `get_alpha_vantage_indicators()`: Indicators
- `get_alpha_vantage_fundamentals()`: Financials
- `get_alpha_vantage_news()`: News articles

**Requirements**: API key (ALPHA_VANTAGE_KEY)

---

### google.py
**Purpose**: Google APIs data provider
**Type**: Vendor Implementation

**Functions**:
- `get_google_news(query)`: News search
- News aggregation and sentiment

**Requirements**: API key

---

### local.py
**Purpose**: Local/cached data provider
**Type**: Vendor Implementation

**Functions**:
- `get_YFin_data()`: Cached stock data
- `get_finnhub_news()`: Cached news
- `get_simfin_*()`: Cached financials
- `get_reddit_*()`: Cached social data

**Data Directory**: Configured in DATA_DIR

**Use Cases**:
- Offline development
- Backtesting
- Avoid rate limits

---

### Other Dataflow Files
- `openai.py`: OpenAI API wrapper
- `stockstats_utils.py`: Technical indicator calculation
- `yfin_utils.py`: Yahoo Finance utilities
- `googlenews_utils.py`: Google News parsing
- `reddit_utils.py`: Reddit API wrapper
- `utils.py`: General utilities

---

## tradingagents/graph/ - Workflow Orchestration

### trading_graph.py
**Purpose**: Main workflow definition
**Type**: Orchestration
**Technology**: LangGraph

**Class**: `TradingAgentsGraph`
**Purpose**: Execute multi-agent analysis workflow

**Methods**:
- `__init__(selected_analysts, config)`: Initialize graph
- `setup_llms()`: Create LLM instances
- `setup_memories()`: Create memory instances
- `setup_agents()`: Initialize selected agents
- `setup_graph()`: Build LangGraph workflow
- `run(ticker, trade_date)`: Execute analysis

**Workflow**:
```
START
  ↓
Selected Analysts (parallel)
  ↓
Bull + Bear Researchers (debate)
  ↓
Research Manager
  ↓
Risk Debators (parallel)
  ↓
Risk Manager
  ↓
Trader
  ↓
END
```

**Communication**:
- ← CLI/GUI: Receives analysis requests
- → Agents: Executes workflow
- ← Agents: Collects results
- → CLI/GUI: Returns final state

---

### setup.py
**Purpose**: Graph construction utilities
**Type**: Utility Module

**Functions**:
- Helper functions for building graphs
- Node and edge definitions

---

### conditional_logic.py
**Purpose**: Workflow routing logic
**Type**: Logic Module

**Functions**:
- `should_continue_debate()`: Check debate continuation
- `check_research_decision()`: Route based on strength
- `evaluate_risk_level()`: Determine risk path

**Used By**: trading_graph.py for conditional edges

---

### propagation.py
**Purpose**: State propagation utilities
**Type**: Utility Module

**Functions**:
- State copying and updating
- Ensure consistency across workflow

---

### reflection.py
**Purpose**: Agent reflection capabilities
**Type**: Enhancement Module

**Functions**:
- Enable agents to reflect on their outputs
- Self-critique and improvement

---

### signal_processing.py
**Purpose**: Signal extraction and processing
**Type**: Utility Module

**Functions**:
- Extract trading signals from agent outputs
- Process and normalize signals

---

## cli/ - Command Line Interface

### cli/__init__.py
**Purpose**: CLI package initialization

---

### cli/main.py
**Purpose**: Command-line interface entry point
**Type**: Application
**Technology**: Typer

**Commands**:
- `analyze`: Run analysis on ticker
- `config`: Manage configuration
- `list-agents`: Show available agents

**Communication**:
- → TradingAgentsGraph: Run analysis
- ← User: CLI commands

---

### cli/models.py
**Purpose**: CLI data models
**Type**: Type Definitions

**Classes**:
- `AnalystType`: Enum of analyst types
- Other CLI-specific models

---

### cli/utils.py
**Purpose**: CLI utility functions
**Type**: Utilities

**Functions**:
- Output formatting
- Table display
- Progress indicators

---

## project_documentation/ - This Documentation

### PROJECT_OVERVIEW.md
**Purpose**: High-level project overview
**Contains**: Capabilities, tech stack, use cases

### ARCHITECTURE.md
**Purpose**: Detailed system architecture
**Contains**: Component details, data flow, design patterns

### MISSING_FEATURES.md
**Purpose**: Development roadmap
**Contains**: Missing features, priorities, timeline

### FILES_INVENTORY.md
**Purpose**: This file - complete file listing

---

## Summary Statistics

**Total Python Files**: 53
**Total Agents**: 12
- Analysts: 4
- Researchers: 2
- Managers: 2
- Risk Analysts: 3
- Trader: 1

**Total Lines of Code**: ~15,000+
**Total Functions**: ~200+
**Total Classes**: ~15+

**External Dependencies**: ~20+
**Data Sources**: 4+ vendors
**LLM Providers**: 3 (Google, OpenAI, Anthropic)

---

For detailed documentation on each component, see the respective documentation files.
