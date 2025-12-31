"""
Comprehensive API Test Script for GeminiTrader

Tests all API endpoints with various scenarios to ensure everything works correctly.
Run with: python test_api.py
"""

import requests
import time
import json
from typing import Dict, Any
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"
TIMEOUT = 120  # 2 minutes for analysis queries


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_test_header(test_name: str):
    """Print formatted test header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}TEST: {test_name}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")


def print_success(message: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")


def print_error(message: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")


def print_warning(message: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")


def print_info(message: str):
    """Print info message"""
    print(f"  {message}")


def test_health_check() -> bool:
    """Test health check endpoint"""
    print_test_header("Health Check")
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"API is healthy (v{data['version']})")
            print_info(f"Active sessions: {data['active_sessions']}")
            print_info(f"Timestamp: {data['timestamp']}")
            return True
        else:
            print_error(f"Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Health check failed: {e}")
        return False


def test_get_agents() -> Dict[str, Any]:
    """Test getting available agents"""
    print_test_header("Get Available Agents")
    try:
        response = requests.get(f"{API_BASE_URL}/api/agents", timeout=10)
        if response.status_code == 200:
            agents = response.json()
            total_agents = sum(len(category_agents) for category_agents in agents.values())
            print_success(f"Retrieved {total_agents} agents across {len(agents)} categories")

            for category, category_agents in agents.items():
                print_info(f"{category}: {len(category_agents)} agents")
                for agent_id, info in category_agents.items():
                    print_info(f"  - {agent_id}: {info['name']}")

            return agents
        else:
            print_error(f"Failed to get agents: {response.status_code}")
            print_error(f"Response: {response.text}")
            return {}
    except Exception as e:
        print_error(f"Failed to get agents: {e}")
        return {}


def test_initialize_pool(session_id: str, selected_agents: list) -> bool:
    """Test initializing agent pool"""
    print_test_header(f"Initialize Pool - Session: {session_id}")
    print_info(f"Selected agents: {', '.join(selected_agents)}")

    try:
        payload = {
            "selected_agents": selected_agents,
            "session_id": session_id
        }

        response = requests.post(
            f"{API_BASE_URL}/api/initialize-pool",
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            print_success(f"Initialized {data['agent_count']} agents")
            print_info(f"Session ID: {data['session_id']}")
            print_info(f"Message: {data['message']}")
            return True
        else:
            print_error(f"Failed to initialize pool: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Failed to initialize pool: {e}")
        return False


def test_query_analysis(session_id: str, ticker: str, query: str, should_succeed: bool = True) -> Dict[str, Any]:
    """Test running stock analysis"""
    print_test_header(f"Query Analysis - {ticker}")
    print_info(f"Query: {query}")
    print_info(f"Session: {session_id}")

    try:
        payload = {
            "query": query,
            "ticker": ticker,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "session_id": session_id
        }

        print_info("Sending query (this may take 30-60 seconds)...")
        start_time = time.time()

        response = requests.post(
            f"{API_BASE_URL}/api/query",
            json=payload,
            timeout=TIMEOUT
        )

        elapsed = time.time() - start_time

        if response.status_code == 200:
            data = response.json()
            print_success(f"Analysis completed in {elapsed:.1f}s")
            print_info(f"Status: {data['status']}")
            print_info(f"Ticker: {data['ticker']}")
            print_info(f"Recommendation: {data['final_verdict']['overall_recommendation']}")
            print_info(f"Confidence: {data['final_verdict']['confidence_level']}")
            print_info(f"Analysts used: {len(data['individual_responses'])}")
            print_info(f"Debate rounds: {len(data['debate'])}")
            return data
        elif response.status_code == 400 and not should_succeed:
            print_warning(f"Query failed as expected: {response.status_code}")
            print_info(f"Error: {response.json().get('detail', 'Unknown error')}")
            return {}
        else:
            print_error(f"Query failed with status {response.status_code}")
            print_error(f"Response: {response.text}")
            return {}
    except Exception as e:
        if should_succeed:
            print_error(f"Query failed: {e}")
        else:
            print_warning(f"Query failed as expected: {e}")
        return {}


def test_list_sessions() -> Dict[str, Any]:
    """Test listing active sessions"""
    print_test_header("List Active Sessions")

    try:
        response = requests.get(f"{API_BASE_URL}/api/sessions", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Found {data['total']} active session(s)")
            for sid, session_info in data['sessions'].items():
                print_info(f"Session: {sid}")
                print_info(f"  Created: {session_info['created_at']}")
                print_info(f"  Agents: {session_info['agent_count']} ({', '.join(session_info['agents'])})")
            return data
        else:
            print_error(f"Failed to list sessions: {response.status_code}")
            return {}
    except Exception as e:
        print_error(f"Failed to list sessions: {e}")
        return {}


def test_get_history(session_id: str) -> list:
    """Test getting query history"""
    print_test_header(f"Get History - Session: {session_id}")

    try:
        response = requests.get(
            f"{API_BASE_URL}/api/history",
            params={"session_id": session_id, "limit": 10},
            timeout=10
        )

        if response.status_code == 200:
            history = response.json()
            print_success(f"Retrieved {len(history)} history entries")
            for i, entry in enumerate(history, 1):
                print_info(f"{i}. {entry.get('ticker', 'N/A')} - {entry.get('timestamp', 'N/A')}")
            return history
        else:
            print_error(f"Failed to get history: {response.status_code}")
            return []
    except Exception as e:
        print_error(f"Failed to get history: {e}")
        return []


def test_clear_history(session_id: str) -> bool:
    """Test clearing query history"""
    print_test_header(f"Clear History - Session: {session_id}")

    try:
        response = requests.delete(
            f"{API_BASE_URL}/api/history",
            params={"session_id": session_id},
            timeout=10
        )

        if response.status_code == 200:
            print_success("History cleared successfully")
            return True
        else:
            print_error(f"Failed to clear history: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Failed to clear history: {e}")
        return False


def test_delete_session(session_id: str) -> bool:
    """Test deleting a session"""
    print_test_header(f"Delete Session: {session_id}")

    try:
        response = requests.delete(
            f"{API_BASE_URL}/api/session/{session_id}",
            timeout=10
        )

        if response.status_code == 200:
            print_success(f"Session {session_id} deleted successfully")
            return True
        else:
            print_error(f"Failed to delete session: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Failed to delete session: {e}")
        return False


def test_debug_controls() -> bool:
    """Test debug enable/disable endpoints"""
    print_test_header("Debug Controls")

    try:
        # Enable debug
        response = requests.post(f"{API_BASE_URL}/api/debug/enable", timeout=5)
        if response.status_code == 200:
            print_success("Debug mode enabled")
        else:
            print_warning(f"Failed to enable debug: {response.status_code}")

        time.sleep(1)

        # Disable debug
        response = requests.post(f"{API_BASE_URL}/api/debug/disable", timeout=5)
        if response.status_code == 200:
            print_success("Debug mode disabled")
            return True
        else:
            print_warning(f"Failed to disable debug: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Debug controls test failed: {e}")
        return False


def run_comprehensive_tests():
    """Run all tests in a comprehensive sequence"""
    print(f"\n{Colors.BOLD}{'='*70}")
    print(f"GeminiTrader API Comprehensive Test Suite")
    print(f"{'='*70}{Colors.RESET}\n")
    print(f"Target: {API_BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}\n")

    results = {
        "passed": 0,
        "failed": 0,
        "warnings": 0
    }

    # Test 1: Health Check
    if test_health_check():
        results["passed"] += 1
    else:
        results["failed"] += 1
        print_error("Health check failed - stopping tests")
        return results

    time.sleep(1)

    # Test 2: Get Agents
    agents = test_get_agents()
    if agents:
        results["passed"] += 1
    else:
        results["failed"] += 1
        print_error("Failed to get agents - stopping tests")
        return results

    time.sleep(1)

    # Test 3: Initialize Pool with minimal agents
    session_1 = "test_session_minimal"
    minimal_agents = ["market_analyst", "fundamentals_analyst"]
    if test_initialize_pool(session_1, minimal_agents):
        results["passed"] += 1
    else:
        results["failed"] += 1

    time.sleep(2)

    # Test 4: Query with minimal setup - Valid ticker
    print_info("\nRunning analysis with valid ticker (AAPL)...")
    query_result = test_query_analysis(
        session_1,
        "AAPL",
        "What is your analysis of this stock? Should I buy or sell?",
        should_succeed=True
    )
    if query_result:
        results["passed"] += 1
    else:
        results["failed"] += 1

    time.sleep(2)

    # Test 5: Initialize Pool with more agents
    session_2 = "test_session_full"
    full_agents = [
        "market_analyst",
        "fundamentals_analyst",
        "news_analyst",
        "bull_researcher",
        "bear_researcher"
    ]
    if test_initialize_pool(session_2, full_agents):
        results["passed"] += 1
    else:
        results["failed"] += 1

    time.sleep(2)

    # Test 6: Query with full setup
    print_info("\nRunning analysis with more agents (MSFT)...")
    query_result_2 = test_query_analysis(
        session_2,
        "MSFT",
        "Should I invest in this company for long-term growth?",
        should_succeed=True
    )
    if query_result_2:
        results["passed"] += 1
    else:
        results["failed"] += 1

    time.sleep(1)

    # Test 7: List Sessions
    sessions = test_list_sessions()
    if sessions and sessions.get("total", 0) > 0:
        results["passed"] += 1
    else:
        results["warnings"] += 1
        print_warning("No sessions found or failed to retrieve")

    time.sleep(1)

    # Test 8: Get History
    history = test_get_history(session_2)
    if history:
        results["passed"] += 1
    else:
        results["warnings"] += 1
        print_warning("No history or failed to retrieve")

    time.sleep(1)

    # Test 9: Debug Controls
    if test_debug_controls():
        results["passed"] += 1
    else:
        results["warnings"] += 1

    time.sleep(1)

    # Test 10: Clear History
    if test_clear_history(session_2):
        results["passed"] += 1
    else:
        results["failed"] += 1

    time.sleep(1)

    # Test 11: Delete Sessions
    if test_delete_session(session_1):
        results["passed"] += 1
    else:
        results["failed"] += 1

    time.sleep(1)

    if test_delete_session(session_2):
        results["passed"] += 1
    else:
        results["failed"] += 1

    # Print summary
    print(f"\n{Colors.BOLD}{'='*70}")
    print(f"Test Summary")
    print(f"{'='*70}{Colors.RESET}\n")

    total = results["passed"] + results["failed"] + results["warnings"]
    print(f"{Colors.GREEN}Passed: {results['passed']}/{total}{Colors.RESET}")
    print(f"{Colors.RED}Failed: {results['failed']}/{total}{Colors.RESET}")
    print(f"{Colors.YELLOW}Warnings: {results['warnings']}/{total}{Colors.RESET}")

    if results["failed"] == 0:
        print(f"\n{Colors.BOLD}{Colors.GREEN}✓ All critical tests passed!{Colors.RESET}\n")
    else:
        print(f"\n{Colors.BOLD}{Colors.RED}✗ Some tests failed - review errors above{Colors.RESET}\n")

    return results


if __name__ == "__main__":
    try:
        results = run_comprehensive_tests()
        exit(0 if results["failed"] == 0 else 1)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Tests interrupted by user{Colors.RESET}\n")
        exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Fatal error: {e}{Colors.RESET}\n")
        exit(1)
