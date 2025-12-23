import json
import os
from pathlib import Path

class PromptManager:
    def __init__(self, prompts_file='agent_prompts.json'):
        self.prompts_file = self._find_prompts_file(prompts_file)
        self.prompts = self._load_prompts()

    def _find_prompts_file(self, filename):
        current_dir = Path(__file__).parent
        prompts_path = current_dir.parent / filename
        if prompts_path.exists():
            return str(prompts_path)

        prompts_path = Path(filename)
        if prompts_path.exists():
            return str(prompts_path)

        raise FileNotFoundError(f"Prompts file not found: {filename}")

    def _load_prompts(self):
        with open(self.prompts_file, 'r') as f:
            return json.load(f)

    def get_system_base(self):
        return self.prompts.get('system_base', '')

    def get_analyst_prompt(self, analyst_type):
        return self.prompts.get('analysts', {}).get(analyst_type, {}).get('prompt', '')

    def get_researcher_prompt(self, researcher_type):
        return self.prompts.get('researchers', {}).get(researcher_type, {}).get('prompt', '')

    def get_manager_prompt(self, manager_type):
        return self.prompts.get('managers', {}).get(manager_type, {}).get('prompt', '')

    def get_trader_prompt(self):
        return self.prompts.get('trader', {}).get('prompt', '')

    def get_risk_analyst_prompt(self, risk_type):
        return self.prompts.get('risk_analysts', {}).get(risk_type, {}).get('prompt', '')

_prompt_manager_instance = None

def get_prompt_manager():
    global _prompt_manager_instance
    if _prompt_manager_instance is None:
        _prompt_manager_instance = PromptManager()
    return _prompt_manager_instance
