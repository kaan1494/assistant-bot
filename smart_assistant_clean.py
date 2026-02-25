"""
Minimal smart assistant implementation used by app.py.
"""

class SmartAssistant:
    def __init__(self, db_path: str = "data/assistant.db"):
        self.db_path = db_path

    async def process_message(self, message: str, user_id=None, user_name=None) -> str:
        return "Size nasıl yardımcı olabilirim?"
