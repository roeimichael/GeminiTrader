"""
Quick API Test Script for GeminiTrader

Fast tests for basic functionality during development.
Run with: python test_api_quick.py
"""

import requests
import sys

API_BASE_URL = "http://localhost:8000"


def test_quick():
    """Quick smoke test of critical endpoints"""
    print("🔍 Quick API Test\n")

    # 1. Health Check
    print("1. Health Check...", end=" ")
    try:
        r = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        if r.status_code == 200:
            print("✓")
        else:
            print(f"✗ (status: {r.status_code})")
            return False
    except Exception as e:
        print(f"✗ ({e})")
        return False

    # 2. Get Agents
    print("2. Get Agents...", end=" ")
    try:
        r = requests.get(f"{API_BASE_URL}/api/agents", timeout=10)
        if r.status_code == 200:
            agents = r.json()
            total = sum(len(v) for v in agents.values())
            print(f"✓ ({total} agents)")
        else:
            print(f"✗ (status: {r.status_code})")
            return False
    except Exception as e:
        print(f"✗ ({e})")
        return False

    # 3. Initialize Pool
    print("3. Initialize Pool...", end=" ")
    try:
        payload = {
            "selected_agents": ["market_analyst", "fundamentals_analyst"],
            "session_id": "quick_test"
        }
        r = requests.post(f"{API_BASE_URL}/api/initialize-pool", json=payload, timeout=30)
        if r.status_code == 200:
            print("✓")
        else:
            print(f"✗ (status: {r.status_code})")
            print(f"   Error: {r.text}")
            return False
    except Exception as e:
        print(f"✗ ({e})")
        return False

    # 4. List Sessions
    print("4. List Sessions...", end=" ")
    try:
        r = requests.get(f"{API_BASE_URL}/api/sessions", timeout=10)
        if r.status_code == 200:
            data = r.json()
            print(f"✓ ({data['total']} active)")
        else:
            print(f"✗ (status: {r.status_code})")
            return False
    except Exception as e:
        print(f"✗ ({e})")
        return False

    # 5. Delete Session
    print("5. Delete Session...", end=" ")
    try:
        r = requests.delete(f"{API_BASE_URL}/api/session/quick_test", timeout=10)
        if r.status_code == 200:
            print("✓")
        else:
            print(f"✗ (status: {r.status_code})")
            return False
    except Exception as e:
        print(f"✗ ({e})")
        return False

    print("\n✅ All quick tests passed!")
    return True


if __name__ == "__main__":
    success = test_quick()
    sys.exit(0 if success else 1)
