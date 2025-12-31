# Gemini Model Configuration Issue Summary

## Current Error
```
404 NOT_FOUND: models/gemini-1.5-flash is not found for API version v1beta,
or is not supported for generateContent.
```

## Problem
The model name `gemini-1.5-flash` is not recognized by the Google Gemini API v1beta endpoint.

## All Locations Using Gemini Models

### 1. **tradingagents/config.py** (Lines 13-14)
**Purpose:** Central configuration for all LLM model names
```python
"deep_think_llm": "gemini-1.5-pro",
"quick_think_llm": "gemini-1.5-flash",  # ❌ THIS MODEL NAME FAILS
```

### 2. **tradingagents/agent_pool.py** (Lines 148-156)
**Purpose:** Initialize LLMs for agent pool (used by REST API)
**Method:** `AgentPool._initialize_llms()`
```python
self.llm_quick = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",  # ❌ HARD-CODED, FAILS
    google_api_key=api_key
)

self.llm_deep = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",  # ❓ May also fail
    google_api_key=api_key
)
```

### 3. **tradingagents/graph/trading_graph.py** (Lines 76-77)
**Purpose:** Initialize LLMs for multi-agent graph execution
**Method:** `TradingAgentsGraph.__init__()`
```python
self.deep_thinking_llm = ChatGoogleGenerativeAI(
    model=self.config["deep_think_llm"]  # Uses config: "gemini-1.5-pro"
)
self.quick_thinking_llm = ChatGoogleGenerativeAI(
    model=self.config["quick_think_llm"]  # Uses config: "gemini-1.5-flash" ❌
)
```

### 4. **tradingagents/query_classifier.py** (Lines 19-22)
**Purpose:** Initialize LLM for query classification (route to appropriate agents)
**Method:** `QueryClassifier.__init__()`
```python
self.llm = ChatGoogleGenerativeAI(
    model=self.config.get("quick_think_llm", "gemini-1.5-flash"),  # ❌ FAILS
    temperature=0.0
)
```

## Why Each Location Exists

| Location | Used By | When It's Called | Purpose |
|----------|---------|------------------|---------|
| `config.py` | All components | App initialization | Central config read by TradingAgentsGraph |
| `agent_pool.py` | REST API | `/api/initialize-pool` endpoint | Creates agents for API sessions |
| `trading_graph.py` | Core engine | Every query analysis | Orchestrates multi-agent workflow |
| `query_classifier.py` | Pre-processing | Every `/api/query` request | Decides which agents to activate |

## Previous Model History

1. **Original:** `gemini-2.0-flash-exp` (10 req/min quota - too restrictive)
2. **Current:** `gemini-1.5-flash` (404 NOT_FOUND error)
3. **Deep model:** `gemini-1.5-pro` (status unknown - may also fail)

## Potential Solutions to Ask Gemini About

### 1. **Correct Model Name Format**
Ask: "What is the correct model name for Gemini 1.5 Flash when using langchain-google-genai with API version v1beta?"

Possibilities:
- `gemini-1.5-flash-latest`
- `gemini-1.5-flash-001`
- `models/gemini-1.5-flash`
- Different naming convention entirely

### 2. **List Available Models**
Ask: "How do I call ListModels to see all available Gemini models and their supported methods for the v1beta API?"

This would show:
- All available model names
- Which models support `generateContent`
- Correct naming format

### 3. **Alternative Stable Models**
Ask: "What Gemini models are available with higher quota limits than gemini-2.0-flash-exp (which has 10 req/min) and support the generateContent method?"

Requirements:
- Support for `generateContent` in v1beta API
- Higher quota than 10 requests/minute
- Suitable for fast inference (analyst agents run in parallel)

### 4. **API Version Compatibility**
Ask: "Does gemini-1.5-flash require a different API version than v1beta? Should I use v1 or v1alpha instead?"

## Technical Context for Gemini

**Library:** `langchain-google-genai` (Python)
**Framework:** LangGraph for multi-agent orchestration
**Use Case:**
- 3-4 analyst agents run in PARALLEL (concurrent LLM calls)
- Each agent makes multiple tool calls (5-10 calls per analysis)
- Total: 15-40 LLM requests per user query

**Current Bottleneck:**
- `gemini-2.0-flash-exp`: 10 requests/minute quota (exhausted immediately)
- `gemini-1.5-flash`: Returns 404 (model not found)

**What We Need:**
- Fast inference model (similar to Flash series)
- Quota ≥ 60 requests/minute (to support parallel execution)
- Compatible with LangChain's `ChatGoogleGenerativeAI` wrapper

## Files to Update Once You Get the Correct Model Name

1. `tradingagents/config.py` - Line 14 (quick_think_llm)
2. `tradingagents/config.py` - Line 13 (deep_think_llm) if needed
3. `tradingagents/agent_pool.py` - Lines 149 and 154
4. `tradingagents/query_classifier.py` - Line 20 (fallback default)

All changes pushed to branch: `claude/refactor-api-backend-O96OJ`

## Quick Diagnostic Tool

Run this script to see all available models in your Google AI account:

```bash
python list_gemini_models.py
```

This will show:
- All models that support `generateContent` method
- Model names, display names, and descriptions
- Recommended models for quick thinking (Flash series)
- Recommended models for deep thinking (Pro series)
