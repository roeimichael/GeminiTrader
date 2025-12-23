import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tradingagents.agent_pool import AgentRegistry, AgentPool
from src.tradingagents.config import DEFAULT_CONFIG

def main():
    load_dotenv()

    print("="*80)
    print("TRADINGAGENTS - INITIALIZE ALL AGENTS")
    print("="*80 + "\n")

    pool = AgentPool(DEFAULT_CONFIG)

    all_agents = AgentRegistry.list_all_agents()

    print(f"Found {len(all_agents)} agent types\n")

    print("Initializing all agents...")
    print("-" * 80)

    for agent_info in all_agents:
        category = agent_info["category"]
        agent_id = agent_info["id"]
        name = agent_info["name"]

        try:
            pool.add_agent(category, agent_id)
            print(f"  OK   [{category:15}] {name}")
        except Exception as e:
            print(f"  FAIL [{category:15}] {name}: {e}")

    print("\n" + "="*80)
    print("INITIALIZATION COMPLETE")
    print("="*80 + "\n")

    active = pool.get_active_agents()
    print(f"Active Agents: {len(active)}\n")

    print("Agents by Category:")
    print("-" * 80)

    categories = {}
    for agent in active:
        cat = agent["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(agent)

    for category, agents in categories.items():
        print(f"\n{category.upper().replace('_', ' ')}:")
        for agent in agents:
            print(f"  - {agent['name']}")
            print(f"    {agent['description']}")

    print("\n" + "="*80)
    print("All agents initialized and ready for use!")
    print("="*80)


if __name__ == "__main__":
    main()
