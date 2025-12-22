from typing import List, Dict, Any
from datetime import datetime

class AgentOrchestrator:
    def __init__(self):
        self.agents = []
        self.moderator = None
        self.results = {
            "selections": [],
            "debate": [],
            "final_decision": None
        }

    def add_agent(self, agent):
        self.agents.append(agent)
        return self

    def set_moderator(self, moderator):
        self.moderator = moderator
        return self

    def run_selection_phase(self, context: Dict[str, Any] = None):
        if context is None:
            context = {"date": datetime.now().strftime("%Y-%m-%d")}

        print("\n" + "="*80)
        print("PHASE 1: STOCK SELECTION")
        print("="*80)

        for agent in self.agents:
            print(f"\n{agent.name} is selecting stocks...")
            result = agent.analyze(context)
            self.results["selections"].append(result)

            if result.get("selected_stocks"):
                print(f"  Selected: {[s['ticker'] for s in result['selected_stocks']]}")
            else:
                print(f"  Error: {result.get('error', 'Unknown error')}")

    def run_debate_phase(self, num_rounds: int = 2):
        print("\n" + "="*80)
        print("PHASE 2: DEBATE")
        print("="*80)

        context = {
            "all_selections": self.results["selections"],
            "debate_history": []
        }

        for round_num in range(num_rounds):
            print(f"\n--- Round {round_num + 1} ---")

            for agent in self.agents:
                print(f"\n{agent.name} is presenting argument...")
                result = agent.analyze(context)
                self.results["debate"].append(result)
                context["debate_history"].append(result)

                print(f"  Argument preview: {result['argument'][:200]}...")

    def run_final_decision(self):
        print("\n" + "="*80)
        print("PHASE 3: FINAL DECISION")
        print("="*80)

        if not self.moderator:
            print("No moderator set!")
            return

        context = {
            "all_selections": self.results["selections"],
            "debate_history": self.results["debate"]
        }

        print(f"\n{self.moderator.name} is making final decision...")
        result = self.moderator.analyze(context)
        self.results["final_decision"] = result

        if "final_decision" in result:
            decision = result["final_decision"]
            print(f"\nFinal Stocks: {decision.get('final_stocks', [])}")
            print(f"\nReasoning: {decision.get('reasoning', 'N/A')}")

    def run_full_analysis(self, num_debate_rounds: int = 2):
        self.run_selection_phase()
        self.run_debate_phase(num_debate_rounds)
        self.run_final_decision()
        return self.results

    def print_summary(self):
        print("\n" + "="*80)
        print("ANALYSIS SUMMARY")
        print("="*80)

        print("\nInitial Selections:")
        for sel in self.results["selections"]:
            stocks = sel.get("selected_stocks", [])
            print(f"\n{sel['agent']} ({sel['role']}):")
            for stock in stocks:
                print(f"  - {stock['ticker']}: {stock['reason']}")

        print("\n" + "-"*80)
        print("Debate Arguments:")
        for i, arg in enumerate(self.results["debate"], 1):
            print(f"\n{i}. {arg['agent']}:")
            print(f"   {arg['argument'][:300]}...")

        print("\n" + "-"*80)
        if self.results["final_decision"]:
            decision = self.results["final_decision"].get("final_decision", {})
            print("\nFinal Decision:")
            print(f"Stocks: {decision.get('final_stocks', [])}")
            print(f"\nReasoning:")
            print(f"{decision.get('reasoning', 'N/A')}")

            if "key_points" in decision:
                print(f"\nKey Points:")
                for point in decision["key_points"]:
                    print(f"  - {point}")

    def export_results(self, filename: str = "debate_results.json"):
        import json
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\nResults exported to {filename}")
