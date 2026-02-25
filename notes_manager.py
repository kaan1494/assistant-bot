import json
import os
from datetime import datetime


def _notes_path(user_id):
    return f"data/notes/user_{user_id}_notes.json"


def save_user_note(user_id, note_text):
    path = _notes_path(user_id)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    notes = []
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                notes = json.load(f)
        except Exception:
            notes = []

    note = {
        "id": len(notes) + 1,
        "text": note_text,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    notes.append(note)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)

    return note


def get_user_notes(user_id, limit=10):
    path = _notes_path(user_id)
    if not os.path.exists(path):
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            notes = json.load(f)
        notes.reverse()
        return notes[:limit]
    except Exception:
        return []
