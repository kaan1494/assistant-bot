"""
Minimal super intelligence fallback module.
"""

class _SuperIntelligence:
    def __init__(self):
        self.ready = True


super_intelligence = _SuperIntelligence()


async def handle_super_intelligent_message(message: str, user_id=None) -> str:
    return ""


def initialize_super_intelligence() -> bool:
    return True
