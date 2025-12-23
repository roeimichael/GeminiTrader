import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tradingagents.agent_pool import AgentRegistry, AgentPool
from src.tradingagents.config import DEFAULT_CONFIG

class AgentSelectorInterface:
    def __init__(self):
        load_dotenv()
        self.registry = AgentRegistry()
        self.pool = AgentPool(DEFAULT_CONFIG)

    def display_header(self):
        print("\n" + "="*80)
        print("TRADINGAGENTS - AGENT SELECTOR INTERFACE")
        print("="*80 + "\n")

    def display_all_agents(self):
        """Display all available agents organized by category"""
        all_agents = self.registry.get_all_agents()

        print("Available Agents:\n")

        for category, agents in all_agents.items():
            print(f"\n{category.upper().replace('_', ' ')}:")
            print("-" * 40)

            for agent_id, info in agents.items():
                print(f"  [{agent_id}] {info['name']}")
                print(f"      {info['description']}")

    def display_active_agents(self):
        """Display currently active agents"""
        active = self.pool.get_active_agents()

        print("\nActive Agents Pool:")
        print("-" * 40)

        if not active:
            print("  (none)")
        else:
            for agent in active:
                print(f"  [{agent['category']}:{agent['id']}] {agent['name']}")

    def add_agent_interactive(self):
        """Interactive agent addition"""
        print("\nAdd Agent")
        print("-" * 40)

        category = input("Category (analysts/researchers/managers/risk_analysts/trader): ").strip()

        if category not in self.registry.get_all_agents():
            print(f"Invalid category: {category}")
            return

        agents_in_category = self.registry.get_all_agents()[category]
        print(f"\nAvailable in {category}:")
        for agent_id in agents_in_category.keys():
            print(f"  - {agent_id}")

        agent_id = input(f"\nAgent ID: ").strip()

        try:
            self.pool.add_agent(category, agent_id)
            print(f"Added: {agents_in_category[agent_id]['name']}")
        except Exception as e:
            print(f"Error: {e}")

    def remove_agent_interactive(self):
        """Interactive agent removal"""
        active = self.pool.get_active_agents()

        if not active:
            print("\nNo active agents to remove.")
            return

        print("\nActive Agents:")
        for i, agent in enumerate(active, 1):
            print(f"  {i}. [{agent['category']}:{agent['id']}] {agent['name']}")

        try:
            choice = int(input("\nSelect agent to remove (number): ").strip())
            if 1 <= choice <= len(active):
                agent = active[choice - 1]
                self.pool.remove_agent(agent['category'], agent['id'])
                print(f"Removed: {agent['name']}")
            else:
                print("Invalid choice")
        except ValueError:
            print("Invalid input")

    def quick_setup(self):
        """Quick setup with predefined configurations"""
        print("\nQuick Setup Options:")
        print("-" * 40)
        print("1. Full Analysis (All Analysts + Researchers + Managers + Risk)")
        print("2. Basic Analysis (Market + Fundamentals)")
        print("3. Research Debate (Market + Fundamentals + Bull + Bear + Manager)")
        print("4. Custom")

        choice = input("\nSelect option (1-4): ").strip()

        self.pool.clear()

        if choice == "1":
            self.pool.add_agent("analysts", "market")
            self.pool.add_agent("analysts", "fundamentals")
            self.pool.add_agent("analysts", "news")
            self.pool.add_agent("analysts", "social")
            self.pool.add_agent("researchers", "bull")
            self.pool.add_agent("researchers", "bear")
            self.pool.add_agent("managers", "research")
            self.pool.add_agent("trader", "trader")
            self.pool.add_agent("risk_analysts", "risky")
            self.pool.add_agent("risk_analysts", "safe")
            self.pool.add_agent("risk_analysts", "neutral")
            self.pool.add_agent("managers", "risk")
            print("Configured: Full Analysis")

        elif choice == "2":
            self.pool.add_agent("analysts", "market")
            self.pool.add_agent("analysts", "fundamentals")
            print("Configured: Basic Analysis")

        elif choice == "3":
            self.pool.add_agent("analysts", "market")
            self.pool.add_agent("analysts", "fundamentals")
            self.pool.add_agent("researchers", "bull")
            self.pool.add_agent("researchers", "bear")
            self.pool.add_agent("managers", "research")
            print("Configured: Research Debate")

        elif choice == "4":
            print("Use 'add' command to add agents manually")

    def export_config(self):
        """Export current configuration"""
        import json

        active = self.pool.get_active_agents()
        config = {
            "agents": [
                {"category": agent["category"], "id": agent["id"]}
                for agent in active
            ]
        }

        filename = input("Export filename (default: agent_config.json): ").strip()
        if not filename:
            filename = "agent_config.json"

        with open(filename, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"Configuration exported to {filename}")

    def import_config(self):
        """Import configuration from file"""
        import json

        filename = input("Import filename: ").strip()

        try:
            with open(filename, 'r') as f:
                config = json.load(f)

            self.pool.clear()

            for agent in config.get("agents", []):
                self.pool.add_agent(agent["category"], agent["id"])

            print(f"Configuration imported from {filename}")
        except FileNotFoundError:
            print(f"File not found: {filename}")
        except Exception as e:
            print(f"Error: {e}")

    def run_menu(self):
        """Main menu loop"""
        while True:
            self.display_header()
            self.display_active_agents()

            print("\nCommands:")
            print("  [list]    - Show all available agents")
            print("  [add]     - Add an agent to the pool")
            print("  [remove]  - Remove an agent from the pool")
            print("  [quick]   - Quick setup configurations")
            print("  [export]  - Export current configuration")
            print("  [import]  - Import configuration")
            print("  [clear]   - Clear all agents")
            print("  [run]     - Run analysis with current agents")
            print("  [exit]    - Exit")

            command = input("\nCommand: ").strip().lower()

            if command == "list":
                self.display_all_agents()
                input("\nPress Enter to continue...")

            elif command == "add":
                self.add_agent_interactive()

            elif command == "remove":
                self.remove_agent_interactive()

            elif command == "quick":
                self.quick_setup()

            elif command == "export":
                self.export_config()

            elif command == "import":
                self.import_config()

            elif command == "clear":
                self.pool.clear()
                print("All agents cleared")

            elif command == "run":
                print("\nRunning analysis with current agents...")
                print("(Analysis execution coming in next version)")
                input("\nPress Enter to continue...")

            elif command == "exit":
                print("\nGoodbye!")
                break

            else:
                print(f"Unknown command: {command}")


def main():
    interface = AgentSelectorInterface()
    interface.run_menu()


if __name__ == "__main__":
    main()
