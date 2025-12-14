import os
from typing import List


class APIKeyManager:
    """
    Manages multiple Gemini API keys for cycling through to avoid rate limits.

    Supports multiple formats:
    1. Single key: GEMINI_API_KEY=your_key
    2. Multiple keys (comma-separated): GEMINI_API_KEYS=key1,key2,key3
    3. Multiple keys (numbered): GEMINI_API_KEY_1=key1, GEMINI_API_KEY_2=key2, etc.
    """

    def __init__(self):
        self.api_keys: List[str] = []
        self.current_index: int = 0
        self._load_api_keys()

    def _load_api_keys(self):
        """Load API keys from environment variables."""
        # Try comma-separated list first
        keys_str = os.getenv('GEMINI_API_KEYS', '').strip()
        if keys_str:
            self.api_keys = [key.strip() for key in keys_str.split(',') if key.strip()]
            print(f"✓ Loaded {len(self.api_keys)} API keys from GEMINI_API_KEYS")
            return

        # Try numbered keys (GEMINI_API_KEY_1, GEMINI_API_KEY_2, etc.)
        numbered_keys = []
        i = 1
        while True:
            key = os.getenv(f'GEMINI_API_KEY_{i}', '').strip()
            if not key:
                break
            numbered_keys.append(key)
            i += 1

        if numbered_keys:
            self.api_keys = numbered_keys
            print(f"✓ Loaded {len(self.api_keys)} API keys from GEMINI_API_KEY_1 to GEMINI_API_KEY_{len(self.api_keys)}")
            return

        # Try single key (backward compatibility)
        single_key = os.getenv('GEMINI_API_KEY', '').strip()
        if single_key:
            self.api_keys = [single_key]
            print(f"✓ Loaded 1 API key from GEMINI_API_KEY")
            return

        raise ValueError(
            "No API keys found! Please set one of:\n"
            "  - GEMINI_API_KEY=your_key (single key)\n"
            "  - GEMINI_API_KEYS=key1,key2,key3 (comma-separated)\n"
            "  - GEMINI_API_KEY_1=key1, GEMINI_API_KEY_2=key2, etc. (numbered)"
        )

    def get_current_key(self) -> str:
        """Get the current API key."""
        if not self.api_keys:
            raise ValueError("No API keys available")
        return self.api_keys[self.current_index]

    def rotate_key(self):
        """Rotate to the next API key."""
        if len(self.api_keys) > 1:
            self.current_index = (self.current_index + 1) % len(self.api_keys)
            print(f"  🔄 Rotated to API key {self.current_index + 1}/{len(self.api_keys)}")

    def get_next_key(self) -> str:
        """Get the next API key and rotate."""
        self.rotate_key()
        return self.get_current_key()

    def get_key_count(self) -> int:
        """Get the total number of API keys."""
        return len(self.api_keys)

    def reset(self):
        """Reset to the first API key."""
        self.current_index = 0
